"""
test_rag_api.py - Integration QA Tests for /api/v1/analyze with RAG Recommendations.
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.main import app

client = TestClient(app)


def test_api_analyze_with_rag_recommendations():
    """Verify POST /api/v1/analyze returns grounded recommendations with citations and preserves backward compatibility."""
    payload = {
        "incident_text": "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting. The bleeder plug ruptured.",
        "incident_id": "INC-STAGE16-TEST01"
    }

    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["incident_id"] == "INC-STAGE16-TEST01"
    assert "sif" in data
    assert "lsr" in data
    assert "recommendations" in data

    rec = data["recommendations"]
    assert "status" in rec
    assert rec["status"] in ["GROUNDED", "INSUFFICIENT_SOURCE_SUPPORT", "FALLBACK"]
    assert "grounded" in rec
    assert "priority" in rec
    assert "summary" in rec
    assert "immediate_actions" in rec
    assert "control_verification" in rec # Backward compatibility check
    assert "escalation" in rec # Backward compatibility check
    assert "sources" in rec
    assert len(rec["sources"]) > 0

    first_source = rec["sources"][0]
    assert "document" in first_source
    assert "page" in first_source


def test_api_analyze_negative_control():
    """Verify POST /api/v1/analyze works for low-risk negative control."""
    payload = {
        "incident_text": "An employee experienced a minor slip while walking on a dry, level office floor. No injury occurred and no hazardous energy was involved.",
        "incident_id": "INC-STAGE16-TEST02"
    }

    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["sif"]["risk_tier"] == "LOW_POTENTIAL_INCIDENT"
    assert data["recommendations"]["priority"] == "LOW"
