"""
test_explainable_output_stage19.py - Stage 19 Explainable Safety Intelligence Output Demo Script.
Executes all 4 safety scenarios and prints user-facing explainable outputs.
"""

import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.safety_pipeline import SafetyPipeline
from inference.recommendation_engine import SafetyRecommendationEngine
from inference.explainability import SafetyIntelligenceFormatter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Stage19Demo")

SCENARIOS = {
    "Scenario_1_Hydrotest": {
        "name": "Scenario 1 — Hydrotest / Pressure",
        "narrative": "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator was exposed to a pressure release after a bleeder plug ruptured."
    },
    "Scenario_2_Crane_Lifting": {
        "name": "Scenario 2 — Crane / Lifting",
        "narrative": "During a crane lifting operation, a suspended load shifted unexpectedly and entered the line of fire of personnel working nearby."
    },
    "Scenario_3_Confined_Space_H2S": {
        "name": "Scenario 3 — Confined Space + H2S",
        "narrative": "During vessel entry preparation, an operator was exposed to a potential H2S atmosphere inside a confined space."
    },
    "Scenario_4_Minor_Slip": {
        "name": "Scenario 4 — Minor Slip Negative Control",
        "narrative": "An employee experienced a minor slip while walking on a dry, level office floor. No injury occurred and no hazardous energy or process safety condition was involved."
    }
}


def run_stage19_demo():
    pipeline = SafetyPipeline()
    rec_engine = SafetyRecommendationEngine()
    formatter = SafetyIntelligenceFormatter()

    print("\n" + "="*80)
    print("STAGE 19 — EXPLAINABLE SAFETY INTELLIGENCE OUTPUT DEMO")
    print("="*80)

    for key, sc in SCENARIOS.items():
        narrative = sc["narrative"]
        print(f"\n\n>>> EVALUATING: {sc['name']}")
        print(f"Incident: \"{narrative}\"\n")

        raw_res = pipeline.analyze_incident(narrative)
        sif_data = raw_res["sif"]
        lsr_data = raw_res["life_saving_rules"]
        risk_tier = raw_res["risk_tier"]

        rec_data = rec_engine.generate_recommendations(
            sif_result={"probability": sif_data["probability"], "is_sif": bool(sif_data["label"] == 1), "risk_tier": risk_tier, "threshold": sif_data["threshold"]},
            lsr_result={"triggered_rules": lsr_data.get("predicted_rules", []), "probabilities": lsr_data["probabilities"]},
            narrative=narrative
        )

        sif_payload = {
            "probability": sif_data["probability"],
            "risk_tier": risk_tier,
            "salient_tokens": sif_data.get("salient_tokens", [])
        }
        lsr_payload = {
            "triggered_rules": lsr_data.get("predicted_rules", []),
            "rule_predictions": [
                {"rule": r, "probability": lsr_data["probabilities"].get(r, 0.0)}
                for r in lsr_data.get("predicted_rules", [])
            ]
        }

        exp_res = formatter.format_output(narrative, sif_payload, lsr_payload, rec_data)

        # Print user-facing text layout
        print(exp_res["formatted_text"])


if __name__ == "__main__":
    run_stage19_demo()
