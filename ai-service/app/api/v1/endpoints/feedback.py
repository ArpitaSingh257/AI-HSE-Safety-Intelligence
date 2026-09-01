"""
feedback.py - FastAPI Endpoint Router for Stage 33 Human-in-the-Loop Analyst Feedback (/api/v1/feedback).
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.feedback_store import FeedbackStore
from app.schemas import FeedbackSubmissionSchema, FeedbackRecordSchema, FeedbackStatsSchema

router = APIRouter()

# Global feedback store instance (singleton)
_store_instance: Optional[FeedbackStore] = None

def get_feedback_store() -> FeedbackStore:
    global _store_instance
    if _store_instance is None:
        _store_instance = FeedbackStore()
    return _store_instance


@router.post(
    "",
    response_model=FeedbackRecordSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Submit HSE Analyst Feedback",
    description="Validates and registers human review feedback (ACCEPT, CORRECT, REJECT) into the evaluation queue without modifying production ML models."
)
def submit_feedback(body: FeedbackSubmissionSchema):
    store = get_feedback_store()
    try:
        record = store.create_feedback_record(
            report_id=body.report_id,
            field_name=body.field_name,
            ai_value=body.ai_value,
            human_value=body.human_value,
            action=body.action,
            comment=body.comment,
            reviewer_id=body.reviewer_id or "HSE_ANALYST_01"
        )
        return record
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/stats",
    response_model=FeedbackStatsSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Analyst Feedback Statistics",
    description="Returns aggregate statistics on accepted, corrected, and rejected AI predictions."
)
def get_feedback_statistics():
    store = get_feedback_store()
    return store.calculate_statistics()


@router.get(
    "/reports/{report_id}",
    response_model=List[FeedbackRecordSchema],
    status_code=status.HTTP_200_OK,
    summary="Get Feedback History for Report",
    description="Returns all analyst feedback records submitted for a specific report ID."
)
def get_feedback_by_report_id(report_id: str):
    store = get_feedback_store()
    return store.get_feedback_for_report(report_id)
