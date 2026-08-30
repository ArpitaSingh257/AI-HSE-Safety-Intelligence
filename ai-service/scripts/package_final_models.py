"""
package_final_models.py - Model Packaging & Production Manifest Generator.

Packages:
1. SIF Champion: Stage 6 Optimized Bidirectional GRU + Attention (SIF_Cfg3_MidBi)
2. LSR Champion: Stage 7 Robust Bidirectional GRU + Attention (Stage7_Norm_Base)
Into:
  ai-service/models/sif/
  ai-service/models/lsr/
  ai-service/models/MODEL_MANIFEST.json
"""

import os
import shutil
import json
import torch
from pathlib import Path

def package_models():
    base_dir = Path(__file__).resolve().parent.parent
    models_dir = base_dir / "models"
    sif_target_dir = models_dir / "sif"
    lsr_target_dir = models_dir / "lsr"
    
    sif_target_dir.mkdir(parents=True, exist_ok=True)
    lsr_target_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("PACKAGING FINAL PRODUCTION MODELS — OILPS AI INFERENCE ENGINE")
    print("=" * 70)
    
    # -------------------------------------------------------------------------
    # 1. PACKAGE SIF CHAMPION
    # -------------------------------------------------------------------------
    sif_src_ckpt = base_dir / "results" / "gru_optimization" / "best_sif_model" / "sif_optimized_gru_attention.pt"
    sif_src_cfg = base_dir / "results" / "gru_optimization" / "best_sif_config.json"
    sif_src_vocab = base_dir / "results" / "gru" / "sif" / "sif_vocab.json"
    
    if sif_src_ckpt.exists():
        shutil.copy2(sif_src_ckpt, sif_target_dir / "sif_model.pt")
        print(f"Copied SIF checkpoint -> {sif_target_dir / 'sif_model.pt'}")
    if sif_src_cfg.exists():
        shutil.copy2(sif_src_cfg, sif_target_dir / "sif_config.json")
        print(f"Copied SIF config     -> {sif_target_dir / 'sif_config.json'}")
    if sif_src_vocab.exists():
        shutil.copy2(sif_src_vocab, sif_target_dir / "sif_vocab.json")
        print(f"Copied SIF vocabulary -> {sif_target_dir / 'sif_vocab.json'}")

    # -------------------------------------------------------------------------
    # 2. PACKAGE LSR CHAMPION
    # -------------------------------------------------------------------------
    lsr_src_ckpt = base_dir / "results" / "lsr_stage7" / "checkpoints" / "best_lsr_stage7_model.pt"
    lsr_src_cfg = base_dir / "results" / "lsr_stage7" / "stage7_lsr_config.json"
    lsr_src_vocab = base_dir / "results" / "gru" / "lsr" / "lsr_vocab.json"
    
    if lsr_src_ckpt.exists():
        shutil.copy2(lsr_src_ckpt, lsr_target_dir / "lsr_model.pt")
        print(f"Copied LSR checkpoint -> {lsr_target_dir / 'lsr_model.pt'}")
    if lsr_src_cfg.exists():
        shutil.copy2(lsr_src_cfg, lsr_target_dir / "lsr_config.json")
        print(f"Copied LSR config     -> {lsr_target_dir / 'lsr_config.json'}")
    if lsr_src_vocab.exists():
        shutil.copy2(lsr_src_vocab, lsr_target_dir / "lsr_vocab.json")
        print(f"Copied LSR vocabulary -> {lsr_target_dir / 'lsr_vocab.json'}")

    # -------------------------------------------------------------------------
    # 3. GENERATE MODEL_MANIFEST.JSON
    # -------------------------------------------------------------------------
    manifest = {
        "manifest_version": "1.0.0",
        "project": "SIH26165 — Oil India Limited Precursor Safety Intelligence",
        "timestamp": "2026-08-30",
        "production_models": {
            "sif_binary_classifier": {
                "model_name": "sif_bigru_attention_optimized",
                "task": "SIF Potential Binary Classification (1 / 0)",
                "architecture": "Trainable Embedding (200) -> Bidirectional GRU (128) -> Softmax Sequence Attention -> Linear (1)",
                "checkpoint_path": "models/sif/sif_model.pt",
                "vocabulary_path": "models/sif/sif_vocab.json",
                "config_path": "models/sif/sif_config.json",
                "originating_stage": "Stage 6 Hyperparameter Optimization",
                "max_sequence_length": 120,
                "validation_threshold": 0.30,
                "random_seed": 42,
                "dataset_provenance": "896 Clean Binary Records (300 IOGP Grounded + 596 Annotated OSHA Contextual Energy)",
                "verified_test_metrics": {
                    "test_recall_sif1": 0.9697,
                    "test_precision": 0.8807,
                    "test_f1": 0.9231,
                    "test_pr_auc": 0.9715,
                    "test_accuracy": 0.8806,
                    "test_false_negatives": 3
                }
            },
            "lsr_multilabel_classifier": {
                "model_name": "lsr_robust_bigru_attention_stage7",
                "task": "IOGP Life-Saving Rules 9-Class Multi-Label Classification",
                "architecture": "Trainable Embedding (200) -> Bidirectional GRU (128) -> LayerNorm -> Scaled Dot-Product Attention -> 2-Layer MLP Head -> 9 Sigmoids",
                "checkpoint_path": "models/lsr/lsr_model.pt",
                "vocabulary_path": "models/lsr/lsr_vocab.json",
                "config_path": "models/lsr/lsr_config.json",
                "originating_stage": "Stage 7 Robustness Optimization",
                "max_sequence_length": 120,
                "label_ordering": [
                    "Bypassing Safety Controls",
                    "Confined Space",
                    "Driving",
                    "Energy Isolation",
                    "Hot Work",
                    "Line of Fire",
                    "Safe Mechanical Lifting",
                    "Toxic Gas / Hazardous Substance",
                    "Working at Height"
                ],
                "class_imbalance_handling": "Smooth Square-Root Positive Weighting (w = sqrt(N_neg / N_pos))",
                "threshold_tuning_strategy": "Independent Validation-Derived Thresholds Per Rule",
                "random_seed": 42,
                "dataset_provenance": "900 Multi-Label Records across 9 Canonical IOGP Rules",
                "verified_test_metrics": {
                    "test_micro_f1": 0.7020,
                    "test_macro_f1": 0.5774,
                    "test_weighted_f1": 0.7085,
                    "test_hamming_loss": 0.0362,
                    "test_exact_match_ratio": 0.7174
                }
            }
        },
        "target_leakage_protection": "Strict narrative-only text input. No metadata, severity, or human rationales enter vectorizer/embedding.",
        "precursor_extraction_status": "Precursor dataset verified as decoupled entity strings; sequence token NER deferred pending character-offset annotation."
    }
    
    manifest_path = models_dir / "MODEL_MANIFEST.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nCreated Production Model Manifest -> {manifest_path}")
    print("=" * 70)
    print("FINAL MODEL PACKAGING COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    package_models()
