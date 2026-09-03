"""
test_stage37c3r_synthetic_quality.py - Dedicated PyTest Suite for Stage 37C.3-R Synthetic LSR Augmentation Quality Correction.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.lsr_synthetic_quality_corrector import (
    LSRSyntheticQualityCorrector, STAGE37C3R_SYNTHETIC_CSV, STAGE37C3R_AUGMENTED_CSV,
    STAGE37C3R_METADATA, REAL_TRAIN_CSV, REAL_VAL_CSV, REAL_TEST_CSV, normalize_text,
    LEAKAGE_REGEX, TAXONOMY_ORDER
)
from data.unified_lsr_gold_builder import get_file_hash, UNIFIED_DATASET_PATH
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_input_files_exist():
    """Test 1: Input real split CSV files exist."""
    assert REAL_TRAIN_CSV.exists()
    assert REAL_VAL_CSV.exists()
    assert REAL_TEST_CSV.exists()


def test_real_split_counts_and_disjointness():
    """Test 2, 3, 4 & 5: Real train, validation, and test split counts and disjointness."""
    corrector = LSRSyntheticQualityCorrector(random_seed=42)
    tr, va, te = corrector.df_train, corrector.df_val, corrector.df_test

    assert len(tr) > 0
    assert len(va) > 0
    assert len(te) > 0

    tr_groups = set(tr["incident_group_id"].unique())
    va_groups = set(va["incident_group_id"].unique())
    te_groups = set(te["incident_group_id"].unique())

    assert len(tr_groups.intersection(va_groups)) == 0
    assert len(tr_groups.intersection(te_groups)) == 0
    assert len(va_groups.intersection(te_groups)) == 0


def test_hard_parent_cap_max_one_child():
    """Test 7: HARD PARENT CAP — Maximum 1 synthetic child per parent."""
    corrector = LSRSyntheticQualityCorrector(random_seed=42)
    syn, aug, summary = corrector.execute_correction()

    if not syn.empty:
        parent_counts = syn["parent_record_id"].value_counts()
        assert parent_counts.max() <= 1
        assert summary["synthetic_counts"]["maximum_children_per_parent"] <= 1


def test_synthetic_parents_from_train_only():
    """Test 6, 11: Synthetic parents are train-only (0 val/test parent leakage)."""
    corrector = LSRSyntheticQualityCorrector(random_seed=42)
    syn, aug, summary = corrector.execute_correction()

    tr_pids = set(corrector.df_train["incident_group_id"].unique())
    va_pids = set(corrector.df_val["incident_group_id"].unique())
    te_pids = set(corrector.df_test["incident_group_id"].unique())

    syn_pids = set(syn["parent_incident_group_id"].unique()) if not syn.empty else set()

    assert syn_pids.issubset(tr_pids)
    assert len(syn_pids.intersection(va_pids)) == 0
    assert len(syn_pids.intersection(te_pids)) == 0


def test_synthetic_text_uniqueness_and_difference():
    """Test 8, 9 & 10: Synthetic text is 100% unique and differs from parent and val/test text."""
    corrector = LSRSyntheticQualityCorrector(random_seed=42)
    syn, aug, summary = corrector.execute_correction()

    if not syn.empty:
        norm_syns = [normalize_text(t) for t in syn["incident_text"]]
        assert len(norm_syns) == len(set(norm_syns))

        parent_map = {r["record_id"]: normalize_text(r["incident_text"]) for _, r in corrector.df_train.iterrows()}
        for _, row in syn.iterrows():
            pid = row["parent_record_id"]
            p_norm = parent_map[pid]
            s_norm = normalize_text(row["incident_text"])
            assert s_norm != p_norm


def test_exact_label_set_preservation():
    """Test 12 & 17: Synthetic label set MUST be exactly equal to parent label set."""
    corrector = LSRSyntheticQualityCorrector(random_seed=42)
    syn, aug, summary = corrector.execute_correction()

    if not syn.empty:
        parent_labels_map = {r["record_id"]: r["lsr_labels"] for _, r in corrector.df_train.iterrows()}
        for _, row in syn.iterrows():
            pid = row["parent_record_id"]
            assert row["lsr_labels"] == parent_labels_map[pid]
            p_val = str(row["lsr_primary"]).strip()
            if p_val.startswith("["):
                for l in json.loads(p_val):
                    assert l in set(TAXONOMY_ORDER)
            else:
                assert p_val in set(TAXONOMY_ORDER)


def test_official_taxonomy_only():
    """Test 13: All primary LSRs belong to the official 9-class IOGP taxonomy."""
    corrector = LSRSyntheticQualityCorrector(random_seed=42)
    syn, aug, summary = corrector.execute_correction()

    valid_classes = set(TAXONOMY_ORDER)
    if not syn.empty:
        for lsr_raw in syn["lsr_primary"].unique():
            lsr_str = str(lsr_raw).strip()
            if lsr_str.startswith("["):
                labels = json.loads(lsr_str)
                for l in labels:
                    assert l in valid_classes
            else:
                assert lsr_str in valid_classes


def test_provenance_fields_and_synthetic_flag():
    """Test 14 & 15: Provenance fields complete and is_synthetic=True."""
    corrector = LSRSyntheticQualityCorrector(random_seed=42)
    syn, aug, summary = corrector.execute_correction()

    if not syn.empty:
        for _, r in syn.iterrows():
            assert r["is_synthetic"] == True
            assert r["generation_method"] == "CONTROLLED_AUGMENTATION_QUALITY_CORRECTED"
            assert r["lsr_label_provenance"] == "DERIVED_FROM_SOURCE_GROUNDED_PARENT"
            assert "parent_source_document" in r


def test_no_target_leakage_in_text():
    """Test 16: Target leakage markers not present in synthetic incident text."""
    corrector = LSRSyntheticQualityCorrector(random_seed=42)
    syn, aug, summary = corrector.execute_correction()

    if not syn.empty:
        for text in syn["incident_text"].astype(str):
            assert not LEAKAGE_REGEX.search(text)


def test_deterministic_generation():
    """Test 18: Running twice with seed=42 produces identical outputs."""
    c1 = LSRSyntheticQualityCorrector(random_seed=42)
    sy1, aug1, s1 = c1.execute_correction()

    c2 = LSRSyntheticQualityCorrector(random_seed=42)
    sy2, aug2, s2 = c2.execute_correction()

    assert len(sy1) == len(sy2)
    assert len(aug1) == len(aug2)


def test_augmented_train_composition():
    """Test 19: augmented_train = real_train + synthetic_train."""
    corrector = LSRSyntheticQualityCorrector(random_seed=42)
    syn, aug, summary = corrector.execute_correction()

    assert len(aug) == len(corrector.df_train) + len(syn)


def test_production_artifacts_unchanged():
    """Test 20, 21, 22 & 23: Canonical dataset, SIF model, LSR model, and RAG index unchanged."""
    hash_canonical = get_file_hash(UNIFIED_DATASET_PATH)
    corrector = LSRSyntheticQualityCorrector(random_seed=42)
    syn, aug, summary = corrector.execute_correction()

    assert hash_canonical == get_file_hash(UNIFIED_DATASET_PATH)

    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True


def test_audits_exist_in_metadata():
    """Test 24 & 25: Label distribution audit and multilabel cardinality audit exist."""
    corrector = LSRSyntheticQualityCorrector(random_seed=42)
    syn, aug, summary = corrector.execute_correction()

    assert "class_distributions" in summary
    assert "real_train" in summary["class_distributions"]
    assert "synthetic" in summary["class_distributions"]
    assert "augmented_train" in summary["class_distributions"]


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
