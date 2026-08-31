"""
test_llm_generation_stage17.py - QA Tests for Stage 17 LLM Generation Baseline & Grounding.
"""

import pytest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from rag.grounded_recommender import RAGSafetyRecommendationEngine


def test_llm_generation_hydrotest():
    """Verify Stage 17 LLM generation produces grounded recommendations for Hydrotest scenario."""
    engine = RAGSafetyRecommendationEngine(ollama_model="llama3.2:1b")
    narrative = "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator was exposed to a pressure release after a bleeder plug ruptured."
    sif_result = {"probability": 0.88, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR", "threshold": 0.30}
    lsr_result = {"triggered_rules": ["Energy Isolation", "Bypassing Safety Controls"], "probabilities": {}}

    res = engine.generate_recommendations(narrative, sif_result, lsr_result)

    assert "recommendation_status" in res
    assert res["recommendation_status"] == "GROUNDED"
    assert res["priority"] == "CRITICAL"
    assert "sources" in res
    assert len(res["sources"]) > 0
    assert len(res["immediate_actions"]) > 0


def test_llm_generation_negative_control():
    """Verify Stage 17 negative control does not produce emergency escalation."""
    engine = RAGSafetyRecommendationEngine(ollama_model="llama3.2:1b")
    narrative = "An employee experienced a minor slip while walking on a dry, level office floor. No injury occurred."
    sif_result = {"probability": 0.02, "is_sif": False, "risk_tier": "LOW_POTENTIAL_INCIDENT", "threshold": 0.30}
    lsr_result = {"triggered_rules": [], "probabilities": {}}

    res = engine.generate_recommendations(narrative, sif_result, lsr_result)

    assert res["priority"] == "LOW"
    assert res["grounded"] is True
    assert "LOW POTENTIAL INCIDENT" in res["summary"]
    # Check that high-energy emergency actions like LOTO/evacuate are NOT present
    for act in res.get("immediate_actions", []):
        assert "evacuate" not in act.lower()
        assert "LOTO" not in act
