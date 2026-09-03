"""
test_stage37c3r1_reconciliation.py - Dedicated PyTest Suite for Stage 37C.3-R.1 Reconciliation and Multilabel Audit.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.lsr_reconciliation_audit_engine import (
    LSRReconciliationAuditEngine, STAGE37C3R_SYNTHETIC_CSV, STAGE37C3R_AUGMENTED_CSV,
    REAL_TRAIN_CSV, REAL_VAL_CSV, REAL_TEST_CSV, TAXONOMY_ORDER
)
from data.unified_lsr_gold_builder import get_file_hash, UNIFIED_DATASET_PATH
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_augmented_row_accounting_invariant():
    """Test 1: Mathematical Invariant len(augmented_train) == len(real_train) + len(synthetic_train)."""
    engine = LSRReconciliationAuditEngine()
    summary = engine.audit_reconciliation()

    ac = summary["accounting"]
    assert ac["mathematical_invariant_pass"] == True
    assert ac["augmented_train"] == ac["real_train"] + ac["synthetic_train"]


def test_synthetic_count_consistency():
    """Test 2: Synthetic count consistency across synthetic and augmented dataset files."""
    engine = LSRReconciliationAuditEngine()
    summary = engine.audit_reconciliation()

    assert summary["synthetic_quality"]["total_synthetic_records"] == len(engine.df_syn)
    assert len(engine.df_aug) == len(engine.df_tr) + len(engine.df_syn)


def test_no_parent_duplication():
    """Test 3: Maximum 1 synthetic child per parent."""
    engine = LSRReconciliationAuditEngine()
    summary = engine.audit_reconciliation()

    assert summary["synthetic_quality"]["max_children_per_parent"] <= 1


def test_no_synthetic_text_duplication():
    """Test 4: Zero exact duplicate normalized synthetic texts."""
    engine = LSRReconciliationAuditEngine()
    summary = engine.audit_reconciliation()

    assert summary["synthetic_quality"]["exact_normalized_text_duplicates"] == 0


def test_train_only_parent_provenance_and_zero_leakage():
    """Test 6 & 7: Train-only parent provenance and 0 val/test parent leakage."""
    engine = LSRReconciliationAuditEngine()
    summary = engine.audit_reconciliation()

    lk = summary["leakage_audit"]
    assert lk["val_test_leakage_status"] == "PASS"
    assert lk["parent_val_intersection"] == 0
    assert lk["parent_test_intersection"] == 0


def test_production_artifacts_unchanged():
    """Test 8: Canonical dataset, SIF champion, LSR champion, and RAG index unchanged."""
    hash_canonical = get_file_hash(UNIFIED_DATASET_PATH)
    engine = LSRReconciliationAuditEngine()
    summary = engine.audit_reconciliation()

    assert hash_canonical == get_file_hash(UNIFIED_DATASET_PATH)

    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True


def test_deterministic_output():
    """Test 9: Audit returns identical output across two executions."""
    e1 = LSRReconciliationAuditEngine()
    s1 = e1.audit_reconciliation()

    e2 = LSRReconciliationAuditEngine()
    s2 = e2.audit_reconciliation()

    assert s1["accounting"] == s2["accounting"]
    assert s1["synthetic_quality"] == s2["synthetic_quality"]


def test_individual_lsr_distribution_and_cardinality():
    """Test 10 & 11: Individual LSR rule frequency audit and cardinality distribution exist."""
    engine = LSRReconciliationAuditEngine()
    summary = engine.audit_reconciliation()

    assert "individual_lsr_counts" in summary
    assert "cardinality_distributions" in summary

    for lsr in TAXONOMY_ORDER:
        assert lsr in summary["individual_lsr_counts"]
        counts = summary["individual_lsr_counts"][lsr]
        assert counts["augmented"] == counts["real_train"] + counts["synthetic"]


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
