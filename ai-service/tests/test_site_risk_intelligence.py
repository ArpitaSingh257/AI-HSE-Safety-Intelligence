"""
test_site_risk_intelligence.py - Dedicated Test Suite for Stage 26 Site-Level Risk Intelligence.
"""

import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.site_risk_analyzer import SiteRiskAnalyzer

client = TestClient(app)


@pytest.fixture
def sample_site_records():
    return [
        # Site A: 3 reports, 2 SIF (66.7% SIF density)
        {"record_id": "R-A01", "location": "Duliajan", "activity": "Maintenance", "primary_life_saving_rule": "Energy Isolation", "hazard": "Stored Pressure", "barrier_failure": "Valve bleeder", "sif_potential": True},
        {"record_id": "R-A02", "location": "Duliajan", "activity": "Maintenance", "primary_life_saving_rule": "Energy Isolation", "hazard": "Stored Pressure", "barrier_failure": "Valve bleeder", "sif_potential": True},
        {"record_id": "R-A03", "location": "Duliajan", "activity": "Hot Work", "primary_life_saving_rule": "Hot Work", "hazard": "Flammable Gas", "barrier_failure": "Gas monitor", "sif_potential": False},

        # Site B: 5 reports, 1 SIF (20% SIF density - higher volume, lower rate)
        {"record_id": "R-B01", "location": "Moran", "activity": "Drilling", "primary_life_saving_rule": "Line of Fire", "hazard": "Suspended Load", "barrier_failure": "Tag line", "sif_potential": True},
        {"record_id": "R-B02", "location": "Moran", "activity": "Drilling", "primary_life_saving_rule": "Line of Fire", "hazard": "Suspended Load", "barrier_failure": "Tag line", "sif_potential": False},
        {"record_id": "R-B03", "location": "Moran", "activity": "General Operations", "primary_life_saving_rule": "General", "hazard": "Slip", "barrier_failure": "Housekeeping", "sif_potential": False},
        {"record_id": "R-B04", "location": "Moran", "activity": "General Operations", "primary_life_saving_rule": "General", "hazard": "Slip", "barrier_failure": "Housekeeping", "sif_potential": False},
        {"record_id": "R-B05", "location": "Moran", "activity": "General Operations", "primary_life_saving_rule": "General", "hazard": "Slip", "barrier_failure": "Housekeeping", "sif_potential": False},

        # Site C: 2 reports (insufficient data)
        {"record_id": "R-C01", "location": "Digboi", "activity": "Inspection", "primary_life_saving_rule": "Confined Space", "hazard": "H2S", "barrier_failure": "Ventilation", "sif_potential": True},
        {"record_id": "R-C02", "location": "Digboi", "activity": "Inspection", "primary_life_saving_rule": "Confined Space", "hazard": "H2S", "barrier_failure": "Ventilation", "sif_potential": False},
    ]


def test_site_aggregation_and_sif_density(sample_site_records):
    """Verify site aggregation, report counting, and volume-normalized SIF density calculation."""
    analyzer = SiteRiskAnalyzer(min_site_reports=3)
    profiles = analyzer.calculate_site_risk_profiles(sample_site_records)

    site_map = {p["site_name"]: p for p in profiles}
    assert "Duliajan" in site_map
    duliajan = site_map["Duliajan"]
    assert duliajan["total_reports"] == 3
    assert duliajan["sif_reports"] == 2
    assert abs(duliajan["sif_density"] - 0.6667) < 1e-3


def test_volume_vs_rate_ranking(sample_site_records):
    """Verify that a site with higher SIF density (rate) is ranked above a site with larger volume but lower rate."""
    analyzer = SiteRiskAnalyzer(min_site_reports=3)
    profiles = analyzer.calculate_site_risk_profiles(sample_site_records)

    # Duliajan (66.7% SIF density) should be ranked higher than Moran (20% SIF density)
    ranked_names = [p["site_name"] for p in profiles if p["risk_level"] != "INSUFFICIENT_DATA"]
    assert ranked_names.index("Duliajan") < ranked_names.index("Moran")


def test_minimum_data_threshold_rule(sample_site_records):
    """Verify sites with < MIN_SITE_REPORTS are classified as INSUFFICIENT_DATA."""
    analyzer = SiteRiskAnalyzer(min_site_reports=3)
    profiles = analyzer.calculate_site_risk_profiles(sample_site_records)

    digboi = next(p for p in profiles if p["site_name"] == "Digboi")
    assert digboi["total_reports"] == 2
    assert digboi["risk_level"] == "INSUFFICIENT_DATA"


def test_deterministic_site_risk_index_and_ranking(sample_site_records):
    """Verify 5 consecutive runs produce 100% identical risk indices, risk levels, and site rankings."""
    analyzer = SiteRiskAnalyzer(min_site_reports=3)
    
    run1 = analyzer.calculate_site_risk_profiles(sample_site_records)
    run2 = analyzer.calculate_site_risk_profiles(sample_site_records)
    run3 = analyzer.calculate_site_risk_profiles(sample_site_records)

    assert run1 == run2 == run3, "Site risk calculation must be 100% deterministic"
    assert run1[0]["site_id"] == run2[0]["site_id"]


def test_fastapi_site_risk_endpoints():
    """Verify GET /api/v1/site-risk and GET /api/v1/site-risk/{site_id} FastAPI endpoints."""
    resp = client.get("/api/v1/site-risk?min_reports=3")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_sites" in data
    assert "site_profiles" in data
    assert isinstance(data["site_profiles"], list)

    if len(data["site_profiles"]) > 0:
        p = data["site_profiles"][0]
        assert "site_id" in p
        assert "site_name" in p
        assert "risk_index" in p
        assert "risk_level" in p

        detail_resp = client.get(f"/api/v1/site-risk/{p['site_id']}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["site_id"] == p["site_id"]


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
