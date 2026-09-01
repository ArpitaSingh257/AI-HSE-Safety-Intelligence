"""
feedback_store.py - Stage 33 Human-in-the-Loop Analyst Feedback Evaluation Engine for OILPS.
Manages evaluation feedback records and computes accuracy/correction statistics.
"""

import sys
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


class FeedbackStore:
    """
    Evaluation queue manager for HSE analyst feedback on AI predictions.
    Human feedback flows into a controlled evaluation queue (SUBMITTED -> REVIEWED -> ACCEPTED_FOR_EVALUATION)
    and does NOT automatically retrain production ML models.
    """

    def __init__(self):
        self._in_memory_records: List[Dict[str, Any]] = []

    def create_feedback_record(
        self,
        report_id: str,
        field_name: str,
        ai_value: Any,
        human_value: Any,
        action: str,
        comment: Optional[str] = None,
        reviewer_id: str = "HSE_ANALYST_01",
        model_version: str = "OILPS_v2.0.0",
        pipeline_version: str = "2.0.0",
        schema_version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """
        Creates a structured feedback evaluation record preserving original AI value and human review overlay.
        """
        action_clean = action.upper()
        if action_clean not in ["ACCEPT", "CORRECT", "REJECT", "NEEDS_REVIEW"]:
            raise ValueError(f"Invalid feedback action '{action}'. Must be ACCEPT, CORRECT, REJECT, or NEEDS_REVIEW.")

        timestamp_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        hash_input = f"{report_id}::{field_name}::{action_clean}::{timestamp_str}"
        fb_id = f"FB-{hashlib.md5(hash_input.encode('utf-8')).hexdigest()[:8].upper()}"

        record = {
            "feedback_id": fb_id,
            "report_id": report_id,
            "field_name": field_name,
            "ai_value": ai_value,
            "human_value": human_value if action_clean == "CORRECT" else ai_value,
            "action": action_clean,
            "comment": comment or "",
            "reviewer_id": reviewer_id,
            "review_timestamp": timestamp_str,
            "model_version": model_version,
            "pipeline_version": pipeline_version,
            "schema_version": schema_version,
            "status": "SUBMITTED",
            "revision": 1,
            "created_at": timestamp_str,
            "updated_at": timestamp_str
        }

        self._in_memory_records.append(record)
        return record

    def get_feedback_for_report(self, report_id: str) -> List[Dict[str, Any]]:
        """
        Returns all feedback evaluation records for a specific report ID.
        """
        return [r for r in self._in_memory_records if r["report_id"] == report_id]

    def calculate_statistics(self, records_override: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Calculates aggregate feedback statistics and field-level correction rates.
        """
        recs = records_override if records_override is not None else self._in_memory_records
        total = len(recs)
        if total == 0:
            return {
                "total_feedback": 0,
                "accepted_count": 0,
                "corrected_count": 0,
                "rejected_count": 0,
                "accept_rate": 1.0,
                "correction_rate": 0.0,
                "reject_rate": 0.0,
                "field_breakdown": {}
            }

        acc = sum(1 for r in recs if r["action"] == "ACCEPT")
        corr = sum(1 for r in recs if r["action"] == "CORRECT")
        rej = sum(1 for r in recs if r["action"] == "REJECT")

        fields = set(r["field_name"] for r in recs)
        field_breakdown = {}
        for f in fields:
            f_recs = [r for r in recs if r["field_name"] == f]
            f_tot = len(f_recs)
            f_acc = sum(1 for r in f_recs if r["action"] == "ACCEPT")
            f_corr = sum(1 for r in f_recs if r["action"] == "CORRECT")
            field_breakdown[f] = {
                "total": f_tot,
                "accepted": f_acc,
                "corrected": f_corr,
                "accuracy_rate": round(f_acc / f_tot, 4) if f_tot > 0 else 1.0
            }

        return {
            "total_feedback": total,
            "accepted_count": acc,
            "corrected_count": corr,
            "rejected_count": rej,
            "accept_rate": round(acc / total, 4),
            "correction_rate": round(corr / total, 4),
            "reject_rate": round(rej / total, 4),
            "field_breakdown": field_breakdown
        }


if __name__ == "__main__":
    store = FeedbackStore()
    fb = store.create_feedback_record(
        report_id="R-1001",
        field_name="primary_life_saving_rule",
        ai_value="Energy Isolation",
        human_value="Line of Fire",
        action="CORRECT",
        comment="Suspended load involved."
    )
    print("Created Feedback Record:\n", fb)
    print("Stats:\n", store.calculate_statistics())
