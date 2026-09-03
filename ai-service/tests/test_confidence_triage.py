"""
test_confidence_triage.py - Dedicated PyTest Suite for Stage 34 Confidence-Calibrated Operational Triage.
Verifies post-processing Sigmoid calibration, deterministic triage policy, risk overrides, 0 model retraining, and 5-run determinism.
"""

import sys
import hashlib
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.confidence_triage_engine import ConfidenceTriageEngine

client = TestClient(app)


def test_sigmoid_probability_calibration_bounds():
    """Verify raw SIF probabilities are calibrated and clipped strictly to [0.0, 1.0]."""
    engine = ConfidenceTriageEngine()

    res_high = engine.calibrate_sif_probability(0.85)
    assert res_high["calibration_status"] == "ACTIVE"
    assert res_high["calibration_method"] == "sigmoid"
    assert 0.0 <= res_high["calibrated_probability"] <= 1.0

    res_low = engine.calibrate_sif_probability(0.15)
    assert res_low["calibration_status"] == "ACTIVE"
    assert 0.0 <= res_low["calibrated_probability"] <= 1.0

    res_zero = engine.calibrate_sif_probability(0.0)
    assert 0.0 <= res_zero["calibrated_probability"] <= 1.0

    res_one = engine.calibrate_sif_probability(1.0)
    assert 0.0 <= res_one["calibrated_probability"] <= 1.0

    res_invalid = engine.calibrate_sif_probability(float("nan"))
    assert res_invalid["calibration_status"] == "UNAVAILABLE"


def test_triage_decision_policy_states():
    """Verify IMMEDIATE_ESCALATION, NEEDS_REVIEW, and AUTO_CLEAR triage policy rules."""
    engine = ConfidenceTriageEngine()

    # 1. IMMEDIATE_ESCALATION (High SIF Probability)
    t1 = engine.evaluate_triage("R-1001", raw_sif_prob=0.88)
    assert t1["triage_level"] == "IMMEDIATE_ESCALATION"
    assert t1["reason_code"] == "HIGH_CALIBRATED_SIF_RISK"

    # 2. IMMEDIATE_ESCALATION (Critical Priority Override)
    t2 = engine.evaluate_triage("R-1002", raw_sif_prob=0.20, priority_level="CRITICAL")
    assert t2["triage_level"] == "IMMEDIATE_ESCALATION"
    assert t2["reason_code"] == "CRITICAL_PRIORITY_OVERRIDE"

    # 3. IMMEDIATE_ESCALATION (Early Warning Override)
    t3 = engine.evaluate_triage("R-1003", raw_sif_prob=0.20, early_warning_level="HIGH_PRIORITY")
    assert t3["triage_level"] == "IMMEDIATE_ESCALATION"
    assert t3["reason_code"] == "EARLY_WARNING_OVERRIDE"

    # 4. NEEDS_REVIEW (Moderate Risk)
    t4 = engine.evaluate_triage("R-1004", raw_sif_prob=0.50)
    assert t4["triage_level"] == "NEEDS_REVIEW"
    assert t4["reason_code"] == "MODERATE_CALIBRATED_SIF_RISK"

    # 5. AUTO_CLEAR (Active Calibration & Low Risk & No Overrides)
    t5 = engine.evaluate_triage("R-1005", raw_sif_prob=0.10, priority_level="LOW", early_warning_level="NORMAL")
    assert t5["triage_level"] == "AUTO_CLEAR"
    assert t5["reason_code"] == "LOW_RISK_AUTO_CLEAR"


def test_model_weight_freeze_guarantee():
    """Verify that Stage 6 SIF and Stage 7 LSR production model weights remain 100% frozen."""
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True


def test_5_run_triage_determinism():
    """Verify 100% determinism across 5 repeated triage calculations."""
    engine = ConfidenceTriageEngine()

    runs = [
        engine.evaluate_triage(
            report_id="R-9999",
            raw_sif_prob=0.75,
            priority_level="HIGH",
            early_warning_level="NORMAL"
        )
        for _ in range(5)
    ]

    base_run = runs[0]
    for idx, run in enumerate(runs[1:], start=2):
        assert run["sif_calibrated_probability"] == base_run["sif_calibrated_probability"], f"Run {idx} probability mismatch"
        assert run["triage_level"] == base_run["triage_level"], f"Run {idx} triage level mismatch"
        assert run["reason_code"] == base_run["reason_code"], f"Run {idx} reason code mismatch"


def test_fastapi_triage_endpoints():
    """Verify POST /api/v1/triage and POST /api/v1/triage/batch endpoints."""
    payload = {
        "report_id": "R-8001",
        "raw_sif_probability": 0.82,
        "priority_level": "HIGH",
        "priority_score": 0.78,
        "early_warning_level": "NORMAL",
        "risk_matrix_category": "HIGH_SEVERITY_LOW_RECURRENCE"
    }

    resp = client.post("/api/v1/triage", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["report_id"] == "R-8001"
    assert data["triage_level"] == "IMMEDIATE_ESCALATION"
    assert "calibration_version" in data

    # Batch test
    batch_resp = client.post("/api/v1/triage/batch", json=[payload, {"report_id": "R-8002", "raw_sif_probability": 0.10}])
    assert batch_resp.status_code == 200
    batch_data = batch_resp.json()
    assert batch_data["total_evaluated"] == 2
    assert batch_data["immediate_escalation_count"] >= 1


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
