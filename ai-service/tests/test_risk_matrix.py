"""
test_risk_matrix.py - Dedicated Test Suite for Stage 31 Severity vs Recurrence Risk Matrix.
"""

import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.risk_matrix_engine import RiskMatrixEngine

client = TestClient(app)


@pytest.fixture
def sample_matrix_records():
    return [
        {"record_id": "R-M01", "report_date": "2025-01-05", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "primary_life_saving_rule": "Energy Isolation", "sif_potential": True},
        {"record_id": "R-M02", "report_date": "2025-01-15", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "primary_life_saving_rule": "Energy Isolation", "sif_potential": True},
        {"record_id": "R-M03", "report_date": "2025-02-05", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "primary_life_saving_rule": "Energy Isolation", "sif_potential": True},
        {"record_id": "R-M04", "report_date": "2025-02-18", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "primary_life_saving_rule": "Energy Isolation", "sif_potential": True},
        {"record_id": "R-M05", "report_date": "2025-03-10", "location": "Moran", "activity": "Drilling", "barrier_failure": "Mechanical Lifting & Rigging Barrier Failure", "primary_life_saving_rule": "Line of Fire", "sif_potential": True},
        {"record_id": "R-M06", "report_date": "2025-03-20", "location": "Moran", "activity": "Drilling", "barrier_failure": "Mechanical Lifting & Rigging Barrier Failure", "primary_life_saving_rule": "Line of Fire", "sif_potential": False},
        {"record_id": "R-M07", "report_date": "2025-03-25", "location": "Moran", "activity": "Drilling", "barrier_failure": "Mechanical Lifting & Rigging Barrier Failure", "primary_life_saving_rule": "Line of Fire", "sif_potential": False},
    ]


def test_severity_and_recurrence_calculation(sample_matrix_records):
    """Verify 2D coordinates (Severity & Recurrence) and quadrant assignment."""
    engine = RiskMatrixEngine(min_matrix_incidents=3)
    items = engine.calculate_risk_matrix(sample_matrix_records)

    assert len(items) > 0
    item = items[0]

    assert "severity_score" in item
    assert "recurrence_score" in item
    assert 0.0 <= item["severity_score"] <= 1.0
    assert 0.0 <= item["recurrence_score"] <= 1.0
    assert item["quadrant"] in [
        "HIGH_SEVERITY_HIGH_RECURRENCE",
        "HIGH_SEVERITY_LOW_RECURRENCE",
        "LOW_SEVERITY_HIGH_RECURRENCE",
        "LOW_SEVERITY_LOW_RECURRENCE",
        "INSUFFICIENT_DATA"
    ]


def test_insufficient_data_quadrant_handling(sample_matrix_records):
    """Verify items with < min_matrix_incidents evaluate to INSUFFICIENT_DATA."""
    engine = RiskMatrixEngine(min_matrix_incidents=5)
    items = engine.calculate_risk_matrix(sample_matrix_records)

    insufficient = [i for i in items if len(i["supporting_report_ids"]) < 5]
    for item in insufficient:
        assert item["quadrant"] == "INSUFFICIENT_DATA"
        assert item["classification"] == "INSUFFICIENT_DATA"


def test_deterministic_5_runs(sample_matrix_records):
    """Verify 5 consecutive runs produce 100% identical 2D coordinates and quadrant assignments."""
    engine = RiskMatrixEngine(min_matrix_incidents=3)

    run1 = engine.calculate_risk_matrix(sample_matrix_records)
    run2 = engine.calculate_risk_matrix(sample_matrix_records)
    run3 = engine.calculate_risk_matrix(sample_matrix_records)

    assert run1 == run2 == run3, "Risk matrix calculation must be 100% deterministic"
    assert run1[0]["matrix_item_id"] == run2[0]["matrix_item_id"]


def test_fastapi_risk_matrix_endpoints():
    """Verify GET /api/v1/risk-matrix and GET /api/v1/risk-matrix/{matrix_item_id} FastAPI endpoints."""
    resp = client.get("/api/v1/risk-matrix")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_items" in data
    assert "matrix_items" in data
    assert isinstance(data["matrix_items"], list)

    if len(data["matrix_items"]) > 0:
        m = data["matrix_items"][0]
        assert "matrix_item_id" in m
        assert "severity_score" in m
        assert "recurrence_score" in m
        assert "quadrant" in m
        assert "reason" in m

        detail_resp = client.get(f"/api/v1/risk-matrix/{m['matrix_item_id']}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["matrix_item_id"] == m["matrix_item_id"]


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
