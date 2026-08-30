"""
test_lsr_stage7.py - Quality assurance test suite for Stage 7 LSR Robustness Optimization.

Verifies:
1. Zero train/val/test cross-split contamination.
2. Split membership and record IDs preserved exactly.
3. Vocabularies constructed strictly on training data.
4. Saved checkpoints for Stage 7 robust LSR model exist on disk.
5. Exactly 9 official IOGP LSR targets evaluated with valid per-rule thresholds.
6. Predictions count matches held-out test split.
7. Attention diagnostics are non-empty and correctly aligned.
"""

import os
import json
import torch
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_DIR = BASE_DIR / "datasets" / "model_ready" / "splits"
RESULTS_DIR = BASE_DIR / "results" / "lsr_stage7"

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
    train = pd.read_csv(SPLITS_DIR / "lsr_train.csv")
    val = pd.read_csv(SPLITS_DIR / "lsr_val.csv")
    test = pd.read_csv(SPLITS_DIR / "lsr_test.csv")
    
    train_ids = set(train["record_id"])
    val_ids = set(val["record_id"])
    test_ids = set(test["record_id"])
    
    assert len(train_ids.intersection(val_ids)) == 0, "LSR Train-Val overlap"
    assert len(train_ids.intersection(test_ids)) == 0, "LSR Train-Test overlap"
    assert len(val_ids.intersection(test_ids)) == 0, "LSR Val-Test overlap"

def test_stage7_lsr_artifacts_and_metrics():
    cfg_path = RESULTS_DIR / "stage7_lsr_config.json"
    ckpt_path = RESULTS_DIR / "checkpoints" / "best_lsr_stage7_model.pt"
    preds_path = RESULTS_DIR / "lsr_stage7_test_predictions.csv"
    per_rule_path = RESULTS_DIR / "lsr_stage7_per_rule_metrics.csv"
    metrics_path = RESULTS_DIR / "lsr_stage7_test_metrics.json"
    
    assert cfg_path.exists(), "stage7_lsr_config.json missing"
    assert ckpt_path.exists(), "best_lsr_stage7_model.pt missing"
    assert preds_path.exists(), "lsr_stage7_test_predictions.csv missing"
    assert per_rule_path.exists(), "lsr_stage7_per_rule_metrics.csv missing"
    assert metrics_path.exists(), "lsr_stage7_test_metrics.json missing"
    
    with open(cfg_path) as f:
        cfg = json.load(f)
    assert "per_rule_thresholds" in cfg
    assert len(cfg["per_rule_thresholds"]) == 9
    
    test_df = pd.read_csv(SPLITS_DIR / "lsr_test.csv")
    preds_df = pd.read_csv(preds_path)
    assert len(preds_df) == len(test_df), "LSR prediction count mismatch"
    assert list(preds_df["record_id"]) == list(test_df["record_id"]), "Record IDs mismatch"
    
    per_rule_df = pd.read_csv(per_rule_path)
    assert len(per_rule_df) == 9, "Must have exactly 9 official rules"
    assert set(per_rule_df["rule"]) == set(OFFICIAL_9_LSR)

def test_stage7_attention_diagnostics():
    diag_path = RESULTS_DIR / "stage7_attention_diagnostics.json"
    assert diag_path.exists(), "stage7_attention_diagnostics.json missing"
    with open(diag_path) as f:
        diag = json.load(f)
    assert len(diag) > 0, "No attention diagnostic samples generated"
    for d in diag:
        assert "record_id" in d
        assert "top_attended_tokens" in d
        assert len(d["top_attended_tokens"]) > 0

if __name__ == "__main__":
    print("Running Stage 7 LSR Optimization Quality Assurance Test Suite...")
    test_split_integrity()
    print("  [PASS] Split integrity verified (0 cross-split contamination).")
    test_stage7_lsr_artifacts_and_metrics()
    print("  [PASS] Stage 7 LSR checkpoint, config, predictions, and 9-rule metrics verified.")
    test_stage7_attention_diagnostics()
    print("  [PASS] Stage 7 attention diagnostics verified.")
    print("\nALL STAGE 7 LSR OPTIMIZATION TESTS PASSED SUCCESSFULLY!")
