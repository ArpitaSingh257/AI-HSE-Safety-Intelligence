"""
activity_risk.py - FastAPI Endpoint Router for Stage 27 Activity-Level Risk Intelligence (/api/v1/activity-risk).
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.activity_risk_analyzer import ActivityRiskAnalyzer
from app.schemas import ActivityRiskListResponse, ActivityRiskProfileSchema

router = APIRouter()

# Global analyzer instance (singleton)
_analyzer_instance: Optional[ActivityRiskAnalyzer] = None

def get_activity_analyzer(min_reports: int = 3) -> ActivityRiskAnalyzer:
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ActivityRiskAnalyzer(min_activity_reports=min_reports)
    return _analyzer_instance


@router.get(
    "",
    response_model=ActivityRiskListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Ranked Activity Risk Intelligence Profiles",
    description="Returns a volume-normalized, ranked list of activity risk profiles across operational tasks."
)
def get_activity_risk_profiles(
    min_reports: int = Query(default=3, ge=1, description="Minimum reports required for full risk classification."),
    risk_level: Optional[str] = Query(default=None, description="Optional filter by risk_level (CRITICAL, HIGH, MEDIUM, LOW, INSUFFICIENT_DATA).")
):
    analyzer = get_activity_analyzer(min_reports=min_reports)
    profiles = analyzer.calculate_activity_risk_profiles()

    if risk_level:
        profiles = [p for p in profiles if p["risk_level"].upper() == risk_level.upper()]

    return ActivityRiskListResponse(
        total_activities=len(profiles),
        min_activity_reports_threshold=min_reports,
        activity_profiles=profiles
    )


@router.get(
    "/{activity_id}",
    response_model=ActivityRiskProfileSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Single Activity Risk Detail Profile",
    description="Returns detailed safety risk profile, top hazards, barrier failures, LSR rules, and associated sites for an activity."
)
def get_activity_risk_profile_by_id(activity_id: str):
    analyzer = get_activity_analyzer()
    profiles = analyzer.calculate_activity_risk_profiles()

    for p in profiles:
        if p["activity_id"].upper() == activity_id.upper() or p["activity_name"].lower() == activity_id.lower():
            return p

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Activity risk profile for '{activity_id}' not found."
    )
