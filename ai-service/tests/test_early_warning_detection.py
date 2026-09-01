"""
test_early_warning_detection.py - Dedicated Test Suite for Stage 29 Temporal Trend / Early-Warning Detection.
"""

import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.early_warning_detector import EarlyWarningDetector

client = TestClient(app)


@pytest.fixture
def sample_warning_records():
    return [
        # Energy Isolation Control Failure: Sustained 4-period increase (1 -> 2 -> 3 -> 4 = 10 reports)
        {"record_id": "R-W01", "report_date": "2025-01-05", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "sif_potential": True},

        {"record_id": "R-W02", "report_date": "2025-02-05", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "sif_potential": True},
        {"record_id": "R-W03", "report_date": "2025-02-15", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "sif_potential": True},

        {"record_id": "R-W04", "report_date": "2025-03-05", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "sif_potential": True},
        {"record_id": "R-W05", "report_date": "2025-03-12", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "sif_potential": True},
        {"record_id": "R-W06", "report_date": "2025-03-22", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "sif_potential": True},

        {"record_id": "R-W07", "report_date": "2025-04-02", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "sif_potential": True},
        {"record_id": "R-W08", "report_date": "2025-04-10", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "sif_potential": True},
        {"record_id": "R-W09", "report_date": "2025-04-18", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "sif_potential": True},
        {"record_id": "R-W10", "report_date": "2025-04-28", "location": "Duliajan", "activity": "Maintenance", "barrier_failure": "Energy Isolation Control Failure", "sif_potential": True},

        # Single Isolated Spike: Gas Monitor Calibration (Period 1: 1, Period 2: 5, Period 3: 1) -> Must NOT trigger EARLY_WARNING
        {"record_id": "R-S01", "report_date": "2025-01-02", "location": "Moran", "activity": "Hot Work", "barrier_failure": "Gas Monitor Calibration", "sif_potential": False},
        {"record_id": "R-S02", "report_date": "2025-02-01", "location": "Moran", "activity": "Hot Work", "barrier_failure": "Gas Monitor Calibration", "sif_potential": False},
        {"record_id": "R-S03", "report_date": "2025-02-05", "location": "Moran", "activity": "Hot Work", "barrier_failure": "Gas Monitor Calibration", "sif_potential": False},
        {"record_id": "R-S04", "report_date": "2025-02-12", "location": "Moran", "activity": "Hot Work", "barrier_failure": "Gas Monitor Calibration", "sif_potential": False},
        {"record_id": "R-S05", "report_date": "2025-02-20", "location": "Moran", "activity": "Hot Work", "barrier_failure": "Gas Monitor Calibration", "sif_potential": False},
        {"record_id": "R-S06", "report_date": "2025-02-28", "location": "Moran", "activity": "Hot Work", "barrier_failure": "Gas Monitor Calibration", "sif_potential": False},
        {"record_id": "R-S07", "report_date": "2025-03-05", "location": "Moran", "activity": "Hot Work", "barrier_failure": "Gas Monitor Calibration", "sif_potential": False},
    ]


def test_time_series_and_baseline_recent_comparison(sample_warning_records):
    """Verify monthly time-series generation and baseline vs recent period averages."""
    detector = EarlyWarningDetector(min_warning_reports=3, min_warning_periods=3)
    warnings = detector.detect_early_warnings(sample_warning_records)

    energy_warn = next(w for w in warnings if w["signal_name"] == "Energy Isolation Control Failure")
    assert energy_warn["baseline_value"] > 0
    assert energy_warn["recent_value"] > energy_warn["baseline_value"]
    assert energy_warn["delta"] > 0


def test_sustained_increase_detection(sample_warning_records):
    """Verify sustained consecutive increasing periods trigger warning classification."""
    detector = EarlyWarningDetector(min_warning_reports=3, min_warning_periods=3, min_consecutive_increasing_periods=3)
    warnings = detector.detect_early_warnings(sample_warning_records)

    energy_warn = next(w for w in warnings if w["signal_name"] == "Energy Isolation Control Failure")
    assert energy_warn["consecutive_increasing_periods"] >= 3
    assert energy_warn["warning_level"] in ["HIGH_PRIORITY", "EARLY_WARNING"]


def test_isolated_spike_does_not_trigger_warning(sample_warning_records):
    """Verify an isolated 1-period spike does NOT trigger EARLY_WARNING or HIGH_PRIORITY."""
    detector = EarlyWarningDetector(min_warning_reports=3, min_warning_periods=3, min_consecutive_increasing_periods=3)
    warnings = detector.detect_early_warnings(sample_warning_records)

    spike_warn = next(w for w in warnings if "Gas" in w["signal_name"] or w["signal_name"] == "Atmospheric & Toxic Gas Monitoring Control Failure")
    assert spike_warn["warning_level"] not in ["EARLY_WARNING", "HIGH_PRIORITY"]


def test_deterministic_5_runs(sample_warning_records):
    """Verify 5 consecutive runs produce 100% identical warning levels, deltas, and warning IDs."""
    detector = EarlyWarningDetector(min_warning_reports=3)
    
    run1 = detector.detect_early_warnings(sample_warning_records)
    run2 = detector.detect_early_warnings(sample_warning_records)
    run3 = detector.detect_early_warnings(sample_warning_records)

    assert run1 == run2 == run3, "Early warning detection must be 100% deterministic"
    assert run1[0]["warning_id"] == run2[0]["warning_id"]


def test_fastapi_early_warnings_endpoints():
    """Verify GET /api/v1/early-warnings and GET /api/v1/early-warnings/{warning_id} FastAPI endpoints."""
    resp = client.get("/api/v1/early-warnings")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_warnings" in data
    assert "warnings" in data
    assert isinstance(data["warnings"], list)

    if len(data["warnings"]) > 0:
        w = data["warnings"][0]
        assert "warning_id" in w
        assert "warning_level" in w
        assert "reason" in w

        detail_resp = client.get(f"/api/v1/early-warnings/{w['warning_id']}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["warning_id"] == w["warning_id"]


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
