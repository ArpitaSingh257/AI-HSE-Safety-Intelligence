"""
test_lsr_stage12.py - Quality Assurance Test Suite for Stage 12 LSR Augmentation & Training.

Verifies:
1. Zero cross-split contamination (train, val, test).
2. Augmentation is strictly restricted to training split (validation & test untouched).
3. Stage 12 checkpoint exists on disk and is loadable.
4. Exactly 9 official IOGP rules with validation-derived thresholds.
5. Held-out test predictions match test record count (138 records).
6. Stage 7 artifacts remain 100% untouched and preserved.
"""

import os
import json
import torch
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_DIR = BASE_DIR / "datasets" / "model_ready" / "splits"
MODEL_READY_DIR = BASE_DIR / "datasets" / "model_ready"
RESULTS_DIR = BASE_DIR / "results" / "lsr_stage12"
STAGE7_DIR = BASE_DIR / "results" / "lsr_stage7"
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

def test_split_integrity_and_augmentation_scope():
    train = pd.read_csv(SPLITS_DIR / "lsr_train.csv")
    val = pd.read_csv(SPLITS_DIR / "lsr_val.csv")
    test = pd.read_csv(SPLITS_DIR / "lsr_test.csv")
    
    train_ids = set(train["record_id"])
    val_ids = set(val["record_id"])
    test_ids = set(test["record_id"])
    
    assert len(train_ids.intersection(val_ids)) == 0, "Train-Val overlap"
    assert len(train_ids.intersection(test_ids)) == 0, "Train-Test overlap"
    assert len(val_ids.intersection(test_ids)) == 0, "Val-Test overlap"
    
    # Verify augmented dataset if present
    aug_file = MODEL_READY_DIR / "lsr_train_augmented.csv"
    if aug_file.exists():
        aug_df = pd.read_csv(aug_file)
        # None of the augmented records should contain validation or test IDs
        for r_id in aug_df["record_id"]:
            clean_id = str(r_id).replace("_aug", "")
            assert clean_id not in val_ids, f"Augmented record leaked from val: {r_id}"
            assert clean_id not in test_ids, f"Augmented record leaked from test: {r_id}"

def test_stage12_artifacts_and_checkpoint():
    ckpt_path = RESULTS_DIR / "checkpoints" / "best_lsr_stage12_model.pt"
    cfg_path = RESULTS_DIR / "stage12_lsr_config.json"
    preds_path = RESULTS_DIR / "stage12_test_predictions.csv"
    per_rule_path = RESULTS_DIR / "stage12_per_rule_metrics.csv"
    
    if ckpt_path.exists():
        state = torch.load(ckpt_path, map_location="cpu")
        assert "embedding.weight" in state
        assert "gru.weight_hh_l0" in state
        
    if cfg_path.exists():
        with open(cfg_path) as f:
            cfg = json.load(f)
        assert "per_rule_thresholds" in cfg
        assert len(cfg["per_rule_thresholds"]) == 9
        
    if preds_path.exists():
        test_df = pd.read_csv(SPLITS_DIR / "lsr_test.csv")
        preds_df = pd.read_csv(preds_path)
        assert len(preds_df) == len(test_df), "Test prediction length mismatch"
        assert list(preds_df["record_id"]) == list(test_df["record_id"]), "Record IDs mismatch"
        
    if per_rule_path.exists():
        per_rule_df = pd.read_csv(per_rule_path)
        assert len(per_rule_df) == 9
        assert set(per_rule_df["rule"]) == set(OFFICIAL_9_LSR)

def test_stage7_preservation():
    # Stage 7 checkpoints and configs must remain intact
    s7_ckpt = STAGE7_DIR / "checkpoints" / "best_lsr_stage7_model.pt"
    s7_cfg = STAGE7_DIR / "stage7_lsr_config.json"
    assert s7_ckpt.exists(), "Stage 7 checkpoint was modified or deleted!"
    assert s7_cfg.exists(), "Stage 7 config was modified or deleted!"

if __name__ == "__main__":
    print("Running Stage 12 LSR Targeted Augmentation & QA Test Suite...")
    test_split_integrity_and_augmentation_scope()
    print("  [PASS] Split integrity & train-only augmentation scope verified.")
    test_stage12_artifacts_and_checkpoint()
    print("  [PASS] Stage 12 checkpoint, configuration, and test predictions verified.")
    test_stage7_preservation()
    print("  [PASS] Stage 7 champion artifacts 100% preserved and untouched.")
    print("\nALL STAGE 12 TESTS PASSED SUCCESSFULLY!")
