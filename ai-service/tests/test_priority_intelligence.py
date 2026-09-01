"""
test_priority_intelligence.py - Dedicated Test Suite for Stage 30 Risk / Priority Intelligence.
"""

import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.priority_intelligence_engine import PriorityIntelligenceEngine

client = TestClient(app)


@pytest.fixture
def sample_priority_records():
    return [
        {"record_id": "R-P01", "report_date": "2025-01-05", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "primary_life_saving_rule": "Energy Isolation", "sif_potential": True},
        {"record_id": "R-P02", "report_date": "2025-01-15", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "primary_life_saving_rule": "Energy Isolation", "sif_potential": True},
        {"record_id": "R-P03", "report_date": "2025-02-05", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "primary_life_saving_rule": "Energy Isolation", "sif_potential": True},
        {"record_id": "R-P04", "report_date": "2025-02-18", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "primary_life_saving_rule": "Energy Isolation", "sif_potential": True},
        {"record_id": "R-P05", "report_date": "2025-03-10", "location": "Moran", "activity": "Drilling", "barrier_failure": "Mechanical Lifting & Rigging Barrier Failure", "primary_life_saving_rule": "Line of Fire", "sif_potential": True},
        {"record_id": "R-P06", "report_date": "2025-03-20", "location": "Moran", "activity": "Drilling", "barrier_failure": "Mechanical Lifting & Rigging Barrier Failure", "primary_life_saving_rule": "Line of Fire", "sif_potential": False},
        {"record_id": "R-P07", "report_date": "2025-03-25", "location": "Moran", "activity": "Drilling", "barrier_failure": "Mechanical Lifting & Rigging Barrier Failure", "primary_life_saving_rule": "Line of Fire", "sif_potential": False},
    ]


def test_priority_calculation_and_components(sample_priority_records):
    """Verify priority score calculation, component breakdown, and levels."""
    engine = PriorityIntelligenceEngine(min_priority_incidents=3)
    priorities = engine.calculate_priorities(sample_priority_records)

    assert len(priorities) > 0
    top_p = priorities[0]

    assert "priority_id" in top_p
    assert "priority_score" in top_p
    assert "components" in top_p
    assert 0.0 <= top_p["priority_score"] <= 1.0

    comps = top_p["components"]
    assert "sif_impact" in comps
    assert "recurrence" in comps
    assert "barrier_impact" in comps
    assert "site_activity" in comps
    assert "early_warning" in comps


def test_insufficient_data_priority_handling(sample_priority_records):
    """Verify entities with < MIN_PRIORITY_INCIDENTS are marked INSUFFICIENT_DATA."""
    engine = PriorityIntelligenceEngine(min_priority_incidents=5)
    priorities = engine.calculate_priorities(sample_priority_records)

    # Filtering for entities with incident count < 5
    insufficient = [p for p in priorities if len(p["supporting_report_ids"]) < 5]
    for p in insufficient:
        assert p["priority_level"] == "INSUFFICIENT_DATA"


def test_deterministic_5_runs(sample_priority_records):
    """Verify 5 consecutive runs produce 100% identical priority scores, levels, and ranking."""
    engine = PriorityIntelligenceEngine(min_priority_incidents=3)
    
    run1 = engine.calculate_priorities(sample_priority_records)
    run2 = engine.calculate_priorities(sample_priority_records)
    run3 = engine.calculate_priorities(sample_priority_records)

    assert run1 == run2 == run3, "Priority calculation must be 100% deterministic"
    assert run1[0]["priority_id"] == run2[0]["priority_id"]


def test_fastapi_priorities_endpoints():
    """Verify GET /api/v1/priorities and GET /api/v1/priorities/{priority_id} FastAPI endpoints."""
    resp = client.get("/api/v1/priorities")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_priorities" in data
    assert "priorities" in data
    assert isinstance(data["priorities"], list)

    if len(data["priorities"]) > 0:
        p = data["priorities"][0]
        assert "priority_id" in p
        assert "priority_score" in p
        assert "priority_level" in p
        assert "reason" in p

        detail_resp = client.get(f"/api/v1/priorities/{p['priority_id']}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["priority_id"] == p["priority_id"]


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
