"""
retriever.py - FAISS Vector Index and Top-K Similarity Search for Safety Corpus.
"""

import sys
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from knowledge.embeddings import SafetyEmbeddingEngine
from knowledge.metadata import save_json, load_json

logger = logging.getLogger("OILPS_Retriever")
logging.basicConfig(level=logging.INFO)

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False


class VectorRetriever:
    """
    FAISS / Vector Index Retriever for Safety Reference Chunks.
    """

    def __init__(self, embedding_engine: Optional[SafetyEmbeddingEngine] = None):
        self.embedding_engine = embedding_engine or SafetyEmbeddingEngine()
        self.index_dir = BASE_DIR / "datasets" / "rag"
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.faiss_index = None
        self.metadata_store: List[Dict[str, Any]] = []
        self.embeddings_matrix: Optional[np.ndarray] = None
        self.vector_dim = self.embedding_engine.vector_dim

    def build_index(self, chunks: List[Dict[str, Any]]):
        """
        Build and persist vector index from semantic chunks list.
        """
        if not chunks:
            logger.warning("No chunks provided to build_index.")
            return

        logger.info(f"Encoding {len(chunks)} chunks for vector store...")
        texts = [c["text"] for c in chunks]
        embeddings = self.embedding_engine.encode(texts, normalize=True)

        self.metadata_store = chunks
        self.embeddings_matrix = embeddings

        if HAS_FAISS:
            self.faiss_index = faiss.IndexFlatIP(self.vector_dim)
            self.faiss_index.add(embeddings)
            faiss.write_index(self.faiss_index, str(self.index_dir / "vector_index.faiss"))
            logger.info(f"FAISS Inner-Product index saved to {self.index_dir / 'vector_index.faiss'}")
        else:
            logger.info("FAISS not installed. Operating with NumPy cosine similarity matrix.")

        # Save metadata store
        save_json(self.metadata_store, self.index_dir / "vector_metadata.json")
        # Save raw embeddings matrix for fallback
        np.save(self.index_dir / "embeddings.npy", embeddings)

    def load_index(self) -> bool:
        """
        Load index and metadata from disk if present.
        """
        meta_path = self.index_dir / "vector_metadata.json"
        emb_path = self.index_dir / "embeddings.npy"
        faiss_path = self.index_dir / "vector_index.faiss"

        if not meta_path.exists():
            return False

        self.metadata_store = load_json(meta_path)

        if HAS_FAISS and faiss_path.exists():
            self.faiss_index = faiss.read_index(str(faiss_path))
            logger.info("Loaded FAISS vector index successfully.")
        elif emb_path.exists():
            self.embeddings_matrix = np.load(emb_path)
            logger.info("Loaded NumPy embeddings matrix fallback.")

        return True

    def retrieve(self, query: str, top_k: int = 5, min_confidence: float = 0.25) -> List[Dict[str, Any]]:
        """
        Perform Top-K retrieval for query string.
        Returns list of matched chunk metadata dicts with 'similarity' score added.
        """
        if not self.metadata_store:
            success = self.load_index()
            if not success:
                logger.warning("Vector index not found on disk and not loaded.")
                return []

        query_vec = self.embedding_engine.encode(query, normalize=True)
        if query_vec.shape[0] == 0:
            return []

        results = []

        if HAS_FAISS and self.faiss_index is not None:
            scores, indices = self.faiss_index.search(query_vec, top_k)
            scores = scores[0]
            indices = indices[0]

            for score, idx in zip(scores, indices):
                if idx < 0 or idx >= len(self.metadata_store):
                    continue
                sim = float(score)
                if sim >= min_confidence:
                    item = dict(self.metadata_store[idx])
                    item["similarity"] = round(sim, 4)
                    results.append(item)
        else:
            # NumPy cosine similarity fallback
            if self.embeddings_matrix is None and emb_path.exists():
                self.embeddings_matrix = np.load(self.index_dir / "embeddings.npy")
            
            if self.embeddings_matrix is not None:
                sims = np.dot(self.embeddings_matrix, query_vec[0])
                top_indices = np.argsort(sims)[::-1][:top_k]
                for idx in top_indices:
                    sim = float(sims[idx])
                    if sim >= min_confidence:
                        item = dict(self.metadata_store[idx])
                        item["similarity"] = round(sim, 4)
                        results.append(item)

        # Keyword / token overlap fallback if vector search returns 0 results
        if not results and self.metadata_store:
            import re
            query_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', query.lower()))
            stopwords = {"this", "that", "with", "from", "have", "been", "were", "what", "which", "when", "where", "must", "should", "shall"}
            clean_query = query_words - stopwords
            
            scored_chunks = []
            for chunk in self.metadata_store:
                chunk_text = chunk.get("text", "").lower()
                chunk_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', chunk_text))
                overlap = clean_query.intersection(chunk_words)
                if overlap:
                    doc_name = chunk.get("document", "")
                    score = 0.55 + (len(overlap) * 0.04)
                    if "IOGP" in doc_name or "Fundamentals" in doc_name:
                        score += 0.10
                    item = dict(chunk)
                    item["similarity"] = round(min(0.95, score), 4)
                    scored_chunks.append((item["similarity"], item))

            scored_chunks.sort(key=lambda x: x[0], reverse=True)
            results = [c[1] for c in scored_chunks[:top_k] if c[0] >= min_confidence]

        return results


if __name__ == "__main__":
    retriever = VectorRetriever()
    res = retriever.retrieve("hydrostatic test pressure line isolated bleeder plug", top_k=3)
    print("Retrieval results count:", len(res))
    for r in res:
        print(f"[{r['similarity']}] {r['document']} (p.{r['page']}): {r['text'][:100]}...")
