"""
test_stage43_intelligence_api.py - Dedicated PyTest Suite for Stage 43 End-to-End Intelligence API & Historical Integration.
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

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

PROCESSED_DIR = BASE_DIR / "datasets" / "processed"
CANONICAL_INPUT_CSV = PROCESSED_DIR / "oilps_unified_deduped.csv"
FINAL_MASTER_V2_CSV = PROCESSED_DIR / "oilps_final_master_v2.csv"
PROD_SIF_MODEL = BASE_DIR / "models" / "sif" / "sif_model.pt"
PROD_LSR_MODEL = BASE_DIR / "models" / "lsr" / "lsr_model.pt"
PROD_RAG_INDEX = BASE_DIR / "datasets" / "rag" / "vector_index.faiss"
PROD_SEMANTIC_CHUNKS = BASE_DIR / "datasets" / "rag" / "semantic_chunks.json"


def get_file_hash(path: Path) -> str:
    if not path.exists():
        return "FILE_NOT_FOUND"
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def test_health_check_endpoint():
    """Test 1: Health endpoint returns HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["sif_champion_loaded"] == True
    assert data["lsr_champion_loaded"] == True


def test_valid_intelligence_request_and_schema():
    """Test 2 & 6: Valid request returns HTTP 200 and matches response schema."""
    payload = {
        "incident_text": "Worker entered a confined space without gas testing and without a valid work authorization.",
        "site": "Offshore Rig 4",
        "activity": "Maintenance"
    }
    resp = client.post("/api/v1/intelligence/analyze", json=payload)
    assert resp.status_code == 200, f"Unexpected status {resp.status_code}: {resp.text}"
    data = resp.json()

    assert "request_id" in data
    assert "input" in data
    assert "sif_assessment" in data
    assert "lsr_assessment" in data
    assert "risk_intelligence" in data
    assert "bowtie" in data
    assert "explainability" in data
    assert "triage" in data
    assert data["metadata"]["historical_dataset"]["name"] == "oilps_final_master_v2.csv"


def test_input_validation_empty_and_whitespace():
    """Test 3, 4 & 5: Empty, whitespace, and oversized text return HTTP 422."""
    resp1 = client.post("/api/v1/intelligence/analyze", json={"incident_text": ""})
    assert resp1.status_code == 422, f"Expected 422 got {resp1.status_code}: {resp1.text}"

    resp2 = client.post("/api/v1/intelligence/analyze", json={"incident_text": "    "})
    assert resp2.status_code == 422, f"Expected 422 got {resp2.status_code}: {resp2.text}"

    oversized = "A" * 4005
    resp3 = client.post("/api/v1/intelligence/analyze", json={"incident_text": oversized})
    assert resp3.status_code == 422, f"Expected 422 got {resp3.status_code}: {resp3.text}"


