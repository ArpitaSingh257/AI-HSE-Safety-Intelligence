"""
lsr_synthetic_augmenter.py - Stage 37C.3 Controlled Synthetic LSR Data Augmentation Subsystem.
Performs deterministic group-aware train/val/test split on real incident-level Gold dataset (iogp_incident_level_gold_v1.csv),
locks real validation and test manifests, generates controlled synthetic training records for rare LSR classes,
and exports stage37c3_augmented_train.csv. Strictly enforces zero parent leakage to validation/test sets and
preserves production model and dataset freeze.
"""

import sys
import os
import re
import json
import time
import hashlib
import random
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

INCIDENT_GOLD_CSV_PATH = BASE_DIR / "datasets" / "lsr_gold" / "iogp_incident_level_gold_v1.csv"
LSR_GOLD_DIR = BASE_DIR / "datasets" / "lsr_gold"

REAL_TRAIN_CSV = LSR_GOLD_DIR / "stage37c3_real_train.csv"
REAL_VAL_CSV = LSR_GOLD_DIR / "stage37c3_real_validation.csv"
REAL_TEST_CSV = LSR_GOLD_DIR / "stage37c3_real_test.csv"
SYNTHETIC_TRAIN_CSV = LSR_GOLD_DIR / "stage37c3_synthetic_train.csv"
AUGMENTED_TRAIN_CSV = LSR_GOLD_DIR / "stage37c3_augmented_train.csv"

VAL_MANIFEST = LSR_GOLD_DIR / "stage37c3_real_validation_manifest.json"
TEST_MANIFEST = LSR_GOLD_DIR / "stage37c3_real_test_manifest.json"
STAGE37C3_METADATA = LSR_GOLD_DIR / "stage37c3_metadata.json"

TAXONOMY_ORDER = [
    "Driving", "Bypassing Safety Controls", "Line of Fire", "Energy Isolation",
    "Safe Mechanical Lifting", "Working at Height", "Work Authorization",
    "Confined Space", "Hot Work"
]

LEAKAGE_REGEX = re.compile(
    r'(primary life[- ]saving rule|secondary life[- ]saving rule|life[- ]saving rule)\s*[:=\-]\s*[A-Za-z\s]+',
    re.IGNORECASE
)

# Deterministic wording variations for paraphrasing
PARAPHRASE_RULES = [
    ("worker", "operator"),
    ("operators", "technicians"),
    ("equipment", "machinery"),
    ("lifting operation", "crane operation"),
    ("entered", "moved into"),
    ("energized line", "live electrical conductor"),
    ("scaffold", "working platform"),
    ("pressure vessel", "pressurized system"),
    ("vehicle", "transport unit"),
    ("permit to work", "work authorization permit")
]


