"""
test_grounding_validator_stage20.py - Automated QA Test Suite for Stage 20 Grounding & Hallucination Guard.
"""

import pytest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.grounding_validator import GroundingValidator
from rag.grounded_recommender import RAGSafetyRecommendationEngine


@pytest.fixture
def validator():
    return GroundingValidator()


@pytest.fixture
def passages():
    return [
        {
            "document": "IOGP Life-Saving Rules.pdf",
            "page": 12,
            "section": "Energy Isolation",
            "chunk_id": "c1",
            "text": "Verify isolation and zero energy state before work begins on pressure systems. Test for trapped pressure before loosening fittings or bleeder plugs."
        },
        {
            "document": "Process Safety Fundamentals.pdf",
            "page": 8,
            "section": "Line of Fire",
            "chunk_id": "c2",
            "text": "Do not stand in the line of fire of pressurized equipment, bleeder valves, or flange bolts."
        }
    ]


def test_supported_recommendation_accepted(validator, passages):
    """Test 1: Supported recommendation is accepted and validated as SUPPORTED."""
    res = validator.validate_single_recommendation("Test for trapped pressure before loosening bleeder plugs.", passages)
    assert res.status == "SUPPORTED"
    assert res.grounding_score >= 0.40
    assert res.supporting_document == "IOGP Life-Saving Rules.pdf"


def test_unsupported_recommendation_rejected(validator, passages):
    """Test 2: Unsupported hallucinated recommendation (e.g. aviation fuel) is rejected as UNSUPPORTED."""
    res = validator.validate_single_recommendation("Verify aviation fuel quality and helideck net integrity.", passages)
    assert res.status == "UNSUPPORTED"
    assert res.grounding_score < 0.25


def test_mixed_recommendations_filtering(validator, passages):
    """Test 3: Mixed supported & unsupported recommendations filter out unsupported items."""
    payload = {
        "immediate_actions": [
            "Test for trapped pressure before loosening bleeder plugs.",
            "Verify aviation fuel quality and aircraft landing clearance." # UNSUPPORTED
        ],
        "verification_actions": [
            "Confirm zero energy state on pressure systems."
        ]
    }
    filtered = validator.validate_and_filter(payload, passages)

    assert len(filtered["immediate_actions"]) == 1
    assert "aviation fuel" not in filtered["immediate_actions"][0]
    assert filtered["grounding_audit"]["unsupported_count"] == 1
    assert filtered["grounding_audit"]["removed_count"] == 1


def test_empty_evidence_handling(validator):
    """Test 4: Empty evidence returns NO_EVIDENCE status safely."""
    payload = {"immediate_actions": ["Isolate energy sources."]}
    filtered = validator.validate_and_filter(payload, [])

    assert filtered["recommendation_status"] == "NO_EVIDENCE"


def test_duplicate_evidence_handling(validator, passages):
    """Test 5: Duplicate passages do not distort validation score or crash validator."""
    dup_passages = passages + passages
    res = validator.validate_single_recommendation("Confirm zero energy state on pressure systems.", dup_passages)
    assert res.status in ["SUPPORTED", "PARTIALLY_SUPPORTED"]


def test_deterministic_validation(validator, passages):
    """Test 6: Validation is 100% deterministic across multiple runs."""
    rec = "Do not stand in the line of fire of pressurized equipment."
    res1 = validator.validate_single_recommendation(rec, passages)
    res2 = validator.validate_single_recommendation(rec, passages)

    assert res1.status == res2.status
    assert res1.grounding_score == res2.grounding_score


def test_hydrotest_regression():
    """Test 7: Hydrotest scenario regression — verify status and grounding audit tracking."""
    engine = RAGSafetyRecommendationEngine(ollama_model="llama3.2:1b")
    narrative = "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator was exposed to a pressure release after a bleeder plug ruptured."
    sif = {"probability": 0.88, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR", "threshold": 0.30}
    lsr = {"triggered_rules": ["Energy Isolation"], "probabilities": {}}

    res = engine.generate_recommendations(narrative, sif, lsr)
    assert res["recommendation_status"] in ["GROUNDED", "PARTIALLY_GROUNDED"]
    assert "grounding_audit" in res
    assert res["grounding_audit"]["supported_count"] >= 1


def test_crane_regression():
    """Test 8: Crane scenario regression — evidence-supported recommendations."""
    engine = RAGSafetyRecommendationEngine(ollama_model="llama3.2:1b")
    narrative = "During a crane lifting operation, a suspended load shifted unexpectedly and entered the line of fire of personnel working nearby."
    sif = {"probability": 0.76, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR", "threshold": 0.30}
    lsr = {"triggered_rules": ["Safe Mechanical Lifting", "Line of Fire"], "probabilities": {}}

    res = engine.generate_recommendations(narrative, sif, lsr)
    assert res["recommendation_status"] in ["GROUNDED", "PARTIALLY_GROUNDED"]
    assert "grounding_audit" in res
    assert res["grounding_audit"]["supported_count"] >= 1


def test_confined_space_h2s_regression():
    """Test 9: Confined Space + H2S scenario regression."""
    engine = RAGSafetyRecommendationEngine(ollama_model="llama3.2:1b")
    narrative = "During vessel entry preparation, an operator was exposed to a potential H2S atmosphere inside a confined space."
    sif = {"probability": 0.92, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR", "threshold": 0.30}
    lsr = {"triggered_rules": ["Confined Space", "Toxic Gas / Hazardous Substance"], "probabilities": {}}

    res = engine.generate_recommendations(narrative, sif, lsr)
    assert res["recommendation_status"] in ["GROUNDED", "PARTIALLY_GROUNDED", "UNSUPPORTED"]
    assert "grounding_audit" in res


def test_minor_slip_negative_control_regression():
    """Test 10: Minor Slip negative control regression — zero false-positive emergency instructions."""
    engine = RAGSafetyRecommendationEngine(ollama_model="llama3.2:1b")
    narrative = "An employee experienced a minor slip while walking on a dry, level office floor."
    sif = {"probability": 0.02, "is_sif": False, "risk_tier": "LOW_POTENTIAL_INCIDENT", "threshold": 0.30}
    lsr = {"triggered_rules": [], "probabilities": {}}

    res = engine.generate_recommendations(narrative, sif, lsr)
    assert res["priority"] == "LOW"
    assert "grounding_audit" in res
    assert res["grounding_audit"]["unsupported_count"] == 0
