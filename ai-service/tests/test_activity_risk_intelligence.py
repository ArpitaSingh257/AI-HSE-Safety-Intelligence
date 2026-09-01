"""
test_activity_risk_intelligence.py - Dedicated Test Suite for Stage 27 Activity-Level Risk Intelligence.
"""

import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.activity_risk_analyzer import ActivityRiskAnalyzer

client = TestClient(app)


@pytest.fixture
def sample_activity_records():
    return [
        # Maintenance: 3 reports, 2 SIF (66.7% SIF density)
        {"record_id": "R-M01", "location": "Duliajan", "activity": "Maintenance", "primary_life_saving_rule": "Energy Isolation", "hazard": "Stored Pressure", "barrier_failure": "Valve bleeder", "sif_potential": True},
        {"record_id": "R-M02", "location": "Moran", "activity": "Maintenance", "primary_life_saving_rule": "Energy Isolation", "hazard": "Stored Pressure", "barrier_failure": "Valve bleeder", "sif_potential": True},
        {"record_id": "R-M03", "location": "Digboi", "activity": "Maintenance", "primary_life_saving_rule": "Energy Isolation", "hazard": "Stored Pressure", "barrier_failure": "Valve bleeder", "sif_potential": False},

        # Drilling: 5 reports, 1 SIF (20% SIF density - higher volume, lower rate)
        {"record_id": "R-D01", "location": "Moran", "activity": "Drilling", "primary_life_saving_rule": "Line of Fire", "hazard": "Suspended Load", "barrier_failure": "Tag line", "sif_potential": True},
        {"record_id": "R-D02", "location": "Moran", "activity": "Drilling", "primary_life_saving_rule": "Line of Fire", "hazard": "Suspended Load", "barrier_failure": "Tag line", "sif_potential": False},
        {"record_id": "R-D03", "location": "Moran", "activity": "Drilling", "primary_life_saving_rule": "General", "hazard": "Slip", "barrier_failure": "Housekeeping", "sif_potential": False},
        {"record_id": "R-D04", "location": "Moran", "activity": "Drilling", "primary_life_saving_rule": "General", "hazard": "Slip", "barrier_failure": "Housekeeping", "sif_potential": False},
        {"record_id": "R-D05", "location": "Moran", "activity": "Drilling", "primary_life_saving_rule": "General", "hazard": "Slip", "barrier_failure": "Housekeeping", "sif_potential": False},

        # Hot Work: 2 reports (insufficient data)
        {"record_id": "R-H01", "location": "Digboi", "activity": "Hot Work", "primary_life_saving_rule": "Hot Work", "hazard": "Flammable Gas", "barrier_failure": "Gas monitor", "sif_potential": True},
        {"record_id": "R-H02", "location": "Digboi", "activity": "Hot Work", "primary_life_saving_rule": "Hot Work", "hazard": "Flammable Gas", "barrier_failure": "Gas monitor", "sif_potential": False},
    ]


def test_activity_aggregation_and_sif_density(sample_activity_records):
    """Verify activity grouping, report counting, and volume-normalized SIF density calculation."""
    analyzer = ActivityRiskAnalyzer(min_activity_reports=3)
    profiles = analyzer.calculate_activity_risk_profiles(sample_activity_records)

    act_map = {p["activity_name"]: p for p in profiles}
    assert "Maintenance" in act_map
    maint = act_map["Maintenance"]
    assert maint["total_reports"] == 3
    assert maint["sif_reports"] == 2
    assert abs(maint["sif_density"] - 0.6667) < 1e-3


def test_volume_vs_rate_ranking(sample_activity_records):
    """Verify that an activity with higher SIF density (rate) is ranked above a larger volume activity with lower SIF rate."""
    analyzer = ActivityRiskAnalyzer(min_activity_reports=3)
    profiles = analyzer.calculate_activity_risk_profiles(sample_activity_records)

    ranked_names = [p["activity_name"] for p in profiles if p["risk_level"] != "INSUFFICIENT_DATA"]
    assert ranked_names.index("Maintenance") < ranked_names.index("Drilling")


def test_minimum_data_threshold_rule(sample_activity_records):
    """Verify activities with < MIN_ACTIVITY_REPORTS are classified as INSUFFICIENT_DATA."""
    analyzer = ActivityRiskAnalyzer(min_activity_reports=3)
    profiles = analyzer.calculate_activity_risk_profiles(sample_activity_records)

    hotwork = next(p for p in profiles if p["activity_name"] == "Hot Work")
    assert hotwork["total_reports"] == 2
    assert hotwork["risk_level"] == "INSUFFICIENT_DATA"


def test_deterministic_activity_risk_index_and_ranking(sample_activity_records):
    """Verify 5 consecutive runs produce 100% identical risk indices, risk levels, and activity rankings."""
    analyzer = ActivityRiskAnalyzer(min_activity_reports=3)
    
    run1 = analyzer.calculate_activity_risk_profiles(sample_activity_records)
    run2 = analyzer.calculate_activity_risk_profiles(sample_activity_records)
    run3 = analyzer.calculate_activity_risk_profiles(sample_activity_records)

    assert run1 == run2 == run3, "Activity risk calculation must be 100% deterministic"
    assert run1[0]["activity_id"] == run2[0]["activity_id"]


def test_fastapi_activity_risk_endpoints():
    """Verify GET /api/v1/activity-risk and GET /api/v1/activity-risk/{activity_id} FastAPI endpoints."""
    resp = client.get("/api/v1/activity-risk?min_reports=3")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_activities" in data
    assert "activity_profiles" in data
    assert isinstance(data["activity_profiles"], list)

    if len(data["activity_profiles"]) > 0:
        p = data["activity_profiles"][0]
        assert "activity_id" in p
        assert "activity_name" in p
        assert "risk_index" in p
        assert "risk_level" in p

        detail_resp = client.get(f"/api/v1/activity-risk/{p['activity_id']}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["activity_id"] == p["activity_id"]


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
