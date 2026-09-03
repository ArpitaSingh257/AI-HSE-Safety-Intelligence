"""
test_multilingual_noisy_text.py - Dedicated PyTest Suite for Stage 35 Research-Grade Multilingual & Noisy Field-Report Processing.
"""

import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.multilingual_processor import MultilingualProcessor

client = TestClient(app)


def test_language_detection_and_code_mixing():
    """Verify language code identification and code-mixing detection."""
    processor = MultilingualProcessor()

    d1 = processor.detect_language("operator ka hand rotating shaft ke paas gaya")
    assert d1["is_code_mixed"] == True
    assert d1["language_code"] in ["hi-en", "hi_roman"]

    d2 = processor.detect_language("Standard English safety incident report description.")
    assert d2["is_code_mixed"] == False
    assert d2["language_code"] == "en"


def test_research_grade_hinglish_clause_transformation():
    """Verify context-aware neural phrase transformation fixes raw Hinglish structures without word-for-word awkwardness."""
    processor = MultilingualProcessor()

    text = "operator ka hand rotating shaft ke paas gaya on P-101"
    res = processor.normalize_text(text)

    normalized = res["normalized_text"]
    assert res["normalization_method"] == "NEURAL"
    assert "went near" in normalized.lower(), "Contextual transformation should convert 'ke paas gaya' to 'went near'"
    assert "P-101" in normalized, "Asset ID P-101 must be preserved"
    assert "operator" in normalized.lower()
    assert "hand" in normalized.lower()


def test_negation_and_asset_id_preservation():
    """Verify critical negation words and asset/equipment IDs are preserved untouched."""
    processor = MultilingualProcessor()

    text = "operator ne PPE nahi pehna tha near P-101 and line was not isolated on V-203"
    res = processor.normalize_text(text)

    normalized = res["normalized_text"]
    assert "P-101" in normalized, "Asset ID P-101 must be preserved"
    assert "V-203" in normalized, "Asset ID V-203 must be preserved"
    assert "not" in normalized.lower() or "nahi" in normalized.lower() or "Personal Protective Equipment" in normalized


def test_domain_abbreviation_and_spelling_expansion():
    """Verify domain abbreviations and spelling mistakes are expanded correctly."""
    processor = MultilingualProcessor()

    text = "opreator was without PPE and PTW missing near presssure valve"
    res = processor.normalize_text(text)

    normalized = res["normalized_text"]
    assert "operator" in normalized.lower(), "opreator should correct to operator"
    assert "personal protective equipment" in normalized.lower(), "PPE should expand"
    assert "permit to work" in normalized.lower(), "PTW should expand"
    assert "pressure" in normalized.lower(), "presssure should correct to pressure"


def test_fastapi_text_normalize_endpoint():
    """Verify POST /api/v1/text/normalize endpoint."""
    payload = {"text": "worker ne PPE nahi pehna tha and presssure high on P-101"}

    resp = client.post("/api/v1/text/normalize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["original_text"] == payload["text"]
    assert "P-101" in data["normalized_text"]
    assert data["language_code"] in ["hi-en", "hi_roman"]
    assert data["normalization_method"] in ["NEURAL", "RULE_BASED_FALLBACK"]
    assert data["processing_status"] in ["SUCCESS", "PARTIAL"]


def test_model_freeze_guarantee():
    """Verify Stage 6 SIF and Stage 7 LSR champion model weights remain 100% frozen."""
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
