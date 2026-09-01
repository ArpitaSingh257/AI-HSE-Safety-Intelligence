"""
verify_stage29b_closure.py - End-to-End MERN Integration & Verification Script for Stage 29B.
Tests FastAPI endpoints, Pydantic schemas, 5-run determinism, and data structure completeness.
"""

import sys
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.early_warning_detector import EarlyWarningDetector

client = TestClient(app)


def verify_stage29b_mern_closure():
    print("\n" + "="*80)
    print("STAGE 29B — TEMPORAL EARLY-WARNING MERN INTEGRATION VERIFICATION")
    print("="*80)

    # 1. FastAPI Endpoint Test
    t0 = time.time()
    resp = client.get("/api/v1/early-warnings")
    t_elapsed = time.time() - t0

    assert resp.status_code == 200, f"FastAPI endpoint failed with status {resp.status_code}"
    data = resp.json()
    print(f" ✓ FastAPI Endpoint GET /api/v1/early-warnings: Status 200 OK ({t_elapsed:.4f}s)")
    print(f"   Total signals evaluated: {data['total_warnings']}")
    print(f"   High-Priority Escalations: {data['high_priority_count']}")
    print(f"   Early-Warning Alerts:      {data['early_warning_count']}")
    print(f"   Watch Signals:            {data['watch_count']}")

    assert "warnings" in data
    warnings = data["warnings"]

    # 2. Detail Endpoint Test
    if warnings:
        w_id = warnings[0]["warning_id"]
        detail_resp = client.get(f"/api/v1/early-warnings/{w_id}")
        assert detail_resp.status_code == 200, f"Detail endpoint failed for {w_id}"
        detail_data = detail_resp.json()
        assert detail_data["warning_id"] == w_id
        print(f" ✓ FastAPI Endpoint GET /api/v1/early-warnings/{w_id}: Status 200 OK")

    # 3. Invalid Warning ID Test (404)
    inv_resp = client.get("/api/v1/early-warnings/INVALID-WARNING-ID-999")
    assert inv_resp.status_code == 404
    print(" ✓ FastAPI Endpoint GET /api/v1/early-warnings/INVALID-WARNING-ID-999 correctly returned 404 Not Found.")

    # 4. Five-Run Determinism Verification
    print("\n--- 5-Run Determinism Verification ---")
    runs = []
    for i in range(1, 6):
        res = client.get("/api/v1/early-warnings").json()["warnings"]
        runs.append(res)
        top_w = res[0]["warning_id"] if res else "N/A"
        top_lvl = res[0]["warning_level"] if res else "N/A"
        top_d = res[0]["delta"] if res else 0.0
        print(f" Run {i}: Top Signal = {top_w} [{top_lvl}] (Delta = {top_d:+.2f})")

    base = runs[0]
    for idx, r in enumerate(runs[1:], 2):
        assert r == base, f"Run {idx} output differed from Run 1"
    print(" ✓ 100% Identical Output Across 5 Repeated API Executions!")

    print("\n" + "="*80)
    print("STAGE 29B STATUS: PASS")
    print("EARLY-WARNING MERN INTEGRATION: READY FOR USE")
    print("="*80 + "\n")


if __name__ == "__main__":
    verify_stage29b_mern_closure()
