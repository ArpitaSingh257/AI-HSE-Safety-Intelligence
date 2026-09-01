"""
patterns.py - FastAPI Endpoint Router for Recurring Precursor Pattern Detection (/api/v1/patterns).
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.pattern_detector import RecurringPatternDetector
from app.schemas import PatternListResponse, RecurringPatternSchema

router = APIRouter()

# Global pattern detector instance (singleton)
_detector_instance: Optional[RecurringPatternDetector] = None

def get_pattern_detector(min_support: int = 3) -> RecurringPatternDetector:
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = RecurringPatternDetector(min_pattern_incidents=min_support)
    return _detector_instance


@router.get(
    "",
    response_model=PatternListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Recurring Precursor Safety Patterns",
    description="Surfaces recurring precursor patterns discovered across historical incident records."
)

def get_recurring_patterns(
    min_support: int = Query(default=3, ge=2, description="Minimum incident support threshold for a pattern."),
    activity: Optional[str] = Query(default=None, description="Optional filter by activity."),
    lsr: Optional[str] = Query(default=None, description="Optional filter by Life-Saving Rule.")
):
    detector = get_pattern_detector(min_support=min_support)
    patterns = detector.detect_patterns()

    filtered = []
    for p in patterns:
        if activity and activity.lower() not in p["dominant_activity"].lower():
            continue
        if lsr and lsr.lower() not in p["dominant_lsr"].lower():
            continue
        filtered.append(p)

    return PatternListResponse(
        total_patterns=len(filtered),
        min_support_threshold=min_support,
        patterns=filtered
    )


@router.get(
    "/{pattern_id}",
    response_model=RecurringPatternSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Single Pattern Details",
    description="Returns detailed recurring pattern attributes and supporting historical incident IDs."
)
def get_pattern_by_id(pattern_id: str):
    detector = get_pattern_detector()
    patterns = detector.detect_patterns()
    
    for p in patterns:
        if p["pattern_id"] == pattern_id or p.get("pattern_code") == pattern_id:
            return p

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Pattern with ID '{pattern_id}' not found."
    )
