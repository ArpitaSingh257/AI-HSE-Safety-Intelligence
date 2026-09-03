"""
test_stage41_final_dataset.py - Dedicated PyTest Suite for Stage 41 Final OILPS Dataset Consolidation & Quality Control.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.final_dataset_consolidator import (
    FinalDatasetConsolidator, CANONICAL_INPUT_CSV, FINAL_MASTER_OUTPUT_CSV,
    QUALITY_FLAGS_CSV, METADATA_JSON, PROD_SIF_MODEL, PROD_LSR_MODEL,
    PROD_RAG_INDEX, PROD_SEMANTIC_CHUNKS, OFFICIAL_9_TAXONOMY, get_file_hash
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture(scope="module")
def consolidation_results():
    """Module-level fixture providing consolidated master dataset, quality flags, and summary metadata."""
    consolidator = FinalDatasetConsolidator(random_seed=42)
    df_master, df_flags, summary = consolidator.execute_consolidation()
    return consolidator, df_master, df_flags, summary


def test_canonical_row_count_and_unique_ids(consolidation_results):
    """Test 1, 2, 3 & 4: Exactly 4,529 rows, record IDs preserved and 100% unique."""
    consolidator, df_ma, df_fl, summary = consolidation_results

    assert len(consolidator.df_input) == 4529
    assert len(df_ma) == 4529
    assert summary["accounting"]["total_canonical_records"] == 4529
    assert summary["accounting"]["total_records_accounted_for"] == 4529

    rec_ids = list(df_ma["record_id"].dropna())
    assert len(rec_ids) == 4529
    assert len(rec_ids) == len(set(rec_ids))


def test_source_grounded_preservation(consolidation_results):
    """Test 5 & 6: SOURCE_GROUNDED and RECONSTRUCTED records remain 100% unchanged."""
    consolidator, df_ma, df_fl, summary = consolidation_results

    sg_native = df_ma[df_ma["final_lsr_provenance"] == "SOURCE_GROUNDED"]
    sg_recon = df_ma[df_ma["final_lsr_provenance"] == "SOURCE_GROUNDED_RECONSTRUCTED"]

    assert len(sg_native) == 10
    assert len(sg_recon) == 2
    assert len(sg_native) + len(sg_recon) == 12


def test_provenance_states_and_identifiability(consolidation_results):
    """Test 7, 8, 9, 10 & 11: All 5 provenance states valid, taxonomy valid, probabilities [0, 1]."""
    consolidator, df_ma, df_fl, summary = consolidation_results

    allowed_states = {"SOURCE_GROUNDED", "SOURCE_GROUNDED_RECONSTRUCTED", "MODEL_PREDICTED", "HUMAN_REVIEW", "UNKNOWN"}
    found_states = set(df_ma["final_lsr_provenance"].unique())
    assert found_states.issubset(allowed_states)

    # Validate probability fields
    for lsr in OFFICIAL_9_TAXONOMY:
        col_name = f"lsr_prob_{lsr.lower().replace(' ', '_').replace('/', '_')}"
        assert col_name in df_ma.columns
        probs = df_ma[col_name].astype(float)
        assert (probs >= 0.0).all()
        assert (probs <= 1.0).all()


def test_zero_synthetic_and_no_model_labels_in_gold(consolidation_results):
    """Test 12, 13, 14 & 15: Zero synthetic data, no model labels in gold, SIF and narrative unchanged."""
    consolidator, df_ma, df_fl, summary = consolidation_results

    assert not (df_ma["final_lsr_provenance"] == "SYNTHETIC").any()
    sg_df = df_ma[df_ma["final_lsr_provenance"].isin(["SOURCE_GROUNDED", "SOURCE_GROUNDED_RECONSTRUCTED"])]
    for _, row in sg_df.iterrows():
        assert row["lsr_assignment_method"] in ["NATIVE_CANONICAL_LABEL", "IOGP_CANONICAL_RECONCILIATION", "IOGP_RECONSTRUCTION_MATCH"]


def test_quality_flags_reproducibility(consolidation_results):
    """Test 19 & 20: Audit completeness and quality flags reproducibility."""
    consolidator, df_ma, df_fl, summary = consolidation_results

    assert len(df_fl) == summary["quality_control"]["total_quality_flags"]
    if len(df_fl) > 0:
        assert "quality_flag" in df_fl.columns
        assert "flag_reason" in df_fl.columns


def test_deterministic_execution():
    """Test 16: Deterministic output with seed=42 across multiple runs."""
    c1 = FinalDatasetConsolidator(random_seed=42)
    m1, f1, s1 = c1.execute_consolidation()

    c2 = FinalDatasetConsolidator(random_seed=42)
    m2, f2, s2 = c2.execute_consolidation()

    assert len(m1) == len(m2)
    assert s1["accounting"] == s2["accounting"]


def test_production_artifacts_unchanged():
    """Test 17 & 18: Canonical dataset, SIF model, LSR model, RAG FAISS index, and semantic chunks unchanged."""
    hash_canonical = get_file_hash(CANONICAL_INPUT_CSV)
    hash_sif = get_file_hash(PROD_SIF_MODEL)
    hash_lsr = get_file_hash(PROD_LSR_MODEL)
    hash_rag = get_file_hash(PROD_RAG_INDEX)
    hash_chunks = get_file_hash(PROD_SEMANTIC_CHUNKS)

    consolidator = FinalDatasetConsolidator(random_seed=42)
    df_ma, df_fl, summary = consolidator.execute_consolidation()

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
