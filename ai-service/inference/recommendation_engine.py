"""
recommendation_engine.py - Production RAG-Based Safety Recommendation Engine for OILPS.
Combines Stage 6 SIF risk classification & Stage 7 IOGP Life-Saving Rules with RAG document retrieval.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from rag.grounded_recommender import RAGSafetyRecommendationEngine
from knowledge.lsr_recommendations_kb import LSR_KNOWLEDGE_BASE

logger = logging.getLogger("OILPS_RecommendationEngine")


class SafetyRecommendationEngine:
    """Production RAG Safety Recommendation Engine operating on frozen ML inference outputs."""

    def __init__(self):
        self.rag_engine = RAGSafetyRecommendationEngine()
        self.kb = LSR_KNOWLEDGE_BASE

    def generate_recommendations(
        self,
        sif_result: Dict[str, Any],
        lsr_result: Dict[str, Any],
        narrative: str = ""
    ) -> Dict[str, Any]:
        """
        Generate actionable, source-grounded safety guidance from SIF risk tier,
        triggered Life-Saving Rules, and retrieved PDF passages.
        """
        try:
            # Generate RAG recommendations
            rec_result = self.rag_engine.generate_recommendations(
                narrative=narrative,
                sif_result=sif_result,
                lsr_result=lsr_result
            )

            # Integrate rule-specific guidance mapping for UI backward compatibility
            triggered_rules = lsr_result.get("triggered_rules", [])
            rule_specific = {}
            for rule in triggered_rules:
                if rule in self.kb:
                    entry = self.kb[rule]
                    rule_specific[rule] = {
                        "immediate_actions": entry["immediate_actions"],
                        "recommended_controls": entry["recommended_controls"],
                        "verification_actions": entry["verification_actions"],
                        "escalation_guidance": entry["escalation_guidance"]
                    }
            rec_result["rule_specific_guidance"] = rule_specific

            return rec_result

        except Exception as e:
            logger.warning(f"RAG recommendation generation error: {e}. Utilizing fallback guidance.")
            # Deterministic fallback if RAG execution hits an error
            sif_prob = sif_result.get("probability", 0.0)
            is_sif = sif_result.get("is_sif", sif_prob >= sif_result.get("threshold", 0.30))
            risk_tier = sif_result.get("risk_tier", "LOW_POTENTIAL_INCIDENT")
            triggered_rules = lsr_result.get("triggered_rules", [])

            priority = "CRITICAL" if is_sif else "MODERATE"
            return {
                "grounded": False,
                "recommendation_status": "FALLBACK",
                "priority": priority,
                "summary": "SYSTEM NOTICE: Standard fallback safety guidance applied.",
                "immediate_actions": ["Verify energy isolation before intervention."],
                "verification_actions": ["Verify job safety analysis controls."],
                "control_verification": ["Verify job safety analysis controls."],
                "escalation_actions": ["Notify HSE supervisor."],
                "escalation": ["Notify HSE supervisor."],
                "preventive_actions": ["Maintain standard work area safety."],
                "sources": [],
                "rule_specific_guidance": {},
                "disclaimer": "Fallback guidance generated."
            }
