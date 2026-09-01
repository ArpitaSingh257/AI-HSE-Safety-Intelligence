"""
early_warnings.py - FastAPI Endpoint Router for Stage 29 Temporal Trend / Early-Warning Detection (/api/v1/early-warnings).
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.early_warning_detector import EarlyWarningDetector
from app.schemas import EarlyWarningListResponse, EarlyWarningProfileSchema

router = APIRouter()

# Global detector instance (singleton)
_detector_instance: Optional[EarlyWarningDetector] = None

def get_early_warning_detector() -> EarlyWarningDetector:
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = EarlyWarningDetector()
    return _detector_instance


@router.get(
    "",
    response_model=EarlyWarningListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Early-Warning Intelligence Signals",
    description="Returns ranked early warning signals evaluating sustained worsening precursor trends across safety patterns and barriers."
)
def get_early_warnings(
    level: Optional[str] = Query(default=None, description="Optional filter by warning_level (HIGH_PRIORITY, EARLY_WARNING, WATCH, NORMAL, INSUFFICIENT_DATA)."),
    signal_type: Optional[str] = Query(default=None, description="Optional filter by signal_type (BARRIER_FAILURE, RECURRING_PATTERN, SIF_DENSITY, SITE_RISK, ACTIVITY_RISK).")
):
    detector = get_early_warning_detector()
    warnings = detector.detect_early_warnings()

    if level:
        warnings = [w for w in warnings if w["warning_level"].upper() == level.upper()]
    if signal_type:
        warnings = [w for w in warnings if w["signal_type"].upper() == signal_type.upper()]

    high_pri = sum(1 for w in warnings if w["warning_level"] == "HIGH_PRIORITY")
    early_warn = sum(1 for w in warnings if w["warning_level"] == "EARLY_WARNING")
    watch_cnt = sum(1 for w in warnings if w["warning_level"] == "WATCH")

    return EarlyWarningListResponse(
        total_warnings=len(warnings),
        high_priority_count=high_pri,
        early_warning_count=early_warn,
        watch_count=watch_cnt,
        warnings=warnings
    )


@router.get(
    "/{warning_id}",
    response_model=EarlyWarningProfileSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Single Early Warning Signal Detail",
    description="Returns detailed time-series metrics, affected sites/tasks, and deterministic reasons for an early warning signal."
)
def get_early_warning_by_id(warning_id: str):
    detector = get_early_warning_detector()
    warnings = detector.detect_early_warnings()

    for w in warnings:
        if w["warning_id"].upper() == warning_id.upper() or w["warning_id"].replace("EW-", "").upper() == warning_id.upper():
            return w

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Early warning signal '{warning_id}' not found."
    )
