"""
synthetic_sif_generator.py - Stage 36A.2 Synthetic SIF Generator & Diversity Improvement Subsystem.
Extracts real SIF safety factor pools, implements coverage-aware candidate generation,
multi-parent provenance tracking, diversity diagnostics, and strict deduplication.
Production models, RAG vector indexes, and historical datasets remain 100% frozen and isolated.
"""

import sys
import os
import re
import json
import random
import time
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

UNIFIED_DATASET_PATH = BASE_DIR / "datasets" / "processed" / "oilps_unified_deduped.csv"
SYNTHETIC_OUTPUT_DIR = BASE_DIR / "datasets" / "synthetic"
SYNTHETIC_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CANDIDATES_CSV_PATH = SYNTHETIC_OUTPUT_DIR / "synthetic_sif_candidates.csv"
METADATA_JSON_PATH = SYNTHETIC_OUTPUT_DIR / "synthetic_sif_metadata.json"
CONFIG_JSON_PATH = SYNTHETIC_OUTPUT_DIR / "generation_config.json"
VALIDATION_REPORT_PATH = SYNTHETIC_OUTPUT_DIR / "validation_report.json"

MISSING_TOKENS_REGEX = re.compile(r'\b(nan|none|null|undefined)\b', re.IGNORECASE)


def is_missing_value(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, (float, np.floating)) and np.isnan(val):
        return True
    if str(val).strip() == "" or str(val).strip().lower() in ("nan", "none", "null", "undefined", "<na>"):
        return True
    return False


def clean_generation_field(val: Any, default: Optional[str] = None) -> Optional[str]:
    if is_missing_value(val):
        return default
    s = str(val).strip()
    return s if s else default


