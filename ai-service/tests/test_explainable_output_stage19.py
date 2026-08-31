"""
test_explainable_output_stage19.py - Automated QA Test Suite for Stage 19 Explainable Output.
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.main import app
from inference.explainability import SafetyIntelligenceFormatter

client = TestClient(app)


def test_stage19_hydrotest_explainability():
    """Verify Hydrotest scenario produces explainable output with Risk=CRITICAL and grounded evidence."""
    payload = {
        "incident_text": "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator was exposed to a pressure release after a bleeder plug ruptured.",
        "incident_id": "INC-STAGE19-01"
    }

    resp = client.post("/api/v1/analyze", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert "explainability" in data
    exp = data["explainability"]

    assert exp["risk_level_display"] == "🔴 CRITICAL"
    assert "Model probability" in exp["sif_interpretation"]
    assert len(exp["why_flagged"]) > 0
    assert len(exp["lsr_explanations"]) > 0
    assert "GROUNDED" in exp["grounding_banner"]
    assert "SAFETY INTELLIGENCE RESULT" in exp["formatted_text"]


def test_stage19_crane_explainability():
    """Verify Crane scenario produces explainable output with Safe Mechanical Lifting explanation."""
    payload = {
        "incident_text": "During a crane lifting operation, a suspended load shifted unexpectedly and entered the line of fire of personnel working nearby.",
        "incident_id": "INC-STAGE19-02"
    }

    resp = client.post("/api/v1/analyze", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    exp = data["explainability"]
    assert exp["risk_level_display"] == "🔴 CRITICAL"
    assert any("Lifting" in l["rule"] or "Fire" in l["rule"] for l in exp["lsr_explanations"])


def test_stage19_confined_space_explainability():
    """Verify Confined Space scenario produces explainable output with toxic gas explanation."""
    payload = {
        "incident_text": "During vessel entry preparation, an operator was exposed to a potential H2S atmosphere inside a confined space.",
        "incident_id": "INC-STAGE19-03"
    }

    resp = client.post("/api/v1/analyze", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    exp = data["explainability"]
    assert exp["risk_level_display"] == "🔴 CRITICAL"
    assert "SIF" in exp["sif_interpretation"]
    assert len(exp["why_flagged"]) > 0


def test_stage19_minor_slip_explainability():
    """Verify Minor Slip scenario produces low-risk explainable output without false grounding or fabrication."""
    payload = {
        "incident_text": "An employee experienced a minor slip while walking on a dry, level office floor. No injury occurred.",
        "incident_id": "INC-STAGE19-04"
    }

    resp = client.post("/api/v1/analyze", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    exp = data["explainability"]
    assert exp["risk_level_display"] == "🟢 LOW"
    assert len(exp["lsr_explanations"]) == 0
    assert "No significant SIF precursor" in exp["sif_interpretation"]


def test_stage19_evidence_traceability():
    """Verify every displayed evidence source is traceable to retrieved PDF metadata."""
    payload = {
        "incident_text": "Pressure line bleeder plug rupture event.",
        "incident_id": "INC-STAGE19-05"
    }

    resp = client.post("/api/v1/analyze", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    rec = data["recommendations"]
    sources = rec.get("sources", [])
    assert len(sources) > 0

    first = sources[0]
    assert "document" in first and first["document"].endswith(".pdf")
    assert "page" in first and first["page"] >= 1
    assert "snippet" in first
