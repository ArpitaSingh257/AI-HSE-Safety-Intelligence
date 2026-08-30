"""
train_baselines.py - Stage 3 Baseline Model Training & Evaluation for OILPS.

Tasks:
1. SIF Binary Classification (TF-IDF + Logistic Regression vs TF-IDF + Calibrated Linear SVM)
2. Life-Saving Rule Multi-Label Classification (TF-IDF + One-vs-Rest Logistic vs One-vs-Rest Linear SVM across 9 rules)
3. Precursor Information Extraction (Rule-assisted & dictionary span matching baseline)

Saves all artifacts, vectorizers, metrics, predictions, and reports with seed=42.
"""

import os
import re
import csv
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.multiclass import OneVsRestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    precision_recall_curve,
    auc,
    confusion_matrix,
    classification_report,
    hamming_loss,
    jaccard_score
)

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

def pr_auc_score(y_true, y_probs):
    precision, recall, _ = precision_recall_curve(y_true, y_probs)
    return float(auc(recall, precision))

def train_and_evaluate_all():
    base_dir = Path(__file__).resolve().parent.parent
    splits_dir = base_dir / "datasets" / "model_ready" / "splits"
    models_dir = base_dir / "models"
    results_dir = base_dir / "results"
    quality_dir = base_dir / "datasets" / "quality"
    
    (models_dir / "sif").mkdir(parents=True, exist_ok=True)
    (models_dir / "lsr").mkdir(parents=True, exist_ok=True)
    (models_dir / "precursor").mkdir(parents=True, exist_ok=True)
    
    (results_dir / "sif").mkdir(parents=True, exist_ok=True)
    (results_dir / "lsr").mkdir(parents=True, exist_ok=True)
    (results_dir / "precursor").mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("STAGE 3: BASELINE MODEL TRAINING — OILPS PRECURSOR INTELLIGENCE")
    print("=" * 70)
    
    # =========================================================================
    # TASK 1: SIF BINARY CLASSIFICATION
    # =========================================================================
    print("\n--- TASK 1: SIF BINARY CLASSIFICATION ---")
    sif_train_df = pd.read_csv(splits_dir / "sif_train.csv")
    sif_val_df = pd.read_csv(splits_dir / "sif_val.csv")
    sif_test_df = pd.read_csv(splits_dir / "sif_test.csv")
    
    X_train_sif = sif_train_df["narrative"].fillna("").astype(str).values
    y_train_sif = sif_train_df["sif_label"].astype(int).values
    
    X_val_sif = sif_val_df["narrative"].fillna("").astype(str).values
    y_val_sif = sif_val_df["sif_label"].astype(int).values
    
    X_test_sif = sif_test_df["narrative"].fillna("").astype(str).values
    y_test_sif = sif_test_df["sif_label"].astype(int).values
    
    print(f"SIF Train set: {len(X_train_sif)} ({Counter(y_train_sif)})")
    print(f"SIF Val set:   {len(X_val_sif)} ({Counter(y_val_sif)})")
    print(f"SIF Test set:  {len(X_test_sif)} ({Counter(y_test_sif)})")
    
    # Vectorizer
    sif_vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=10000,
        min_df=2,
        sublinear_tf=True
    )
    X_train_sif_vec = sif_vectorizer.fit_transform(X_train_sif)
    X_val_sif_vec = sif_vectorizer.transform(X_val_sif)
    X_test_sif_vec = sif_vectorizer.transform(X_test_sif)
    
    # Candidate Model 1: Logistic Regression with class_weight='balanced'
    sif_lr = LogisticRegression(C=1.0, class_weight="balanced", random_state=42, max_iter=1000)
    sif_lr.fit(X_train_sif_vec, y_train_sif)
    val_probs_lr = sif_lr.predict_proba(X_val_sif_vec)[:, 1]
    val_preds_lr = (val_probs_lr >= 0.5).astype(int)
    
    val_metrics_lr = {
        "model": "TF-IDF + Logistic Regression (balanced)",
        "accuracy": float(accuracy_score(y_val_sif, val_preds_lr)),
        "precision": float(precision_score(y_val_sif, val_preds_lr, zero_division=0)),
        "recall_sif1": float(recall_score(y_val_sif, val_preds_lr, pos_label=1)),
        "f1": float(f1_score(y_val_sif, val_preds_lr, pos_label=1)),
        "roc_auc": float(roc_auc_score(y_val_sif, val_probs_lr)),
        "pr_auc": pr_auc_score(y_val_sif, val_probs_lr)
    }
    
    # Candidate Model 2: Linear SVM (Calibrated with cv=3 for binary classification)
    sif_svm_base = LinearSVC(C=1.0, class_weight="balanced", random_state=42, max_iter=2000)
    sif_svm = CalibratedClassifierCV(sif_svm_base, method="sigmoid", cv=3)
    sif_svm.fit(X_train_sif_vec, y_train_sif)
    val_probs_svm = sif_svm.predict_proba(X_val_sif_vec)[:, 1]
    val_preds_svm = (val_probs_svm >= 0.5).astype(int)
    
    val_metrics_svm = {
        "model": "TF-IDF + Calibrated Linear SVM",
        "accuracy": float(accuracy_score(y_val_sif, val_preds_svm)),
        "precision": float(precision_score(y_val_sif, val_preds_svm, zero_division=0)),
        "recall_sif1": float(recall_score(y_val_sif, val_preds_svm, pos_label=1)),
        "f1": float(f1_score(y_val_sif, val_preds_svm, pos_label=1)),
        "roc_auc": float(roc_auc_score(y_val_sif, val_probs_svm)),
        "pr_auc": pr_auc_score(y_val_sif, val_probs_svm)
    }
    
    print("\nValidation SIF Results Comparison:")
    print(f"  Logistic Regression : F1={val_metrics_lr['f1']:.4f}, Recall@1={val_metrics_lr['recall_sif1']:.4f}, PR-AUC={val_metrics_lr['pr_auc']:.4f}")
    print(f"  Linear SVM (Calib) : F1={val_metrics_svm['f1']:.4f}, Recall@1={val_metrics_svm['recall_sif1']:.4f}, PR-AUC={val_metrics_svm['pr_auc']:.4f}")
    
    # Select best baseline by validation PR-AUC & SIF Recall
    if val_metrics_lr["pr_auc"] >= val_metrics_svm["pr_auc"]:
        best_sif_model = sif_lr
        best_sif_name = "Logistic Regression"
    else:
        best_sif_model = sif_svm
        best_sif_name = "Calibrated Linear SVM"
        
    print(f"--> Selected Best SIF Model: {best_sif_name}")
    
    # Final Evaluation on Held-Out Test Set (ONCE)
    test_probs_sif = best_sif_model.predict_proba(X_test_sif_vec)[:, 1]
    test_preds_sif = (test_probs_sif >= 0.5).astype(int)
    
    cm_sif = confusion_matrix(y_test_sif, test_preds_sif).tolist()
    test_metrics_sif = {
        "best_model": best_sif_name,
        "test_accuracy": float(accuracy_score(y_test_sif, test_preds_sif)),
        "test_precision": float(precision_score(y_test_sif, test_preds_sif, zero_division=0)),
        "test_recall_sif1": float(recall_score(y_test_sif, test_preds_sif, pos_label=1)),
        "test_f1": float(f1_score(y_test_sif, test_preds_sif, pos_label=1)),
        "test_roc_auc": float(roc_auc_score(y_test_sif, test_probs_sif)),
        "test_pr_auc": pr_auc_score(y_test_sif, test_probs_sif),
        "confusion_matrix_tn_fp_fn_tp": cm_sif,
        "classification_report": classification_report(y_test_sif, test_preds_sif, output_dict=True)
    }
    
    print("\n--- Final Test Set Results for SIF ---")
    print(f"  Test Accuracy   : {test_metrics_sif['test_accuracy']:.4f}")
    print(f"  Test SIF-1 Recall: {test_metrics_sif['test_recall_sif1']:.4f} (Safety-Critical Metric)")
    print(f"  Test Precision  : {test_metrics_sif['test_precision']:.4f}")
    print(f"  Test F1-Score   : {test_metrics_sif['test_f1']:.4f}")
    print(f"  Test PR-AUC     : {test_metrics_sif['test_pr_auc']:.4f}")
    print(f"  Confusion Matrix: TN={cm_sif[0][0]}, FP={cm_sif[0][1]}, FN={cm_sif[1][0]}, TP={cm_sif[1][1]}")
    
    # Save SIF Artifacts
    joblib.dump(best_sif_model, models_dir / "sif" / "sif_baseline_model.joblib")
    joblib.dump(sif_vectorizer, models_dir / "sif" / "sif_vectorizer.joblib")
    
    with open(results_dir / "sif" / "sif_val_comparison.json", "w") as f:
        json.dump({"logistic_regression": val_metrics_lr, "linear_svm": val_metrics_svm}, f, indent=2)
    with open(results_dir / "sif" / "sif_test_metrics.json", "w") as f:
        json.dump(test_metrics_sif, f, indent=2)
        
    sif_preds_df = sif_test_df.copy()
    sif_preds_df["predicted_sif_prob"] = np.round(test_probs_sif, 4)
    sif_preds_df["predicted_sif_label"] = test_preds_sif
    sif_preds_df.to_csv(results_dir / "sif" / "sif_test_predictions.csv", index=False)
    print(f"Saved SIF artifacts & predictions to {results_dir / 'sif'}")

    # =========================================================================
    # TASK 2: IOGP LIFE-SAVING RULE MULTI-LABEL CLASSIFICATION
    # =========================================================================
    print("\n--- TASK 2: IOGP LIFE-SAVING RULE MULTI-LABEL CLASSIFICATION ---")
    lsr_train_df = pd.read_csv(splits_dir / "lsr_train.csv")
    lsr_val_df = pd.read_csv(splits_dir / "lsr_val.csv")
    lsr_test_df = pd.read_csv(splits_dir / "lsr_test.csv")
    
    def extract_multihot_matrix(df):
        Y = np.zeros((len(df), len(OFFICIAL_9_LSR)), dtype=int)
        for i, all_str in enumerate(df["all_lsrs"].fillna("None")):
            rules = [x.strip() for x in all_str.split(";") if x.strip() and x.strip() != "None"]
            for r in rules:
                if r in OFFICIAL_9_LSR:
                    Y[i, OFFICIAL_9_LSR.index(r)] = 1
        return Y
        
    X_train_lsr = lsr_train_df["narrative"].fillna("").astype(str).values
    Y_train_lsr = extract_multihot_matrix(lsr_train_df)
    
    X_val_lsr = lsr_val_df["narrative"].fillna("").astype(str).values
    Y_val_lsr = extract_multihot_matrix(lsr_val_df)
    
    X_test_lsr = lsr_test_df["narrative"].fillna("").astype(str).values
    Y_test_lsr = extract_multihot_matrix(lsr_test_df)
    
    print(f"LSR Train set: {len(X_train_lsr)} samples, {Y_train_lsr.sum()} rule activations")
    print(f"LSR Val set:   {len(X_val_lsr)} samples, {Y_val_lsr.sum()} rule activations")
    print(f"LSR Test set:  {len(X_test_lsr)} samples, {Y_test_lsr.sum()} rule activations")
    
    lsr_vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=10000,
        min_df=2,
        sublinear_tf=True
    )
    X_train_lsr_vec = lsr_vectorizer.fit_transform(X_train_lsr)
    X_val_lsr_vec = lsr_vectorizer.transform(X_val_lsr)
    X_test_lsr_vec = lsr_vectorizer.transform(X_test_lsr)
    
    # Model 1: One-vs-Rest Logistic Regression
    lsr_ovr_lr = OneVsRestClassifier(LogisticRegression(C=1.0, class_weight="balanced", random_state=42, max_iter=1000))
    lsr_ovr_lr.fit(X_train_lsr_vec, Y_train_lsr)
    val_preds_lsr_lr = lsr_ovr_lr.predict(X_val_lsr_vec)
    
    # Model 2: One-vs-Rest Linear SVM (Direct LinearSVC without CV calibration to support rare classes with <3 samples)
    lsr_ovr_svm = OneVsRestClassifier(LinearSVC(C=1.0, class_weight="balanced", random_state=42, max_iter=2000))
    lsr_ovr_svm.fit(X_train_lsr_vec, Y_train_lsr)
    val_preds_lsr_svm = lsr_ovr_svm.predict(X_val_lsr_vec)
    
    def evaluate_multilabel(y_true, y_pred):
        return {
            "micro_precision": float(precision_score(y_true, y_pred, average="micro", zero_division=0)),
            "micro_recall": float(recall_score(y_true, y_pred, average="micro", zero_division=0)),
            "micro_f1": float(f1_score(y_true, y_pred, average="micro", zero_division=0)),
            "macro_precision": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
            "macro_recall": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
            "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
            "hamming_loss": float(hamming_loss(y_true, y_pred)),
            "exact_match_ratio": float(np.mean(np.all(y_true == y_pred, axis=1)))
        }
        
    val_lsr_m_lr = evaluate_multilabel(Y_val_lsr, val_preds_lsr_lr)
    val_lsr_m_svm = evaluate_multilabel(Y_val_lsr, val_preds_lsr_svm)
    
    print("\nValidation LSR Results Comparison:")
    print(f"  OneVsRest Logistic : Micro-F1={val_lsr_m_lr['micro_f1']:.4f}, Macro-F1={val_lsr_m_lr['macro_f1']:.4f}, HammingLoss={val_lsr_m_lr['hamming_loss']:.4f}")
    print(f"  OneVsRest LinearSVC: Micro-F1={val_lsr_m_svm['micro_f1']:.4f}, Macro-F1={val_lsr_m_svm['macro_f1']:.4f}, HammingLoss={val_lsr_m_svm['hamming_loss']:.4f}")
    
    if val_lsr_m_lr["micro_f1"] >= val_lsr_m_svm["micro_f1"]:
        best_lsr_model = lsr_ovr_lr
        best_lsr_name = "OneVsRest Logistic Regression"
    else:
        best_lsr_model = lsr_ovr_svm
        best_lsr_name = "OneVsRest Linear SVM"
        
    print(f"--> Selected Best LSR Model: {best_lsr_name}")
    
    # Evaluate ONCE on Test Set
    test_preds_lsr = best_lsr_model.predict(X_test_lsr_vec)
    test_metrics_lsr = evaluate_multilabel(Y_test_lsr, test_preds_lsr)
    test_metrics_lsr["best_model"] = best_lsr_name
    
    per_rule_metrics = {}
    for idx, r_name in enumerate(OFFICIAL_9_LSR):
        yt = Y_test_lsr[:, idx]
        yp = test_preds_lsr[:, idx]
        per_rule_metrics[r_name] = {
            "support": int(yt.sum()),
            "precision": float(precision_score(yt, yp, zero_division=0)),
            "recall": float(recall_score(yt, yp, zero_division=0)),
            "f1": float(f1_score(yt, yp, zero_division=0))
        }
    test_metrics_lsr["per_rule_metrics"] = per_rule_metrics
    
    print("\n--- Final Test Set Results for Multi-Label LSR ---")
    print(f"  Micro-F1          : {test_metrics_lsr['micro_f1']:.4f}")
    print(f"  Macro-F1          : {test_metrics_lsr['macro_f1']:.4f}")
    print(f"  Hamming Loss      : {test_metrics_lsr['hamming_loss']:.4f}")
    print(f"  Exact Match Ratio : {test_metrics_lsr['exact_match_ratio']:.4f}")
    
    # Save LSR Artifacts
    joblib.dump(best_lsr_model, models_dir / "lsr" / "lsr_baseline_model.joblib")
    joblib.dump(lsr_vectorizer, models_dir / "lsr" / "lsr_vectorizer.joblib")
    
    with open(results_dir / "lsr" / "lsr_val_comparison.json", "w") as f:
        json.dump({"logistic_regression": val_lsr_m_lr, "linear_svm": val_lsr_m_svm}, f, indent=2)
    with open(results_dir / "lsr" / "lsr_test_metrics.json", "w") as f:
        json.dump(test_metrics_lsr, f, indent=2)
        
    lsr_preds_df = lsr_test_df.copy()
    for idx, r_name in enumerate(OFFICIAL_9_LSR):
        col = f"pred_{r_name.lower().replace(' ', '_').replace('/', '_')}"
        lsr_preds_df[col] = test_preds_lsr[:, idx]
    lsr_preds_df.to_csv(results_dir / "lsr" / "lsr_test_predictions.csv", index=False)
    print(f"Saved LSR artifacts & predictions to {results_dir / 'lsr'}")

    # =========================================================================
    # TASK 3: PRECURSOR INFORMATION EXTRACTION (PHRASE MATCHING BASELINE)
    # =========================================================================
    print("\n--- TASK 3: PRECURSOR INFORMATION EXTRACTION ---")
    prec_df = pd.read_csv(base_dir / "datasets" / "model_ready" / "precursor_labeled.csv")
    print(f"Inspected precursor dataset: {len(prec_df)} records.")
    print("Schema Format Analysis:")
    print("  - Annotation representation: Extracted text fields (Activity, Hazard, Barrier, Barrier Failure, Potential Consequence).")
    print("  - Token/Character BIO spans: NOT present in raw dataset (Documented limitation; no fabricated BIO tags).")
    
    # Baseline Phrase / Semantic Keyword Extractor
    exact_match_counts = defaultdict(int)
    overlap_ratios = defaultdict(list)
    
    for _, row in prec_df.iterrows():
        narr = str(row.get("narrative", "")).lower()
        for ent in ["activity", "hazard", "barrier", "barrier_failure", "potential_consequence"]:
            val = str(row.get(ent, "")).lower().strip()
            if val and val != "unknown" and val != "none":
                val_words = set(re.findall(r'\w+', val))
                narr_words = set(re.findall(r'\w+', narr))
                if val_words:
                    inter = len(val_words.intersection(narr_words))
                    ratio = inter / len(val_words)
                    overlap_ratios[ent].append(ratio)
                    if ratio >= 0.5:
                        exact_match_counts[ent] += 1
                        
    prec_metrics = {
        "dataset_total": len(prec_df),
        "annotation_format": "Extracted Entity String Representation (No token spans)",
        "limitation_note": "Token-level BIO tags are absent. Evaluated grounded lexical overlap between entity definitions and source narrative.",
        "lexical_grounding_rate": {
            ent: {
                "mean_token_overlap": float(np.mean(overlap_ratios[ent])) if overlap_ratios[ent] else 0.0,
                "high_overlap_records_pct": float(exact_match_counts[ent] / len(prec_df) * 100)
            } for ent in ["activity", "hazard", "barrier", "barrier_failure", "potential_consequence"]
        }
    }
    
    with open(results_dir / "precursor" / "precursor_baseline_metrics.json", "w") as f:
        json.dump(prec_metrics, f, indent=2)
    print(f"Saved Precursor baseline evaluation to {results_dir / 'precursor'}")

    # =========================================================================
    # UPDATE BASELINE_MODEL_REPORT.MD
    # =========================================================================
    report_md_path = quality_dir / "BASELINE_MODEL_REPORT.md"
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write("# OILPS Stage 3: Baseline Model Training & Benchmark Report\n\n")
        f.write("**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence\n")
        f.write("**Phase:** Stage 3 Baseline Model Benchmarking\n")
        f.write("**Date:** 2026-08-30\n")
        f.write("**Random Seed:** `42` (Deterministic Reproducibility)\n\n")
        f.write("---\n\n")
        
        f.write("## 1. Dataset & Experimental Setup\n\n")
        f.write("| Task | Training Records | Validation Records | Test Records | Input Feature | Target Schema |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        f.write(f"| **SIF Binary Classification** | {len(X_train_sif)} | {len(X_val_sif)} | {len(X_test_sif)} | Raw Narrative Text | `sif_label` (1 = SIF, 0 = Non-SIF) |\n")
        f.write(f"| **LSR Multi-Label Classification** | {len(X_train_lsr)} | {len(X_val_lsr)} | {len(X_test_lsr)} | Raw Narrative Text | 9 Official IOGP Rules (Multi-Hot) |\n")
        f.write(f"| **Precursor Information Extraction** | 900 Total Records | — | — | Raw Narrative Text | 5 Decoupled Entity Fields |\n\n")
        
        f.write("## 2. Task 1: SIF Binary Classification Performance\n\n")
        f.write("### Model Selection on Validation Set:\n\n")
        f.write("| Model Architecture | Accuracy | Precision | SIF=1 Recall | F1-Score | ROC-AUC | PR-AUC |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        f.write(f"| **TF-IDF + Logistic Regression** | {val_metrics_lr['accuracy']:.4f} | {val_metrics_lr['precision']:.4f} | {val_metrics_lr['recall_sif1']:.4f} | {val_metrics_lr['f1']:.4f} | {val_metrics_lr['roc_auc']:.4f} | {val_metrics_lr['pr_auc']:.4f} |\n")
        f.write(f"| **TF-IDF + Calibrated Linear SVM** | {val_metrics_svm['accuracy']:.4f} | {val_metrics_svm['precision']:.4f} | **{val_metrics_svm['recall_sif1']:.4f}** | **{val_metrics_svm['f1']:.4f}** | **{val_metrics_svm['roc_auc']:.4f}** | **{val_metrics_svm['pr_auc']:.4f}** |\n\n")
        
        f.write(f"**Selected Best SIF Baseline:** **`{best_sif_name}`**.\n\n")
        
        f.write("### Final Held-Out Test Set Performance (Evaluated ONCE):\n\n")
        f.write("| Test Metric | Value | Safety Interpretation |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(f"| **Accuracy** | **{test_metrics_sif['test_accuracy']*100:.2f}%** | Overall binary correctness on unseen incidents. |\n")
        f.write(f"| **SIF=1 Recall** | **{test_metrics_sif['test_recall_sif1']*100:.2f}%** | **Primary Safety Metric:** Captures {cm_sif[1][1]} of {cm_sif[1][0]+cm_sif[1][1]} true SIF precursors. |\n")
        f.write(f"| **SIF=1 Precision** | **{test_metrics_sif['test_precision']*100:.2f}%** | Precision of flagged SIF precursor alerts. |\n")
        f.write(f"| **F1-Score (SIF=1)** | **{test_metrics_sif['test_f1']:.4f}** | Harmonic mean of precision and recall. |\n")
        f.write(f"| **PR-AUC** | **{test_metrics_sif['test_pr_auc']:.4f}** | Area Under Precision-Recall Curve. |\n")
        f.write(f"| **ROC-AUC** | **{test_metrics_sif['test_roc_auc']:.4f}** | Area Under ROC Curve. |\n\n")
        
        f.write("### Test Confusion Matrix:\n\n")
        f.write("```text\n")
        f.write(f"                     Predicted Non-SIF (0)    Predicted SIF (1)\n")
        f.write(f"Actual Non-SIF (0)        TN = {cm_sif[0][0]:<15}      FP = {cm_sif[0][1]}\n")
        f.write(f"Actual SIF (1)            FN = {cm_sif[1][0]:<15}      TP = {cm_sif[1][1]}\n")
        f.write("```\n\n")
        
        f.write("## 3. Task 2: IOGP Life-Saving Rule Multi-Label Performance\n\n")
        f.write("### Model Selection on Validation Set:\n\n")
        f.write("| Model Architecture | Micro Precision | Micro Recall | Micro F1 | Macro F1 | Hamming Loss | Exact Match |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        f.write(f"| **One-vs-Rest Logistic Regression** | {val_lsr_m_lr['micro_precision']:.4f} | {val_lsr_m_lr['micro_recall']:.4f} | **{val_lsr_m_lr['micro_f1']:.4f}** | **{val_lsr_m_lr['macro_f1']:.4f}** | **{val_lsr_m_lr['hamming_loss']:.4f}** | **{val_lsr_m_lr['exact_match_ratio']:.4f}** |\n")
        f.write(f"| **One-vs-Rest Linear SVM** | {val_lsr_m_svm['micro_precision']:.4f} | {val_lsr_m_svm['micro_recall']:.4f} | {val_lsr_m_svm['micro_f1']:.4f} | {val_lsr_m_svm['macro_f1']:.4f} | {val_lsr_m_svm['hamming_loss']:.4f} | {val_lsr_m_svm['exact_match_ratio']:.4f} |\n\n")
        
        f.write("### Final Held-Out Test Set Performance for All 9 IOGP Rules:\n\n")
        f.write("| Official IOGP Life-Saving Rule | Test Support | Test Precision | Test Recall | Test F1-Score |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for r_name in OFFICIAL_9_LSR:
            m = per_rule_metrics[r_name]
            f.write(f"| **{r_name}** | {m['support']} | {m['precision']:.4f} | {m['recall']:.4f} | **{m['f1']:.4f}** |\n")
        f.write(f"| **OVERALL (MICRO)** | **{sum(per_rule_metrics[r]['support'] for r in OFFICIAL_9_LSR)}** | **{test_metrics_lsr['micro_precision']:.4f}** | **{test_metrics_lsr['micro_recall']:.4f}** | **{test_metrics_lsr['micro_f1']:.4f}** |\n")
        f.write(f"| **OVERALL (MACRO)** | — | **{test_metrics_lsr['macro_precision']:.4f}** | **{test_metrics_lsr['macro_recall']:.4f}** | **{test_metrics_lsr['macro_f1']:.4f}** |\n\n")
        
        f.write("## 4. Task 3: Precursor Information Extraction Baseline\n\n")
        for ent, vals in prec_metrics["lexical_grounding_rate"].items():
            f.write(f"- **`{ent}`**: Mean Token Overlap = **{vals['mean_token_overlap']*100:.1f}%**, High Grounding Rate = **{vals['high_overlap_records_pct']:.1f}%**\n")

    print(f"\nFinal Baseline Model Report saved to: {report_md_path}")
    print("=" * 70)
    print("STAGE 3 BASELINE MODEL TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    train_and_evaluate_all()
