"""
analyze.py - Production AI Inference Endpoint (/api/v1/analyze).
"""

import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.safety_pipeline import SafetyPipeline
from inference.recommendation_engine import SafetyRecommendationEngine
from app.schemas import (
    IncidentAnalysisRequest,
    IncidentAnalysisResponse,
    SIFAnalysisResponse,
    LSRAnalysisResponse,
    LSRRulePrediction,
    SalientToken,
    SafetyRecommendationsResponse,
    ModelInfo
)

router = APIRouter()

# Global instances (initialized once at startup)
_pipeline_instance = None
_rec_engine_instance = None

def get_pipeline():
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = SafetyPipeline()
    return _pipeline_instance

def get_rec_engine():
    global _rec_engine_instance
    if _rec_engine_instance is None:
        _rec_engine_instance = SafetyRecommendationEngine()
    return _rec_engine_instance

OFFICIAL_9_LSR = [
    "Bypassing Safety Controls",
    "Confined Space",
    "Driving",
    "Energy Isolation",
    "Hot Work",
    "Line of Fire",
    "Safe Mechanical Lifting",
    "Toxic Gas / Hazardous Substance",
    "Working at Height"
]

@router.post(
    "/analyze",
    response_model=IncidentAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Incident Narrative for SIF Precursor Risk & Life-Saving Rules",
    description="Accepts an unstructured oilfield incident report narrative and returns calibrated SIF precursor classification, risk tier, multi-label IOGP Life-Saving Rules, and actionable safety recommendations."
)
async def analyze_incident_endpoint(request: IncidentAnalysisRequest):
    narrative_text = request.incident_text
    rec_engine = get_rec_engine()
    
    if not isinstance(narrative_text, str) or not narrative_text.strip():
        # Safe handling of empty or whitespace input
        return IncidentAnalysisResponse(
            incident_id=request.incident_id,
            incident_text="",
            sif=SIFAnalysisResponse(
                probability=0.0,
                threshold=0.30,
                is_sif=False,
                risk_tier="LOW_POTENTIAL_INCIDENT",
                salient_tokens=[]
            ),
            lsr=LSRAnalysisResponse(
                triggered_rules=[],
                rule_predictions=[
                    LSRRulePrediction(rule=r, probability=0.0, threshold=0.50, triggered=False)
                    for r in OFFICIAL_9_LSR
                ],
                salient_tokens=[]
            ),
            recommendations=SafetyRecommendationsResponse(
                priority="LOW",
                summary="LOW POTENTIAL INCIDENT: Minor event with no critical SIF precursor or Life-Saving Rule breach. Apply standard first-aid and routine housekeeping.",
                immediate_actions=[],
                control_verification=[],
                escalation=[],
                rule_specific_guidance={}
            ),
            model_info=ModelInfo()
        )
        
    try:
        pipeline = get_pipeline()
        raw_result = pipeline.analyze_incident(narrative_text)
        
        # Parse SIF payload
        sif_raw = raw_result["sif"]
        sif_salient = [
            SalientToken(token=t["token"], weight=t["weight"])
            for t in sif_raw.get("salient_tokens", [])
        ]
        sif_response = SIFAnalysisResponse(
            probability=sif_raw["probability"],
            threshold=sif_raw["threshold"],
            is_sif=bool(sif_raw["label"] == 1),
            risk_tier=raw_result["risk_tier"],
            salient_tokens=sif_salient
        )
        
        # Parse LSR payload
        lsr_raw = raw_result["life_saving_rules"]
        rule_predictions = []
        for r_name in OFFICIAL_9_LSR:
            p = lsr_raw["probabilities"].get(r_name, 0.0)
            t = lsr_raw["thresholds"].get(r_name, 0.50)
            is_trig = bool(p >= t)
            rule_predictions.append(
                LSRRulePrediction(
                    rule=r_name,
                    probability=p,
                    threshold=t,
                    triggered=is_trig
                )
            )
            
        lsr_salient = [
            SalientToken(token=t["token"], weight=t["weight"])
            for t in lsr_raw.get("salient_tokens", [])
        ]
        lsr_response = LSRAnalysisResponse(
            triggered_rules=lsr_raw.get("predicted_rules", []),
            rule_predictions=rule_predictions,
            salient_tokens=lsr_salient
        )
        
        # Generate Deterministic Recommendations
        rec_data = rec_engine.generate_recommendations(
            sif_result={"probability": sif_raw["probability"], "is_sif": bool(sif_raw["label"] == 1), "risk_tier": raw_result["risk_tier"], "threshold": sif_raw["threshold"]},
            lsr_result={"triggered_rules": lsr_raw.get("predicted_rules", []), "probabilities": lsr_raw["probabilities"]}
        )
        
        rec_response = SafetyRecommendationsResponse(
            priority=rec_data["priority"],
            summary=rec_data["summary"],
            immediate_actions=rec_data["immediate_actions"],
            control_verification=rec_data["control_verification"],
            escalation=rec_data["escalation"],
            rule_specific_guidance=rec_data["rule_specific_guidance"],
            disclaimer=rec_data["disclaimer"]
        )
        
        return IncidentAnalysisResponse(
            incident_id=request.incident_id,
            incident_text=narrative_text,
            sif=sif_response,
            lsr=lsr_response,
            recommendations=rec_response,
            model_info=ModelInfo()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failure: {str(e)}"
        )
