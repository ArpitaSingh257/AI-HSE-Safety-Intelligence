"""
evaluate_stage20_grounding.py - Stage 20 Grounding & Hallucination Guard Benchmark Script.
Evaluates recommendation grounding, hallucination removal, and Confined Space + H2S investigation.
"""

import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.grounding_validator import GroundingValidator
from rag.grounded_recommender import RAGSafetyRecommendationEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Stage20Benchmark")


def run_hallucination_rejection_demo():
    logger.info("=== DEMONSTRATING HALLUCINATION REJECTION (Aviation Fuel Test) ===")
    validator = GroundingValidator()

    dirty_payload = {
        "immediate_actions": [
            "Initiate immediate Stop Work Authority and depressurize pressure line.",
            "Verify aviation fuel quality and aircraft helideck clearance." # HALLUCINATED ITEM
        ],
        "verification_actions": [
            "Test for trapped pressure before loosening bleeder plug."
        ]
    }
    passages = [
        {
            "document": "IOGP Life-Saving Rules.pdf",
            "page": 12,
            "section": "Energy Isolation",
            "chunk_id": "iogp_p12_c01",
            "text": "Verify isolation and zero energy state before work begins on pressure systems. Test for trapped pressure before loosening fittings or bleeder plugs."
        }
    ]

    filtered = validator.validate_and_filter(dirty_payload, passages)
    audit = filtered["grounding_audit"]

    print("\nBEFORE FILTERING (Immediate Actions):")
    for a in dirty_payload["immediate_actions"]:
        print(f" - {a}")

    print("\nAFTER STAGE 20 GROUNDING VALIDATOR:")
    for a in filtered["immediate_actions"]:
        print(f" - {a}")

    print("\nREMOVED UNSUPPORTED HALLUCINATIONS:")
    for r in audit["removed_recommendations"]:
        print(f" ❌ REMOVED: '{r}'")

    print(f"\nGrounding Rate: {audit['grounding_rate']*100:.1f}% | Unsupported Rate: {audit['unsupported_rate']*100:.1f}%\n")


def run_four_scenarios_evaluation():
    logger.info("=== STAGE 20 FOUR SCENARIOS EVALUATION ===")
    engine = RAGSafetyRecommendationEngine(ollama_model="llama3.2:1b")

    scenarios = {
        "Scenario 1 — Hydrotest": {
            "narrative": "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator was exposed to a pressure release after a bleeder plug ruptured.",
            "sif": {"probability": 0.88, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR", "threshold": 0.30},
            "lsr": {"triggered_rules": ["Energy Isolation"], "probabilities": {}}
        },
        "Scenario 2 — Crane / Lifting": {
            "narrative": "During a crane lifting operation, a suspended load shifted unexpectedly and entered the line of fire of personnel working nearby.",
            "sif": {"probability": 0.76, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR", "threshold": 0.30},
            "lsr": {"triggered_rules": ["Safe Mechanical Lifting", "Line of Fire"], "probabilities": {}}
        },
        "Scenario 3 — Confined Space + H2S": {
            "narrative": "During vessel entry preparation, an operator was exposed to a potential H2S atmosphere inside a confined space.",
            "sif": {"probability": 0.92, "is_sif": True, "risk_tier": "CRITICAL_SIF_PRECURSOR", "threshold": 0.30},
            "lsr": {"triggered_rules": ["Confined Space", "Toxic Gas / Hazardous Substance"], "probabilities": {}}
        },
        "Scenario 4 — Minor Slip Negative Control": {
            "narrative": "An employee experienced a minor slip while walking on a dry, level office floor.",
            "sif": {"probability": 0.02, "is_sif": False, "risk_tier": "LOW_POTENTIAL_INCIDENT", "threshold": 0.30},
            "lsr": {"triggered_rules": [], "probabilities": {}}
        }
    }

    for name, data in scenarios.items():
        res = engine.generate_recommendations(data["narrative"], data["sif"], data["lsr"])
        audit = res.get("grounding_audit", {})
        print(f"[{name}] Status: {res['recommendation_status']} | Priority: {res['priority']} | Grounded: {audit.get('grounding_rate', 1.0)*100:.1f}% | Removed: {audit.get('removed_count', 0)}")


if __name__ == "__main__":
    run_hallucination_rejection_demo()
    run_four_scenarios_evaluation()
