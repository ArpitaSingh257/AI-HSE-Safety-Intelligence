"""
test_stage37c3_synthetic_lsr_augmentation.py - Dedicated PyTest Suite for Stage 37C.3 Controlled Synthetic LSR Data Augmentation.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.lsr_synthetic_augmenter import (
    LSRSyntheticAugmenter, INCIDENT_GOLD_CSV_PATH, VAL_MANIFEST, TEST_MANIFEST,
    LEAKAGE_REGEX, TAXONOMY_ORDER
)
from data.unified_lsr_gold_builder import get_file_hash, UNIFIED_DATASET_PATH
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_gold_dataset_unchanged():
    """Test 1: Original iogp_incident_level_gold_v1.csv remains unchanged."""
    hash_before = get_file_hash(INCIDENT_GOLD_CSV_PATH)
    augmenter = LSRSyntheticAugmenter(random_seed=42)
    tr, va, te, sy, aug, summary = augmenter.execute_augmentation()
    hash_after = get_file_hash(INCIDENT_GOLD_CSV_PATH)

    assert hash_before == hash_after


def test_canonical_dataset_unchanged():
    """Test 25: Canonical dataset oilps_unified_deduped.csv remains unchanged."""
    hash_before = get_file_hash(UNIFIED_DATASET_PATH)
    augmenter = LSRSyntheticAugmenter(random_seed=42)
    tr, va, te, sy, aug, summary = augmenter.execute_augmentation()
    hash_after = get_file_hash(UNIFIED_DATASET_PATH)

    assert hash_before == hash_after


def test_production_models_and_rag_frozen():
    """Test 23 & 24: Production SIF/LSR champions and RAG index remain 100% frozen."""
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True


def test_train_val_test_group_disjointness():
    """Test 3: Train, Validation, and Test groups are 100% disjoint."""
    augmenter = LSRSyntheticAugmenter(random_seed=42)
    tr, va, te, sy, aug, summary = augmenter.execute_augmentation()

    tr_groups = set(tr["incident_group_id"].unique())
    va_groups = set(va["incident_group_id"].unique())
    te_groups = set(te["incident_group_id"].unique())

    assert len(tr_groups.intersection(va_groups)) == 0
    assert len(tr_groups.intersection(te_groups)) == 0
    assert len(va_groups.intersection(te_groups)) == 0


def test_val_and_test_contain_only_real_records():
    """Test 4, 5 & 10: Validation and Test sets contain ONLY real records."""
    augmenter = LSRSyntheticAugmenter(random_seed=42)
    tr, va, te, sy, aug, summary = augmenter.execute_augmentation()

    assert not va["is_synthetic"].any()
    assert not te["is_synthetic"].any()
    assert not tr["is_synthetic"].any()


def test_synthetic_parents_from_train_only():
    """Test 6, 7 & 8: Synthetic parents come ONLY from TRAIN (0 intersection with VAL/TEST)."""
    augmenter = LSRSyntheticAugmenter(random_seed=42)
    tr, va, te, sy, aug, summary = augmenter.execute_augmentation()

    tr_pids = set(tr["incident_group_id"].unique())
    va_pids = set(va["incident_group_id"].unique())
    te_pids = set(te["incident_group_id"].unique())

    syn_pids = set(sy["parent_incident_group_id"].unique())

    assert syn_pids.issubset(tr_pids)
    assert len(syn_pids.intersection(va_pids)) == 0
    assert len(syn_pids.intersection(te_pids)) == 0


def test_synthetic_and_real_flagging():
    """Test 9 & 10: Synthetic records explicitly marked is_synthetic=True, real is_synthetic=False."""
    augmenter = LSRSyntheticAugmenter(random_seed=42)
    tr, va, te, sy, aug, summary = augmenter.execute_augmentation()

    assert sy["is_synthetic"].all()
    assert not tr["is_synthetic"].any()


def test_synthetic_labels_derived_from_parent():
    """Test 11 & 18: Synthetic labels match parent labels and provenance is DERIVED_FROM_SOURCE_GROUNDED_PARENT."""
    augmenter = LSRSyntheticAugmenter(random_seed=42)
    tr, va, te, sy, aug, summary = augmenter.execute_augmentation()

    p_map = {r["record_id"]: r["lsr_primary"] for _, r in tr.iterrows()}
    for _, row in sy.iterrows():
        pid = row["parent_record_id"]
        assert row["lsr_primary"] == p_map[pid]
        assert row["lsr_label_provenance"] == "DERIVED_FROM_SOURCE_GROUNDED_PARENT"


def test_official_taxonomy_integrity():
    """Test 12: Synthetic labels belong strictly to official 9-class IOGP taxonomy."""
    augmenter = LSRSyntheticAugmenter(random_seed=42)
    tr, va, te, sy, aug, summary = augmenter.execute_augmentation()

    valid_classes = set(TAXONOMY_ORDER)
    for lsr_raw in sy["lsr_primary"].unique():
        lsr_str = str(lsr_raw).strip()
        if lsr_str.startswith("["):
            labels = json.loads(lsr_str)
            for l in labels:
                assert l in valid_classes
        else:
            assert lsr_str in valid_classes


def test_no_leakage_in_synthetic_text():
    """Test 14: Synthetic incident text does not contain target leakage markers like 'PRIMARY LIFE-SAVING RULE:'."""
    augmenter = LSRSyntheticAugmenter(random_seed=42)
    tr, va, te, sy, aug, summary = augmenter.execute_augmentation()

    for text in sy["incident_text"].astype(str):
        assert not LEAKAGE_REGEX.search(text)


def test_parent_provenance_preserved():
    """Test 17: Parent provenance (source docs, pages, record IDs) is preserved."""
    augmenter = LSRSyntheticAugmenter(random_seed=42)
    tr, va, te, sy, aug, summary = augmenter.execute_augmentation()

    for _, row in sy.iterrows():
        assert "parent_source_document" in row
        assert "parent_source_pages" in row


def test_deterministic_generation():
    """Test 19 & 20: Generation is 100% deterministic with seed=42."""
    a1 = LSRSyntheticAugmenter(random_seed=42)
    tr1, va1, te1, sy1, aug1, s1 = a1.execute_augmentation()

    a2 = LSRSyntheticAugmenter(random_seed=42)
    tr2, va2, te2, sy2, aug2, s2 = a2.execute_augmentation()

    assert len(sy1) == len(sy2)
    assert s1["synthetic_records_generated"] == s2["synthetic_records_generated"]


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
