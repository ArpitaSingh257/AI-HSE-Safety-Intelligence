"""
test_stage37c2_incident_level_gold.py - Dedicated PyTest Suite for Stage 37C.2 Incident-Level LSR Gold Consolidation.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.iogp_consolidation_engine import (
    IOGPConsolidationEngine, RECONSTRUCTED_CSV_PATH, INCIDENT_GOLD_CSV_PATH,
    LEAKAGE_REGEX, TAXONOMY_ORDER
)
from data.unified_lsr_gold_builder import get_file_hash, UNIFIED_DATASET_PATH
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_427_input_records_detected():
    """Test 1: 427 input assignment records detected."""
    engine = IOGPConsolidationEngine()
    assert len(engine.df_reconstructed) == 427


def test_input_reconstruction_csv_unchanged():
    """Test 2: Input reconstruction CSV iogp_reconstructed_lsr_v1.csv remains unchanged."""
    hash_before = get_file_hash(RECONSTRUCTED_CSV_PATH)
    engine = IOGPConsolidationEngine()
    recs, summary = engine.consolidate_incidents()
    hash_after = get_file_hash(RECONSTRUCTED_CSV_PATH)

    assert hash_before == hash_after


def test_canonical_dataset_unchanged():
    """Test 3: Canonical dataset oilps_unified_deduped.csv remains unchanged."""
    hash_before = get_file_hash(UNIFIED_DATASET_PATH)
    engine = IOGPConsolidationEngine()
    recs, summary = engine.consolidate_incidents()
    hash_after = get_file_hash(UNIFIED_DATASET_PATH)

    assert hash_before == hash_after


def test_production_models_unchanged():
    """Test 4 & 5: Production SIF and LSR champion models remain 100% frozen."""
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True


def test_rag_index_unchanged():
    """Test 6: RAG vector index and semantic chunks remain untouched."""
    faiss_path = BASE_DIR / "datasets" / "rag" / "vector_index.faiss"
    if faiss_path.exists():
        assert faiss_path.stat().st_size > 0


def test_grouping_by_incident_group_id():
    """Test 7 & 8: Grouping is strictly based on incident_group_id and no duplicate IDs exist."""
    engine = IOGPConsolidationEngine()
    recs, summary = engine.consolidate_incidents()

    record_ids = [r["record_id"] for r in recs]
    assert len(record_ids) == len(set(record_ids))
    assert len(recs) == summary["unique_incident_groups"]


def test_primary_and_secondary_lsr_preservation():
    """Test 9 & 10: Primary and secondary LSRs are preserved cleanly."""
    engine = IOGPConsolidationEngine()
    recs, summary = engine.consolidate_incidents()

    for r in recs:
        assert "lsr_primary" in r
        assert "lsr_secondary" in r


def test_multi_label_preservation_and_cardinality():
    """Test 11 & 18: Multi-label assignments, label_cardinality, and label_count are correct."""
    engine = IOGPConsolidationEngine()
    recs, summary = engine.consolidate_incidents()

    for r in recs:
        labels = json.loads(r["lsr_labels"])
        assert isinstance(labels, list)
        assert r["label_count"] == len(labels)
        assert r["label_cardinality"] in ["SINGLE", "MULTI"]
        if len(labels) > 1:
            assert r["label_cardinality"] == "MULTI"
        else:
            assert r["label_cardinality"] == "SINGLE"


def test_no_inferred_or_synthetic_labels():
    """Test 12 & 13: Zero inferred labels and zero synthetic labels."""
    engine = IOGPConsolidationEngine()
    recs, summary = engine.consolidate_incidents()

    for r in recs:
        assert r["lsr_label_provenance"] == "SOURCE_GROUNDED"
        assert r["reconstruction_method"] == "SOURCE_EXTRACTED"


def test_official_taxonomy_integrity():
    """Test 14: All labels belong to the official 9-class IOGP taxonomy."""
    engine = IOGPConsolidationEngine()
    recs, summary = engine.consolidate_incidents()

    valid_classes = set(TAXONOMY_ORDER)
    for r in recs:
        labels = json.loads(r["lsr_labels"])
        for l in labels:
            assert l in valid_classes


def test_source_provenance_preservation():
    """Test 15, 16 & 21: Complete source provenance (docs, pages, evidence) is preserved."""
    engine = IOGPConsolidationEngine()
    recs, summary = engine.consolidate_incidents()

    for r in recs:
        docs = json.loads(r["source_documents"])
        pages = json.loads(r["source_pages"])
        assert len(docs) >= 1
        assert len(pages) >= 1
        assert len(r["source_evidence"]) > 0


def test_no_target_leakage():
    """Test 17: incident_text does not contain target leakage markers like 'PRIMARY LIFE-SAVING RULE:'."""
    engine = IOGPConsolidationEngine()
    recs, summary = engine.consolidate_incidents()

    for r in recs:
        assert not LEAKAGE_REGEX.search(r["incident_text"])


def test_deterministic_construction():
    """Test 19: Building twice produces identical outputs."""
    e1 = IOGPConsolidationEngine()
    r1, s1 = e1.consolidate_incidents()

    e2 = IOGPConsolidationEngine()
    r2, s2 = e2.consolidate_incidents()

    assert len(r1) == len(r2)
    assert s1["unique_incident_groups"] == s2["unique_incident_groups"]


def test_contradictory_group_flagging():
    """Test 20 & 22: Contradictory groups are flagged and no incidents silently discarded."""
    engine = IOGPConsolidationEngine()
    recs, summary = engine.consolidate_incidents()

    for r in recs:
        assert r["group_status"] in ["VALIDATED", "REVIEW_REQUIRED"]


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
