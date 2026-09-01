"""
risk_matrix.py - FastAPI Endpoint Router for Stage 31 Severity vs Recurrence Risk Matrix (/api/v1/risk-matrix).
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.risk_matrix_engine import RiskMatrixEngine
from app.schemas import RiskMatrixListResponse, RiskMatrixItemSchema

router = APIRouter()

# Global engine instance (singleton)
_engine_instance: Optional[RiskMatrixEngine] = None

def get_risk_matrix_engine() -> RiskMatrixEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RiskMatrixEngine()
    return _engine_instance


@router.get(
    "",
    response_model=RiskMatrixListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Severity vs Recurrence 2D Risk Matrix",
    description="Returns 2D normalized coordinates (Severity vs Recurrence) and quadrant classifications for safety entities."
)
def get_risk_matrix(
    quadrant: Optional[str] = Query(default=None, description="Optional filter by quadrant (HIGH_SEVERITY_HIGH_RECURRENCE, HIGH_SEVERITY_LOW_RECURRENCE, LOW_SEVERITY_HIGH_RECURRENCE, LOW_SEVERITY_LOW_RECURRENCE, INSUFFICIENT_DATA)."),
    entity_type: Optional[str] = Query(default=None, description="Optional filter by entity_type (BARRIER_FAILURE, RECURRING_PATTERN, SITE, ACTIVITY).")
):
    engine = get_risk_matrix_engine()
    items = engine.calculate_risk_matrix()

    if quadrant:
        items = [i for i in items if i["quadrant"].upper() == quadrant.upper()]
    if entity_type:
        items = [i for i in items if i["entity_type"].upper() == entity_type.upper()]

    c_hh = sum(1 for i in items if i["quadrant"] == "HIGH_SEVERITY_HIGH_RECURRENCE")
    c_hl = sum(1 for i in items if i["quadrant"] == "HIGH_SEVERITY_LOW_RECURRENCE")
    c_lh = sum(1 for i in items if i["quadrant"] == "LOW_SEVERITY_HIGH_RECURRENCE")
    c_ll = sum(1 for i in items if i["quadrant"] == "LOW_SEVERITY_LOW_RECURRENCE")

    return RiskMatrixListResponse(
        total_items=len(items),
        critical_priority_count=c_hh,
        high_potential_rare_count=c_hl,
        frequent_lower_potential_count=c_lh,
        low_priority_monitor_count=c_ll,
        matrix_items=items
    )


@router.get(
    "/{matrix_item_id}",
    response_model=RiskMatrixItemSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Single Risk Matrix Item Profile",
    description="Returns 2D coordinates, quadrant assignment, deterministic reason, and traceability IDs for a single risk matrix item."
)
def get_risk_matrix_item_by_id(matrix_item_id: str):
    engine = get_risk_matrix_engine()
    items = engine.calculate_risk_matrix()

    for i in items:
        if i["matrix_item_id"].upper() == matrix_item_id.upper() or i["matrix_item_id"].replace("MATRIX-", "").upper() == matrix_item_id.upper():
            return i

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Risk matrix item '{matrix_item_id}' not found."
    )
