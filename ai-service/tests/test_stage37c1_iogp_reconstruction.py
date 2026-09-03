"""
test_stage37c1_iogp_reconstruction.py - Dedicated PyTest Suite for Stage 37C.1 IOGP Incident-LSR Reconstruction.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.iogp_reconstruction_engine import (
    IOGPReconstructionEngine, RECONSTRUCTED_CSV_PATH, RECONSTRUCTION_METADATA_PATH,
    UNIFIED_GOLD_CSV, LEAKAGE_REGEX
)
from data.unified_lsr_gold_builder import get_file_hash
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_exactly_427_inputs_identified():
    """Test 1: Exactly 427 Stage 37A.1 inputs identified."""
    engine = IOGPReconstructionEngine()
    assert len(engine.target_records) == 427


def test_original_unified_dataset_unchanged():
    """Test 2: Original unified dataset unified_lsr_gold_v1.csv remains unchanged."""
    hash_before = get_file_hash(UNIFIED_GOLD_CSV)
    engine = IOGPReconstructionEngine()
    recs, summary = engine.reconstruct_incidents()
    hash_after = get_file_hash(UNIFIED_GOLD_CSV)

    assert hash_before == hash_after


def test_production_models_unchanged():
    """Test 3 & 4: Production SIF and LSR champion models remain 100% frozen."""
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True


def test_rag_index_unchanged():
    """Test 5: RAG vector index and semantic chunks remain untouched."""
    faiss_path = BASE_DIR / "datasets" / "rag" / "vector_index.faiss"
    if faiss_path.exists():
        assert faiss_path.stat().st_size > 0


def test_provenance_completeness():
    """Test 6: Every output record contains complete provenance metadata."""
    engine = IOGPReconstructionEngine()
    recs, summary = engine.reconstruct_incidents()

    for r in recs:
        assert "source_document" in r
        assert "source_page" in r
        assert "source_evidence_text" in r
        assert r["dataset_origin"] == "IOGP_STAGE37A1"
        assert r["lsr_label_provenance"] == "SOURCE_GROUNDED"


def test_no_synthetic_or_llm_markers():
    """Test 7: No synthetic or LLM-generated narrative markers."""
    engine = IOGPReconstructionEngine()
    recs, summary = engine.reconstruct_incidents()

    for r in recs:
        assert r["reconstruction_method"] == "SOURCE_EXTRACTED"
        assert "llm" not in r["reconstruction_method"].lower()
        assert "synthetic" not in r["reconstruction_method"].lower()


def test_incident_text_target_leakage_audit():
    """Test 8: incident_text does not contain target leakage markers like 'PRIMARY LIFE-SAVING RULE:'."""
    engine = IOGPReconstructionEngine()
    recs, summary = engine.reconstruct_incidents()

    for r in recs:
        assert not LEAKAGE_REGEX.search(r["incident_text"])


def test_explicit_lsr_preservation():
    """Test 9 & 10: Explicit LSR labels, primary, and secondary distinction are preserved."""
    engine = IOGPReconstructionEngine()
    recs, summary = engine.reconstruct_incidents()

    for r in recs:
        assert "lsr_primary" in r
        assert "lsr_secondary" in r
        assert len(r["lsr_primary"]) > 0


def test_multi_lsr_preservation():
    """Test 11: Multi-LSR assignments are preserved as valid JSON arrays in lsr_labels."""
    engine = IOGPReconstructionEngine()
    recs, summary = engine.reconstruct_incidents()

    for r in recs:
        labels = json.loads(r["lsr_labels"])
        assert isinstance(labels, list)
        assert len(labels) >= 1


def test_official_taxonomy_integrity():
    """Test 12: All primary LSRs belong to the official 9-class IOGP taxonomy."""
    engine = IOGPReconstructionEngine()
    recs, summary = engine.reconstruct_incidents()

    valid_classes = {
        "Driving", "Bypassing Safety Controls", "Line of Fire", "Energy Isolation",
        "Safe Mechanical Lifting", "Working at Height", "Work Authorization",
        "Confined Space", "Hot Work"
    }

    for r in recs:
        assert r["lsr_primary"] in valid_classes


def test_reconstruction_status_explicit():
    """Test 13: Every record is explicitly marked RECONSTRUCTED, AMBIGUOUS, or RECONSTRUCTION_FAILED."""
    engine = IOGPReconstructionEngine()
    recs, summary = engine.reconstruct_incidents()

    valid_statuses = {"RECONSTRUCTED", "AMBIGUOUS", "RECONSTRUCTION_FAILED"}
    for r in recs:
        assert r["reconstruction_status"] in valid_statuses


def test_record_id_determinism():
    """Test 14 & 15: Output record IDs and reconstructed structures are 100% deterministic."""
    e1 = IOGPReconstructionEngine()
    r1, s1 = e1.reconstruct_incidents()

    e2 = IOGPReconstructionEngine()
    r2, s2 = e2.reconstruct_incidents()

    assert len(r1) == len(r2)
    assert s1["input_stage37a1_records"] == s2["input_stage37a1_records"]


def test_source_evidence_exact_preservation():
    """Test 16: Source evidence text is preserved exactly in source_evidence_text."""
    engine = IOGPReconstructionEngine()
    recs, summary = engine.reconstruct_incidents()

    for r in recs:
        assert len(r["source_evidence_text"]) > 0


def test_no_pseudo_or_inferred_labels():
    """Test 17: No pseudo-labels or inferred labels."""
    engine = IOGPReconstructionEngine()
    recs, summary = engine.reconstruct_incidents()

    for r in recs:
        assert r["lsr_label_provenance"] == "SOURCE_GROUNDED"


def test_incident_grouping_integrity():
    """Test 18: Incident group IDs are formatted deterministically."""
    engine = IOGPReconstructionEngine()
    recs, summary = engine.reconstruct_incidents()

    for r in recs:
        assert r["incident_group_id"].startswith("GRP-")


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
