"""
graph.py - Graph RAG Lineage API Endpoint (GET /api/v1/graph/lineage).
"""

import sys
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from services.graph_service import KnowledgeGraphService

router = APIRouter()

_graph_service_instance = None


def get_graph_service() -> KnowledgeGraphService:
    global _graph_service_instance
    if _graph_service_instance is None:
        _graph_service_instance = KnowledgeGraphService()
    return _graph_service_instance


@router.get(
    "/lineage",
    status_code=status.HTTP_200_OK,
    summary="Retrieve Graph RAG Safety Lineage Network Topology",
    description="Returns multi-tiered directed graph topology linking Sites, Activities, LSR Rules, SIF Tiers, and Grounded Incidents."
)
def get_graph_lineage(
    site: Optional[str] = Query(None, description="Optional site filter"),
    activity: Optional[str] = Query(None, description="Optional activity filter"),
    min_risk: float = Query(0.0, description="Minimum risk score filter"),
    service: KnowledgeGraphService = Depends(get_graph_service)
):
    try:
        return service.get_lineage_graph(
            site_filter=site,
            activity_filter=activity,
            min_risk=min_risk
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph RAG Error: {str(e)}"
        )
