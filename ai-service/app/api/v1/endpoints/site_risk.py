"""
site_risk.py - FastAPI Endpoint Router for Stage 26 Site-Level Risk Intelligence (/api/v1/site-risk).
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.site_risk_analyzer import SiteRiskAnalyzer
from app.schemas import SiteRiskListResponse, SiteRiskProfileSchema

router = APIRouter()

# Global analyzer instance (singleton)
_analyzer_instance: Optional[SiteRiskAnalyzer] = None

def get_site_analyzer(min_reports: int = 3) -> SiteRiskAnalyzer:
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = SiteRiskAnalyzer(min_site_reports=min_reports)
    return _analyzer_instance


@router.get(
    "",
    response_model=SiteRiskListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Ranked Site Risk Intelligence Profiles",
    description="Returns a volume-normalized, ranked list of site risk profiles across operational facilities."
)
def get_site_risk_profiles(
    min_reports: int = Query(default=3, ge=1, description="Minimum reports required for full risk classification."),
    risk_level: Optional[str] = Query(default=None, description="Optional filter by risk_level (CRITICAL, HIGH, MEDIUM, LOW, INSUFFICIENT_DATA).")
):
    analyzer = get_site_analyzer(min_reports=min_reports)
    profiles = analyzer.calculate_site_risk_profiles()

    if risk_level:
        profiles = [p for p in profiles if p["risk_level"].upper() == risk_level.upper()]

    return SiteRiskListResponse(
        total_sites=len(profiles),
        min_site_reports_threshold=min_reports,
        site_profiles=profiles
    )


@router.get(
    "/{site_id}",
    response_model=SiteRiskProfileSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Single Site Risk Detail Profile",
    description="Returns detailed safety risk profile, top activities, hazards, barrier failures, and LSR rules for a site."
)
def get_site_risk_profile_by_id(site_id: str):
    analyzer = get_site_analyzer()
    profiles = analyzer.calculate_site_risk_profiles()

    for p in profiles:
        if p["site_id"].upper() == site_id.upper() or p["site_name"].lower() == site_id.lower():
            return p

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Site risk profile for '{site_id}' not found."
    )
