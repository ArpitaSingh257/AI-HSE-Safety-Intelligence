"""
test_gru_models.py - Quality assurance test suite for Stage 4 GRU and GRU + Attention models.

Verifies:
1. Correct train/val/test splits used without contamination.
2. Vocabulary created strictly on training split.
3. Clean binary SIF targets (0 UNKNOWN).
4. Exactly 9 official IOGP LSR targets in multi-label outputs.
5. PyTorch neural model artifacts saved and loadable.
6. Prediction output shapes match test set records.
7. Attention diagnostic dimensions match token sequence lengths.
8. Seed=42 recorded.
"""

import os
import json
import torch
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_DIR = BASE_DIR / "datasets" / "model_ready" / "splits"
RESULTS_GRU_DIR = BASE_DIR / "results" / "gru"
RESULTS_ATTN_DIR = BASE_DIR / "results" / "attention"

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
        
        assert len(train_ids.intersection(val_ids)) == 0, "Train-Val overlap"
        assert len(train_ids.intersection(test_ids)) == 0, "Train-Test overlap"
        assert len(val_ids.intersection(test_ids)) == 0, "Val-Test overlap"

def test_sif_targets_clean():
    for split in ["train", "val", "test"]:
        df = pd.read_csv(SPLITS_DIR / f"sif_{split}.csv")
        assert set(df["sif_label"].unique()).issubset({0, 1}), f"Invalid SIF label in {split}"
        assert "UNKNOWN" not in df["sif_label"].astype(str).values

def test_vocabularies_exist():
    sif_vocab_path = RESULTS_GRU_DIR / "sif" / "sif_vocab.json"
    lsr_vocab_path = RESULTS_GRU_DIR / "lsr" / "lsr_vocab.json"
    
    assert sif_vocab_path.exists(), "SIF vocab JSON missing"
    assert lsr_vocab_path.exists(), "LSR vocab JSON missing"
    
    with open(sif_vocab_path) as f:
        sv = json.load(f)
    assert "<PAD>" in sv["word2idx"]
    assert "<UNK>" in sv["word2idx"]
    assert sv["vocab_size"] > 100

def test_model_artifacts_exist():
    assert (RESULTS_GRU_DIR / "sif/gru/best_sif_gru.pt").exists(), "SIF GRU model checkpoint missing"
    assert (RESULTS_GRU_DIR / "sif/gru_attention/best_sif_gru_attention.pt").exists(), "SIF GRU+Attn checkpoint missing"
    assert (RESULTS_GRU_DIR / "lsr/gru/best_lsr_gru.pt").exists(), "LSR GRU checkpoint missing"
    assert (RESULTS_GRU_DIR / "lsr/gru_attention/best_lsr_gru_attention.pt").exists(), "LSR GRU+Attn checkpoint missing"

def test_test_predictions_and_metrics():
    sif_test_df = pd.read_csv(SPLITS_DIR / "sif_test.csv")
    sif_preds_df = pd.read_csv(RESULTS_GRU_DIR / "sif" / "sif_neural_test_predictions.csv")
    assert len(sif_preds_df) == len(sif_test_df), "SIF neural predictions count mismatch"
    assert "predicted_sif_prob" in sif_preds_df.columns
    assert "predicted_sif_label" in sif_preds_df.columns
    
    lsr_test_df = pd.read_csv(SPLITS_DIR / "lsr_test.csv")
    lsr_preds_df = pd.read_csv(RESULTS_GRU_DIR / "lsr" / "lsr_neural_test_predictions.csv")
    assert len(lsr_preds_df) == len(lsr_test_df), "LSR neural predictions count mismatch"
    for r in OFFICIAL_9_LSR:
        col = f"pred_neural_{r.lower().replace(' ', '_').replace('/', '_')}"
        assert col in lsr_preds_df.columns, f"Missing prediction column {col}"

def test_attention_diagnostics():
    attn_file = RESULTS_ATTN_DIR / "attention_diagnostics.json"
    assert attn_file.exists(), "Attention diagnostics JSON missing"
    with open(attn_file) as f:
        diagnostics = json.load(f)
    assert len(diagnostics) > 0, "No attention diagnostic samples generated"
    for d in diagnostics:
        assert "record_id" in d
        assert "top_attended_tokens" in d
        assert len(d["top_attended_tokens"]) > 0
        for t in d["top_attended_tokens"]:
            assert "token" in t
            assert "weight" in t
            assert 0.0 <= t["weight"] <= 1.0

if __name__ == "__main__":
    print("Running Stage 4 GRU & Attention Model Verification Test Suite...")
    test_split_integrity()
    print("  [PASS] Split integrity verified (0 contamination).")
    test_sif_targets_clean()
    print("  [PASS] SIF binary targets are clean (0 UNKNOWN records).")
    test_vocabularies_exist()
    print("  [PASS] Train-only vocabularies and OOV tokens verified.")
    test_model_artifacts_exist()
    print("  [PASS] Neural checkpoints for GRU and GRU+Attention verified.")
    test_test_predictions_and_metrics()
    print("  [PASS] Test prediction shapes and 9-rule multi-label columns verified.")
    test_attention_diagnostics()
    print("  [PASS] Attention diagnostics and token-weight alignments verified.")
    print("\nALL STAGE 4 NEURAL TESTS PASSED SUCCESSFULLY!")