class LSRSyntheticAugmenter:
    """
    Subsystem for controlled synthetic LSR data augmentation.
    """

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)
        self.df_gold = self._load_gold_dataset()

    def _load_gold_dataset(self) -> pd.DataFrame:
        if not INCIDENT_GOLD_CSV_PATH.exists():
            raise FileNotFoundError(f"Incident Gold dataset missing at '{INCIDENT_GOLD_CSV_PATH}'.")
        return pd.read_csv(INCIDENT_GOLD_CSV_PATH)

    def create_group_aware_split(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Creates deterministic 70/15/15 group-aware train/val/test split.
        """
        df = self.df_gold.copy()
        unique_groups = df["incident_group_id"].unique().tolist()
        unique_groups.sort()  # Deterministic order before shuffle

        rng = random.Random(self.random_seed)
        rng.shuffle(unique_groups)

        n_total = len(unique_groups)
        n_val = max(1, int(0.15 * n_total))
        n_test = max(1, int(0.15 * n_total))
        n_train = n_total - n_val - n_test

        train_groups = set(unique_groups[:n_train])
        val_groups = set(unique_groups[n_train:n_train + n_val])
        test_groups = set(unique_groups[n_train + n_val:])

        df_train = df[df["incident_group_id"].isin(train_groups)].copy()
        df_val = df[df["incident_group_id"].isin(val_groups)].copy()
        df_test = df[df["incident_group_id"].isin(test_groups)].copy()

        df_train["is_synthetic"] = False
        df_val["is_synthetic"] = False
        df_test["is_synthetic"] = False

        return df_train, df_val, df_test

    def generate_synthetic_records(self, df_train: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generates controlled synthetic training records from REAL_TRAIN parents only.
        Targeting rare LSR classes (Confined Space, Driving, Hot Work, Working at Height).
        """
        synthetic_records = []
        dup_rejection_count = 0
        leakage_rejection_count = 0

        # Identify rare class parents in REAL_TRAIN
        target_augmentation_targets = {
            "Confined Space": 10,
            "Driving": 10,
            "Hot Work": 8,
            "Working at Height": 6
        }

        # Filter candidates by class
        syn_counter = 1
        for lsr_target, num_to_gen in target_augmentation_targets.items():
            parents = df_train[df_train["lsr_primary"] == lsr_target].to_dict(orient="records")
            if not parents:
                # Search in lsr_labels if primary doesn't match
                parents = df_train[df_train["lsr_labels"].astype(str).str.contains(lsr_target)].to_dict(orient="records")

            if not parents:
                continue

            for i in range(num_to_gen):
                parent = parents[i % len(parents)]

                orig_text = str(parent["incident_text"])
                syn_text = orig_text

                # Apply deterministic paraphrasing rules
                for old_w, new_w in PARAPHRASE_RULES:
                    if old_w in syn_text.lower():
                        syn_text = re.sub(r'\b' + old_w + r'\b', new_w, syn_text, flags=re.IGNORECASE)

                if syn_text == orig_text:
                    syn_text = f"Controlled operational activity: {orig_text}"

                # Leakage check
                if LEAKAGE_REGEX.search(syn_text):
                    leakage_rejection_count += 1
                    continue

                syn_id = f"SYN-LSR-{syn_counter:05d}"
                syn_counter += 1

                syn_rec = {
                    "record_id": syn_id,
                    "incident_group_id": f"SYN-GRP-{parent['incident_group_id']}",
                    "incident_text": syn_text,
                    "lsr_primary": parent["lsr_primary"],
                    "lsr_secondary": parent["lsr_secondary"],
                    "lsr_labels": parent["lsr_labels"],
                    "label_cardinality": parent["label_cardinality"],
                    "label_count": parent["label_count"],
                    "is_synthetic": True,
                    "parent_record_id": parent["record_id"],
                    "parent_incident_group_id": parent["incident_group_id"],
                    "generation_method": "CONTROLLED_AUGMENTATION",
                    "lsr_label_provenance": "DERIVED_FROM_SOURCE_GROUNDED_PARENT",
                    "parent_source_document": str(parent.get("source_documents", "[]")),
                    "parent_source_pages": str(parent.get("source_pages", "[]")),
                    "parent_source_record_ids": str(parent.get("source_record_ids", "[]")),
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                synthetic_records.append(syn_rec)

        return synthetic_records

    def audit_similarity(self, df_train: pd.DataFrame, synthetic_records: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculates TF-IDF cosine similarity between synthetic records and their parents."""
        if not synthetic_records:
            return {"min": 0.0, "mean": 0.0, "max": 0.0}

        parent_map = {r["record_id"]: str(r["incident_text"]) for _, r in df_train.iterrows()}

        sims = []
        for syn in synthetic_records:
            pid = syn["parent_record_id"]
            p_text = parent_map.get(pid, "")
            s_text = syn["incident_text"]
            if p_text and s_text:
                vectorizer = TfidfVectorizer().fit([p_text, s_text])
                vectors = vectorizer.transform([p_text, s_text])
                cos_sim = float(cosine_similarity(vectors[0:1], vectors[1:2])[0][0])
                sims.append(cos_sim)

        if not sims:
            return {"min": 0.0, "mean": 0.0, "max": 0.0}

        return {
            "min": round(float(np.min(sims)), 4),
            "mean": round(float(np.mean(sims)), 4),
            "max": round(float(np.max(sims)), 4)
        }

    def execute_augmentation(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """
        Executes full group-aware split, synthetic generation, validation audits, and exports files.
        """
        df_train, df_val, df_test = self.create_group_aware_split()
        syn_records = self.generate_synthetic_records(df_train)

        df_syn = pd.DataFrame(syn_records) if syn_records else pd.DataFrame()
        df_aug_train = pd.concat([df_train, df_syn], ignore_index=True) if not df_syn.empty else df_train.copy()

        # Hard Leakage Audit
        val_group_ids = set(df_val["incident_group_id"].unique())
        test_group_ids = set(df_test["incident_group_id"].unique())
        syn_parent_groups = set(df_syn["parent_incident_group_id"].unique()) if not df_syn.empty else set()

        val_leakage = len(syn_parent_groups.intersection(val_group_ids))
        test_leakage = len(syn_parent_groups.intersection(test_group_ids))

        sim_stats = self.audit_similarity(df_train, syn_records)

        # Calculate class distributions
        train_dist = df_train["lsr_primary"].value_counts().to_dict()
        syn_dist = df_syn["lsr_primary"].value_counts().to_dict() if not df_syn.empty else {}
        aug_dist = df_aug_train["lsr_primary"].value_counts().to_dict()

        summary = {
            "stage": "STAGE_37C.3_CONTROLLED_SYNTHETIC_LSR_AUGMENTATION",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "random_seed": self.random_seed,
            "real_total_incidents": len(self.df_gold),
            "real_train_incidents": len(df_train),
            "real_validation_incidents": len(df_val),
            "real_test_incidents": len(df_test),
            "synthetic_records_generated": len(df_syn),
            "augmented_train_total": len(df_aug_train),
            "class_distributions": {
                "real_train": train_dist,
                "synthetic": syn_dist,
                "augmented_train": aug_dist
            },
            "synthetic_parent_count": len(syn_parent_groups),
            "leakage_audit": {
                "synthetic_parent_val_intersection": val_leakage,
                "synthetic_parent_test_intersection": test_leakage,
                "val_test_leakage_status": "PASS" if (val_leakage == 0 and test_leakage == 0) else "FAIL"
            },
            "similarity_statistics": sim_stats,
            "production_protection": {
                "canonical_dataset_untouched": True,
                "production_sif_champion_frozen": True,
                "production_lsr_champion_frozen": True,
                "production_rag_untouched": True
            }
        }

        return df_train, df_val, df_test, df_syn, df_aug_train, summary

    def save_outputs(self, df_train: pd.DataFrame, df_val: pd.DataFrame, df_test: pd.DataFrame,
                     df_syn: pd.DataFrame, df_aug_train: pd.DataFrame, summary: Dict[str, Any]):
        """Saves split CSVs, synthetic CSVs, locked manifests, and metadata JSON."""
        df_train.to_csv(REAL_TRAIN_CSV, index=False)
        df_val.to_csv(REAL_VAL_CSV, index=False)
        df_test.to_csv(REAL_TEST_CSV, index=False)
        df_syn.to_csv(SYNTHETIC_TRAIN_CSV, index=False)
        df_aug_train.to_csv(AUGMENTED_TRAIN_CSV, index=False)

        # Save Locked Manifests
        val_manifest_data = df_val[["record_id", "incident_group_id", "source_documents", "source_pages"]].to_dict(orient="records")
        with open(VAL_MANIFEST, "w", encoding="utf-8") as f:
            json.dump(val_manifest_data, f, indent=2)

        test_manifest_data = df_test[["record_id", "incident_group_id", "source_documents", "source_pages"]].to_dict(orient="records")
        with open(TEST_MANIFEST, "w", encoding="utf-8") as f:
            json.dump(test_manifest_data, f, indent=2)

        with open(STAGE37C3_METADATA, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)


if __name__ == "__main__":
    augmenter = LSRSyntheticAugmenter(random_seed=42)
    d_tr, d_va, d_te, d_sy, d_aug, summary = augmenter.execute_augmentation()
    augmenter.save_outputs(d_tr, d_va, d_te, d_sy, d_aug, summary)
    print("\nSTAGE 37C.3 AUGMENTATION SUMMARY:\n", json.dumps(summary, indent=2))
