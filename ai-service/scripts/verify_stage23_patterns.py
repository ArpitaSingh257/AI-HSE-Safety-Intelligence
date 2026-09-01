"""
verify_stage23_patterns.py - Dedicated Benchmark & 5-Repetition Determinism Verification for Stage 23.
"""

import sys
import json
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.pattern_detector import RecurringPatternDetector


def run_stage23_pattern_benchmark():
    print("\n" + "="*80)
    print("STAGE 23 — RECURRING PRECURSOR PATTERN DETECTION BENCHMARK")
    print("="*80)

    detector = RecurringPatternDetector(min_pattern_incidents=3)

    # 1. Verify embedding dimension
    dim = detector.embedding_engine.vector_dim
    print(f" ✓ Embedding Model: {detector.embedding_engine.model_name} (Vector Dimension: {dim})")
    assert dim == 384, f"Expected 384-dimensional embeddings, got {dim}"

    # 2. Run pattern discovery across historical dataset
    incidents = detector.load_historical_records()
    print(f" ✓ Loaded Historical Dataset: {len(incidents):,} records normalized & stably sorted.")

    patterns = detector.detect_patterns()
    print(f" ✓ Discovered Recurring Precursor Patterns: {len(patterns)} patterns (min_support >= 3).")

    if patterns:
        high_cnt = sum(1 for p in patterns if p["pattern_strength"] == "HIGH")
        med_cnt = sum(1 for p in patterns if p["pattern_strength"] == "MEDIUM")
        low_cnt = sum(1 for p in patterns if p["pattern_strength"] == "LOW")

        print(f"   - Pattern Strength Breakdown: HIGH={high_cnt}, MEDIUM={med_cnt}, LOW={low_cnt}")
        print("\n--- Top Discovered Pattern ---")
        top_pat = patterns[0]
        print(f"   Code: {top_pat.get('pattern_code')} | ID: {top_pat['pattern_id']}")
        print(f"   Name: {top_pat['pattern_name']}")
        print(f"   Summary: {top_pat['summary']}")
        print(f"   Incidents: {top_pat['incident_count']} (SIF Count: {top_pat['sif_incident_count']}, SIF Density: {top_pat['sif_density']*100:.1f}%)")
        print(f"   Locations: {', '.join(top_pat['locations'])}")
        print(f"   Traceable Incident IDs: {', '.join(top_pat['incident_ids'][:5])}...")

    # 3. Five-Repetition Determinism Verification
    print("\n" + "="*80)
    print("STAGE 23 — 5-REPETITION DETERMINISM VERIFICATION")
    print("="*80)

    runs = []
    for r_idx in range(1, 6):
        det = RecurringPatternDetector(min_pattern_incidents=3)
        res = det.detect_patterns()
        runs.append(res)
        print(f" Run {r_idx}: Discovered {len(res)} patterns | Top ID={res[0]['pattern_id'] if res else 'N/A'}")

    base_run = runs[0]
    for r_idx, r in enumerate(runs[1:], 2):
        assert len(r) == len(base_run), f"Run {r_idx} pattern count mismatch"
        for i in range(len(r)):
            assert r[i]["pattern_id"] == base_run[i]["pattern_id"], f"Run {r_idx} pattern_id mismatch at index {i}"
            assert r[i]["incident_ids"] == base_run[i]["incident_ids"], f"Run {r_idx} incident_ids mismatch at index {i}"
            assert r[i]["pattern_strength"] == base_run[i]["pattern_strength"], f"Run {r_idx} strength mismatch at index {i}"

    print(" ✓ 100% Identical Output Across 5 Repeated Inferences! (Run 1 == Run 2 == Run 3 == Run 4 == Run 5)")
    print("\n" + "="*80)
    print("STAGE 23 STATUS: PASS")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_stage23_pattern_benchmark()
