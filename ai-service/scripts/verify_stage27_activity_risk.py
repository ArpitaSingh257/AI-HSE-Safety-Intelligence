"""
verify_stage27_activity_risk.py - Benchmark & 5-Repetition Determinism Verification for Stage 27.
"""

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.activity_risk_analyzer import ActivityRiskAnalyzer


def run_stage27_activity_risk_benchmark():
    print("\n" + "="*80)
    print("STAGE 27 — ACTIVITY-LEVEL RISK INTELLIGENCE BENCHMARK")
    print("="*80)

    analyzer = ActivityRiskAnalyzer(min_activity_reports=3)
    profiles = analyzer.calculate_activity_risk_profiles()

    print(f" ✓ Evaluated {len(profiles)} unique operational activity risk profiles from dataset.\n")

    print("--- Ranked Operational Activity Profiles ---")
    for idx, p in enumerate(profiles, 1):
        print(f" #{idx} Activity: {p['activity_name']} ({p['activity_id']})")
        print(f"     Risk Level:         {p['risk_level']} (Activity Risk Index R_a = {p['risk_index']:.4f})")
        print(f"     Total Reports:      {p['total_reports']} (SIF Reports: {p['sif_reports']}, SIF Density: {p['sif_density']*100:.1f}%)")
        print(f"     Stage 23 Patterns:  {p['recurring_pattern_count']} recurring patterns")
        print(f"     Stage 24 Barriers:  {p['barrier_failure_pattern_count']} barrier patterns")
        if p["associated_sites"]:
            top_site = p["associated_sites"][0]
            print(f"     Top Site:           {top_site['site_name']} ({top_site['count']} reports)")
        if p["top_hazards"]:
            top_hz = p["top_hazards"][0]
            print(f"     Top Hazard:         {top_hz['name']} ({top_hz['count']} reports)")
        if p["top_barrier_failures"]:
            top_bf = p["top_barrier_failures"][0]
            print(f"     Top Barrier Gap:    {top_bf['name']} ({top_bf['count']} occurrences)")
        print()

    # Data Quality & Coverage Summary
    total_recs = sum(p["total_reports"] for p in profiles)
    valid_acts = [p for p in profiles if p["activity_name"] != "UNKNOWN_ACTIVITY"]
    sufficient_acts = [p for p in profiles if p["risk_level"] != "INSUFFICIENT_DATA"]

    print("--- Data Quality & Activity Metadata Coverage ---")
    print(f" Total Historical Reports Processed: {total_recs:,}")
    print(f" Unique Operational Activities Identified: {len(profiles)}")
    print(f" Activities with Sufficient Data (>= 3 reports): {len(sufficient_acts)}")
    print(f" Activities with Insufficient Data (< 3 reports): {len(profiles) - len(sufficient_acts)}")

    # Five-Repetition Determinism Verification
    print("\n" + "="*80)
    print("STAGE 27 — 5-REPETITION DETERMINISM VERIFICATION")
    print("="*80)

    runs = []
    for r_idx in range(1, 6):
        a = ActivityRiskAnalyzer(min_activity_reports=3)
        res = a.calculate_activity_risk_profiles()
        runs.append(res)
        top_name = res[0]['activity_name'] if res else 'N/A'
        top_r_a = res[0]['risk_index'] if res else 0.0
        print(f" Run {r_idx}: Top Ranked Activity = {top_name} (Risk Index R_a = {top_r_a:.4f})")

    base_run = runs[0]
    for r_idx, r in enumerate(runs[1:], 2):
        assert len(r) == len(base_run), f"Run {r_idx} activity count mismatch"
        for i in range(len(r)):
            assert r[i]["activity_id"] == base_run[i]["activity_id"], f"Run {r_idx} ID mismatch at index {i}"
            assert abs(r[i]["risk_index"] - base_run[i]["risk_index"]) < 1e-4, f"Run {r_idx} risk index mismatch at index {i}"

    print(" ✓ 100% Identical Output Across 5 Repeated Calculations! (Run 1 == Run 2 == Run 3 == Run 4 == Run 5)")
    print("\n" + "="*80)
    print("STAGE 27 STATUS: PASS")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_stage27_activity_risk_benchmark()
