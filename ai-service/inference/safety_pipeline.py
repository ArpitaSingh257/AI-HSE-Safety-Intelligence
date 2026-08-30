"""
safety_pipeline.py - Production AI Safety Intelligence Pipeline.
Combines SIF Binary Classification & Multi-Label Life-Saving Rules into a single unified analysis endpoint.
"""

from pathlib import Path
from .sif_predictor import SIFPredictor
from .lsr_predictor import LSRPredictor

class SafetyPipeline:
    """Unified Production Pipeline for Precursor Safety Analysis."""
    def __init__(self, sif_model_dir: str = None, lsr_model_dir: str = None, device: str = None):
        self.sif_predictor = SIFPredictor(model_dir=sif_model_dir, device=device)
        self.lsr_predictor = LSRPredictor(model_dir=lsr_model_dir, device=device)
        
    def analyze_incident(self, narrative: str) -> dict:
        """
        Analyze an incident narrative to produce SIF precursor detection,
        associated IOGP Life-Saving Rules, and attention interpretability highlights.
        """
        narrative_clean = str(narrative).strip() if narrative is not None else ""
        
        sif_result = self.sif_predictor.predict(narrative_clean)
        lsr_result = self.lsr_predictor.predict(narrative_clean)
        
        # Determine risk tier based on SIF probability and rule triggers
        prob = sif_result["sif_probability"]
        if prob >= 0.70:
            risk_tier = "CRITICAL_SIF_PRECURSOR"
        elif prob >= sif_result["threshold"]:
            risk_tier = "ELEVATED_SIF_POTENTIAL"
        elif prob >= 0.15:
            risk_tier = "MODERATE_HAZARD"
        else:
            risk_tier = "LOW_POTENTIAL_INCIDENT"
            
        return {
            "narrative": narrative_clean,
            "risk_tier": risk_tier,
            "sif": {
                "label": sif_result["sif_label"],
                "probability": sif_result["sif_probability"],
                "threshold": sif_result["threshold"],
                "model": sif_result["model"],
                "salient_tokens": sif_result["top_attended_tokens"]
            },
            "life_saving_rules": {
                "predicted_rules": lsr_result["predicted_rules"],
                "probabilities": lsr_result["rule_probabilities"],
                "thresholds": lsr_result["rule_thresholds"],
                "salient_tokens": lsr_result["top_attended_tokens"]
            }
        }
