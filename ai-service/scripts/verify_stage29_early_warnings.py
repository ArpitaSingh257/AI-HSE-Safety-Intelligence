"""
verify_stage29_early_warnings.py - Stage 29 Benchmark & 5-Repetition Determinism Verification Script.
"""

import sys
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.early_warning_detector import EarlyWarningDetector


def run_stage29_early_warnings_verification():
    print("\n" + "="*80)
    print("STAGE 29 — TEMPORAL TREND / EARLY-WARNING DETECTION VERIFICATION")
    print("="*80)

    t0 = time.time()
    detector = EarlyWarningDetector()
    warnings = detector.detect_early_warnings()
    t_elapsed = time.time() - t0

    high_pri = [w for w in warnings if w["warning_level"] == "HIGH_PRIORITY"]
    early_warn = [w for w in warnings if w["warning_level"] == "EARLY_WARNING"]
    watch_cnt = [w for w in warnings if w["warning_level"] == "WATCH"]

    print(f" ✓ Early-Warning Detector execution time: {t_elapsed:.4f} seconds")
    print(f" ✓ Total warning signals evaluated:    {len(warnings)}")
    print(f"   - High-Priority Escalations:      {len(high_pri)}")
    print(f"   - Early-Warning Alerts:           {len(early_warn)}")
    print(f"   - Watch Signals:                 {len(watch_cnt)}\n")

    print("--- Top Evaluated Early Warning Signals ---")
    for idx, w in enumerate(warnings[:5], 1):
        print(f" #{idx} [{w['warning_level']}] {w['signal_name']} ({w['signal_type']})")
        print(f"     ID: {w['warning_id']} | Period: {w['period']}")
        print(f"     Baseline: {w['baseline_value']} → Recent: {w['recent_value']} (Delta: {w['delta']:+.2f})")
        print(f"     Consecutive Increasing Periods: {w['consecutive_increasing_periods']}")
        print(f"     Rationale: {w['reason']}")
        if w["affected_sites"]:
            print(f"     Top Site: {w['affected_sites'][0]['site_name']} ({w['affected_sites'][0]['count']} reports)")
        if w["affected_activities"]:
            print(f"     Top Task: {w['affected_activities'][0]['activity_name']} ({w['affected_activities'][0]['count']} reports)")
        print()

    # ---------------------------------------------------------
    # 5-REPETITION DETERMINISM VERIFICATION
    # ---------------------------------------------------------
    print("\n" + "="*80)
    print("STAGE 29 — 5-REPETITION DETERMINISM VERIFICATION")
    print("="*80)

    runs = []
    for r_idx in range(1, 6):
        d = EarlyWarningDetector()
        res = d.detect_early_warnings()
        runs.append(res)
        top_w = res[0]["warning_id"] if res else "N/A"
        top_lvl = res[0]["warning_level"] if res else "N/A"
        top_d = res[0]["delta"] if res else 0.0
        print(f" Run {r_idx}: Top Signal = {top_w} [{top_lvl}] (Delta = {top_d:+.2f})")

    base_run = runs[0]
    for r_idx, r in enumerate(runs[1:], 2):
        assert len(r) == len(base_run), f"Run {r_idx} length mismatch: {len(r)} vs {len(base_run)}"
        for i in range(len(r)):
            assert r[i]["warning_id"] == base_run[i]["warning_id"], f"Run {r_idx} ID mismatch at index {i}"
            assert r[i]["warning_level"] == base_run[i]["warning_level"], f"Run {r_idx} level mismatch at index {i}"
            assert abs(r[i]["delta"] - base_run[i]["delta"]) < 1e-4, f"Run {r_idx} delta mismatch at index {i}"

    print(" ✓ 100% Identical Output Across 5 Repeated API Executions! (Run 1 == Run 2 == Run 3 == Run 4 == Run 5)")

    # ---------------------------------------------------------
    # FASTAPI ENDPOINT PYDANTIC SCHEMA VALIDATION
    # ---------------------------------------------------------
    print("\n" + "="*80)
    print("STAGE 29 — FASTAPI PYDANTIC SCHEMA VALIDATION")
    print("="*80)
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    resp = client.get("/api/v1/early-warnings")
    assert resp.status_code == 200, f"FastAPI endpoint failed: {resp.status_code} {resp.text}"
    data = resp.json()
    print(f" ✓ GET /api/v1/early-warnings: Status 200 OK")
    print(f"   Total signals returned: {data['total_warnings']}")

    if data["warnings"]:
        w_id = data["warnings"][0]["warning_id"]
        detail_resp = client.get(f"/api/v1/early-warnings/{w_id}")
        assert detail_resp.status_code == 200
        print(f" ✓ GET /api/v1/early-warnings/{w_id}: Status 200 OK")

    print("\n" + "="*80)
    print("STAGE 29 STATUS: PASS")
    print("TEMPORAL EARLY-WARNING: READY FOR USE")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_stage29_early_warnings_verification()
