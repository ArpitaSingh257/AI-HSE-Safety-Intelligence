"""
diagnose_retrieval.py - Retrieval-Only Diagnostic Script for Stage 16 FAISS Index.
Analyzes exact Top-10 FAISS retrieval results for the hydrotest scenario without calling Ollama or modifying production code.
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
logger = logging.getLogger("RetrievalDiagnostic")


def run_hydrotest_retrieval_diagnostic(top_k: int = 10):
    logger.info("=== STAGE 16 FAISS RETRIEVAL DIAGNOSTIC ===")

    # Define exact hydrotest scenario narrative
    hydrotest_narrative = (
        "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, "
        "an operator was exposed to a pressure release after a bleeder plug ruptured."
    )

    # Initialize components (Read-Only)
    retriever = VectorRetriever()
    loaded = retriever.load_index()
    if not loaded:
        logger.error("Failed to load vector index or metadata store from datasets/rag/")
        return

    context_builder = SafetyContextBuilder()
    
    # Mock SIF & LSR context for context query construction
    sif_result = {"probability": 0.88, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"}
    lsr_result = {"triggered_rules": ["Energy Isolation", "Bypassing Safety Controls"]}

    constructed_query = context_builder.build_query(
        narrative=hydrotest_narrative,
        sif_result=sif_result,
        lsr_result=lsr_result
    )

    logger.info(f"Raw Narrative: '{hydrotest_narrative}'")
    logger.info(f"Constructed Context Query: '{constructed_query}'")

    # 1. FAISS Raw Vector Retrieval (Top-10) using Constructed Context Query
    raw_results = retriever.retrieve(constructed_query, top_k=top_k, min_confidence=0.0)

    # Also perform retrieval on raw narrative for comparison
    raw_narrative_results = retriever.retrieve(hydrotest_narrative, top_k=top_k, min_confidence=0.0)

    # Print Top-10 Diagnostic Output for Context Query
    print("\n" + "="*80)
    print("FAISS RETRIEVAL TOP-10 DIAGNOSTIC (CONSTRUCTED CONTEXT QUERY)")
    print("="*80)

    for rank, item in enumerate(raw_results[:top_k], start=1):
        print(f"Rank: {rank}")
        print(f"Chunk ID: {item.get('chunk_id')}")
        print(f"Similarity Score: {item.get('similarity'):.4f}")
        print(f"Document: {item.get('document')}")
        print(f"Page: {item.get('page')}")
        print(f"Section: {item.get('section', 'General')}")
        print(f"Chunk Text:\n{item.get('text')}")
        print("-" * 80)

    # Compact Summary
    unique_docs = sorted(list(set(r.get('document') for r in raw_results)))
    doc_counts = {}
    for r in raw_results:
        d = r.get('document')
        doc_counts[d] = doc_counts.get(d, 0) + 1

    scores = [r.get('similarity') for r in raw_results]
    score_min = min(scores) if scores else 0.0
    score_max = max(scores) if scores else 0.0

    print("\n" + "="*80)
    print("COMPACT RETRIEVAL SUMMARY")
    print("="*80)
    print(f"Query: {constructed_query}")
    print(f"Total retrieved: {len(raw_results)}")
    print(f"Unique documents count: {len(unique_docs)}")
    print(f"Documents represented: {doc_counts}")
    print(f"Score range: [{score_min:.4f} to {score_max:.4f}]")
    print("="*80 + "\n")

    # Also Print Raw Narrative Comparison
    print("\n" + "="*80)
    print("FAISS RETRIEVAL TOP-10 DIAGNOSTIC (RAW NARRATIVE QUERY)")
    print("="*80)
    for rank, item in enumerate(raw_narrative_results[:top_k], start=1):
        print(f"Rank {rank}: [{item.get('similarity'):.4f}] {item.get('document')} (Page {item.get('page')}, Section: '{item.get('section')}'): {item.get('text')[:120]}...")
    print("="*80 + "\n")


if __name__ == "__main__":
    run_hydrotest_retrieval_diagnostic()
