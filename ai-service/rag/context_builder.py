"""
context_builder.py - Dynamic Safety Context Query Constructor.
Translates raw incident narrative + Stage 6 SIF classification + Stage 7 LSR triggers into a targeted search query.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


class SafetyContextBuilder:
    """
    Constructs safety-domain search queries and context representations from model predictions.
    """

    def build_query(self, narrative: str, sif_result: Dict[str, Any], lsr_result: Dict[str, Any]) -> str:
        """
        Build an enriched search query tailored for safety reference document retrieval.
        """
        narrative_clean = str(narrative).strip() if narrative else ""
        sif_prob = sif_result.get("probability", 0.0)
        risk_tier = sif_result.get("risk_tier", "LOW_POTENTIAL_INCIDENT")
        triggered_rules = lsr_result.get("triggered_rules", [])

        query_parts = []

        # Add risk intensity descriptor
        if risk_tier in ["CRITICAL_SIF_PRECURSOR", "ELEVATED_SIF_POTENTIAL"]:
            query_parts.append("Critical safety controls, immediate isolation, stop work authority, and emergency response for")
        elif risk_tier == "MODERATE_HAZARD":
            query_parts.append("Operational safety verification and Job Safety Analysis controls for")
        else:
            query_parts.append("Standard workplace safety and housekeeping guidance for")

        # Include triggered LSR rule canonical names
        if triggered_rules:
            rules_str = ", ".join(triggered_rules)
            query_parts.append(f"Life-Saving Rules: {rules_str}.")

        # Add key incident narrative words
        query_parts.append(narrative_clean)

        constructed_query = " ".join(query_parts)
        return constructed_query


if __name__ == "__main__":
    builder = SafetyContextBuilder()
    q = builder.build_query(
        narrative="Operator attempted to tighten a fitting while a high-pressure line remained pressurized",
        sif_result={"probability": 0.85, "risk_tier": "CRITICAL_SIF_PRECURSOR"},
        lsr_result={"triggered_rules": ["Energy Isolation", "Bypassing Safety Controls"]}
    )
    print("Constructed Query:\n", q)