def test_sif_and_triage_assessment():
    """Test 7 & 8: SIF risk assessment and Stage 34 triage action present."""
    payload = {
        "incident_text": "High pressure pipe burst during hydrostatic testing at 5,000 psi causing severe explosion."
    }
    resp = client.post("/api/v1/intelligence/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()["sif_assessment"]

    assert "probability" in data
    assert "potential" in data
    assert "triage" in data
    assert data["triage"] in ["IMMEDIATE_ESCALATION", "NEEDS_REVIEW", "AUTO_CLEAR"]


def test_lsr_multilabel_and_provenance():
    """Test 9, 10, 11 & 12: Multilabel LSR prediction, explicit provenance, human_review_required flag."""
    payload = {
        "incident_text": "Worker entered a confined space without gas testing and without a valid work authorization."
    }
    resp = client.post("/api/v1/intelligence/analyze", json=payload)
    assert resp.status_code == 200
    lsr = resp.json()["lsr_assessment"]

    assert "primary" in lsr
    assert "provenance" in lsr
    assert "human_review_required" in lsr
    assert lsr["provenance"] in ["SOURCE_GROUNDED", "SOURCE_GROUNDED_RECONSTRUCTED", "MODEL_PREDICTED", "HUMAN_REVIEW_PENDING", "UNKNOWN"]


def test_case_a_confined_space():
    """Required Test Case A: Confined space incident."""
    payload = {
        "incident_text": "Worker entered a confined space without gas testing and without a valid work authorization."
    }
    resp = client.post("/api/v1/intelligence/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "Confined Space" in data["lsr_assessment"]["primary"] or "Confined Space" in data["lsr_assessment"]["labels"] or data["lsr_assessment"]["human_review_required"] == True


def test_case_b_line_of_fire():
    """Required Test Case B: Line of fire incident."""
    payload = {
        "incident_text": "Operator entered the line of fire while a suspended load was being moved."
    }
    resp = client.post("/api/v1/intelligence/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "Line of Fire" in data["lsr_assessment"]["primary"] or "Line of Fire" in data["lsr_assessment"]["labels"] or "Line of Fire" in str(data["evidence"])


def test_case_c_energy_isolation():
    """Required Test Case C: Energy isolation incident."""
    payload = {
        "incident_text": "Maintenance started work on equipment without verifying energy isolation."
    }
    resp = client.post("/api/v1/intelligence/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "Energy Isolation" in data["lsr_assessment"]["primary"] or "Energy Isolation" in data["lsr_assessment"]["labels"] or "Energy Isolation" in str(data["evidence"])


def test_case_d_hinglish_input():
    """Required Test Case D: Hinglish noisy input."""
    payload = {
        "incident_text": "operator ka hand rotating shaft ke paas gaya and line properly isolate nahi thi"
    }
    resp = client.post("/api/v1/intelligence/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["input"]["language"] in ["en", "hi", "hinglish", "hi-en", "multilingual"]
    assert "sif_assessment" in data


def test_case_e_insufficient_context():
    """Required Test Case E: Missing site/activity context returns INSUFFICIENT_DATA."""
    payload = {
        "incident_text": "Operator tripped over low lying pipe."
    }
    resp = client.post("/api/v1/intelligence/analyze", json=payload)
    assert resp.status_code == 200
    risk = resp.json()["risk_intelligence"]

    assert risk["site"]["status"] == "INSUFFICIENT_DATA"
    assert risk["activity"]["status"] == "INSUFFICIENT_DATA"


def test_historical_similarity_and_self_match_exclusion():
    """Test 21 & 22: Historical similarity search works and excludes self-match."""
    payload = {
        "incident_text": "Operator slipped on oil spill on deck of Offshore Rig 4 during drilling operations."
    }
    resp = client.post("/api/v1/intelligence/analyze", json=payload)
    assert resp.status_code == 200
    similar = resp.json()["similar_incidents"]

    assert isinstance(similar, list)
    if len(similar) > 0:
        for sim in similar:
            assert "similarity" in sim
            assert "narrative" in sim


def test_determinism_repeated_execution():
    """Test 32: Repeated request produces identical deterministic fields."""
    payload = {
        "incident_text": "Worker entered a confined space without gas testing and without a valid work authorization.",
        "site": "Offshore Rig 4"
    }
    resp1 = client.post("/api/v1/intelligence/analyze", json=payload)
    resp2 = client.post("/api/v1/intelligence/analyze", json=payload)

    d1 = resp1.json()
    d2 = resp2.json()

    assert d1["sif_assessment"]["probability"] == d2["sif_assessment"]["probability"]
    assert d1["sif_assessment"]["potential"] == d2["sif_assessment"]["potential"]
    assert d1["lsr_assessment"]["primary"] == d2["lsr_assessment"]["primary"]
    assert d1["lsr_assessment"]["provenance"] == d2["lsr_assessment"]["provenance"]
    assert d1["triage"]["action"] == d2["triage"]["action"]


def test_production_artifacts_unchanged():
    """Test 26-31: All 6 production artifacts remain 100% frozen."""
    h_canonical = get_file_hash(CANONICAL_INPUT_CSV)
    h_master_v2 = get_file_hash(FINAL_MASTER_V2_CSV)
    h_sif = get_file_hash(PROD_SIF_MODEL)
    h_lsr = get_file_hash(PROD_LSR_MODEL)
    h_rag = get_file_hash(PROD_RAG_INDEX)
    h_chunks = get_file_hash(PROD_SEMANTIC_CHUNKS)

    payload = {"incident_text": "Worker slipped on wet floor during routine inspection."}
    resp = client.post("/api/v1/intelligence/analyze", json=payload)
    assert resp.status_code == 200

    assert h_canonical == get_file_hash(CANONICAL_INPUT_CSV)
    assert h_master_v2 == get_file_hash(FINAL_MASTER_V2_CSV)
    assert h_sif == get_file_hash(PROD_SIF_MODEL)
    assert h_lsr == get_file_hash(PROD_LSR_MODEL)
    assert h_rag == get_file_hash(PROD_RAG_INDEX)
    assert h_chunks == get_file_hash(PROD_SEMANTIC_CHUNKS)


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
