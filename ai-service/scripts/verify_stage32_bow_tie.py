"""
verify_stage32_bow_tie.py - Stage 32 Benchmark & 5-Repetition Determinism Verification Script.
"""

import sys
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.bow_tie_mapper import BowTieMapper


def run_stage32_bow_tie_verification():
    print("\n" + "="*80)
    print("STAGE 32 — BOW-TIE / BARRIER FAILURE MAPPING VERIFICATION")
    print("="*80)

    t0 = time.time()
    mapper = BowTieMapper()
    bt = mapper.get_bow_tie_by_report_id("R-1001")
    t_elapsed = time.time() - t0

    print(f" ✓ BowTieMapper execution time: {t_elapsed:.4f} seconds")
    print(f" ✓ Report ID:                   {bt['report_id']}")
    print(f" ✓ Bow-Tie ID:                  {bt['bow_tie_id']}")
    print(f" ✓ Total Nodes:                 {len(bt['nodes'])}")
    print(f" ✓ Total Edges:                 {len(bt['edges'])}")
    print(f" ✓ Mapping Confidence:          {bt['mapping_confidence']}\n")

    print("--- Graph Nodes Breakdown ---")
    for n in bt["nodes"]:
        canon_str = f" ({n['canonical_barrier']})" if n.get("canonical_barrier") else ""
        print(f" - [{n['type']}] {n['label']}{canon_str} | Provenance: {n['provenance']}")

    print("\n--- Graph Edges Breakdown ---")
    for e in bt["edges"]:
        print(f" - Edge: {e['source']} -> {e['target']} | Provenance: {e['provenance']}")

    # ---------------------------------------------------------
    # 5-REPETITION DETERMINISM VERIFICATION
    # ---------------------------------------------------------
    print("\n" + "="*80)
    print("STAGE 32 — 5-REPETITION DETERMINISM VERIFICATION")
    print("="*80)

    runs = []
    for r_idx in range(1, 6):
        m = BowTieMapper()
        res = m.get_bow_tie_by_report_id("R-1001")
        runs.append(res)
        top_node = res["nodes"][0]["label"] if res["nodes"] else "N/A"
        print(f" Run {r_idx}: Bow-Tie ID = {res['bow_tie_id']} | Nodes = {len(res['nodes'])} | Edges = {len(res['edges'])}")

    base_run = runs[0]
    for r_idx, r in enumerate(runs[1:], 2):
        assert r == base_run, f"Run {r_idx} differs from Run 1"

    print(" ✓ 100% Identical Output Across 5 Repeated Calculations! (Run 1 == Run 2 == Run 3 == Run 4 == Run 5)")

    # ---------------------------------------------------------
    # FASTAPI ENDPOINT PYDANTIC SCHEMA VALIDATION
    # ---------------------------------------------------------
    print("\n" + "="*80)
    print("STAGE 32 — FASTAPI PYDANTIC SCHEMA VALIDATION")
    print("="*80)
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    resp = client.get("/api/v1/bow-ties/R-1001")
    assert resp.status_code == 200, f"FastAPI endpoint failed: {resp.status_code} {resp.text}"
    data = resp.json()
    print(f" ✓ GET /api/v1/bow-ties/R-1001: Status 200 OK")
    print(f"   Bow-Tie ID returned: {data['bow_tie_id']}")

    print("\n" + "="*80)
    print("STAGE 32 STATUS: PASS")
    print("BOW-TIE / BARRIER FAILURE MAPPING: READY FOR USE")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_stage32_bow_tie_verification()
