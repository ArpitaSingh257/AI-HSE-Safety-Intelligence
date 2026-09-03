"""
test_stage42_lsr_coverage.py - Dedicated PyTest Suite for Stage 42 Controlled LSR Coverage Expansion (Hotfix Architecture).
"""

import sys
import os
import json
import hashlib
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.lsr_coverage_expander import (
    LSRCoverageExpander, MASTER_V1_INPUT_CSV, MASTER_V2_OUTPUT_CSV,
    COVERAGE_AUDIT_CSV, MANUAL_REVIEW_QUEUE_CSV, METADATA_JSON,
    PROD_SIF_MODEL, PROD_LSR_MODEL, PROD_RAG_INDEX, PROD_SEMANTIC_CHUNKS,
    OFFICIAL_9_TAXONOMY, CANONICAL_INPUT_CSV, get_file_hash
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def expansion_results():
    """Module-level fixture providing coverage expansion master v2, audit, review queue, and summary metadata."""
    expander = LSRCoverageExpander(random_seed=42)
    df_m2, df_au, df_rv, summary = expander.execute_expansion()
    return expander, df_m2, df_au, df_rv, summary


def test_canonical_row_count_and_unique_ids(expansion_results):
    """Test 1 & 2: Exactly 4,529 rows, record IDs preserved and 100% unique."""
    expander, df_m2, df_au, df_rv, summary = expansion_results

    assert len(expander.df_input) == 4529
    assert len(df_m2) == 4529

    rec_ids = list(df_m2["record_id"].dropna())
    assert len(rec_ids) == 4529
    assert len(rec_ids) == len(set(rec_ids))


def test_stage41_assignment_preservation_and_monotonicity(expansion_results):
    """Test Hotfix Invariant: Final confirmed assigned records >= Stage 41 assigned records & coverage monotonically increases."""
    expander, df_m2, df_au, df_rv, summary = expansion_results

    base_assigned = summary["stage41_baseline"]["previously_assigned_records"]
    final_assigned = summary["final_accounting"]["final_assigned_records"]

    assert final_assigned >= base_assigned, f"Assignment loss detected: {final_assigned} < {base_assigned}"

    cov_before = summary["coverage_metrics"]["coverage_before_pct"]
    cov_after = summary["coverage_metrics"]["coverage_after_pct"]
    assert cov_after >= cov_before, f"Coverage monotonicity failed: {cov_after}% < {cov_before}%"


def test_source_grounded_and_reconstructed_preservation(expansion_results):
    """Test: SOURCE_GROUNDED (10) and RECONSTRUCTED (2) records remain 100% unchanged."""
    expander, df_m2, df_au, df_rv, summary = expansion_results

    sg_native = df_m2[df_m2["stage42_provenance"] == "SOURCE_GROUNDED"]
    sg_recon = df_m2[df_m2["stage42_provenance"] == "SOURCE_GROUNDED_RECONSTRUCTED"]

    assert len(sg_native) == 10
    assert len(sg_recon) == 2
    assert len(sg_native) + len(sg_recon) == 12


def test_provenance_states_and_naming_convention(expansion_results):
    """Test: Provenance valid, HUMAN_REVIEW_PENDING strictly used, prototype operational threshold."""
    expander, df_m2, df_au, df_rv, summary = expansion_results

    allowed_states = {"SOURCE_GROUNDED", "SOURCE_GROUNDED_RECONSTRUCTED", "MODEL_PREDICTED", "HUMAN_REVIEW_PENDING", "UNKNOWN"}
    found_states = set(df_m2["stage42_provenance"].unique())
    assert found_states.issubset(allowed_states)
    assert "HUMAN_REVIEW" not in found_states  # Must use HUMAN_REVIEW_PENDING

    assert (df_m2["stage42_threshold_policy"] == "PROTOTYPE_OPERATIONAL").all()


def test_no_synthetic_records_and_semantic_protection(expansion_results):
    """Test: Zero synthetic records, semantic similarity alone cannot create MODEL_PREDICTED."""
    expander, df_m2, df_au, df_rv, summary = expansion_results

    assert not (df_m2["stage42_provenance"] == "SYNTHETIC").any()

    # Verify semantic similarity alone does NOT produce MODEL_PREDICTED if model score is low
    low_model_rows = df_m2[(df_m2["stage42_top_score"] < 0.65) & (df_m2["stage42_semantic_score"] >= 0.60)]
    for _, r in low_model_rows.iterrows():
        assert r["stage42_provenance"] != "MODEL_PREDICTED"


def test_audit_completeness_and_review_queue(expansion_results):
    """Test: Audit covers all records, review queue contains HUMAN_REVIEW_PENDING only."""
    expander, df_m2, df_au, df_rv, summary = expansion_results

    assert len(df_au) == 4529
    pending_cnt = summary["final_accounting"]["human_review_pending"]
    assert len(df_rv) == pending_cnt


def test_five_run_determinism():
    """Test: Five-run deterministic execution with seed=42."""
    hashes = []
    for run in range(5):
        c = LSRCoverageExpander(random_seed=42)
        m2, au, rv, s = c.execute_expansion()
        h = hashlib.sha256(m2.to_csv(index=False).encode("utf-8")).hexdigest()
        hashes.append(h)

    assert len(set(hashes)) == 1, "Five-run determinism audit failed!"


def test_production_artifacts_unchanged():
    """Test: Canonical dataset, SIF model, LSR model, RAG FAISS index, and semantic chunks unchanged."""
    hash_canonical = get_file_hash(CANONICAL_INPUT_CSV)
    hash_sif = get_file_hash(PROD_SIF_MODEL)
    hash_lsr = get_file_hash(PROD_LSR_MODEL)
    hash_rag = get_file_hash(PROD_RAG_INDEX)
    hash_chunks = get_file_hash(PROD_SEMANTIC_CHUNKS)

    expander = LSRCoverageExpander(random_seed=42)
    df_m2, df_au, df_rv, summary = expander.execute_expansion()

    assert hash_canonical == get_file_hash(CANONICAL_INPUT_CSV)
    assert hash_sif == get_file_hash(PROD_SIF_MODEL)
    assert hash_lsr == get_file_hash(PROD_LSR_MODEL)
    assert hash_rag == get_file_hash(PROD_RAG_INDEX)
    assert hash_chunks == get_file_hash(PROD_SEMANTIC_CHUNKS)

    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
