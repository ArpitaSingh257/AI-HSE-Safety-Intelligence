"""
recommendation_engine.py - Deterministic Safety Recommendation Engine for OILPS.
Combines frozen SIF precursor risk classification & IOGP Life-Saving Rules into structured safety recommendations.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from knowledge.lsr_recommendations_kb import LSR_KNOWLEDGE_BASE

class SafetyRecommendationEngine:
    """Production Safety Recommendation Engine operating on frozen ML inference outputs."""
    def __init__(self):
        self.kb = LSR_KNOWLEDGE_BASE
        
    def generate_recommendations(self, sif_result: Dict[str, Any], lsr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate actionable safety guidance from SIF risk tier and triggered Life-Saving Rules.
        Does NOT modify model probabilities or thresholds.
        """
        sif_prob = sif_result.get("probability", 0.0)
        is_sif = sif_result.get("is_sif", sif_prob >= sif_result.get("threshold", 0.30))
        risk_tier = sif_result.get("risk_tier", "LOW_POTENTIAL_INCIDENT")
        triggered_rules = lsr_result.get("triggered_rules", [])
        
        # 1. Determine Safety Action Priority
        if is_sif or risk_tier == "CRITICAL_SIF_PRECURSOR":
            priority = "CRITICAL"
        elif risk_tier == "ELEVATED_SIF_POTENTIAL" or len(triggered_rules) >= 2:
            priority = "HIGH"
        elif risk_tier == "MODERATE_HAZARD" or len(triggered_rules) == 1:
            priority = "MODERATE"
        else:
            priority = "LOW"
            
        # 2. Build High-Level Narrative Summary
        if priority == "CRITICAL":
            summary = "CRITICAL PRECURSOR EVENT: Immediate high-energy hazard detected. Work in affected area must be placed on hold until critical barriers and energy isolation are physically verified."
        elif priority == "HIGH":
            summary = "ELEVATED SAFETY RISK: Operational hazard with multiple Life-Saving Rules activated. Conduct pre-job barrier verification and supervisor review before resuming work."
        elif priority == "MODERATE":
            summary = "MODERATE HAZARD: Routine operational risk identified. Verify applicable safety controls and communicate hazard during toolbox talk."
        else:
            summary = "LOW POTENTIAL INCIDENT: Minor event with no critical SIF precursor or Life-Saving Rule breach. Apply standard first-aid and routine housekeeping."
            
        immediate_actions = []
        control_verification = []
        escalation_guidance = []
        rule_specific = {}
        
        # 3. Add SIF Risk-Tier Base Guidance
        if is_sif or risk_tier in ["CRITICAL_SIF_PRECURSOR", "ELEVATED_SIF_POTENTIAL"]:
            immediate_actions.append("Initiate immediate 'Stop Work Authority' (SWA) if high-energy operations remain active.")
            control_verification.append("Verify primary and secondary safety barriers for all active energy sources.")
            escalation_guidance.append("Notify Site Superintendent, Safety Officer, and Operations Manager for mandatory SIF review.")
        elif priority == "MODERATE":
            control_verification.append("Verify standard job safety analysis (JSA) controls and personal protective equipment (PPE).")
            
        # 4. Integrate Rule-Specific Actions from Knowledge Base
        for rule in triggered_rules:
            if rule in self.kb:
                entry = self.kb[rule]
                rule_specific[rule] = {
                    "immediate_actions": entry["immediate_actions"],
                    "recommended_controls": entry["recommended_controls"],
                    "verification_actions": entry["verification_actions"],
                    "escalation_guidance": entry["escalation_guidance"]
                }
                immediate_actions.extend(entry["immediate_actions"])
                control_verification.extend(entry["verification_actions"])
                if entry["escalation_guidance"] not in escalation_guidance:
                    escalation_guidance.append(entry["escalation_guidance"])
                    
        # Remove duplicates while preserving order
        def deduplicate(seq):
            seen = set()
            return [x for x in seq if not (x in seen or seen.add(x))]
            
        return {
            "priority": priority,
            "summary": summary,
            "immediate_actions": deduplicate(immediate_actions),
            "control_verification": deduplicate(control_verification),
            "escalation": deduplicate(escalation_guidance),
            "rule_specific_guidance": rule_specific,
            "disclaimer": "Recommendations are generated as decision-support guidance from detected IOGP Life-Saving Rules and SIF precursor risk tiers. They do not replace site-specific operating procedures or competent HSE professional review."
        }
