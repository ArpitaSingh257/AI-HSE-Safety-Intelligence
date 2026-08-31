"""
explainability.py - Stage 19 Explainable Safety Intelligence Output Subsystem for OILPS.
Transforms technical AI/ML model inferences and RAG citations into intuitive, human-understandable safety responses.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class LSRExplanation(BaseModel):
    rule: str = Field(..., description="Official IOGP Life-Saving Rule canonical name.")
    model_probability: str = Field(..., description="Model probability expressed as percentage, e.g. '82.4%'")
    why_triggered: str = Field(..., description="Non-technical explanation of why this rule was activated.")


class ExplainableSafetyOutput(BaseModel):
    risk_level_display: str = Field(..., description="User-facing categorical risk indicator: 🔴 CRITICAL, 🟠 HIGH, 🟡 MODERATE, or 🟢 LOW.")
    sif_interpretation: str = Field(..., description="Clear explanation of SIF precursor potential without converting probability to certainty.")
    why_flagged: List[str] = Field(default_factory=list, description="Bullet points explaining key hazard factors and energy mechanisms.")
    lsr_explanations: List[LSRExplanation] = Field(default_factory=list, description="User-friendly breakdown of each activated Life-Saving Rule.")
    grounding_banner: str = Field(..., description="Clear status badge indicating if recommendations are grounded in reference PDFs.")
    formatted_text: str = Field(..., description="Clean ASCII/terminal formatted response layout for human readability.")


class SafetyIntelligenceFormatter:
    """Formatter that translates raw AI predictions & RAG citations into Explainable Safety Intelligence Output."""

    def format_output(
        self,
        narrative: str,
        sif_data: Dict[str, Any],
        lsr_data: Dict[str, Any],
        rec_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        sif_prob = sif_data.get("probability", 0.0)
        risk_tier = sif_data.get("risk_tier", "LOW_POTENTIAL_INCIDENT")
        triggered_rules = lsr_data.get("triggered_rules", [])
        rule_probs = lsr_data.get("rule_predictions", [])
        priority = rec_data.get("priority", "LOW")
        grounded = rec_data.get("grounded", True)
        status = rec_data.get("status", "GROUNDED")

        # 1. Determine Risk Display Badge
        if priority == "CRITICAL" or risk_tier == "CRITICAL_SIF_PRECURSOR":
            risk_display = "🔴 CRITICAL"
        elif priority == "HIGH" or risk_tier == "ELEVATED_SIF_POTENTIAL":
            risk_display = "🟠 HIGH"
        elif priority == "MODERATE" or risk_tier == "MODERATE_HAZARD":
            risk_display = "🟡 MODERATE"
        else:
            risk_display = "🟢 LOW"

        # 2. Construct SIF Interpretation
        if sif_prob >= 0.30 or risk_tier in ["CRITICAL_SIF_PRECURSOR", "ELEVATED_SIF_POTENTIAL"]:
            sif_interp = f"Model probability: {sif_prob * 100:.2f}%. The incident narrative contains operational characteristics associated with a potential Serious Injury or Fatality (SIF) precursor event."
        else:
            sif_interp = f"Model probability: {sif_prob * 100:.2f}%. No significant SIF precursor potential detected."

        # 3. Build 'Why Was This Flagged?' Explanations
        why_flagged = []
        salient_tokens = sif_data.get("salient_tokens", [])
        if salient_tokens:
            top_words = [t["token"] if isinstance(t, dict) else getattr(t, "token", str(t)) for t in salient_tokens[:4]]
            why_flagged.append(f"Key energy & hazard indicators detected: {', '.join(top_words)}.")

        if triggered_rules:
            why_flagged.append(f"Incident activity activated {len(triggered_rules)} IOGP Life-Saving Rule(s): {', '.join(triggered_rules)}.")

        if rec_data.get("sources"):
            sources_count = len(rec_data.get("sources", []))
            why_flagged.append(f"Matched {sources_count} authoritative reference passage(s) in approved safety PDFs.")

        if not why_flagged:
            why_flagged.append("Standard routine event with minor workplace hazard conditions.")

        # 4. Build LSR Explanations
        lsr_explanations = []
        for rule_name in triggered_rules:
            prob_val = 0.0
            for r_pred in rule_probs:
                r_name = r_pred.get("rule") if isinstance(r_pred, dict) else getattr(r_pred, "rule", "")
                if r_name == rule_name:
                    prob_val = r_pred.get("probability", 0.0) if isinstance(r_pred, dict) else getattr(r_pred, "probability", 0.0)
                    break

            rule_why = f"The incident narrative describes operational conditions and barrier requirements associated with {rule_name}."
            lsr_explanations.append({
                "rule": rule_name,
                "model_probability": f"{prob_val * 100:.1f}%",
                "why_triggered": rule_why
            })

        # 5. Grounding Status Banner
        if grounded and status == "GROUNDED":
            grounding_banner = "✓ GROUNDED — Recommendations are directly supported by retrieved safety-resource evidence."
        elif status == "INSUFFICIENT_SOURCE_SUPPORT":
            grounding_banner = "⚠ INSUFFICIENT EVIDENCE — The system could not retrieve sufficient source evidence to support specific recommendations."
        else:
            grounding_banner = "ℹ ROUTINE GUIDANCE — Standard low-risk workplace housekeeping guidelines apply."

        # 6. Format ASCII User-Facing Text Layout
        lines = []
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("                     SAFETY INTELLIGENCE RESULT                            ")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"RISK LEVEL: {risk_display}")
        lines.append(f"SIF POTENTIAL: {sif_interp}")
        lines.append("")
        lines.append("WHY WAS THIS FLAGGED?")
        for item in why_flagged:
            lines.append(f" • {item}")
        lines.append("")
        if lsr_explanations:
            lines.append("LIFE-SAVING RULES ACTIVATED:")
            for l_exp in lsr_explanations:
                lines.append(f" ✓ {l_exp['rule']} (Model Probability: {l_exp['model_probability']})")
                lines.append(f"   Reason: {l_exp['why_triggered']}")
        else:
            lines.append("LIFE-SAVING RULES: None activated.")
        lines.append("")
        imm_actions = rec_data.get("immediate_actions", [])
        if imm_actions:
            lines.append("IMMEDIATE ACTIONS:")
            for idx, act in enumerate(imm_actions, 1):
                lines.append(f" {idx}. {act}")
            lines.append("")

        ver_actions = rec_data.get("verification_actions", rec_data.get("control_verification", []))
        if ver_actions:
            lines.append("VERIFY BEFORE RESUMING:")
            for act in ver_actions:
                lines.append(f" ✓ {act}")
            lines.append("")

        esc_actions = rec_data.get("escalation_actions", rec_data.get("escalation", []))
        if esc_actions:
            lines.append("ESCALATION PROTOCOL:")
            for act in esc_actions:
                lines.append(f" • {act}")
            lines.append("")

        lines.append("EVIDENCE SOURCES:")
        sources = rec_data.get("sources", [])
        if sources:
            for s in sources:
                doc_name = s.get("document", "Unknown") if isinstance(s, dict) else getattr(s, "document", "Unknown")
                p_num = s.get("page", 0) if isinstance(s, dict) else getattr(s, "page", 0)
                sec_name = s.get("section", "General") if isinstance(s, dict) else getattr(s, "section", "General")
                lines.append(f" 📄 {doc_name} (Page: {p_num}, Section: {sec_name})")
        else:
            lines.append(" None attached.")

        lines.append("")
        lines.append(f"GROUNDING STATUS: {grounding_banner}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("IMPORTANT: This AI system provides decision-support guidance. It does not replace")
        lines.append("site operating procedures, competent person review, or emergency requirements.")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        formatted_text = "\n".join(lines)

        return {
            "risk_level_display": risk_display,
            "sif_interpretation": sif_interp,
            "why_flagged": why_flagged,
            "lsr_explanations": lsr_explanations,
            "grounding_banner": grounding_banner,
            "formatted_text": formatted_text
        }
