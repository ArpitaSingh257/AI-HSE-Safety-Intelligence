"""
analyze.py - Production AI Inference Endpoint (/api/v1/analyze).
"""

import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.safety_pipeline import SafetyPipeline
from app.schemas import (
    IncidentAnalysisRequest,
    IncidentAnalysisResponse,
    SIFAnalysisResponse,
    LSRAnalysisResponse,
    LSRRulePrediction,
    SalientToken,
    ModelInfo
)

router = APIRouter()

# Global pipeline instance (initialized once at startup)
_pipeline_instance = None

def get_pipeline():
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = SafetyPipeline()
    return _pipeline_instance

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
    description="Accepts an unstructured oilfield incident report narrative and returns calibrated SIF precursor classification, risk tier, multi-label IOGP Life-Saving Rules, and interpretability attention highlights."
)
async def analyze_incident_endpoint(request: IncidentAnalysisRequest):
    narrative_text = request.incident_text
    
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
        
        return IncidentAnalysisResponse(
            incident_id=request.incident_id,
            incident_text=narrative_text,
            sif=sif_response,
            lsr=lsr_response,
            model_info=ModelInfo()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failure: {str(e)}"
        )
