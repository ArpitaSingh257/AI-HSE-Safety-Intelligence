"""
barrier_patterns.py - FastAPI Router for Stage 24 Barrier Failure Pattern Mining (/api/v1/barrier-patterns).
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.barrier_pattern_miner import BarrierPatternMiner
from app.schemas import BarrierPatternListResponse, BarrierPatternSchema

router = APIRouter()

# Global miner instance (singleton)
_miner_instance: Optional[BarrierPatternMiner] = None

def get_barrier_miner(min_support: int = 3) -> BarrierPatternMiner:
    global _miner_instance
    if _miner_instance is None:
        _miner_instance = BarrierPatternMiner(min_barrier_incidents=min_support)
    return _miner_instance


@router.get(
    "",
    response_model=BarrierPatternListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Mined Barrier Failure Patterns",
    description="Surfaces repeated safety barrier failure patterns mined across historical incident records."
)
def get_barrier_patterns(
    min_support: int = Query(default=3, ge=2, description="Minimum incident support threshold."),
    activity: Optional[str] = Query(default=None, description="Optional filter by activity."),
    lsr: Optional[str] = Query(default=None, description="Optional filter by Life-Saving Rule.")
):
    miner = get_barrier_miner(min_support=min_support)
    patterns = miner.mine_barrier_patterns()

    filtered = []
    for p in patterns:
        if activity and activity.lower() not in p["dominant_activity"].lower():
            continue
        if lsr and lsr.lower() not in p["dominant_lsr"].lower():
            continue
        filtered.append(p)

    return BarrierPatternListResponse(
        total_barrier_patterns=len(filtered),
        min_support_threshold=min_support,
        barrier_patterns=filtered
    )


@router.get(
    "/{barrier_pattern_id}",
    response_model=BarrierPatternSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Single Barrier Pattern Details",
    description="Returns detailed recurring barrier failure pattern attributes and traceable incident IDs."
)
def get_barrier_pattern_by_id(barrier_pattern_id: str):
    miner = get_barrier_miner()
    patterns = miner.mine_barrier_patterns()

    for p in patterns:
        if p["barrier_pattern_id"] == barrier_pattern_id or p.get("barrier_code_prefix") == barrier_pattern_id:
            return p

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Barrier pattern with ID '{barrier_pattern_id}' not found."
    )
