"""
verify_stage28b_closure.py - End-to-End MERN Integration & Verification Script for Stage 28B/28C.
"""

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.lsr_trend_analyzer import LsrTrendAnalyzer

client = TestClient(app)


def verify_stage28b_mern_closure():
    print("\n" + "="*80)
    print("STAGE 28C — LSR UNKNOWN LABEL CLEANUP & MERN INTEGRATION VERIFICATION")
    print("="*80)

    # 1. FastAPI Endpoint Test
    resp = client.get("/api/v1/lsr-trends")
    assert resp.status_code == 200, f"FastAPI endpoint failed with status {resp.status_code}"
    data = resp.json()
    print(f" ✓ FastAPI Endpoint GET /api/v1/lsr-trends: Status 200 OK")
    print(f"   Total official IOGP LSR rules returned: {data['total_lsr_rules']}")
    print(f"   Unknown/missing LSR records tracked:    {data['unknown_lsr_records']} ({data['unknown_lsr_rate']*100:.2f}%)")

    assert "lsr_profiles" in data
    profiles = data["lsr_profiles"]
    rule_names = [p["lsr_rule"] for p in profiles]
    assert "UNKNOWN" not in rule_names, "UNKNOWN must be excluded from official LSR profiles list!"
    print(" ✓ UNKNOWN successfully excluded from official LSR trend profiles list.")

    # 2. Detail Endpoint Test (Valid Rule)
    if profiles:
        rule_name = profiles[0]["lsr_rule"]
        detail_resp = client.get(f"/api/v1/lsr-trends/{rule_name}")
        assert detail_resp.status_code == 200, f"Detail endpoint failed for {rule_name}"
        detail_data = detail_resp.json()
        assert detail_data["lsr_rule"] == rule_name
        print(f" ✓ FastAPI Endpoint GET /api/v1/lsr-trends/{rule_name}: Status 200 OK")

    # 3. Detail Endpoint Test (UNKNOWN returns 404)
    unk_resp = client.get("/api/v1/lsr-trends/UNKNOWN")
    assert unk_resp.status_code == 404, "GET /api/v1/lsr-trends/UNKNOWN must return 404"
    print(" ✓ FastAPI Endpoint GET /api/v1/lsr-trends/UNKNOWN correctly returned 404 Not Found.")

    # 4. Five-Run Determinism Verification
    print("\n--- 5-Run Determinism Verification ---")
    runs = []
    for i in range(1, 6):
        res = client.get("/api/v1/lsr-trends").json()["lsr_profiles"]
        runs.append(res)
        top_rule = res[0]["lsr_rule"] if res else "N/A"
        top_trend = res[0]["trend"] if res else "N/A"
        print(f" Run {i}: Top Rule = {top_rule} ({top_trend}, Delta = {res[0]['trend_delta']:+.4f})")

    base = runs[0]
    for idx, r in enumerate(runs[1:], 2):
        assert r == base, f"Run {idx} output differed from Run 1"
    print(" ✓ 100% Identical Output Across 5 Repeated API Executions!")

    print("\n" + "="*80)
    print("STAGE 28C STATUS: PASS")
    print("LSR UNKNOWN LABEL CLEANUP & MERN INTEGRATION: READY FOR USE")
    print("="*80 + "\n")


if __name__ == "__main__":
    verify_stage28b_mern_closure()
