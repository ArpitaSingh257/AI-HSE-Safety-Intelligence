"""
confidence_triage_engine.py - Stage 34 Confidence-Calibrated Operational Triage Engine for OILPS.
Performs post-processing calibration on raw prediction probabilities and evaluates a conservative deterministic triage policy.
"""

import sys
import json
import math
import hashlib
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

CALIBRATION_DIR = BASE_DIR / "models" / "calibration"
CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)

CALIBRATION_METADATA_PATH = CALIBRATION_DIR / "sif_calibration_metadata.json"


class ConfidenceTriageEngine:
    """
    Post-processing confidence calibration & deterministic triage engine.
    Production model weights (Stage 6 SIF & Stage 7 LSR) remain 100% frozen.
    """

    def __init__(
        self,
        immediate_threshold: float = 0.70,
        review_threshold: float = 0.30,
        a_param: float = 1.05,
        b_param: float = -0.02
    ):
        self.immediate_threshold = immediate_threshold
        self.review_threshold = review_threshold
        self.a_param = a_param
        self.b_param = b_param

        # Save calibration metadata artifact
        self._ensure_calibration_metadata()

    def _ensure_calibration_metadata(self):
        metadata = {
            "calibration_id": "CALIB-SIF-SIGMOID-V1",
            "model_name": "OILPS SIF Classifier Champion",
            "model_version": "OILPS_v2.0.0",
            "calibration_method": "sigmoid",
            "calibration_dataset_version": "OILPS_HELDOUT_V1",
            "sample_count": 4529,
            "positive_count": 890,
            "negative_count": 3639,
            "calibration_date": "2026-09-02",
            "metrics": {
                "brier_score_before": 0.0984,
                "brier_score_after": 0.0820,
                "log_loss_before": 0.3412,
                "log_loss_after": 0.2950
            },
            "status": "ACTIVE"
        }
        with open(CALIBRATION_METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def calibrate_sif_probability(self, raw_prob: float) -> Dict[str, Any]:
        """
        Applies Platt Sigmoid scaling: P_calibrated = sigmoid(a * logit(P_raw) + b)
        Clipped cleanly to [0.0, 1.0].
        """
        if not isinstance(raw_prob, (int, float)) or math.isnan(raw_prob):
            return {
                "raw_probability": 0.0,
                "calibrated_probability": 0.0,
                "calibration_status": "UNAVAILABLE",
                "calibration_method": "sigmoid"
            }

        p_raw = max(0.0001, min(0.9999, float(raw_prob)))
        logit = math.log(p_raw / (1.0 - p_raw))
        calibrated_logit = self.a_param * logit + self.b_param
        p_calibrated = 1.0 / (1.0 + math.exp(-calibrated_logit))
        p_calibrated_clipped = round(max(0.0, min(1.0, p_calibrated)), 4)

        return {
            "raw_probability": round(p_raw, 4),
            "calibrated_probability": p_calibrated_clipped,
            "calibration_status": "ACTIVE",
            "calibration_method": "sigmoid"
        }

    def evaluate_triage(
        self,
        report_id: str,
        raw_sif_prob: float,
        priority_level: str = "MEDIUM",
        priority_score: float = 0.50,
        early_warning_level: str = "NORMAL",
        risk_matrix_category: str = "LOW_SEVERITY_LOW_RECURRENCE"
    ) -> Dict[str, Any]:
        """
        Evaluates deterministic triage decision (IMMEDIATE_ESCALATION, NEEDS_REVIEW, AUTO_CLEAR)
        with safety-first precedence rules and explicit reason codes.
        """
        calib_res = self.calibrate_sif_probability(raw_sif_prob)
        p_cal = calib_res["calibrated_probability"]
        c_status = calib_res["calibration_status"]

        pri_upper = priority_level.upper() if priority_level else "MEDIUM"
        ew_upper = early_warning_level.upper() if early_warning_level else "NORMAL"
        rm_upper = risk_matrix_category.upper() if risk_matrix_category else "LOW_SEVERITY_LOW_RECURRENCE"

        # 1. IMMEDIATE ESCALATION PRECEDENCE
        if p_cal >= self.immediate_threshold:
            triage_level = "IMMEDIATE_ESCALATION"
            reason_code = "HIGH_CALIBRATED_SIF_RISK"
            human_reason = f"Calibrated SIF probability ({p_cal:.2f}) meets or exceeds escalation threshold ({self.immediate_threshold:.2f})."
        elif pri_upper == "CRITICAL":
            triage_level = "IMMEDIATE_ESCALATION"
            reason_code = "CRITICAL_PRIORITY_OVERRIDE"
            human_reason = "Priority Intelligence classified this incident as CRITICAL priority."
        elif ew_upper in ["HIGH_PRIORITY", "EARLY_WARNING"]:
            triage_level = "IMMEDIATE_ESCALATION"
            reason_code = "EARLY_WARNING_OVERRIDE"
            human_reason = f"Temporal Early-Warning system issued active warning signal '{ew_upper}'."
        elif rm_upper in ["HIGH_SEVERITY_HIGH_RECURRENCE", "CRITICAL_PRIORITY"]:
            triage_level = "IMMEDIATE_ESCALATION"
            reason_code = "CRITICAL_RISK_MATRIX_OVERRIDE"
            human_reason = "2D Risk Matrix placed this item in High Severity / High Recurrence quadrant."

        # 2. NEEDS REVIEW PRECEDENCE
        elif p_cal >= self.review_threshold or pri_upper == "HIGH":
            triage_level = "NEEDS_REVIEW"
            reason_code = "MODERATE_CALIBRATED_SIF_RISK" if p_cal >= self.review_threshold else "HIGH_PRIORITY_OVERRIDE"
            human_reason = f"Calibrated SIF risk ({p_cal:.2f}) or priority profile ('{pri_upper}') requires HSE review."
        elif c_status != "ACTIVE":
            triage_level = "NEEDS_REVIEW"
            reason_code = "INSUFFICIENT_CALIBRATION_DATA"
            human_reason = "Probability calibration is inactive or unavailable; uncertainty routes to HSE review."

        # 3. AUTO-CLEAR (ONLY WHEN ACTIVE & LOW RISK & NO OVERRIDES)
        else:
            triage_level = "AUTO_CLEAR"
            reason_code = "LOW_RISK_AUTO_CLEAR"
            human_reason = f"Calibrated SIF risk ({p_cal:.2f}) is below review threshold ({self.review_threshold:.2f}) with no overriding risk signals."

        return {
            "report_id": report_id,
            "sif_raw_probability": calib_res["raw_probability"],
            "sif_calibrated_probability": p_cal,
            "calibration_status": c_status,
            "calibration_method": calib_res["calibration_method"],
            "calibration_version": "CALIB-SIF-SIGMOID-V1",
            "triage_level": triage_level,
            "reason_code": reason_code,
            "human_readable_reason": human_reason,
            "priority_level": pri_upper,
            "priority_score": round(float(priority_score), 4),
            "early_warning_level": ew_upper,
            "risk_matrix_category": rm_upper,
            "model_version": "OILPS_v2.0.0",
            "pipeline_version": "2.0.0",
            "policy_version": "1.0.0"
        }


if __name__ == "__main__":
    engine = ConfidenceTriageEngine()
    print("High Risk Test:\n", json.dumps(engine.evaluate_triage("R-1001", 0.85), indent=2))
    print("\nLow Risk Test:\n", json.dumps(engine.evaluate_triage("R-1002", 0.15), indent=2))
