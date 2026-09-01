"""
bow_ties.py - FastAPI Endpoint Router for Stage 32 Bow-Tie / Barrier Failure Mapping (/api/v1/bow-ties).
"""

import sys
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.bow_tie_mapper import BowTieMapper
from app.schemas import BowTieProfileSchema

router = APIRouter()

# Global mapper instance (singleton)
_mapper_instance: Optional[BowTieMapper] = None

def get_bow_tie_mapper() -> BowTieMapper:
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = BowTieMapper()
    return _mapper_instance


@router.get(
    "/{report_id}",
    response_model=BowTieProfileSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Bow-Tie Risk Pathway Mapping for Safety Report",
    description="Returns qualitative Bow-Tie pathway (Threat -> Failed Barrier -> Top Event -> Consequence) with explicit node and edge provenance."
)
def get_bow_tie_by_report_id(report_id: str):
    mapper = get_bow_tie_mapper()
    result = mapper.get_bow_tie_by_report_id(report_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bow-Tie pathway for report '{report_id}' not found."
        )
    return result
