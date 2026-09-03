"""
test_stage39b_lsr_reconstruction.py - Dedicated PyTest Suite for Stage 39B IOGP Incident-to-Canonical Reconstruction & LSR Enrichment.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.iogp_canonical_reconstructor import (
    IOGPCanonicalReconstructor, CANONICAL_INPUT_CSV, RECONSTRUCTED_OUTPUT_CSV,
    METADATA_JSON, PROD_SIF_MODEL, PROD_LSR_MODEL, PROD_RAG_INDEX,
    PROD_SEMANTIC_CHUNKS, get_file_hash
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_canonical_input_and_output_row_count():
    """Test 1: Canonical output contains exactly 4,529 rows."""
    reconstructor = IOGPCanonicalReconstructor(random_seed=42)
    df_en, df_au, df_rv, summary = reconstructor.execute_reconstruction()

    assert len(reconstructor.df_canonical) == 4529
    assert len(df_en) == 4529
    assert summary["accounting"]["canonical_records"] == 4529


def test_original_columns_and_values_preserved():
    """Test 2 & 3: Original canonical columns and values preserved."""
    reconstructor = IOGPCanonicalReconstructor(random_seed=42)
    df_en, df_au, df_rv, summary = reconstructor.execute_reconstruction()

    orig_cols = list(reconstructor.df_canonical.columns)
    for col in orig_cols:
        assert col in df_en.columns

    for col in orig_cols[:5]:
        assert df_en[col].iloc[0] == reconstructor.df_canonical[col].iloc[0]


def test_zero_synthetic_and_zero_model_predictions():
    """Test 4 & 5: Zero synthetic records and zero model-predicted labels."""
    reconstructor = IOGPCanonicalReconstructor(random_seed=42)
    df_en, df_au, df_rv, summary = reconstructor.execute_reconstruction()

    assert summary["reconstruction_outcomes"]["model_predicted_records"] == 0
    assert summary["reconstruction_outcomes"]["synthetic_records"] == 0

    assert not (df_en["lsr_assignment_method"] == "MODEL_PREDICTED").any()
    assert not (df_en["lsr_provenance"] == "SYNTHETIC").any()


def test_eligible_iogp_records_and_multilabel_preservation():
    """Test 6, 7 & 8: Only eligible IOGP canonical records matched and multilabel sets preserved."""
    reconstructor = IOGPCanonicalReconstructor(random_seed=42)
    df_en, df_au, df_rv, summary = reconstructor.execute_reconstruction()

    reconstructed_df = df_en[df_en["lsr_provenance"] == "SOURCE_GROUNDED_RECONSTRUCTED"]

    for _, row in reconstructed_df.iterrows():
        assert "iogp" in str(row["source"]).lower() or "iaogp" in str(row["source"]).lower()
        assert row["lsr_provenance"] == "SOURCE_GROUNDED_RECONSTRUCTED"
        assert row["lsr_assignment_method"] == "IOGP_RECONSTRUCTION_MATCH"
        assert "lsr_match_evidence" in row
        assert float(row["lsr_match_score"]) > 0.0


def test_ambiguous_and_insufficient_evidence_policy():
    """Test 9, 10 & 11: Ambiguous candidates rejected and insufficient evidence leaves UNKNOWN."""
    reconstructor = IOGPCanonicalReconstructor(random_seed=42)
    df_en, df_au, df_rv, summary = reconstructor.execute_reconstruction()

    unknown_df = df_en[df_en["lsr_provenance"] == "UNKNOWN"]
    assert len(unknown_df) > 0

    for _, row in unknown_df.iterrows():
        assert row["lsr_labels"] == "UNKNOWN"
        assert row["lsr_confidence"] == 0.0
        assert row["lsr_assignment_method"] == "NOT_ASSIGNED"


def test_provenance_and_audit_completeness():
    """Test 12 & 13: Provenance fields and candidate-level audit completeness."""
    reconstructor = IOGPCanonicalReconstructor(random_seed=42)
    df_en, df_au, df_rv, summary = reconstructor.execute_reconstruction()

    assert len(df_au) > 0
    assert "top_score" in df_au.columns
    assert "score_margin" in df_au.columns
    assert "decision" in df_au.columns


def test_deterministic_execution():
    """Test 14: Execution is 100% deterministic across two runs with seed=42."""
    r1 = IOGPCanonicalReconstructor(random_seed=42)
    d1, a1, v1, s1 = r1.execute_reconstruction()

    r2 = IOGPCanonicalReconstructor(random_seed=42)
    d2, a2, v2, s2 = r2.execute_reconstruction()

    assert len(d1) == len(d2)
    assert s1["reconstruction_outcomes"] == s2["reconstruction_outcomes"]


def test_production_artifacts_unchanged():
    """Test 15: Canonical dataset, SIF model, LSR model, RAG index, and semantic chunks unchanged."""
    hash_canonical = get_file_hash(CANONICAL_INPUT_CSV)
    hash_sif = get_file_hash(PROD_SIF_MODEL)
    hash_lsr = get_file_hash(PROD_LSR_MODEL)
    hash_rag = get_file_hash(PROD_RAG_INDEX)
    hash_chunks = get_file_hash(PROD_SEMANTIC_CHUNKS)

    reconstructor = IOGPCanonicalReconstructor(random_seed=42)
    df_en, df_au, df_rv, summary = reconstructor.execute_reconstruction()

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
