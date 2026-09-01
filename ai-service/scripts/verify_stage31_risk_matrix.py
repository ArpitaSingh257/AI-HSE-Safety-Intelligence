"""
verify_stage31_risk_matrix.py - Stage 31 Benchmark & 5-Repetition Determinism Verification Script.
"""

import sys
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.risk_matrix_engine import RiskMatrixEngine


def run_stage31_risk_matrix_verification():
    print("\n" + "="*80)
    print("STAGE 31 — SEVERITY VS RECURRENCE RISK MATRIX VERIFICATION")
    print("="*80)

    t0 = time.time()
    engine = RiskMatrixEngine()
    items = engine.calculate_risk_matrix()
    t_elapsed = time.time() - t0

    c_hh = [i for i in items if i["quadrant"] == "HIGH_SEVERITY_HIGH_RECURRENCE"]
    c_hl = [i for i in items if i["quadrant"] == "HIGH_SEVERITY_LOW_RECURRENCE"]
    c_lh = [i for i in items if i["quadrant"] == "LOW_SEVERITY_HIGH_RECURRENCE"]
    c_ll = [i for i in items if i["quadrant"] == "LOW_SEVERITY_LOW_RECURRENCE"]

    print(f" ✓ Risk Matrix Engine execution time: {t_elapsed:.4f} seconds")
    print(f" ✓ Total 2D matrix items evaluated: {len(items)}")
    print(f"   - Critical Priority (High/High):  {len(c_hh)}")
    print(f"   - High-Potential Rare (High/Low): {len(c_hl)}")
    print(f"   - Frequent (Low/High):           {len(c_lh)}")
    print(f"   - Low Priority Monitor (Low/Low): {len(c_ll)}\n")

    print("--- Top 5 Placed 2D Risk Matrix Items ---")
    for idx, item in enumerate(items[:5], 1):
        print(f" #{idx} [{item['classification']}] {item['entity_name']} ({item['entity_type']})")
        print(f"     ID: {item['matrix_item_id']} | Quadrant: {item['quadrant']}")
        print(f"     2D Coordinates: Severity = {item['severity_score']:.4f} | Recurrence = {item['recurrence_score']:.4f}")
        print(f"     Rationale: {item['reason']}")
        print()

    # ---------------------------------------------------------
    # 5-REPETITION DETERMINISM VERIFICATION
    # ---------------------------------------------------------
    print("\n" + "="*80)
    print("STAGE 31 — 5-REPETITION DETERMINISM VERIFICATION")
    print("="*80)

    runs = []
    for r_idx in range(1, 6):
        e = RiskMatrixEngine()
        res = e.calculate_risk_matrix()
        runs.append(res)
        top_item = res[0]["matrix_item_id"] if res else "N/A"
        top_cls = res[0]["classification"] if res else "N/A"
        top_sev = res[0]["severity_score"] if res else 0.0
        top_rec = res[0]["recurrence_score"] if res else 0.0
        print(f" Run {r_idx}: Top Item = {top_item} [{top_cls}] (Sev = {top_sev:.4f}, Rec = {top_rec:.4f})")

    base_run = runs[0]
    for r_idx, r in enumerate(runs[1:], 2):
        assert len(r) == len(base_run), f"Run {r_idx} length mismatch: {len(r)} vs {len(base_run)}"
        for i in range(len(r)):
            assert r[i]["matrix_item_id"] == base_run[i]["matrix_item_id"], f"Run {r_idx} ID mismatch at index {i}"
            assert r[i]["quadrant"] == base_run[i]["quadrant"], f"Run {r_idx} quadrant mismatch at index {i}"
            assert abs(r[i]["severity_score"] - base_run[i]["severity_score"]) < 1e-4, f"Run {r_idx} severity mismatch at index {i}"
            assert abs(r[i]["recurrence_score"] - base_run[i]["recurrence_score"]) < 1e-4, f"Run {r_idx} recurrence mismatch at index {i}"

    print(" ✓ 100% Identical Output Across 5 Repeated Calculations! (Run 1 == Run 2 == Run 3 == Run 4 == Run 5)")

    # ---------------------------------------------------------
    # FASTAPI ENDPOINT PYDANTIC SCHEMA VALIDATION
    # ---------------------------------------------------------
    print("\n" + "="*80)
    print("STAGE 31 — FASTAPI PYDANTIC SCHEMA VALIDATION")
    print("="*80)
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    resp = client.get("/api/v1/risk-matrix")
    assert resp.status_code == 200, f"FastAPI endpoint failed: {resp.status_code} {resp.text}"
    data = resp.json()
    print(f" ✓ GET /api/v1/risk-matrix: Status 200 OK")
    print(f"   Total items returned: {data['total_items']}")

    if data["matrix_items"]:
        m_id = data["matrix_items"][0]["matrix_item_id"]
        detail_resp = client.get(f"/api/v1/risk-matrix/{m_id}")
        assert detail_resp.status_code == 200
        print(f" ✓ GET /api/v1/risk-matrix/{m_id}: Status 200 OK")

    print("\n" + "="*80)
    print("STAGE 31 STATUS: PASS")
    print("SEVERITY VS RECURRENCE RISK MATRIX: READY FOR USE")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_stage31_risk_matrix_verification()
