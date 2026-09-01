"""
similar_report_finder.py - Stage 25 Similar Historical Report Linking Engine for OILPS.
Retrieves semantically similar historical safety reports using 384-D sentence embeddings and a dedicated FAISS vector index.
"""

import sys
import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from knowledge.embeddings import SafetyEmbeddingEngine
from inference.pattern_detector import RecurringPatternDetector
from inference.barrier_pattern_miner import BarrierPatternMiner

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False


class SimilarReportFinder:
    """
    Deterministic vector similarity engine for retrieving semantically similar
    historical safety reports using 384-dimensional embeddings + FAISS.
    """

    def __init__(
        self,
        top_k: int = 5,
        min_similarity: float = 0.40,
        data_path: Optional[Path] = None
    ):
        self.top_k = max(1, top_k)
        self.min_similarity = min_similarity
        self.data_path = data_path or (BASE_DIR / "datasets" / "processed" / "oilps_unified_deduped.csv")
        self.embeddings_path = BASE_DIR / "knowledge" / "historical_report_embeddings.npy"
        self.faiss_index_path = BASE_DIR / "knowledge" / "historical_reports.faiss"

        self.embedding_engine = SafetyEmbeddingEngine(model_name="all-MiniLM-L6-v2")
        self.vector_dim = self.embedding_engine.vector_dim
        
        self.records: List[Dict[str, Any]] = []
        self.record_by_id: Dict[str, Dict[str, Any]] = {}
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.faiss_index = None

        # Cross-stage pattern maps
        self.stage23_map: Dict[str, str] = {}
        self.stage24_map: Dict[str, str] = {}

        self._init_engine()

    def _init_engine(self):
        """
        Load historical incident records, generate/load embeddings, build FAISS index,
        and populate Stage 23/24 cross-stage pattern maps.
        """
        # 1. Load historical records
        detector = RecurringPatternDetector()
        self.records = detector.load_historical_records()
        self.record_by_id = {r["record_id"]: r for r in self.records}

        # 2. Build Stage 23 & Stage 24 pattern lookup maps
        try:
            s23_patterns = detector.detect_patterns(self.records)
            for pat in s23_patterns:
                for inc_id in pat["incident_ids"]:
                    self.stage23_map[inc_id] = pat["pattern_id"]

            miner = BarrierPatternMiner()
            s24_patterns = miner.mine_barrier_patterns(self.records)
            for bpat in s24_patterns:
                for inc_id in bpat["incident_ids"]:
                    self.stage24_map[inc_id] = bpat["barrier_pattern_id"]
        except Exception as e:
            pass

        if not self.records:
            return

        # 3. Generate or load cached normalized embeddings
        if self.embeddings_path.exists() and os.path.getsize(self.embeddings_path) > 0:
            self.embeddings_matrix = np.load(self.embeddings_path)
            if self.embeddings_matrix.shape[0] != len(self.records):
                self._compute_and_cache_embeddings()
        else:
            self._compute_and_cache_embeddings()

        # 4. Build or load dedicated FAISS Index (Inner Product on L2-normalized vectors = Cosine Sim)
        if HAS_FAISS:
            self.faiss_index = faiss.IndexFlatIP(self.vector_dim)
            self.faiss_index.add(self.embeddings_matrix.astype(np.float32))

    def _compute_and_cache_embeddings(self):
        """Compute 384-D normalized embeddings for all historical records and persist array."""
        texts = []
        for r in self.records:
            text = (
                f"Activity: {r['activity']}. Hazard: {r['hazard']}. "
                f"Barrier Failure: {r['barrier_failure']}. Life-Saving Rule: {r['primary_life_saving_rule']}. "
                f"{r['narrative']}"
            )
            texts.append(text)

        raw_embeddings = self.embedding_engine.encode(texts, normalize=True)
        # Ensure L2 normalization for cosine similarity
        norms = np.linalg.norm(raw_embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.embeddings_matrix = (raw_embeddings / norms).astype(np.float32)

        os.makedirs(self.embeddings_path.parent, exist_ok=True)
        np.save(self.embeddings_path, self.embeddings_matrix)

    def find_similar_reports(
        self,
        query_text: Optional[str] = None,
        query_report_id: Optional[str] = None,
        top_k: Optional[int] = None,
        min_similarity: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Find top-K semantically similar historical safety reports.
        Excludes self-match when querying by query_report_id.
        """
        k_val = top_k or self.top_k
        min_sim = min_similarity if min_similarity is not None else self.min_similarity

        if not self.records or self.embeddings_matrix is None:
            return []

        # Determine query text and vector
        target_text = ""
        exclude_id = query_report_id

        if query_report_id and query_report_id in self.record_by_id:
            rec = self.record_by_id[query_report_id]
            target_text = (
                f"Activity: {rec['activity']}. Hazard: {rec['hazard']}. "
                f"Barrier Failure: {rec['barrier_failure']}. Life-Saving Rule: {rec['primary_life_saving_rule']}. "
                f"{rec['narrative']}"
            )
        elif query_text:
            target_text = query_text.strip()

        if not target_text:
            return []

        # Encode query vector and L2-normalize
        q_vec = self.embedding_engine.encode(target_text, normalize=True)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = (q_vec / q_norm).astype(np.float32)

        if len(q_vec.shape) == 1:
            q_vec = np.expand_dims(q_vec, axis=0)

        # Execute Cosine Vector Search
        search_k = min(len(self.records), k_val * 4 + 1)

        if HAS_FAISS and self.faiss_index is not None:
            scores, indices = self.faiss_index.search(q_vec, search_k)
            sim_scores = scores[0]
            candidate_indices = indices[0]
        else:
            # Fallback numpy inner product
            sim_scores = np.dot(self.embeddings_matrix, q_vec.T).flatten()
            candidate_indices = np.argsort(-sim_scores)[:search_k]
            sim_scores = sim_scores[candidate_indices]

        similar_reports = []

        for idx, score in zip(candidate_indices, sim_scores):
            if idx < 0 or idx >= len(self.records):
                continue
            rec = self.records[idx]
            rec_id = rec["record_id"]

            # Self-match exclusion rule
            if exclude_id and rec_id == exclude_id:
                continue

            sim_val = round(float(score), 4)

            # Minimum similarity threshold filtering
            if sim_val < min_sim:
                continue

            # Deterministic explanation construction
            explanation_parts = []
            if rec.get("activity"):
                explanation_parts.append(f"Activity: {rec['activity']}")
            if rec.get("primary_life_saving_rule"):
                explanation_parts.append(f"LSR: {rec['primary_life_saving_rule']}")

            explanation = (
                f"Semantically similar historical safety report (Similarity: {int(sim_val*100)}%). "
                f"Involves {', '.join(explanation_parts) if explanation_parts else 'similar operational factors'}."
            )

            similar_item = {
                "report_id": rec_id,
                "similarity_score": sim_val,
                "similarity_percentage": int(sim_val * 100),
                "report_date": rec.get("report_date", "Unknown"),
                "location": rec.get("location", "Unspecified"),
                "activity": rec.get("activity", "General Operations"),
                "hazard": rec.get("hazard", "Operational Hazard"),
                "barrier_failure": rec.get("barrier_failure", "Control Gap"),
                "primary_life_saving_rule": rec.get("primary_life_saving_rule", "General Safety"),
                "is_sif": rec.get("is_sif", False),
                "narrative_excerpt": (rec.get("narrative") or "")[:180] + "...",
                "explanation": explanation,
                "stage23_pattern_id": self.stage23_map.get(rec_id),
                "stage24_barrier_id": self.stage24_map.get(rec_id)
            }
            similar_reports.append(similar_item)

        # Sort stably by (-similarity_score, report_id)
        similar_reports.sort(key=lambda x: (-x["similarity_score"], x["report_id"]))
        return similar_reports[:k_val]


if __name__ == "__main__":
    finder = SimilarReportFinder(top_k=5, min_similarity=0.40)
    res = finder.find_similar_reports(query_text="Technician started maintenance before electrical isolation.")
    print(f"Found {len(res)} similar historical reports.")
    if res:
        print("Top Similar Report:\n", json.dumps(res[0], indent=2))
