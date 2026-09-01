"""
lsr_trends.py - FastAPI Endpoint Router for Stage 28 Life-Saving Rule (LSR) Trend Analytics (/api/v1/lsr-trends).
Excludes UNKNOWN/missing LSR labels from official IOGP trend analytics and raises 404 for UNKNOWN detail queries.
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.lsr_trend_analyzer import LsrTrendAnalyzer
from app.schemas import LsrTrendListResponse, LsrTrendProfileSchema

router = APIRouter()

# Global analyzer instance (singleton)
_analyzer_instance: Optional[LsrTrendAnalyzer] = None

def get_lsr_analyzer(min_reports: int = 3) -> LsrTrendAnalyzer:
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = LsrTrendAnalyzer(min_lsr_reports=min_reports)
    return _analyzer_instance


@router.get(
    "",
    response_model=LsrTrendListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Life-Saving Rule Trend Intelligence Profiles",
    description="Returns time-series metrics and trend trajectories for official IOGP Life-Saving Rules."
)
def get_lsr_trend_profiles(
    min_reports: int = Query(default=3, ge=1, description="Minimum reports required for trend calculation."),
    trend: Optional[str] = Query(default=None, description="Optional filter by trend state (INCREASING, STABLE, DECREASING, INSUFFICIENT_DATA).")
):
    analyzer = get_lsr_analyzer(min_reports=min_reports)
    summary = analyzer.get_lsr_analytics_summary()
    profiles = summary["official_lsr_profiles"]

    if trend:
        profiles = [p for p in profiles if p["trend"].upper() == trend.upper()]

    return LsrTrendListResponse(
        total_lsr_rules=len(profiles),
        min_lsr_reports_threshold=min_reports,
        unknown_lsr_records=summary["unknown_lsr_records"],
        unknown_lsr_rate=summary["unknown_lsr_rate"],
        lsr_profiles=profiles
    )


@router.get(
    "/{lsr_rule}",
    response_model=LsrTrendProfileSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Single Life-Saving Rule Trend Detail Profile",
    description="Returns detailed time-series metrics, trend trajectory, top sites, activities, and barrier failures for an official LSR."
)
def get_lsr_trend_profile_by_rule(lsr_rule: str):
    if lsr_rule.upper() in ["UNKNOWN", "MISSING", "N/A", "NONE", "UNCLASSIFIED", "NULL"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{lsr_rule}' is a data-quality bucket and not an official Life-Saving Rule."
        )

    analyzer = get_lsr_analyzer()
    profiles = analyzer.calculate_lsr_trend_profiles()

    for p in profiles:
        if p["lsr_rule"].lower() == lsr_rule.lower() or p["lsr_rule"].replace(" ", "-").lower() == lsr_rule.lower():
            return p

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Life-Saving Rule trend profile for '{lsr_rule}' not found."
    )
