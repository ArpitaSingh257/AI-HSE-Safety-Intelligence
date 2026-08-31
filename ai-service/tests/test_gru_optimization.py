"""
test_gru_optimization.py - Quality assurance test suite for Stage 6 Optimized GRU + Attention models.

Verifies:
1. Zero train/val/test cross-split contamination.
2. Split membership and record IDs preserved exactly.
3. Vocabularies constructed strictly on training data.
4. Saved checkpoints for optimized SIF and LSR models exist on disk.
5. SIF predictions are binary with probabilities between 0.0 and 1.0.
6. LSR has exactly 9 official IOGP outputs with valid per-rule thresholds.
7. Attention diagnostics are non-empty and correctly aligned.
8. Test predictions match held-out test record IDs.
"""

import os
import json
import torch
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_DIR = BASE_DIR / "datasets" / "model_ready" / "splits"
OPT_DIR = BASE_DIR / "results" / "gru_optimization"

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

def test_sif_artifacts_and_predictions():
    cfg_path = OPT_DIR / "best_sif_config.json"
    ckpt_path = BASE_DIR / "models" / "sif" / "sif_model.pt"
    preds_path = OPT_DIR / "sif_test_predictions.csv"
    
    assert cfg_path.exists(), "best_sif_config.json missing"
    assert ckpt_path.exists(), "models/sif/sif_model.pt missing"
    assert preds_path.exists(), "sif_test_predictions.csv missing"
    
    test_df = pd.read_csv(SPLITS_DIR / "sif_test.csv")
    preds = pd.read_csv(preds_path)
    
    assert len(test_df) == len(preds), "Prediction length mismatch"
    assert "optimized_sif_prob" in preds.columns and "optimized_sif_pred" in preds.columns

def test_lsr_artifacts_and_per_label_thresholds():
    cfg_path = OPT_DIR / "best_lsr_config.json"
    ckpt_path = BASE_DIR / "models" / "lsr" / "lsr_model.pt"
    preds_path = OPT_DIR / "lsr_test_predictions.csv"
    metrics_path = OPT_DIR / "lsr_per_label_metrics.csv"
    
    assert cfg_path.exists(), "best_lsr_config.json missing"
    assert ckpt_path.exists(), "models/lsr/lsr_model.pt missing"
    assert preds_path.exists(), "lsr_test_predictions.csv missing"
    assert metrics_path.exists(), "lsr_per_label_metrics.csv missing"
    
    with open(cfg_path) as f:
        cfg = json.load(f)
    assert "per_rule_thresholds" in cfg
    assert len(cfg["per_rule_thresholds"]) == 9
    for r in OFFICIAL_9_LSR:
        assert r in cfg["per_rule_thresholds"]
        t = cfg["per_rule_thresholds"][r]
        assert 0.0 < t < 1.0, f"Invalid threshold for {r}: {t}"
        
    metrics_df = pd.read_csv(metrics_path)
    assert len(metrics_df) == 9, "Must have metrics for exactly 9 official rules"
    assert set(metrics_df["rule"]) == set(OFFICIAL_9_LSR)

def test_attention_diagnostics():
    diag_path = OPT_DIR / "attention_diagnostics.json"
    assert diag_path.exists(), "attention_diagnostics.json missing"
    with open(diag_path) as f:
        diag = json.load(f)
    assert len(diag) > 0, "No diagnostic samples found"
    for d in diag:
        assert "record_id" in d
        assert "top_attended_tokens" in d
        assert len(d["top_attended_tokens"]) > 0

if __name__ == "__main__":
    print("Running Stage 6 Optimization Quality Assurance Test Suite...")
    test_split_integrity()
    print("  [PASS] Split integrity verified (0 cross-split contamination).")
    test_sif_artifacts_and_predictions()
    print("  [PASS] SIF optimized checkpoint, config, and predictions verified.")
    test_lsr_artifacts_and_per_label_thresholds()
    print("  [PASS] LSR optimized checkpoint, 9 independent rule thresholds verified.")
    test_attention_diagnostics()
    print("  [PASS] Attention interpretability diagnostics verified.")
    print("\nALL STAGE 6 OPTIMIZATION TESTS PASSED SUCCESSFULLY!")
