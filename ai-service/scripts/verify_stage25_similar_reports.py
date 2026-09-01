"""
verify_stage25_similar_reports.py - Benchmark & 5-Repetition Determinism Verification for Stage 25.
"""

import sys
import json
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.similar_report_finder import SimilarReportFinder


def run_stage25_similar_reports_benchmark():
    print("\n" + "="*80)
    print("STAGE 25 — SIMILAR HISTORICAL REPORT LINKING BENCHMARK")
    print("="*80)

    finder = SimilarReportFinder(top_k=5, min_similarity=0.40)

    # 1. Verify embedding model & dimension
    dim = finder.vector_dim
    print(f" ✓ Embedding Model: {finder.embedding_engine.model_name} (Vector Dimension: {dim})")
    assert dim == 384, f"Expected 384-dimensional embeddings, got {dim}"

    # 2. Verify dedicated historical FAISS vector index
    indexed_cnt = len(finder.records)
    print(f" ✓ Loaded Historical Report Corpus: {indexed_cnt:,} records indexed in FAISS vector store.")

    # 3. Test Cases (Energy Isolation, Crane/Lifting, Confined Space, Unrelated)
    test_cases = [
        ("Case A: Energy Isolation", "Technician started maintenance before electrical isolation."),
        ("Case B: Crane / Lifting", "A suspended load shifted unexpectedly during crane lifting."),
        ("Case C: Confined Space", "Operator exposed to potential H2S atmosphere inside confined space."),
        ("Case D: Negative Unrelated Control", "Office clerk dropped paper sheet on desk surface.")
    ]

    print("\n--- Test Queries Benchmark ---")
    for title, q_text in test_cases:
        res = finder.find_similar_reports(query_text=q_text, top_k=5, min_similarity=0.40)
        print(f"\n {title}")
        print(f"   Query: \"{q_text}\"")
        print(f"   Matches Returned: {len(res)} similar historical reports")

        if res:
            top_match = res[0]
            print(f"   Top Match: {top_match['report_id']} (Similarity: {top_match['similarity_percentage']}%)")
            print(f"   Activity: {top_match['activity']} | LSR: {top_match['primary_life_saving_rule']}")
            print(f"   Barrier Failure: {top_match['barrier_failure']}")
            if top_match.get("stage23_pattern_id"):
                print(f"   Linked Stage 23 Pattern: {top_match['stage23_pattern_id']}")
            if top_match.get("stage24_barrier_id"):
                print(f"   Linked Stage 24 Barrier: {top_match['stage24_barrier_id']}")

    # 4. Self-Match Exclusion Verification
    first_id = finder.records[0]["record_id"]
    self_res = finder.find_similar_reports(query_report_id=first_id, top_k=5)
    matched_ids = [r["report_id"] for r in self_res]
    print(f"\n ✓ Self-Match Exclusion Test for '{first_id}': Excluded successfully! (In returned results: {first_id in matched_ids})")
    assert first_id not in matched_ids

    # 5. Five-Repetition Determinism Verification
    print("\n" + "="*80)
    print("STAGE 25 — 5-REPETITION DETERMINISM VERIFICATION")
    print("="*80)

    q = "Pressurized bleeder line ruptured during hydrotest."
    runs = []
    for r_idx in range(1, 6):
        f = SimilarReportFinder(top_k=5, min_similarity=0.40)
        res = f.find_similar_reports(query_text=q)
        runs.append(res)
        top_id = res[0]['report_id'] if res else 'N/A'
        top_sim = res[0]['similarity_score'] if res else 0.0
        print(f" Run {r_idx}: Top Similar Report ID={top_id} (Score={top_sim})")

    base_run = runs[0]
    for r_idx, r in enumerate(runs[1:], 2):
        assert len(r) == len(base_run), f"Run {r_idx} count mismatch"
        for i in range(len(r)):
            assert r[i]["report_id"] == base_run[i]["report_id"], f"Run {r_idx} ID mismatch at index {i}"
            assert abs(r[i]["similarity_score"] - base_run[i]["similarity_score"]) < 1e-4, f"Run {r_idx} score mismatch at index {i}"

    print(" ✓ 100% Identical Output Across 5 Repeated Searches! (Run 1 == Run 2 == Run 3 == Run 4 == Run 5)")
    print("\n" + "="*80)
    print("STAGE 25 STATUS: PASS")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_stage25_similar_reports_benchmark()
