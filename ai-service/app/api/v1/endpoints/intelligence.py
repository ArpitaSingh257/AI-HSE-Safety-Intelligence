"""
intelligence.py - Stage 43 End-to-End Intelligence API Router (POST /api/v1/intelligence/analyze).
"""

import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Depends

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.schemas import (
    IntelligenceAnalysisRequest,
    IntelligenceAnalysisResponse
)
from services.intelligence_service import IntelligenceService

router = APIRouter()

# Global singleton service instance
_intelligence_service_instance = None


def get_intelligence_service() -> IntelligenceService:
    global _intelligence_service_instance
    if _intelligence_service_instance is None:
        _intelligence_service_instance = IntelligenceService()
    return _intelligence_service_instance


@router.post(
    "/analyze",
    response_model=IntelligenceAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="End-to-End Safety Intelligence & Risk Analysis",
    description="Analyzes workplace safety incidents, providing SIF potential classification, IOGP Life-Saving Rules mapping, historical similarity, site/activity risk analytics using oilps_final_master_v2.csv, Bow-Tie mapping, RAG recommendations, and explainable triage."
)
def analyze_intelligence(
    request: IntelligenceAnalysisRequest,
    service: IntelligenceService = Depends(get_intelligence_service)
) -> IntelligenceAnalysisResponse:
    try:
        res = service.analyze_incident(
            incident_text=request.incident_text,
            site=request.site,
            activity=request.activity,
            incident_id=request.incident_id
        )
        return IntelligenceAnalysisResponse(**res)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intelligence Analysis Error: {str(e)}"
        )
