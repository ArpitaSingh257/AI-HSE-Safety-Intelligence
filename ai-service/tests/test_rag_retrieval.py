"""
test_rag_retrieval.py - QA Tests for Stage 16 Vector Index Retrieval & Reranking.
"""

import pytest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from knowledge.ingest_pipeline import run_rag_ingestion
from rag.retriever import VectorRetriever
from rag.reranker import SafetyReranker
from rag.context_builder import SafetyContextBuilder


@pytest.fixture(scope="module", autouse=True)
def setup_vector_index():
    """Ensure vector index is initialized before retrieval tests."""
    run_rag_ingestion()


def test_vector_retrieval_top_k():
    """Verify Top-K vector retrieval returns requested number of items with similarity scores."""
    retriever = VectorRetriever()
    results = retriever.retrieve("Energy isolation hydrostatic line pressure bleeder plug", top_k=5, min_confidence=0.10)

    assert len(results) > 0
    assert len(results) <= 5

    for item in results:
        assert "chunk_id" in item
        assert "document" in item
        assert "page" in item
        assert "text" in item
        assert "similarity" in item
        assert item["similarity"] >= 0.10


def test_lsr_aware_context_query():
    """Verify SafetyContextBuilder constructs LSR-aware enriched queries."""
    builder = SafetyContextBuilder()
    query = builder.build_query(
        narrative="Worker opened line without isolation",
        sif_result={"probability": 0.80, "risk_tier": "CRITICAL_SIF_PRECURSOR"},
        lsr_result={"triggered_rules": ["Energy Isolation", "Bypassing Safety Controls"]}
    )

    assert "Critical safety controls" in query
    assert "Energy Isolation" in query
    assert "Bypassing Safety Controls" in query


def test_reranker():
    """Verify SafetyReranker enhances score for domain hazard matches."""
    reranker = SafetyReranker()
    raw = [
        {"chunk_id": "c1", "text": "General office paperwork guidelines.", "similarity": 0.50, "document": "doc1", "page": 1},
        {"chunk_id": "c2", "text": "Energy isolation and hydrostatic line pressure release.", "similarity": 0.48, "document": "doc2", "page": 2}
    ]

    reranked = reranker.rerank("hydrostatic pressure line energy isolation", raw, top_n=2)
    assert len(reranked) == 2
    # The second chunk should be reranked higher due to hazard keyword density
    assert reranked[0]["chunk_id"] == "c2"