class SyntheticSIFGenerator:
    """
    Synthetic SIF Generator with Coverage-Aware Diversity Improvement,
    Multi-Parent Provenance, and Quality Validation.
    """

    def __init__(self, target_count: int = 20, candidate_multiplier: int = 3, random_seed: int = 42):
        self.target_count = target_count
        self.candidate_multiplier = candidate_multiplier
        self.random_seed = random_seed
        random.seed(random_seed)
        np.random.seed(random_seed)

        self.df_real = self._load_and_audit_real_dataset()
        self.verified_parents = self.df_real[self.df_real["sif_potential"] == 1].copy()
        self.safety_pools = self._build_safety_factor_pools()

    def _load_and_audit_real_dataset(self) -> pd.DataFrame:
        if not UNIFIED_DATASET_PATH.exists():
            raise FileNotFoundError(f"Real dataset path '{UNIFIED_DATASET_PATH}' does not exist.")

        df = pd.read_csv(UNIFIED_DATASET_PATH)
        df["sif_potential"] = pd.to_numeric(df["sif_potential"], errors="coerce").fillna(0).astype(int)
        return df

    def _build_safety_factor_pools(self) -> Dict[str, List[str]]:
        """
        Extracts verified safety factor pools directly from real SIF positive records.
        """
        df_sif = self.verified_parents

        def get_unique_clean(col_names: List[str], default_fallback: List[str]) -> List[str]:
            found_vals = set()
            for col in col_names:
                if col in df_sif.columns:
                    vals = df_sif[col].dropna().astype(str).str.strip().tolist()
                    for v in vals:
                        if not is_missing_value(v) and len(v) > 2 and v.lower() != "nan":
                            found_vals.add(v)
            return sorted(list(found_vals)) if found_vals else default_fallback

        activities = get_unique_clean(["activity_category", "event_type", "work_activity"], ["hot work", "pipe maintenance", "pressure testing", "confined space entry", "heavy lifting"])
        hazards = get_unique_clean(["primary_hazard", "hazard_category", "hazard_type"], ["toxic gas release", "high pressure stored energy", "uncontrolled flame", "suspended load", "electrical arc flash"])
        barriers = get_unique_clean(["barrier_failure", "failed_barrier", "control_failure"], ["isolation verification failure", "lockout tagout defect", "inadequate ventilation", "defective safety latch", "permit scope non-compliance"])
        locations = get_unique_clean(["site_location", "location_detail", "plant_area"], ["process unit 4", "compressor station B", "offshore rig alpha", "storage tank farm", "refinery pipe rack"])

        return {
            "activities": activities,
            "hazards": hazards,
            "barriers": barriers,
            "locations": locations
        }

    def audit_real_dataset(self) -> Dict[str, Any]:
        df = self.df_real
        total_records = len(df)
        sif_positives = int((df["sif_potential"] == 1).sum())
        sif_negatives = int((df["sif_potential"] == 0).sum())
        imbalance_ratio = round(sif_negatives / max(1, sif_positives), 2)
        pos_pct = round((sif_positives / max(1, total_records)) * 100, 2)

        source_counts = df["source_dataset"].value_counts().to_dict() if "source_dataset" in df.columns else {}

        return {
            "total_records": total_records,
            "sif_positive_records": sif_positives,
            "sif_negative_records": sif_negatives,
            "sif_positive_percentage": pos_pct,
            "sif_class_imbalance_ratio": imbalance_ratio,
            "source_distribution": source_counts,
            "pool_diversity": {
                "unique_activities_count": len(self.safety_pools["activities"]),
                "unique_hazards_count": len(self.safety_pools["hazards"]),
                "unique_barriers_count": len(self.safety_pools["barriers"]),
                "unique_locations_count": len(self.safety_pools["locations"])
            }
        }

    def generate_candidates(self) -> List[Dict[str, Any]]:
        """
        Generates diverse synthetic candidates using coverage-aware sampling across safety factor pools
        and multi-parent provenance tracking.
        """
        if self.verified_parents.empty:
            raise ValueError("No verified real SIF parent records (sif_potential=1) found.")

        total_to_generate = self.target_count * self.candidate_multiplier
        candidates = []
        parents_list = self.verified_parents.to_dict(orient="records")
        timestamp_now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        templates = [
            "During {activity}, an unexpected {hazard} occurred at {location} following {barrier}, creating critical SIF exposure.",
            "Field observation during {activity}: {hazard} detected at {location} due to {barrier} with potential serious consequence.",
            "Work involving {activity} resulted in {hazard} at {location} because of {barrier}. Immediate isolation initiated.",
            "Uncontrolled {hazard} identified while performing {activity} at {location}. Root cause traced to {barrier}."
        ]

        activities = self.safety_pools["activities"]
        hazards = self.safety_pools["hazards"]
        barriers = self.safety_pools["barriers"]
        locations = self.safety_pools["locations"]

        for idx in range(1, total_to_generate + 1):
            # Select 1 or 2 distinct real SIF parents for multi-parent provenance
            parent_sample = random.sample(parents_list, k=min(2, len(parents_list)))
            parent_ids = [str(p.get("report_id", f"REAL-SIF-{i}")) for i, p in enumerate(parent_sample)]

            # Coverage-aware factor selection with seeded round-robin / sample
            act = activities[(idx - 1) % len(activities)]
            haz = hazards[(idx - 1) % len(hazards)]
            fail = barriers[(idx - 1) % len(barriers)]
            loc = locations[(idx - 1) % len(locations)]

            template = templates[(idx - 1) % len(templates)]
            synthetic_text = template.format(
                activity=act.lower(),
                hazard=haz.lower(),
                barrier=fail.lower(),
                location=loc
            )

            # Context fragment from primary parent
            p0 = parent_sample[0]
            p0_desc = clean_generation_field(p0.get("description", p0.get("text_description", p0.get("report_text"))))
            if p0_desc and len(p0_desc) > 30 and p0_desc.lower() != "nan":
                words = [w for w in p0_desc.split()[:10] if not is_missing_value(w)]
                if words:
                    synthetic_text += f" Parent Context: {' '.join(words)}."

            syn_id = f"SYN-SIF-{idx:06d}"

            record = {
                "synthetic_id": syn_id,
                "source_type": "SYNTHETIC",
                "is_synthetic": True,
                "sif_potential": 1,
                "description": synthetic_text,
                "synthetic_parent_ids": json.dumps(parent_ids),
                "activity_category": act,
                "primary_hazard": haz,
                "barrier_failure": fail,
                "site_location": loc,
                "generation_method": "COVERAGE_AWARE_VARIATION",
                "generation_model": "OILPS_SyntheticSIFGen_v2",
                "generation_version": "2.0.0",
                "created_at": timestamp_now
            }
            candidates.append(record)

        return candidates

    def validate_candidates(self, candidates: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Validates synthetic candidates: schema, missing-value leakage check, contamination check,
        and strict intra-set duplicate filtering. Limits accepted records to target_count.
        """
        validated_records = []
        c_accepted = 0
        c_rejected = 0
        c_flagged = 0
        reasons_summary = {}

        text_col = next((col for col in ["description", "text_description", "report_text"] if col in self.df_real.columns), None)
        real_descriptions = set(self.df_real[text_col].dropna().str.lower().tolist()) if text_col else set()

        accepted_descriptions = set()

        for cand in candidates:
            syn_id = cand["synthetic_id"]
            desc = cand["description"].strip()
            desc_lower = desc.lower()

            status = "ACCEPTED"
            reason = "VALID"

            # 1. Schema Check
            if not syn_id.startswith("SYN-SIF-") or cand.get("source_type") != "SYNTHETIC" or not cand.get("is_synthetic"):
                status = "REJECTED"
                reason = "MISSING_PROVENANCE"
            elif len(desc) < 20:
                status = "REJECTED"
                reason = "LOW_QUALITY_TEXT"

            # 2. Missing-Value Leakage Check
            elif MISSING_TOKENS_REGEX.search(desc_lower):
                status = "REJECTED"
                reason = "MISSING_VALUE_LEAKAGE"

            # 3. Real Dataset Contamination Check
            elif desc_lower in real_descriptions:
                status = "REJECTED"
                reason = "REAL_DATA_CONTAMINATION"

            # 4. Intra-Set Duplicate Check
            elif desc_lower in accepted_descriptions:
                status = "REJECTED"
                reason = "DUPLICATE"

            # 5. Safety Contradiction Check
            elif "not exposed" in desc_lower or "no hazard" in desc_lower:
                status = "FLAGGED"
                reason = "SAFETY_CONTRADICTION"

            # Limit accepted count to target_count
            if status == "ACCEPTED":
                if c_accepted < self.target_count:
                    c_accepted += 1
                    accepted_descriptions.add(desc_lower)
                else:
                    status = "REJECTED"
                    reason = "TARGET_COUNT_CAP_REACHED"

            if status == "REJECTED":
                c_rejected += 1
            elif status == "FLAGGED":
                c_flagged += 1

            reasons_summary[reason] = reasons_summary.get(reason, 0) + 1

            record_copy = dict(cand)
            record_copy["validation_status"] = status
            record_copy["validation_reason"] = reason
            validated_records.append(record_copy)

        report = {
            "total_candidates": len(candidates),
            "accepted_count": c_accepted,
            "rejected_count": c_rejected,
            "flagged_count": c_flagged,
            "acceptance_rate": round(c_accepted / max(1, len(candidates)), 4),
            "reasons_breakdown": reasons_summary
        }

        return validated_records, report

    def compute_diversity_diagnostics(self, validated_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Computes diversity metrics across accepted synthetic records vs real parent pools.
        """
        accepted = [r for r in validated_records if r["validation_status"] == "ACCEPTED"]
        if not accepted:
            return {"accepted_count": 0, "coverage": {}}

        syn_activities = set(r["activity_category"] for r in accepted if "activity_category" in r)
        syn_hazards = set(r["primary_hazard"] for r in accepted if "primary_hazard" in r)
        syn_barriers = set(r["barrier_failure"] for r in accepted if "barrier_failure" in r)
        syn_locations = set(r["site_location"] for r in accepted if "site_location" in r)

        pool_act = len(self.safety_pools["activities"])
        pool_haz = len(self.safety_pools["hazards"])
        pool_bar = len(self.safety_pools["barriers"])
        pool_loc = len(self.safety_pools["locations"])

        return {
            "accepted_count": len(accepted),
            "synthetic_unique_activities": len(syn_activities),
            "synthetic_unique_hazards": len(syn_hazards),
            "synthetic_unique_barriers": len(syn_barriers),
            "synthetic_unique_locations": len(syn_locations),
            "coverage_pct": {
                "activities_coverage": round((len(syn_activities) / max(1, pool_act)) * 100, 1),
                "hazards_coverage": round((len(syn_hazards) / max(1, pool_haz)) * 100, 1),
                "barriers_coverage": round((len(syn_barriers) / max(1, pool_bar)) * 100, 1),
                "locations_coverage": round((len(syn_locations) / max(1, pool_loc)) * 100, 1)
            }
        }

    def save_synthetic_dataset(self, validated_records: List[Dict[str, Any]], report: Dict[str, Any]):
        df_syn = pd.DataFrame(validated_records)
        df_syn.to_csv(CANDIDATES_CSV_PATH, index=False)

        diversity = self.compute_diversity_diagnostics(validated_records)

        config = {
            "target_count": self.target_count,
            "candidate_multiplier": self.candidate_multiplier,
            "random_seed": self.random_seed,
            "generation_method": "COVERAGE_AWARE_VARIATION",
            "generation_model": "OILPS_SyntheticSIFGen_v2",
            "diversity_strategy": "SAFETY_FACTOR_POOLS",
            "source_dataset_version": "OILPS_UNIFIED_V1",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        with open(CONFIG_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        full_report = {**report, "diversity_diagnostics": diversity}
        with open(VALIDATION_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(full_report, f, indent=2)

        metadata = {
            "dataset_name": "OILPS Synthetic Rare-SIF Dataset",
            "version": "2.0.0",
            "total_candidates": len(validated_records),
            "accepted_count": report["accepted_count"],
            "rejected_count": report["rejected_count"],
            "diversity_diagnostics": diversity,
            "isolation_status": "STRICTLY_ISOLATED",
            "production_models_affected": False,
            "production_rag_affected": False,
            "created_at": config["timestamp"]
        }

        with open(METADATA_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)


if __name__ == "__main__":
    generator = SyntheticSIFGenerator(target_count=20, candidate_multiplier=3, random_seed=42)
    cands = generator.generate_candidates()
    records, val_report = generator.validate_candidates(cands)
    generator.save_synthetic_dataset(records, val_report)
    diversity = generator.compute_diversity_diagnostics(records)
    print("\nValidation Report:\n", json.dumps(val_report, indent=2))
    print("\nDiversity Diagnostics:\n", json.dumps(diversity, indent=2))
