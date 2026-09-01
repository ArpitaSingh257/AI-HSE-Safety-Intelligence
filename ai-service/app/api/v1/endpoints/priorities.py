"""
priorities.py - FastAPI Endpoint Router for Stage 30 Risk / Priority Intelligence (/api/v1/priorities).
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.priority_intelligence_engine import PriorityIntelligenceEngine
from app.schemas import PriorityListResponse, PriorityProfileSchema

router = APIRouter()

# Global engine instance (singleton)
_engine_instance: Optional[PriorityIntelligenceEngine] = None

def get_priority_engine() -> PriorityIntelligenceEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = PriorityIntelligenceEngine()
    return _engine_instance


@router.get(
    "",
    response_model=PriorityListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get HSE Priority Intelligence Rankings",
    description="Returns ranked HSE priorities synthesizing SIF impact, recurrence, barrier failures, site/activity risk indices, and early-warning signals."
)
def get_priorities(
    level: Optional[str] = Query(default=None, description="Optional filter by priority_level (CRITICAL, HIGH, MEDIUM, LOW, INSUFFICIENT_DATA)."),
    entity_type: Optional[str] = Query(default=None, description="Optional filter by entity_type (BARRIER_FAILURE, RECURRING_PATTERN, SITE, ACTIVITY).")
):
    engine = get_priority_engine()
    priorities = engine.calculate_priorities()

    if level:
        priorities = [p for p in priorities if p["priority_level"].upper() == level.upper()]
    if entity_type:
        priorities = [p for p in priorities if p["entity_type"].upper() == entity_type.upper()]

    crit_cnt = sum(1 for p in priorities if p["priority_level"] == "CRITICAL")
    high_cnt = sum(1 for p in priorities if p["priority_level"] == "HIGH")
    med_cnt = sum(1 for p in priorities if p["priority_level"] == "MEDIUM")

    return PriorityListResponse(
        total_priorities=len(priorities),
        critical_count=crit_cnt,
        high_count=high_cnt,
        medium_count=med_cnt,
        priorities=priorities
    )


@router.get(
    "/{priority_id}",
    response_model=PriorityProfileSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Single HSE Priority Detail Profile",
    description="Returns detailed component breakdown, entity information, deterministic reason, and cross-stage traceability IDs for a priority item."
)
def get_priority_by_id(priority_id: str):
    engine = get_priority_engine()
    priorities = engine.calculate_priorities()

    for p in priorities:
        if p["priority_id"].upper() == priority_id.upper() or p["priority_id"].replace("PRI-", "").upper() == priority_id.upper():
            return p

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"HSE priority item '{priority_id}' not found."
    )
