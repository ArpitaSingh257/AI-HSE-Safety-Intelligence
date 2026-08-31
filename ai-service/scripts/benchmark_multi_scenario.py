"""
benchmark_multi_scenario.py - Stage 16.3 Multi-Scenario Retrieval & Reranker Benchmark Script.
Evaluates FAISS Top-10 + Reranker Top-5 across all 4 mandatory safety scenarios in read-only mode.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from knowledge.embeddings import SafetyEmbeddingEngine
from rag.retriever import VectorRetriever
from rag.reranker import SafetyReranker
from rag.context_builder import SafetyContextBuilder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MultiScenarioBenchmark")


SCENARIOS = {
    "Scenario 1 — Hydrotest / Pressure": {
        "narrative": "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator was exposed to a pressure release after a bleeder plug ruptured.",
        "sif": {"probability": 0.88, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"},
        "lsr": {"triggered_rules": ["Energy Isolation", "Bypassing Safety Controls"]},
        "expected_concepts": ["hydrostatic", "pressure", "bleeder", "isolation", "trapped pressure", "line of fire"]
    },
    "Scenario 2 — Crane / Lifting": {
        "narrative": "During a crane lifting operation, a suspended load shifted unexpectedly and entered the line of fire of personnel working nearby.",
        "sif": {"probability": 0.76, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"},
        "lsr": {"triggered_rules": ["Safe Mechanical Lifting", "Line of Fire"]},
        "expected_concepts": ["crane", "lifting", "suspended load", "line of fire", "rigging", "exclusion zone"]
    },
    "Scenario 3 — Confined Space + H2S": {
        "narrative": "During vessel entry preparation, an operator was exposed to a potential H2S atmosphere inside a confined space.",
        "sif": {"probability": 0.92, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"},
        "lsr": {"triggered_rules": ["Confined Space", "Toxic Gas / Hazardous Substance"]},
        "expected_concepts": ["confined space", "h2s", "toxic gas", "atmospheric", "vessel entry", "gas detector"]
    },
    "Scenario 4 — Minor Slip Negative Control": {
        "narrative": "An employee experienced a minor slip while walking on a dry, level office floor. No injury occurred and no hazardous energy or process safety condition was involved.",
        "sif": {"probability": 0.02, "is_sif": False, "risk_tier": "LOW_POTENTIAL_INCIDENT"},
        "lsr": {"triggered_rules": []},
        "expected_concepts": ["minor", "housekeeping", "slip", "office", "reporting"]
    }
}


def run_benchmark():
    logger.info("=== STAGE 16.3 MULTI-SCENARIO RETRIEVAL BENCHMARK ===")

    retriever = VectorRetriever()
    if not retriever.load_index():
        logger.error("Vector index not found.")
        return

    context_builder = SafetyContextBuilder()
    reranker = SafetyReranker()

    scenario_summaries = []

    for name, sc in SCENARIOS.items():
        query = context_builder.build_query(sc["narrative"], sc["sif"], sc["lsr"])

        # 1. FAISS Top-10
        faiss_hits = retriever.retrieve(query, top_k=10, min_confidence=0.0)
        for rank, item in enumerate(faiss_hits, start=1):
            item["faiss_rank"] = rank

        # 2. Reranked Top-5
        reranked_hits = reranker.rerank(query, faiss_hits, top_n=5)

        print("\n" + "="*80)
        print(f"SCENARIO: {name}")
        print("="*80)
        print(f"QUERY:\n{query}\n")

        print("-"*80)
        print("FAISS TOP-10")
        print("-"*80)
        print(f"{'Rank':<5} | {'Score':<7} | {'Document':<35} | {'Page':<5} | {'Chunk ID':<30}")
        print("-" * 90)
        for h in faiss_hits:
            doc_short = Path(h['document']).name[:33]
            print(f"{h['faiss_rank']:<5} | {h.get('similarity'):<7.4f} | {doc_short:<35} | {h.get('page'):<5} | {h.get('chunk_id'):<30}")

        print("\n" + "-"*80)
        print("RERANKED TOP-5")
        print("-"*80)
        print(f"{'NewRank':<7} | {'RerankScore':<11} | {'OrigRank':<8} | {'Document':<35} | {'Page':<5} | {'Chunk ID':<30}")
        print("-" * 100)
        for new_rank, h in enumerate(reranked_hits, start=1):
            doc_short = Path(h['document']).name[:33]
            print(f"{new_rank:<7} | {h.get('rerank_score'):<11.4f} | {h.get('faiss_rank'):<8} | {doc_short:<35} | {h.get('page'):<5} | {h.get('chunk_id'):<30}")
            print(f"   Snippet: {h.get('text')[:130]}...\n")

        best_hit = reranked_hits[0] if reranked_hits else {}
        scenario_summaries.append({
            "scenario": name,
            "best_source": Path(best_hit.get("document", "")).name,
            "best_page": best_hit.get("page", 0),
            "best_score": round(best_hit.get("rerank_score", 0.0), 4),
            "top5_hits": reranked_hits
        })

    print("="*80)
    print("BENCHMARK EXECUTION COMPLETED")
    print("="*80)


if __name__ == "__main__":
    run_benchmark()
