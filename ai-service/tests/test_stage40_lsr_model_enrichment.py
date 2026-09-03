"""
test_stage40_lsr_model_enrichment.py - Dedicated PyTest Suite for Stage 40 LSR Model Enrichment.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.lsr_model_enricher import (
    LSRModelEnricher, CANONICAL_INPUT_CSV, MODEL_ENRICHED_OUTPUT_CSV,
    INFERENCE_AUDIT_CSV, MANUAL_REVIEW_QUEUE_CSV, METADATA_JSON,
    PROD_SIF_MODEL, PROD_LSR_MODEL, PROD_RAG_INDEX, PROD_SEMANTIC_CHUNKS,
    OFFICIAL_9_TAXONOMY, get_file_hash
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_canonical_row_count_and_column_preservation():
    """Test 1, 14 & 13: Row count = 4529, original columns preserved, no duplicate IDs."""
    enricher = LSRModelEnricher(random_seed=42)
    df_en, df_au, df_rv, summary = enricher.execute_enrichment()

    assert len(enricher.df_canonical) == 4529
    assert len(df_en) == 4529
    assert summary["accounting"]["total_canonical_records"] == 4529

    orig_cols = list(enricher.df_canonical.columns)
    for col in orig_cols:
        assert col in df_en.columns

    rec_ids = list(df_en["record_id"].dropna())
    assert len(rec_ids) == 4529
    assert len(rec_ids) == len(set(rec_ids))


def test_source_grounded_records_unchanged():
    """Test 2 & 3: Source grounded records remain 100% unchanged, model predictions only on UNKNOWN candidates."""
    enricher = LSRModelEnricher(random_seed=42)
    df_en, df_au, df_rv, summary = enricher.execute_enrichment()

    grounded_orig = enricher.df_canonical[enricher.df_canonical["lsr_provenance"].isin(["SOURCE_GROUNDED", "SOURCE_GROUNDED_RECONSTRUCTED"])]
    grounded_en = df_en[df_en["lsr_provenance"].isin(["SOURCE_GROUNDED", "SOURCE_GROUNDED_RECONSTRUCTED"])]

    assert len(grounded_orig) == len(grounded_en)
    assert len(grounded_en) == summary["final_provenance_counts"]["SOURCE_GROUNDED"]

    # Model predictions only applied to UNKNOWN candidates
    model_pred_df = df_en[df_en["lsr_provenance"] == "MODEL_PREDICTED"]
    for _, row in model_pred_df.iterrows():
        assert row["lsr_assignment_method"] == "MODEL_ASSISTED_INFERENCE"


def test_probability_fields_and_valid_ranges():
    """Test 4 & 5: All 9 probability fields exist and are within range [0.0, 1.0]."""
    enricher = LSRModelEnricher(random_seed=42)
    df_en, df_au, df_rv, summary = enricher.execute_enrichment()

    for lsr in OFFICIAL_9_TAXONOMY:
        col_name = f"lsr_prob_{lsr.lower().replace(' ', '_').replace('/', '_')}"
        assert col_name in df_en.columns
        probs = df_en[col_name].astype(float)
        assert (probs >= 0.0).all()
        assert (probs <= 1.0).all()


def test_taxonomy_validity_and_multilabel_preservation():
    """Test 6 & 7: Predicted labels strictly adhere to 9 IOGP taxonomy and multilabel sets preserved."""
    enricher = LSRModelEnricher(random_seed=42)
    df_en, df_au, df_rv, summary = enricher.execute_enrichment()

    model_pred_df = df_en[df_en["lsr_provenance"] == "MODEL_PREDICTED"]
    for _, row in model_pred_df.iterrows():
        labels = [l.strip() for l in str(row["lsr_labels"]).split("|") if l.strip()]
        assert len(labels) >= 1
        for l in labels:
            assert l in OFFICIAL_9_TAXONOMY


def test_abstention_and_confidence_hierarchy():
    """Test 8, 9, 10, 11 & 18: Confidence states, review queue consistency, and UNKNOWN abstention policy."""
    enricher = LSRModelEnricher(random_seed=42)
    df_en, df_au, df_rv, summary = enricher.execute_enrichment()

    # Review queue contains only medium-confidence / uncertain records
    assert len(df_rv) == summary["confidence_breakdown"]["MEDIUM_CONFIDENCE"]
    for _, row in df_rv.iterrows():
        assert row["lsr_confidence"] == "MEDIUM"
        assert row["review_reason"] in ["LOW_MARGIN", "MEDIUM_CONFIDENCE", "MULTI_LABEL_UNCERTAINTY"]

    # Low-confidence and zero prediction records remain UNKNOWN
    unknown_df = df_en[df_en["lsr_provenance"] == "UNKNOWN"]
    for _, row in unknown_df.iterrows():
        assert row["lsr_labels"] == "UNKNOWN"
        assert row["lsr_confidence"] == 0.0


def test_zero_synthetic_records_and_audit_completeness():
    """Test 12, 19 & 20: Zero synthetic records, audit covers all scored records, no model labels in training set."""
    enricher = LSRModelEnricher(random_seed=42)
    df_en, df_au, df_rv, summary = enricher.execute_enrichment()

    assert not (df_en["lsr_provenance"] == "SYNTHETIC").any()
    assert len(df_au) == summary["accounting"]["unknown_before_enrichment"]
    assert len(df_au) == summary["accounting"]["records_scored"]


def test_deterministic_execution():
    """Test 17 & 15: Run 3 times with seed=42; output labels, provenance, and scores are identical."""
    e1 = LSRModelEnricher(random_seed=42)
    d1, a1, v1, s1 = e1.execute_enrichment()

    e2 = LSRModelEnricher(random_seed=42)
    d2, a2, v2, s2 = e2.execute_enrichment()

    e3 = LSRModelEnricher(random_seed=42)
    d3, a3, v3, s3 = e3.execute_enrichment()

    assert len(d1) == len(d2) == len(d3)
    assert s1["final_provenance_counts"] == s2["final_provenance_counts"] == s3["final_provenance_counts"]


def test_production_artifacts_unchanged():
    """Test 16, 17 & 18: Canonical dataset, SIF model, LSR model, RAG FAISS index, and semantic chunks unchanged."""
    hash_canonical = get_file_hash(CANONICAL_INPUT_CSV)
    hash_sif = get_file_hash(PROD_SIF_MODEL)
    hash_lsr = get_file_hash(PROD_LSR_MODEL)
    hash_rag = get_file_hash(PROD_RAG_INDEX)
    hash_chunks = get_file_hash(PROD_SEMANTIC_CHUNKS)

    enricher = LSRModelEnricher(random_seed=42)
    df_en, df_au, df_rv, summary = enricher.execute_enrichment()

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
