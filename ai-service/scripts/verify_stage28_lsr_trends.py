"""
verify_stage28_lsr_trends.py - Benchmark & 5-Repetition Determinism Verification for Stage 28 / 28C.
"""

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.lsr_trend_analyzer import LsrTrendAnalyzer


def run_stage28_lsr_trends_benchmark():
    print("\n" + "="*80)
    print("STAGE 28C — LIFE-SAVING RULE (LSR) TREND ANALYTICS BENCHMARK")
    print("="*80)

    analyzer = LsrTrendAnalyzer(min_lsr_reports=3, min_trend_periods=2)
    summary = analyzer.get_lsr_analytics_summary()
    profiles = summary["official_lsr_profiles"]

    print(f" ✓ Evaluated {len(profiles)} official IOGP Life-Saving Rule trend profiles.")
    print(f" ✓ Tracked {summary['unknown_lsr_records']} reports with missing/unclassified LSR labels ({summary['unknown_lsr_rate']*100:.2f}%).\n")

    print("--- Official IOGP Life-Saving Rule Temporal Trend Profiles ---")
    for idx, p in enumerate(profiles, 1):
        print(f" #{idx} Rule: {p['lsr_rule']}")
        print(f"     Total Reports:     {p['total_reports']} (SIF Reports: {p['sif_reports']}, SIF Density: {p['sif_density']*100:.1f}%)")
        print(f"     Trend Trajectory:  {p['trend']} (Delta: {p['trend_delta']*100:+.1f}%)")
        print(f"     Time Periods:      {len(p['time_series'])} monthly buckets")
        if p["top_sites"]:
            print(f"     Top Associated Site: {p['top_sites'][0]['site_name']} ({p['top_sites'][0]['count']} reports)")
        if p["top_activities"]:
            print(f"     Top Associated Task: {p['top_activities'][0]['activity_name']} ({p['top_activities'][0]['count']} reports)")
        if p["top_barrier_failures"]:
            print(f"     Top Barrier Gap:     {p['top_barrier_failures'][0]['name']} ({p['top_barrier_failures'][0]['count']} occurrences)")
        print()

    # Five-Repetition Determinism Verification
    print("\n" + "="*80)
    print("STAGE 28C — 5-REPETITION DETERMINISM VERIFICATION")
    print("="*80)

    runs = []
    for r_idx in range(1, 6):
        a = LsrTrendAnalyzer(min_lsr_reports=3, min_trend_periods=2)
        res = a.calculate_lsr_trend_profiles()
        runs.append(res)
        top_rule = res[0]['lsr_rule'] if res else 'N/A'
        top_trend = res[0]['trend'] if res else 'N/A'
        print(f" Run {r_idx}: Top Rule = {top_rule} (Trend State = {top_trend}, Delta = {res[0]['trend_delta']:+.4f})")

    base_run = runs[0]
    for r_idx, r in enumerate(runs[1:], 2):
        assert len(r) == len(base_run), f"Run {r_idx} rule count mismatch"
        for i in range(len(r)):
            assert r[i]["lsr_rule"] == base_run[i]["lsr_rule"], f"Run {r_idx} rule mismatch at index {i}"
            assert r[i]["trend"] == base_run[i]["trend"], f"Run {r_idx} trend state mismatch at index {i}"
            assert abs(r[i]["trend_delta"] - base_run[i]["trend_delta"]) < 1e-4, f"Run {r_idx} delta mismatch at index {i}"

    print(" ✓ 100% Identical Output Across 5 Repeated Calculations! (Run 1 == Run 2 == Run 3 == Run 4 == Run 5)")

    # FastAPI Endpoint Pydantic Schema Validation & UNKNOWN Exclusion
    print("\n" + "="*80)
    print("STAGE 28C — FASTAPI PYDANTIC SCHEMA VALIDATION & UNKNOWN EXCLUSION")
    print("="*80)
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    resp = client.get("/api/v1/lsr-trends?min_reports=3")
    assert resp.status_code == 200, f"FastAPI endpoint failed: {resp.status_code} {resp.text}"
    data = resp.json()
    print(f" ✓ GET /api/v1/lsr-trends validated cleanly against Pydantic schema! Returned {data['total_lsr_rules']} official IOGP rules.")
    rule_names = [p["lsr_rule"] for p in data["lsr_profiles"]]
    assert "UNKNOWN" not in rule_names

    if data['lsr_profiles']:
        first_rule = data['lsr_profiles'][0]['lsr_rule']
        detail_resp = client.get(f"/api/v1/lsr-trends/{first_rule}")
        assert detail_resp.status_code == 200, f"Detail endpoint failed: {detail_resp.status_code} {detail_resp.text}"
        print(f" ✓ GET /api/v1/lsr-trends/{first_rule} validated cleanly against Pydantic schema!")

    unk_resp = client.get("/api/v1/lsr-trends/UNKNOWN")
    assert unk_resp.status_code == 404
    print(" ✓ GET /api/v1/lsr-trends/UNKNOWN returned 404 Not Found.")

    print("\n" + "="*80)
    print("STAGE 28C STATUS: PASS")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_stage28_lsr_trends_benchmark()
