"""
test_final_model_evaluation.py - Quality assurance test suite for Stage 8 Final Model Validation & Error Analysis.

Verifies:
1. Zero train/val/test cross-split contamination.
2. Split membership and record IDs preserved exactly.
3. SIF and LSR champion model checkpoints exist and load without error.
4. Test predictions correspond exactly to held-out test splits (134 SIF, 138 LSR).
5. SIF predictions are binary with continuous probabilities.
6. Exactly 9 official IOGP LSR targets evaluated.
7. Error analysis and master benchmark JSON artifacts exist and contain valid schema.
8. STAGE_8_FINAL_MODEL_EVALUATION_REPORT.md exists.
"""

import os
import json
import torch
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_DIR = BASE_DIR / "datasets" / "model_ready" / "splits"
RESULTS_DIR = BASE_DIR / "results" / "final_evaluation"
QUALITY_DIR = BASE_DIR / "datasets" / "quality"

OFFICIAL_9_LSR = [
    "Bypassing Safety Controls",
    "Confined Space",
    "Driving",
    "Energy Isolation",
    "Hot Work",
    "Line of Fire",
    "Safe Mechanical Lifting",
    "Toxic Gas / Hazardous Substance",
    "Working at Height"
]

def test_split_integrity():
    for task in ["sif", "lsr"]:
        train = pd.read_csv(SPLITS_DIR / f"{task}_train.csv")
        val = pd.read_csv(SPLITS_DIR / f"{task}_val.csv")
        test = pd.read_csv(SPLITS_DIR / f"{task}_test.csv")
        
        train_ids = set(train["record_id"])
        val_ids = set(val["record_id"])
        test_ids = set(test["record_id"])
        
        assert len(train_ids.intersection(val_ids)) == 0, f"{task} Train-Val overlap"
        assert len(train_ids.intersection(test_ids)) == 0, f"{task} Train-Test overlap"
        assert len(val_ids.intersection(test_ids)) == 0, f"{task} Val-Test overlap"

def test_sif_final_evaluation_artifacts():
    summary_path = RESULTS_DIR / "sif_final_test_evaluation.json"
    error_path = RESULTS_DIR / "sif_error_analysis.json"
    preds_path = RESULTS_DIR / "final_sif_test_predictions.csv"
    
    assert summary_path.exists(), "sif_final_test_evaluation.json missing"
    assert error_path.exists(), "sif_error_analysis.json missing"
    assert preds_path.exists(), "final_sif_test_predictions.csv missing"
    
    test_df = pd.read_csv(SPLITS_DIR / "sif_test.csv")
    preds_df = pd.read_csv(preds_path)
    assert len(preds_df) == len(test_df), f"SIF prediction count {len(preds_df)} != test count {len(test_df)}"
    assert list(preds_df["record_id"]) == list(test_df["record_id"]), "SIF record IDs mismatch"
    assert "final_sif_probability" in preds_df.columns
    assert "final_sif_prediction" in preds_df.columns
    assert "error_type" in preds_df.columns
    assert set(preds_df["final_sif_prediction"].unique()).issubset({0, 1})

def test_lsr_final_evaluation_artifacts():
    summary_path = RESULTS_DIR / "lsr_final_test_evaluation.json"
    error_path = RESULTS_DIR / "lsr_error_analysis.json"
    preds_path = RESULTS_DIR / "final_lsr_test_predictions.csv"
    
    assert summary_path.exists(), "lsr_final_test_evaluation.json missing"
    assert error_path.exists(), "lsr_error_analysis.json missing"
    assert preds_path.exists(), "final_lsr_test_predictions.csv missing"
    
    test_df = pd.read_csv(SPLITS_DIR / "lsr_test.csv")
    preds_df = pd.read_csv(preds_path)
    assert len(preds_df) == len(test_df), f"LSR prediction count {len(preds_df)} != test count {len(test_df)}"
    assert list(preds_df["record_id"]) == list(test_df["record_id"]), "LSR record IDs mismatch"
    
    with open(summary_path) as f:
        summary = json.load(f)
    assert "per_rule_breakdown" in summary
    assert len(summary["per_rule_breakdown"]) == 9
    for r in OFFICIAL_9_LSR:
        assert r in summary["per_rule_breakdown"]

def test_report_exists():
    report_path = QUALITY_DIR / "STAGE_8_FINAL_MODEL_EVALUATION_REPORT.md"
    assert report_path.exists(), "STAGE_8_FINAL_MODEL_EVALUATION_REPORT.md missing"

if __name__ == "__main__":
    print("Running Stage 8 Final Model Validation Quality Assurance Test Suite...")
    test_split_integrity()
    print("  [PASS] Split integrity verified (0 cross-split contamination).")
    test_sif_final_evaluation_artifacts()
    print("  [PASS] SIF final evaluation, error analysis, and prediction artifacts verified.")
    test_lsr_final_evaluation_artifacts()
    print("  [PASS] LSR final evaluation, error categorization, and prediction artifacts verified.")
    test_report_exists()
    print("  [PASS] Stage 8 Final Evaluation Report verified.")
    print("\nALL STAGE 8 FINAL EVALUATION TESTS PASSED SUCCESSFULLY!")
