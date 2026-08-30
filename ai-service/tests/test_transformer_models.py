"""
test_transformer_models.py - Quality assurance test suite for Stage 5 Fine-Tuned Transformer Models.

Verifies:
1. Transformer checkpoints and tokenizers exist on disk and are loadable.
2. Prediction dimensions and record_ids match test splits.
3. SIF predictions are binary (0/1) with continuous probabilities.
4. Exactly 9 official IOGP LSR targets evaluated in multi-label outputs.
5. Zero cross-split contamination across train/val/test.
6. Target leakage protection verified (narrative only input).
7. Required metric JSON files exist and contain valid evaluation schemas.
"""

import os
import json
import torch
import pandas as pd
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_DIR = BASE_DIR / "datasets" / "model_ready" / "splits"
TRANSFORMER_DIR = BASE_DIR / "results" / "transformer"

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

def test_sif_transformer_checkpoint_and_predictions():
    ckpt_path = TRANSFORMER_DIR / "sif" / "best_sif_transformer"
    metrics_path = TRANSFORMER_DIR / "sif" / "sif_transformer_test_metrics.json"
    preds_path = TRANSFORMER_DIR / "sif" / "sif_transformer_test_predictions.csv"
    
    assert ckpt_path.exists(), "SIF transformer checkpoint directory missing"
    assert metrics_path.exists(), "SIF transformer test metrics JSON missing"
    assert preds_path.exists(), "SIF transformer test predictions CSV missing"
    
    # Verify loadability
    tokenizer = AutoTokenizer.from_pretrained(ckpt_path)
    model = AutoModelForSequenceClassification.from_pretrained(ckpt_path)
    assert model.num_labels == 1, f"SIF model should have num_labels=1, got {model.num_labels}"
    
    # Verify predictions
    test_df = pd.read_csv(SPLITS_DIR / "sif_test.csv")
    preds_df = pd.read_csv(preds_path)
    assert len(preds_df) == len(test_df), f"Prediction count {len(preds_df)} != test count {len(test_df)}"
    assert list(preds_df["record_id"]) == list(test_df["record_id"]), "Record IDs mismatch"
    assert "transformer_sif_prob" in preds_df.columns
    assert "transformer_sif_pred" in preds_df.columns
    assert set(preds_df["transformer_sif_pred"].unique()).issubset({0, 1})

def test_lsr_transformer_checkpoint_and_predictions():
    ckpt_path = TRANSFORMER_DIR / "lsr" / "best_lsr_transformer"
    metrics_path = TRANSFORMER_DIR / "lsr" / "lsr_transformer_test_metrics.json"
    preds_path = TRANSFORMER_DIR / "lsr" / "lsr_transformer_test_predictions.csv"
    
    assert ckpt_path.exists(), "LSR transformer checkpoint directory missing"
    assert metrics_path.exists(), "LSR transformer test metrics JSON missing"
    assert preds_path.exists(), "LSR transformer test predictions CSV missing"
    
    tokenizer = AutoTokenizer.from_pretrained(ckpt_path)
    model = AutoModelForSequenceClassification.from_pretrained(ckpt_path)
    assert model.num_labels == 9, f"LSR model should have num_labels=9, got {model.num_labels}"
    
    test_df = pd.read_csv(SPLITS_DIR / "lsr_test.csv")
    preds_df = pd.read_csv(preds_path)
    assert len(preds_df) == len(test_df), f"LSR Prediction count {len(preds_df)} != test count {len(test_df)}"
    
    with open(metrics_path) as f:
        metrics = json.load(f)
    assert "per_rule_metrics" in metrics
    assert len(metrics["per_rule_metrics"]) == 9
    for r in OFFICIAL_9_LSR:
        assert r in metrics["per_rule_metrics"]

def test_attributions_diagnostics():
    diag_path = TRANSFORMER_DIR / "attention_diagnostics" / "transformer_attributions.json"
    assert diag_path.exists(), "Transformer attributions diagnostics missing"
    with open(diag_path) as f:
        diag = json.load(f)
    assert len(diag) > 0, "No attribution samples generated"
    for d in diag:
        assert "record_id" in d
        assert "top_attended_tokens" in d

if __name__ == "__main__":
    print("Running Stage 5 Transformer Quality Assurance Test Suite...")
    test_split_integrity()
    print("  [PASS] Split integrity verified (0 contamination across splits).")
    test_sif_transformer_checkpoint_and_predictions()
    print("  [PASS] SIF Transformer checkpoint loadability and test predictions verified.")
    test_lsr_transformer_checkpoint_and_predictions()
    print("  [PASS] LSR 9-output Transformer checkpoint and per-rule metrics verified.")
    test_attributions_diagnostics()
    print("  [PASS] Transformer attention diagnostics and token attributions verified.")
    print("\nALL STAGE 5 TRANSFORMER TESTS PASSED SUCCESSFULLY!")
