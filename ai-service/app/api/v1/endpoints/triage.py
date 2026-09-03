"""
triage.py - FastAPI Endpoint Router for Stage 34 Confidence-Calibrated Operational Triage (/api/v1/triage).
"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.confidence_triage_engine import ConfidenceTriageEngine
from app.schemas import TriageRequestSchema, TriageResultSchema, TriageBatchResponseSchema

router = APIRouter()

# Global triage engine instance (singleton)
_engine_instance: Optional[ConfidenceTriageEngine] = None

def get_triage_engine() -> ConfidenceTriageEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ConfidenceTriageEngine()
    return _engine_instance


@router.post(
    "",
    response_model=TriageResultSchema,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Confidence-Calibrated Triage Decision",
    description="Applies Sigmoid post-processing calibration to raw SIF probability and evaluates conservative operational triage policy."
)
def evaluate_triage(body: TriageRequestSchema):
    engine = get_triage_engine()
    raw_sif = body.raw_sif_probability if body.raw_sif_probability is not None else 0.50

    return engine.evaluate_triage(
        report_id=body.report_id,
        raw_sif_prob=raw_sif,
        priority_level=body.priority_level or "MEDIUM",
        priority_score=body.priority_score if body.priority_score is not None else 0.50,
        early_warning_level=body.early_warning_level or "NORMAL",
        risk_matrix_category=body.risk_matrix_category or "LOW_SEVERITY_LOW_RECURRENCE"
    )


@router.post(
    "/batch",
    response_model=TriageBatchResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Batch Triage Decisions",
    description="Evaluates operational triage decisions for a list of safety reports."
)
def evaluate_triage_batch(requests: List[TriageRequestSchema]):
    engine = get_triage_engine()
    results = []
    c_esc = 0
    c_rev = 0
    c_clr = 0

    for req in requests:
        raw_sif = req.raw_sif_probability if req.raw_sif_probability is not None else 0.50
        res = engine.evaluate_triage(
            report_id=req.report_id,
            raw_sif_prob=raw_sif,
            priority_level=req.priority_level or "MEDIUM",
            priority_score=req.priority_score if req.priority_score is not None else 0.50,
            early_warning_level=req.early_warning_level or "NORMAL",
            risk_matrix_category=req.risk_matrix_category or "LOW_SEVERITY_LOW_RECURRENCE"
        )
        results.append(res)
        if res["triage_level"] == "IMMEDIATE_ESCALATION":
            c_esc += 1
        elif res["triage_level"] == "NEEDS_REVIEW":
            c_rev += 1
        else:
            c_clr += 1

    return TriageBatchResponseSchema(
        total_evaluated=len(results),
        immediate_escalation_count=c_esc,
        needs_review_count=c_rev,
        auto_clear_count=c_clr,
        triage_results=results
    )
