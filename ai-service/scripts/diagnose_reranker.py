"""
diagnose_reranker.py - Diagnostic Benchmark for Safety Reranker Subsystem.
Compares raw FAISS Top-10 rankings with SafetyReranker outputs for the hydrotest scenario.
Read-only script; makes zero changes to production code.
"""

import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from knowledge.embeddings import SafetyEmbeddingEngine
from rag.retriever import VectorRetriever
from rag.reranker import SafetyReranker
from rag.context_builder import SafetyContextBuilder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RerankerDiagnostic")


def run_reranker_diagnostic(top_k: int = 10):
    logger.info("=== STAGE 16.2 RERANKER DIAGNOSTIC BENCHMARK ===")

    hydrotest_narrative = (
        "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, "
        "an operator was exposed to a pressure release after a bleeder plug ruptured."
    )

    retriever = VectorRetriever()
    loaded = retriever.load_index()
    if not loaded:
        logger.error("Vector index not found.")
        return

    context_builder = SafetyContextBuilder()
    reranker = SafetyReranker()

    sif_result = {"probability": 0.88, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"}
    lsr_result = {"triggered_rules": ["Energy Isolation", "Bypassing Safety Controls"]}

    constructed_query = context_builder.build_query(
        narrative=hydrotest_narrative,
        sif_result=sif_result,
        lsr_result=lsr_result
    )

    # 1. Retrieve FAISS Top-10
    faiss_results = retriever.retrieve(constructed_query, top_k=top_k, min_confidence=0.0)

    # Attach original FAISS rank
    for rank, item in enumerate(faiss_results, start=1):
        item["faiss_rank"] = rank

    # 2. Run existing Reranker on FAISS Top-10
    reranked_results = reranker.rerank(query=constructed_query, retrieved_passages=faiss_results, top_n=top_k)

    print("\n" + "="*80)
    print("FAISS vs RERANKER DIAGNOSTIC")
    print("="*80)
    print(f"\nQUERY:\n{constructed_query}\n")

    print("-"*80)
    print("FAISS ORIGINAL RANKING")
    print("-"*80)
    for item in faiss_results:
        print(f"Rank {item['faiss_rank']}")
        print(f"FAISS Score: {item.get('similarity'):.4f}")
        print(f"Document: {item.get('document')}")
        print(f"Page: {item.get('page')}")
        print(f"Section: {item.get('section', 'General')}")
        print(f"Chunk ID: {item.get('chunk_id')}")
        print(f"Text: {item.get('text')}\n")

    print("-"*80)
    print("RERANKED RESULTS")
    print("-"*80)
    for new_rank, item in enumerate(reranked_results, start=1):
        print(f"Rank {new_rank}")
        print(f"Reranker Score: {item.get('rerank_score'):.4f}")
        print(f"Original FAISS Rank: {item.get('faiss_rank')}")
        print(f"Document: {item.get('document')}")
        print(f"Page: {item.get('page')}")
        print(f"Section: {item.get('section', 'General')}")
        print(f"Chunk ID: {item.get('chunk_id')}")
        print(f"Text: {item.get('text')}\n")

    print("="*80)
    print("RANKING CHANGES")
    print("="*80)
    for new_rank, item in enumerate(reranked_results, start=1):
        orig_rank = item.get("faiss_rank")
        doc_short = Path(item.get("document")).stem[:25]
        print(f"FAISS Rank {orig_rank:2d}  →  Reranker Rank {new_rank:2d} | Score: {item.get('rerank_score'):.4f} | [{doc_short}] p.{item.get('page')}")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_reranker_diagnostic()
