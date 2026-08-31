"""
test_grounded_recommendations.py - QA Tests for Grounded Recommendation Generation & Anti-Hallucination.
"""

import pytest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from rag.grounded_recommender import RAGSafetyRecommendationEngine


def test_grounded_recommendation_critical_hydrotest():
    """Verify Scenario A (Hydrotest / pressure incident) generates grounded CRITICAL recommendations."""
    engine = RAGSafetyRecommendationEngine()
    res = engine.generate_recommendations(
        narrative="During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting. The bleeder plug ruptured.",
        sif_result={"probability": 0.88, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR"},
        lsr_result={"triggered_rules": ["Energy Isolation"]}
    )

    assert res["recommendation_status"] == "GROUNDED"
    assert res["grounded"] is True
    assert res["priority"] == "CRITICAL"
    assert len(res["sources"]) > 0
    assert len(res["immediate_actions"]) > 0


def test_minor_slip_negative_control():
    """Verify Scenario D (Minor Slip) receives low/no safety escalation."""
    engine = RAGSafetyRecommendationEngine()
    res = engine.generate_recommendations(
        narrative="Cleaner slipped on recently mopped office hallway and felt mild discomfort.",
        sif_result={"probability": 0.02, "is_sif": False, "risk_tier": "LOW_POTENTIAL_INCIDENT"},
        lsr_result={"triggered_rules": []}
    )

    assert res["priority"] == "LOW"
    assert res["grounded"] is True
    assert "LOW POTENTIAL INCIDENT" in res["summary"]
    assert len(res["immediate_actions"]) <= 2


def test_anti_hallucination_insufficient_support():
    """Verify anti-hallucination rule returns INSUFFICIENT_SOURCE_SUPPORT when confidence threshold fails."""
    engine = RAGSafetyRecommendationEngine()
    # Temporarily set high confidence threshold to simulate no retrieval match
    engine.min_retrieval_confidence = 0.999

    res = engine.generate_recommendations(
        narrative="Unrelated nonsensical input xyz1239999",
        sif_result={"probability": 0.50, "is_sif": False, "risk_tier": "MODERATE_HAZARD"},
        lsr_result={"triggered_rules": []}
    )

    assert res["recommendation_status"] == "INSUFFICIENT_SOURCE_SUPPORT"
    assert res["grounded"] is False
    assert "INSUFFICIENT SOURCE SUPPORT" in res["summary"]
