"""
verify_stage33_feedback.py - Stage 33 Benchmark & Verification Script.
"""

import sys
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.feedback_store import FeedbackStore


def run_stage33_feedback_verification():
    print("\n" + "="*80)
    print("STAGE 33 — HUMAN-IN-THE-LOOP / ANALYST FEEDBACK VERIFICATION")
    print("="*80)

    t0 = time.time()
    store = FeedbackStore()

    fb1 = store.create_feedback_record(
        report_id="R-1001",
        field_name="primary_life_saving_rule",
        ai_value="Energy Isolation",
        human_value="Energy Isolation",
        action="ACCEPT",
        comment="AI prediction validated against site log."
    )

    fb2 = store.create_feedback_record(
        report_id="R-1002",
        field_name="primary_life_saving_rule",
        ai_value="Energy Isolation",
        human_value="Line of Fire",
        action="CORRECT",
        comment="Suspended load involved in incident area."
    )

    t_elapsed = time.time() - t0

    stats = store.calculate_statistics()

    print(f" ✓ FeedbackStore execution time: {t_elapsed:.4f} seconds")
    print(f" ✓ Total feedback records created: {stats['total_feedback']}")
    print(f"   - Accepted: {stats['accepted_count']} (Rate: {stats['accept_rate']*100:.1f}%)")
    print(f"   - Corrected: {stats['corrected_count']} (Rate: {stats['correction_rate']*100:.1f}%)")
    print(f"   - Rejected:  {stats['rejected_count']} (Rate: {stats['reject_rate']*100:.1f}%)\n")

    print("--- Created Feedback Record #1 (ACCEPT) ---")
    print(json.dumps(fb1, indent=2))

    print("\n--- Created Feedback Record #2 (CORRECT) ---")
    print(json.dumps(fb2, indent=2))

    # ---------------------------------------------------------
    # FASTAPI ENDPOINT PYDANTIC SCHEMA VALIDATION
    # ---------------------------------------------------------
    print("\n" + "="*80)
    print("STAGE 33 — FASTAPI PYDANTIC SCHEMA VALIDATION")
    print("="*80)
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    payload = {
        "report_id": "R-1003",
        "field_name": "sif_potential",
        "ai_value": True,
        "human_value": True,
        "action": "ACCEPT",
        "comment": "Confirmed SIF precursor status.",
        "reviewer_id": "HSE_ANALYST_01"
    }

    resp = client.post("/api/v1/feedback", json=payload)
    assert resp.status_code == 201, f"FastAPI POST /api/v1/feedback failed: {resp.status_code} {resp.text}"
    print(f" ✓ POST /api/v1/feedback: Status 201 Created")

    stats_resp = client.get("/api/v1/feedback/stats")
    assert stats_resp.status_code == 200, f"FastAPI GET /api/v1/feedback/stats failed: {stats_resp.status_code}"
    print(f" ✓ GET /api/v1/feedback/stats: Status 200 OK")

    print("\n" + "="*80)
    print("STAGE 33 STATUS: PASS")
    print("HUMAN-IN-THE-LOOP FEEDBACK: READY FOR USE")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_stage33_feedback_verification()
