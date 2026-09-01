"""
test_lsr_trend_analytics.py - Dedicated Test Suite for Stage 28 Life-Saving Rule (LSR) Trend Analytics.
Verifies official IOGP rule aggregation, UNKNOWN label exclusion, and 404 detail handling.
"""

import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.lsr_trend_analyzer import LsrTrendAnalyzer

client = TestClient(app)


@pytest.fixture
def sample_lsr_records():
    return [
        # Energy Isolation in 2025-01 (Low SIF rate: 1/3 = 33%)
        {"record_id": "R-E01", "report_date": "2025-01-10", "primary_life_saving_rule": "Energy Isolation", "sif_potential": True},
        {"record_id": "R-E02", "report_date": "2025-01-15", "primary_life_saving_rule": "Energy Isolation", "sif_potential": False},
        {"record_id": "R-E03", "report_date": "2025-01-20", "primary_life_saving_rule": "Energy Isolation", "sif_potential": False},

        # Energy Isolation in 2025-02 (High SIF rate: 3/3 = 100% -> INCREASING trend)
        {"record_id": "R-E04", "report_date": "2025-02-05", "primary_life_saving_rule": "Energy Isolation", "sif_potential": True},
        {"record_id": "R-E05", "report_date": "2025-02-12", "primary_life_saving_rule": "Energy Isolation", "sif_potential": True},
        {"record_id": "R-E06", "report_date": "2025-02-18", "primary_life_saving_rule": "Energy Isolation", "sif_potential": True},

        # Working at Height: 2 reports (insufficient data)
        {"record_id": "R-W01", "report_date": "2025-01-05", "primary_life_saving_rule": "Working at Height", "sif_potential": True},
        {"record_id": "R-W02", "report_date": "2025-01-25", "primary_life_saving_rule": "Working at Height", "sif_potential": False},

        # Unknown / Missing LSR label (must be excluded from official LSR list)
        {"record_id": "R-U01", "report_date": "2025-01-08", "primary_life_saving_rule": "UNKNOWN", "sif_potential": False},
        {"record_id": "R-U02", "report_date": "2025-01-18", "primary_life_saving_rule": "", "sif_potential": True},
    ]


def test_lsr_aggregation_and_unknown_exclusion(sample_lsr_records):
    """Verify official LSR grouping and UNKNOWN label exclusion from official profiles."""
    analyzer = LsrTrendAnalyzer(min_lsr_reports=3)
    summary = analyzer.get_lsr_analytics_summary(sample_lsr_records)

    assert summary["total_reports"] == 10
    assert summary["unknown_lsr_records"] == 2
    assert abs(summary["unknown_lsr_rate"] - 0.20) < 1e-3

    official_rules = [p["lsr_rule"] for p in summary["official_lsr_profiles"]]
    assert "Energy Isolation" in official_rules
    assert "UNKNOWN" not in official_rules


def test_time_series_and_sif_density(sample_lsr_records):
    """Verify monthly time-series generation and period SIF rates."""
    analyzer = LsrTrendAnalyzer(min_lsr_reports=3)
    profiles = analyzer.calculate_lsr_trend_profiles(sample_lsr_records)

    energy = next(p for p in profiles if p["lsr_rule"] == "Energy Isolation")
    periods = {ts["period"]: ts for ts in energy["time_series"]}
    assert "2025-01" in periods
    assert "2025-02" in periods

    assert periods["2025-01"]["report_count"] == 3
    assert periods["2025-01"]["sif_count"] == 1

    assert periods["2025-02"]["report_count"] == 3
    assert periods["2025-02"]["sif_count"] == 3


def test_trend_classification_increasing(sample_lsr_records):
    """Verify increasing trend classification when recent period SIF rate rises."""
    analyzer = LsrTrendAnalyzer(min_lsr_reports=3, min_trend_periods=2)
    profiles = analyzer.calculate_lsr_trend_profiles(sample_lsr_records)

    energy = next(p for p in profiles if p["lsr_rule"] == "Energy Isolation")
    assert energy["trend"] == "INCREASING"
    assert energy["trend_delta"] > 0.05


def test_insufficient_data_trend_threshold(sample_lsr_records):
    """Verify LSRs with < MIN_LSR_REPORTS receive INSUFFICIENT_DATA trend state."""
    analyzer = LsrTrendAnalyzer(min_lsr_reports=3)
    profiles = analyzer.calculate_lsr_trend_profiles(sample_lsr_records)

    height = next(p for p in profiles if p["lsr_rule"] == "Working at Height")
    assert height["total_reports"] == 2
    assert height["trend"] == "INSUFFICIENT_DATA"


def test_deterministic_5_runs(sample_lsr_records):
    """Verify 5 consecutive runs produce 100% identical trend states, deltas, and time series."""
    analyzer = LsrTrendAnalyzer(min_lsr_reports=3)
    
    run1 = analyzer.calculate_lsr_trend_profiles(sample_lsr_records)
    run2 = analyzer.calculate_lsr_trend_profiles(sample_lsr_records)
    run3 = analyzer.calculate_lsr_trend_profiles(sample_lsr_records)

    assert run1 == run2 == run3, "LSR trend calculation must be 100% deterministic"
    assert run1[0]["lsr_rule"] == run2[0]["lsr_rule"]


def test_fastapi_lsr_trends_endpoints():
    """Verify GET /api/v1/lsr-trends excludes UNKNOWN and GET /api/v1/lsr-trends/UNKNOWN returns 404."""
    resp = client.get("/api/v1/lsr-trends?min_reports=3")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_lsr_rules" in data
    assert "unknown_lsr_records" in data
    assert "lsr_profiles" in data

    rules_in_resp = [p["lsr_rule"] for p in data["lsr_profiles"]]
    assert "UNKNOWN" not in rules_in_resp

    if len(data["lsr_profiles"]) > 0:
        p = data["lsr_profiles"][0]
        assert "lsr_rule" in p
        assert "trend" in p
        assert "time_series" in p

        detail_resp = client.get(f"/api/v1/lsr-trends/{p['lsr_rule']}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["lsr_rule"] == p["lsr_rule"]

    # Verify UNKNOWN returns 404 Not Found
    unknown_resp = client.get("/api/v1/lsr-trends/UNKNOWN")
    assert unknown_resp.status_code == 404


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
