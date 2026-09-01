"""
similar_reports.py - FastAPI Endpoint Router for Stage 25 Similar Historical Report Linking (/api/v1/similar-reports).
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.similar_report_finder import SimilarReportFinder
from app.schemas import SimilarReportsResponse, SimilarReportItemSchema, SimilarReportSearchRequest

router = APIRouter()

# Global finder instance (singleton)
_finder_instance: Optional[SimilarReportFinder] = None

def get_similar_finder(top_k: int = 5, min_similarity: float = 0.40) -> SimilarReportFinder:
    global _finder_instance
    if _finder_instance is None:
        _finder_instance = SimilarReportFinder(top_k=top_k, min_similarity=min_similarity)
    return _finder_instance


@router.get(
    "/{report_id}",
    response_model=SimilarReportsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Similar Historical Reports for Existing Report",
    description="Retrieves the top semantically similar historical safety reports for an existing report ID."
)
def get_similar_reports_by_id(
    report_id: str,
    top_k: int = Query(default=5, ge=1, le=20, description="Top-K count."),
    min_similarity: float = Query(default=0.40, ge=0.0, le=1.0, description="Minimum similarity threshold.")
):
    finder = get_similar_finder(top_k=top_k, min_similarity=min_similarity)
    reports = finder.find_similar_reports(query_report_id=report_id, top_k=top_k, min_similarity=min_similarity)

    return SimilarReportsResponse(
        query_report_id=report_id,
        total_matches=len(reports),
        top_k=top_k,
        min_similarity_threshold=min_similarity,
        similar_reports=reports
    )


@router.post(
    "",
    response_model=SimilarReportsResponse,
    status_code=status.HTTP_200_OK,
    summary="Find Similar Historical Reports for Free Text",
    description="Retrieves the top semantically similar historical safety reports for a raw text narrative query."
)
def find_similar_reports_by_text(req: SimilarReportSearchRequest):
    if not req.query_text or not req.query_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="query_text must be provided."
        )

    finder = get_similar_finder(top_k=req.top_k, min_similarity=req.min_similarity)
    reports = finder.find_similar_reports(query_text=req.query_text, top_k=req.top_k, min_similarity=req.min_similarity)

    return SimilarReportsResponse(
        query_report_id=None,
        total_matches=len(reports),
        top_k=req.top_k,
        min_similarity_threshold=req.min_similarity,
        similar_reports=reports
    )
