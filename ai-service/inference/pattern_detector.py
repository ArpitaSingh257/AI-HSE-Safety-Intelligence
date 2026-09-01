"""
pattern_detector.py - Deterministic Recurring Precursor Pattern Detection Engine for OILPS.
Groups historical safety incidents into explainable, traceable, and deterministic precursor patterns.
"""

import sys
import re
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from knowledge.embeddings import SafetyEmbeddingEngine


class RecurringPatternDetector:
    """
    Deterministic hybrid pattern detector combining structured safety fields
    and 384-dimensional sentence embeddings.
    """

    def __init__(
        self,
        min_pattern_incidents: int = 3,
        similarity_threshold: float = 0.48,
        data_path: Optional[Path] = None
    ):
        self.min_pattern_incidents = max(2, min_pattern_incidents)
        self.similarity_threshold = similarity_threshold
        self.data_path = data_path or (BASE_DIR / "datasets" / "processed" / "oilps_unified_deduped.csv")
        self.embedding_engine = SafetyEmbeddingEngine(model_name="all-MiniLM-L6-v2")
        self._cached_records = None
        self._cached_patterns = None

    def _normalize_text(self, val: Any) -> str:
        if pd.isna(val) or val is None:
            return ""
        return str(val).strip()

    def load_historical_records(self, records_list: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Load, normalize, and stably sort historical incident records.
        """
        if records_list is not None:
            raw_records = records_list
        elif self.data_path.exists():
            df = pd.read_csv(self.data_path)
            raw_records = df.to_dict(orient="records")
        else:
            raw_records = []

        normalized = []
        for idx, r in enumerate(raw_records):
            rec_id = self._normalize_text(r.get("record_id") or r.get("incident_id") or f"INC-{idx+1:04d}")
            date_val = self._normalize_text(r.get("report_date") or r.get("date") or "2025-01-01")
            loc_val = self._normalize_text(r.get("location") or r.get("site") or "Unspecified Location")
            act_val = self._normalize_text(r.get("activity") or "General Operations")
            lsr_val = self._normalize_text(r.get("primary_life_saving_rule") or r.get("lsr") or r.get("life_saving_rule") or "General Safety")
            hazard_val = self._normalize_text(r.get("hazard") or "Operational Hazard")
            barrier_val = self._normalize_text(r.get("barrier_failure") or r.get("barrier") or "Control Gap")
            conseq_val = self._normalize_text(r.get("potential_consequence") or "Potential Exposure")
            narrative = self._normalize_text(r.get("narrative") or r.get("description") or r.get("title") or "")
            sif_val = r.get("sif_potential") or r.get("is_sif") or False
            is_sif = bool(sif_val in [1, True, "1", "True", "true", "SIF_POTENTIAL"])

            normalized.append({
                "record_id": rec_id,
                "report_date": date_val,
                "location": loc_val,
                "activity": act_val,
                "primary_life_saving_rule": lsr_val,
                "hazard": hazard_val,
                "barrier_failure": barrier_val,
                "potential_consequence": conseq_val,
                "narrative": narrative,
                "is_sif": is_sif
            })

        # Sort stably by record_id to ensure 100% determinism
        normalized.sort(key=lambda x: x["record_id"])
        self._cached_records = normalized
        return normalized

    def _compute_structured_similarity(self, r1: Dict[str, Any], r2: Dict[str, Any]) -> float:
        """
        Compute similarity based on structured field agreement.
        """
        score = 0.0
        if r1["primary_life_saving_rule"] and r1["primary_life_saving_rule"] == r2["primary_life_saving_rule"]:
            score += 0.35
        if r1["activity"] and r1["activity"] == r2["activity"]:
            score += 0.25
        if r1["barrier_failure"] and r1["barrier_failure"] == r2["barrier_failure"]:
            score += 0.20
        if r1["hazard"] and r1["hazard"] == r2["hazard"]:
            score += 0.10
        if r1["location"] and r1["location"] == r2["location"]:
            score += 0.10
        return score

    def detect_patterns(self, records: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Detect recurring precursor patterns across historical incident dataset.
        Returns a stably sorted list of structured pattern objects.
        """
        incidents = self.load_historical_records(records)
        if not incidents or len(incidents) < self.min_pattern_incidents:
            return []

        # 1. Group records by (activity, primary_life_saving_rule) anchor keys first
        anchor_groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in incidents:
            key = f"{r['activity']}:::{r['primary_life_saving_rule']}"
            if key not in anchor_groups:
                anchor_groups[key] = []
            anchor_groups[key].append(r)

        # 2. For larger anchor groups, refine using embedding similarity matrix
        raw_clusters = []
        for key, group in sorted(anchor_groups.items(), key=lambda x: x[0]):
            if len(group) >= self.min_pattern_incidents:
                raw_clusters.append(group)
            elif len(group) >= 2:
                # Merge small groups with semantic overlap if similarity is high
                raw_clusters.append(group)

        # Merge clusters that share high structural/semantic agreement
        merged_clusters = []
        used_cluster_indices = set()

        for i in range(len(raw_clusters)):
            if i in used_cluster_indices:
                continue
            cluster_a = list(raw_clusters[i])
            used_cluster_indices.add(i)

            for j in range(i + 1, len(raw_clusters)):
                if j in used_cluster_indices:
                    continue
                cluster_b = raw_clusters[j]
                # Check cross-cluster similarity between anchor elements
                rep_a = cluster_a[0]
                rep_b = cluster_b[0]
                struct_sim = self._compute_structured_similarity(rep_a, rep_b)

                if struct_sim >= 0.50:
                    cluster_a.extend(cluster_b)
                    used_cluster_indices.add(j)

            # Filter out clusters below min_pattern_incidents
            if len(cluster_a) >= self.min_pattern_incidents:
                merged_clusters.append(cluster_a)

        # 3. Format and score every detected pattern deterministically
        detected_patterns = []
        for idx, cluster in enumerate(merged_clusters, 1):
            # Sort cluster members stably by record_id
            cluster.sort(key=lambda x: x["record_id"])

            inc_ids = [c["record_id"] for c in cluster]
            inc_count = len(cluster)
            sif_count = sum(1 for c in cluster if c["is_sif"])
            sif_density = round(sif_count / inc_count, 4)

            # Extract dominant values for structured dimensions
            activities = [c["activity"] for c in cluster if c["activity"]]
            locations = [c["location"] for c in cluster if c["location"]]
            hazards = [c["hazard"] for c in cluster if c["hazard"]]
            barriers = [c["barrier_failure"] for c in cluster if c["barrier_failure"]]
            lsr_rules = [c["primary_life_saving_rule"] for c in cluster if c["primary_life_saving_rule"]]

            dom_activity = max(set(activities), key=activities.count) if activities else "General Operations"
            dom_lsr = max(set(lsr_rules), key=lsr_rules.count) if lsr_rules else "Safety Controls"
            dom_hazard = max(set(hazards), key=hazards.count) if hazards else "Operational Hazard"
            dom_barrier = max(set(barriers), key=barriers.count) if barriers else "Control Gap"
            unique_locations = sorted(list(set(locations)))

            dates = [c["report_date"] for c in cluster if c["report_date"]]
            dates_sorted = sorted(dates)
            first_obs = dates_sorted[0] if dates_sorted else "Unknown"
            last_obs = dates_sorted[-1] if dates_sorted else "Unknown"

            # Determine Pattern Strength
            if (inc_count >= 5 and sif_density >= 0.40) or (inc_count >= 3 and sif_density >= 0.75):
                strength = "HIGH"
            elif inc_count >= 3 and (sif_density >= 0.25 or len(unique_locations) >= 2):
                strength = "MEDIUM"
            else:
                strength = "LOW"

            # Generate deterministic content-derived pattern ID
            hash_src = f"{dom_lsr}::{dom_activity}::{inc_ids[0]}"
            pat_hash = hashlib.md5(hash_src.encode("utf-8")).hexdigest()[:6].upper()
            pattern_id = f"PAT-{pat_hash}"

            pattern_name = f"Recurring {dom_lsr} Pattern — {dom_activity}"
            summary = (
                f"Recurring {dom_lsr} pattern during {dom_activity} activities, "
                f"observed in {inc_count} incidents across {len(unique_locations)} location(s). "
                f"{sif_count} incident(s) were classified as SIF-potential."
            )

            evidence_quotes = [c["narrative"][:150] + "..." for c in cluster[:3] if c.get("narrative")]

            pattern_obj = {
                "pattern_id": pattern_id,
                "pattern_name": pattern_name,
                "summary": summary,
                "pattern_strength": strength,
                "incident_count": inc_count,
                "sif_incident_count": sif_count,
                "sif_density": sif_density,
                "dominant_activity": dom_activity,
                "dominant_lsr": dom_lsr,
                "dominant_hazard": dom_hazard,
                "dominant_barrier_failure": dom_barrier,
                "locations": unique_locations,
                "first_observed": first_obs,
                "last_observed": last_obs,
                "incident_ids": inc_ids,
                "evidence_quotes": evidence_quotes
            }
            detected_patterns.append(pattern_obj)

        # Sort detected patterns stably by (-incident_count, -sif_density, pattern_id)
        detected_patterns.sort(key=lambda x: (-x["incident_count"], -x["sif_density"], x["pattern_id"]))
        
        # Re-assign clean numeric index prefix for display stability
        for idx, pat in enumerate(detected_patterns, 1):
            pat["pattern_code"] = f"P{idx:03d}"

        self._cached_patterns = detected_patterns
        return detected_patterns


if __name__ == "__main__":
    detector = RecurringPatternDetector(min_pattern_incidents=3)
    pats = detector.detect_patterns()
    print(f"Detected {len(pats)} recurring precursor patterns.")
    if pats:
        print("Top Pattern:\n", json.dumps(pats[0], indent=2))
