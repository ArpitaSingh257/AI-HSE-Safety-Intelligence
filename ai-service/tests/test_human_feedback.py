"""
test_human_feedback.py - Dedicated Test Suite for Stage 33 Human-in-the-Loop Analyst Feedback.
"""

import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.feedback_store import FeedbackStore

client = TestClient(app)


def test_feedback_record_creation_and_actions():
    """Verify ACCEPT, CORRECT, REJECT actions preserve original AI values and human reviews."""
    store = FeedbackStore()

    # 1. ACCEPT Action
    r1 = store.create_feedback_record(
        report_id="R-1001",
        field_name="sif_potential",
        ai_value=True,
        human_value=True,
        action="ACCEPT",
        comment="Confirmed high energy exposure."
    )
    assert r1["action"] == "ACCEPT"
    assert r1["ai_value"] == True
    assert r1["human_value"] == True

    # 2. CORRECT Action
    r2 = store.create_feedback_record(
        report_id="R-1002",
        field_name="primary_life_saving_rule",
        ai_value="Energy Isolation",
        human_value="Line of Fire",
        action="CORRECT",
        comment="Suspended load involved."
    )
    assert r2["action"] == "CORRECT"
    assert r2["ai_value"] == "Energy Isolation"
    assert r2["human_value"] == "Line of Fire"

    # 3. REJECT Action
    r3 = store.create_feedback_record(
        report_id="R-1003",
        field_name="barrier_failure",
        ai_value="Control Failure",
        human_value="Control Failure",
        action="REJECT",
        comment="AI extraction unhelpful."
    )
    assert r3["action"] == "REJECT"

    # Verify report feedback retrieval
    history = store.get_feedback_for_report("R-1002")
    assert len(history) == 1
    assert history[0]["human_value"] == "Line of Fire"


def test_invalid_action_rejection():
    """Verify invalid action strings raise ValueError."""
    store = FeedbackStore()
    with pytest.raises(ValueError):
        store.create_feedback_record(
            report_id="R-1001",
            field_name="sif_potential",
            ai_value=True,
            human_value=True,
            action="INVALID_ACTION"
        )


def test_feedback_statistics_calculation():
    """Verify feedback stats and field-level accuracy rate calculations."""
    store = FeedbackStore()
    store.create_feedback_record("R-1001", "lsr", "Energy Isolation", "Energy Isolation", "ACCEPT")
    store.create_feedback_record("R-1002", "lsr", "Energy Isolation", "Line of Fire", "CORRECT")
    store.create_feedback_record("R-1003", "lsr", "Energy Isolation", "Energy Isolation", "ACCEPT")

    stats = store.calculate_statistics()
    assert stats["total_feedback"] == 3
    assert stats["accepted_count"] == 2
    assert stats["corrected_count"] == 1
    assert stats["accept_rate"] == round(2 / 3, 4)
    assert stats["correction_rate"] == round(1 / 3, 4)


def test_fastapi_feedback_endpoints():
    """Verify POST /api/v1/feedback and GET /api/v1/feedback/stats endpoints."""
    payload = {
        "report_id": "R-1001",
        "field_name": "primary_life_saving_rule",
        "ai_value": "Energy Isolation",
        "human_value": "Line of Fire",
        "action": "CORRECT",
        "comment": "Test analyst correction.",
        "reviewer_id": "HSE_ANALYST_01"
    }

    resp = client.post("/api/v1/feedback", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "feedback_id" in data
    assert data["report_id"] == "R-1001"
    assert data["action"] == "CORRECT"

    stats_resp = client.get("/api/v1/feedback/stats")
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    assert "total_feedback" in stats_data
    assert stats_data["total_feedback"] >= 1


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
