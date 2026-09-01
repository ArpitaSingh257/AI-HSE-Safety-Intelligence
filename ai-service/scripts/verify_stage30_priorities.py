"""
verify_stage30_priorities.py - Stage 30 Benchmark & 5-Repetition Determinism Verification Script.
"""

import sys
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.priority_intelligence_engine import PriorityIntelligenceEngine


def run_stage30_priorities_verification():
    print("\n" + "="*80)
    print("STAGE 30 — RISK / PRIORITY INTELLIGENCE VERIFICATION")
    print("="*80)

    t0 = time.time()
    engine = PriorityIntelligenceEngine()
    priorities = engine.calculate_priorities()
    t_elapsed = time.time() - t0

    crit_cnt = [p for p in priorities if p["priority_level"] == "CRITICAL"]
    high_cnt = [p for p in priorities if p["priority_level"] == "HIGH"]
    med_cnt = [p for p in priorities if p["priority_level"] == "MEDIUM"]

    print(f" ✓ Priority Intelligence Engine execution time: {t_elapsed:.4f} seconds")
    print(f" ✓ Total HSE priorities evaluated:   {len(priorities)}")
    print(f"   - Critical Priorities:           {len(crit_cnt)}")
    print(f"   - High Priorities:               {len(high_cnt)}")
    print(f"   - Medium Priorities:             {len(med_cnt)}\n")

    print("--- Top 5 Ranked HSE Priorities ---")
    for idx, p in enumerate(priorities[:5], 1):
        print(f" #{idx} [{p['priority_level']}] {p['entity_name']} ({p['entity_type']})")
        print(f"     ID: {p['priority_id']} | Priority Score: {p['priority_score']:.4f}")
        print(f"     Components: SIF={p['components']['sif_impact']:.2f}, Rec={p['components']['recurrence']:.2f}, Bar={p['components']['barrier_impact']:.2f}, SA={p['components']['site_activity']:.2f}, EW={p['components']['early_warning']:.2f}")
        print(f"     Rationale: {p['reason']}")
        print()

    # ---------------------------------------------------------
    # 5-REPETITION DETERMINISM VERIFICATION
    # ---------------------------------------------------------
    print("\n" + "="*80)
    print("STAGE 30 — 5-REPETITION DETERMINISM VERIFICATION")
    print("="*80)

    runs = []
    for r_idx in range(1, 6):
        e = PriorityIntelligenceEngine()
        res = e.calculate_priorities()
        runs.append(res)
        top_p = res[0]["priority_id"] if res else "N/A"
        top_lvl = res[0]["priority_level"] if res else "N/A"
        top_s = res[0]["priority_score"] if res else 0.0
        print(f" Run {r_idx}: Top Priority = {top_p} [{top_lvl}] (Score = {top_s:.4f})")

    base_run = runs[0]
    for r_idx, r in enumerate(runs[1:], 2):
        assert len(r) == len(base_run), f"Run {r_idx} length mismatch: {len(r)} vs {len(base_run)}"
        for i in range(len(r)):
            assert r[i]["priority_id"] == base_run[i]["priority_id"], f"Run {r_idx} ID mismatch at index {i}"
            assert r[i]["priority_level"] == base_run[i]["priority_level"], f"Run {r_idx} level mismatch at index {i}"
            assert abs(r[i]["priority_score"] - base_run[i]["priority_score"]) < 1e-4, f"Run {r_idx} score mismatch at index {i}"

    print(" ✓ 100% Identical Output Across 5 Repeated Calculations! (Run 1 == Run 2 == Run 3 == Run 4 == Run 5)")

    # ---------------------------------------------------------
    # FASTAPI ENDPOINT PYDANTIC SCHEMA VALIDATION
    # ---------------------------------------------------------
    print("\n" + "="*80)
    print("STAGE 30 — FASTAPI PYDANTIC SCHEMA VALIDATION")
    print("="*80)
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    resp = client.get("/api/v1/priorities")
    assert resp.status_code == 200, f"FastAPI endpoint failed: {resp.status_code} {resp.text}"
    data = resp.json()
    print(f" ✓ GET /api/v1/priorities: Status 200 OK")
    print(f"   Total priorities returned: {data['total_priorities']}")

    if data["priorities"]:
        p_id = data["priorities"][0]["priority_id"]
        detail_resp = client.get(f"/api/v1/priorities/{p_id}")
        assert detail_resp.status_code == 200
        print(f" ✓ GET /api/v1/priorities/{p_id}: Status 200 OK")

    print("\n" + "="*80)
    print("STAGE 30 STATUS: PASS")
    print("RISK / PRIORITY INTELLIGENCE: READY FOR USE")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_stage30_priorities_verification()
