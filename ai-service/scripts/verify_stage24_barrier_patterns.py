"""
verify_stage24_barrier_patterns.py - Benchmark & 5-Repetition Determinism Verification for Stage 24.
"""

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.barrier_pattern_miner import BarrierPatternMiner


def run_stage24_barrier_benchmark():
    print("\n" + "="*80)
    print("STAGE 24 — BARRIER FAILURE PATTERN MINING BENCHMARK")
    print("="*80)

    miner = BarrierPatternMiner(min_barrier_incidents=3)

    # 1. Mine barrier failure patterns across historical dataset
    patterns = miner.mine_barrier_patterns()
    print(f" ✓ Discovered Recurring Barrier Failure Patterns: {len(patterns)} patterns (min_support >= 3).")

    if patterns:
        high_cnt = sum(1 for p in patterns if p["pattern_strength"] == "HIGH")
        med_cnt = sum(1 for p in patterns if p["pattern_strength"] == "MEDIUM")
        low_cnt = sum(1 for p in patterns if p["pattern_strength"] == "LOW")

        print(f"   - Pattern Strength Breakdown: HIGH={high_cnt}, MEDIUM={med_cnt}, LOW={low_cnt}")
        print("\n--- Top Discovered Barrier Failure Pattern ---")
        top_pat = patterns[0]
        print(f"   Code: {top_pat.get('barrier_code_prefix')} | ID: {top_pat['barrier_pattern_id']}")
        print(f"   Name: {top_pat['barrier_name']} (Canonical: {top_pat['barrier_code']})")
        print(f"   Incidents: {top_pat['incident_count']} (SIF Count: {top_pat['sif_incident_count']}, SIF Density: {top_pat['sif_density']*100:.1f}%)")
        print(f"   Dominant Activity: {top_pat['dominant_activity']} | LSR: {top_pat['dominant_lsr']}")
        print(f"   Locations: {', '.join(top_pat['locations'])}")
        print(f"   Traceable Incident IDs: {', '.join(top_pat['incident_ids'][:5])}...")

    # 2. Five-Repetition Determinism Verification
    print("\n" + "="*80)
    print("STAGE 24 — 5-REPETITION DETERMINISM VERIFICATION")
    print("="*80)

    runs = []
    for r_idx in range(1, 6):
        m = BarrierPatternMiner(min_barrier_incidents=3)
        res = m.mine_barrier_patterns()
        runs.append(res)
        print(f" Run {r_idx}: Mined {len(res)} barrier patterns | Top ID={res[0]['barrier_pattern_id'] if res else 'N/A'}")

    base_run = runs[0]
    for r_idx, r in enumerate(runs[1:], 2):
        assert len(r) == len(base_run), f"Run {r_idx} pattern count mismatch"
        for i in range(len(r)):
            assert r[i]["barrier_pattern_id"] == base_run[i]["barrier_pattern_id"], f"Run {r_idx} ID mismatch at index {i}"
            assert r[i]["incident_ids"] == base_run[i]["incident_ids"], f"Run {r_idx} incident_ids mismatch at index {i}"
            assert r[i]["pattern_strength"] == base_run[i]["pattern_strength"], f"Run {r_idx} strength mismatch at index {i}"

    print(" ✓ 100% Identical Output Across 5 Repeated Inferences! (Run 1 == Run 2 == Run 3 == Run 4 == Run 5)")
    print("\n" + "="*80)
    print("STAGE 24 STATUS: PASS")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_stage24_barrier_benchmark()
