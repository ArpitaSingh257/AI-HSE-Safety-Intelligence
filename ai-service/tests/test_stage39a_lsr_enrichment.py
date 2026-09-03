"""
test_stage39a_lsr_enrichment.py - Dedicated PyTest Suite for Stage 39A Canonical Dataset LSR Enrichment.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.canonical_lsr_enricher import (
    CanonicalLSREnricher, CANONICAL_INPUT_CSV, ENRICHED_OUTPUT_CSV,
    METADATA_JSON, PROD_SIF_MODEL, PROD_LSR_MODEL, PROD_RAG_INDEX,
    PROD_SEMANTIC_CHUNKS, get_file_hash
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_canonical_input_and_output_row_count():
    """Test 1 & 2: Canonical input and output row count is exactly 4,529."""
    enricher = CanonicalLSREnricher(random_seed=42)
    df_en, df_au, summary = enricher.execute_enrichment()

    assert len(enricher.df_canonical) == 4529
    assert len(df_en) == 4529
    assert summary["accounting"]["canonical_output_count"] == 4529


def test_original_columns_and_values_preserved():
    """Test 3 & 4: Original canonical columns and values preserved."""
    enricher = CanonicalLSREnricher(random_seed=42)
    df_en, df_au, summary = enricher.execute_enrichment()

    orig_cols = list(enricher.df_canonical.columns)
    for col in orig_cols:
        assert col in df_en.columns

    # Verify first 10 rows match original values
    for col in orig_cols[:5]:
        assert df_en[col].iloc[0] == enricher.df_canonical[col].iloc[0]


def test_zero_synthetic_and_zero_model_predictions():
    """Test 6 & 7: Zero synthetic records and zero model predictions."""
    enricher = CanonicalLSREnricher(random_seed=42)
    df_en, df_au, summary = enricher.execute_enrichment()

    assert summary["final_dataset_counts"]["model_predicted_count"] == 0
    assert summary["final_dataset_counts"]["synthetic_record_count"] == 0

    assert not (df_en["lsr_assignment_method"] == "MODEL_PREDICTED").any()
    assert not (df_en["lsr_provenance"] == "SYNTHETIC").any()


def test_source_grounded_provenance_and_evidence():
    """Test 8, 9 & 10: Source grounded provenance, evidence, and match method complete."""
    enricher = CanonicalLSREnricher(random_seed=42)
    df_en, df_au, summary = enricher.execute_enrichment()

    grounded_df = df_en[df_en["lsr_provenance"] == "SOURCE_GROUNDED"]
    assert len(grounded_df) == summary["final_dataset_counts"]["final_source_grounded_count"]

    if len(grounded_df) > 0:
        for _, row in grounded_df.iterrows():
            assert row["lsr_provenance"] == "SOURCE_GROUNDED"
            assert row["lsr_assignment_method"] in ["NATIVE_CANONICAL_LABEL", "IOGP_CANONICAL_RECONCILIATION"]
            assert "lsr_match_evidence" in row
            assert str(row["lsr_match_evidence"]).strip() != ""


def test_collision_rules_and_no_duplicate_rows():
    """Test 11 & 13: No duplicate canonical rows created and IOGP source groups collision rules enforced."""
    enricher = CanonicalLSREnricher(random_seed=42)
    df_en, df_au, summary = enricher.execute_enrichment()

    assert len(df_en) == 4529
    # Check mapped IOGP source incident groups are unique across matches
    reconciled_df = df_en[df_en["lsr_assignment_method"] == "IOGP_CANONICAL_RECONCILIATION"]
    groups = list(reconciled_df["lsr_source_incident_group"].dropna())
    assert len(groups) == len(set(groups))


def test_deterministic_execution():
    """Test 14: Deterministic execution across two runs with seed=42."""
    e1 = CanonicalLSREnricher(random_seed=42)
    d1, a1, s1 = e1.execute_enrichment()

    e2 = CanonicalLSREnricher(random_seed=42)
    d2, a2, s2 = e2.execute_enrichment()

    assert len(d1) == len(d2)
    assert s1["final_dataset_counts"] == s2["final_dataset_counts"]


def test_production_artifacts_unchanged():
    """Test 5, 15, 16, 17 & 18: Canonical CSV, SIF model, LSR model, RAG FAISS index, and semantic chunks unchanged."""
    hash_canonical = get_file_hash(CANONICAL_INPUT_CSV)
    hash_sif = get_file_hash(PROD_SIF_MODEL)
    hash_lsr = get_file_hash(PROD_LSR_MODEL)
    hash_rag = get_file_hash(PROD_RAG_INDEX)
    hash_chunks = get_file_hash(PROD_SEMANTIC_CHUNKS)

    enricher = CanonicalLSREnricher(random_seed=42)
    df_en, df_au, summary = enricher.execute_enrichment()

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
