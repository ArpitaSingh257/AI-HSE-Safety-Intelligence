"""
test_recommendation_citations.py - QA Tests for Source Citation Provenance & Auditability.
"""

import pytest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from rag.grounded_recommender import RAGSafetyRecommendationEngine


def test_source_citation_provenance_schema():
    """Verify every recommendation includes full traceable source citations."""
    engine = RAGSafetyRecommendationEngine()
    res = engine.generate_recommendations(
        narrative="Worker entering vessel smelled toxic gas without breathing apparatus.",
        sif_result={"probability": 0.90, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"},
        lsr_result={"triggered_rules": ["Confined Space", "Toxic Gas / Hazardous Substance"]}
    )

    assert "sources" in res
    sources = res["sources"]
    assert len(sources) > 0

    citation = sources[0]
    required_keys = ["document", "page", "section", "chunk_id", "similarity", "snippet"]
    for k in required_keys:
        assert k in citation, f"Missing citation provenance key '{k}'"

    assert citation["page"] >= 1
    assert citation["document"].endswith(".pdf")
