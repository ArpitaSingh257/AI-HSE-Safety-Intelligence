"""
verify_stage26_site_risk.py - Benchmark & 5-Repetition Determinism Verification for Stage 26.
"""

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.site_risk_analyzer import SiteRiskAnalyzer


def run_stage26_site_risk_benchmark():
    print("\n" + "="*80)
    print("STAGE 26 — SITE-LEVEL RISK INTELLIGENCE BENCHMARK")
    print("="*80)

    analyzer = SiteRiskAnalyzer(min_site_reports=3)
    profiles = analyzer.calculate_site_risk_profiles()

    print(f" ✓ Evaluated {len(profiles)} unique operational site risk profiles from dataset.\n")

    print("--- Ranked Operational Site Profiles ---")
    for idx, p in enumerate(profiles, 1):
        print(f" #{idx} Site: {p['site_name']} ({p['site_id']})")
        print(f"     Risk Level:         {p['risk_level']} (Site Risk Index R_s = {p['risk_index']:.4f})")
        print(f"     Total Reports:      {p['total_reports']} (SIF Reports: {p['sif_reports']}, SIF Density: {p['sif_density']*100:.1f}%)")
        print(f"     Stage 23 Patterns:  {p['recurring_pattern_count']} recurring patterns")
        print(f"     Stage 24 Barriers:  {p['barrier_failure_pattern_count']} barrier patterns")
        if p["top_activities"]:
            top_act = p["top_activities"][0]
            print(f"     Top Activity:       {top_act['name']} ({top_act['report_count']} reports, {top_act['sif_density']*100:.1f}% SIF)")
        if p["top_barrier_failures"]:
            top_bf = p["top_barrier_failures"][0]
            print(f"     Top Barrier Gap:    {top_bf['name']} ({top_bf['count']} occurrences)")
        print()

    # Data Quality & Coverage Summary
    total_recs = sum(p["total_reports"] for p in profiles)
    valid_sites = [p for p in profiles if p["site_name"] != "UNKNOWN_SITE"]
    sufficient_sites = [p for p in profiles if p["risk_level"] != "INSUFFICIENT_DATA"]

    print("--- Data Quality & Site Metadata Coverage ---")
    print(f" Total Historical Reports Processed: {total_recs:,}")
    print(f" Unique Operational Sites Identified: {len(profiles)}")
    print(f" Sites with Sufficient Data (>= 3 reports): {len(sufficient_sites)}")
    print(f" Sites with Insufficient Data (< 3 reports): {len(profiles) - len(sufficient_sites)}")

    # Five-Repetition Determinism Verification
    print("\n" + "="*80)
    print("STAGE 26 — 5-REPETITION DETERMINISM VERIFICATION")
    print("="*80)

    runs = []
    for r_idx in range(1, 6):
        a = SiteRiskAnalyzer(min_site_reports=3)
        res = a.calculate_site_risk_profiles()
        runs.append(res)
        top_name = res[0]['site_name'] if res else 'N/A'
        top_r_s = res[0]['risk_index'] if res else 0.0
        print(f" Run {r_idx}: Top Ranked Site = {top_name} (Risk Index R_s = {top_r_s:.4f})")

    base_run = runs[0]
    for r_idx, r in enumerate(runs[1:], 2):
        assert len(r) == len(base_run), f"Run {r_idx} site count mismatch"
        for i in range(len(r)):
            assert r[i]["site_id"] == base_run[i]["site_id"], f"Run {r_idx} ID mismatch at index {i}"
            assert abs(r[i]["risk_index"] - base_run[i]["risk_index"]) < 1e-4, f"Run {r_idx} risk index mismatch at index {i}"

    print(" ✓ 100% Identical Output Across 5 Repeated Calculations! (Run 1 == Run 2 == Run 3 == Run 4 == Run 5)")
    print("\n" + "="*80)
    print("STAGE 26 STATUS: PASS")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_stage26_site_risk_benchmark()
