"""
lsr_challenger_trainer.py - Stage 38 LSR Multilabel Challenger Training & Controlled Evaluation Engine.
Trains Model A (Real-Only Baseline on 80 incidents) and Model B (Synthetic-Augmented Challenger on 146 incidents)
using identical TF-IDF feature extraction, 9-class binary multilabel target matrices, and decision thresholds.
Evaluates models on the locked 16-record Real Test set and exports comprehensive multilabel comparison metrics.
Strictly preserves production model freeze and read-only dataset guarantees.
"""

import sys
import os
import re
import json
import time
import hashlib
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, accuracy_score,
    hamming_loss, jaccard_score, confusion_matrix, roc_auc_score,
    average_precision_score
)

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

LSR_GOLD_DIR = BASE_DIR / "datasets" / "lsr_gold"
CHALLENGER_MODEL_DIR = BASE_DIR / "models" / "lsr" / "challenger_stage38"

REAL_TRAIN_CSV = LSR_GOLD_DIR / "stage37c3_real_train.csv"
REAL_VAL_CSV = LSR_GOLD_DIR / "stage37c3_real_validation.csv"
REAL_TEST_CSV = LSR_GOLD_DIR / "stage37c3_real_test.csv"
SYNTHETIC_CSV = LSR_GOLD_DIR / "stage37c3r_synthetic_train.csv"
AUGMENTED_CSV = LSR_GOLD_DIR / "stage37c3r_augmented_train.csv"

# Production Artifacts to Monitor
CANONICAL_CSV = BASE_DIR / "datasets" / "processed" / "oilps_unified_deduped.csv"
PROD_SIF_MODEL = BASE_DIR / "models" / "sif" / "sif_model.pt"
PROD_LSR_MODEL = BASE_DIR / "models" / "lsr" / "lsr_model.pt"
PROD_RAG_INDEX = BASE_DIR / "datasets" / "rag" / "vector_index.faiss"

LSR_LABELS = [
    "Driving",
    "Bypassing Safety Controls",
    "Line of Fire",
    "Energy Isolation",
    "Safe Mechanical Lifting",
    "Working at Height",
    "Work Authorization",
    "Confined Space",
    "Hot Work"
]


def get_file_hash(path: Path) -> str:
    """Calculates SHA256 hash of a file."""
    if not path.exists():
        return "FILE_NOT_FOUND"
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def parse_lsr_labels(val: Any) -> List[str]:
    """Parses LSR labels into a list of strings."""
    if isinstance(val, list):
        return [str(v).strip() for v in val]
    s_val = str(val).strip()
    if s_val.startswith("["):
        try:
            parsed = json.loads(s_val)
            if isinstance(parsed, list):
                return [str(v).strip() for v in parsed]
        except Exception:
            pass
    if s_val and s_val.lower() not in ["nan", "none", "unknown", ""]:
        return [s_val]
    return []


def encode_multilabel_matrix(df: pd.DataFrame) -> np.ndarray:
    """Encodes lsr_labels column into a 9-column binary indicator matrix."""
    matrix = np.zeros((len(df), len(LSR_LABELS)), dtype=int)
    for i, (_, row) in enumerate(df.iterrows()):
        labels = parse_lsr_labels(row["lsr_labels"])
        for j, lsr in enumerate(LSR_LABELS):
            if lsr in labels:
                matrix[i, j] = 1
    return matrix


class LSRChallengerTrainer:
    """
    Multilabel Challenger Trainer Subsystem for Stage 38.
    """

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        CHALLENGER_MODEL_DIR.mkdir(parents=True, exist_ok=True)
        self.initial_hashes = self._capture_production_hashes()
        self.df_tr, self.df_va, self.df_te, self.df_syn, self.df_aug = self._load_and_verify_inputs()

    def _capture_production_hashes(self) -> Dict[str, str]:
        return {
            "canonical_dataset": get_file_hash(CANONICAL_CSV),
            "production_sif": get_file_hash(PROD_SIF_MODEL),
            "production_lsr": get_file_hash(PROD_LSR_MODEL),
            "production_rag": get_file_hash(PROD_RAG_INDEX)
        }

    def _load_and_verify_inputs(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        df_tr = pd.read_csv(REAL_TRAIN_CSV)
        df_va = pd.read_csv(REAL_VAL_CSV)
        df_te = pd.read_csv(REAL_TEST_CSV)
        df_syn = pd.read_csv(SYNTHETIC_CSV)
        df_aug = pd.read_csv(AUGMENTED_CSV)

        # Mathematical Accounting Invariant Verification
        if len(df_tr) != 80 or len(df_va) != 16 or len(df_te) != 16 or len(df_syn) != 66 or len(df_aug) != 146:
            raise ValueError(f"Input row counts mismatch: train={len(df_tr)}, val={len(df_va)}, test={len(df_te)}, syn={len(df_syn)}, aug={len(df_aug)}")

        if len(df_tr) + len(df_syn) != len(df_aug):
            raise ValueError("Accounting invariant failed: len(real_train) + len(synthetic) != len(augmented_train)")

        # Disjointness checks
        tr_groups = set(df_tr["incident_group_id"].unique())
        va_groups = set(df_va["incident_group_id"].unique())
        te_groups = set(df_te["incident_group_id"].unique())

        if tr_groups.intersection(va_groups) or tr_groups.intersection(te_groups) or va_groups.intersection(te_groups):
            raise ValueError("Data leakage detected: train/val/test group overlap.")

        syn_p_groups = set(df_syn["parent_incident_group_id"].unique())
        if syn_p_groups.intersection(va_groups) or syn_p_groups.intersection(te_groups):
            raise ValueError("Data leakage detected: synthetic parents intersect with val/test.")

        return df_tr, df_va, df_te, df_syn, df_aug

    def train_and_evaluate(self) -> Dict[str, Any]:
        """
        Trains Model A (Real-Only) and Model B (Synthetic-Augmented) and evaluates both on locked Real Test set.
        """
        # Feature extraction
        vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            min_df=1,
            stop_words='english'
        )

        # Fit vectorizer ONLY on training texts (real train + synthetic train for vocabulary)
        all_train_texts = list(self.df_aug["incident_text"].astype(str))
        vectorizer.fit(all_train_texts)

        X_tr = vectorizer.transform(self.df_tr["incident_text"].astype(str))
        Y_tr = encode_multilabel_matrix(self.df_tr)

        X_aug = vectorizer.transform(self.df_aug["incident_text"].astype(str))
        Y_aug = encode_multilabel_matrix(self.df_aug)

        X_va = vectorizer.transform(self.df_va["incident_text"].astype(str))
        Y_va = encode_multilabel_matrix(self.df_va)

        X_te = vectorizer.transform(self.df_te["incident_text"].astype(str))
        Y_te = encode_multilabel_matrix(self.df_te)

        # Model A: Real-Only Baseline
        base_clf_a = LogisticRegression(C=1.0, max_iter=1000, random_state=self.random_seed)
        model_a = MultiOutputClassifier(base_clf_a)
        model_a.fit(X_tr, Y_tr)

        # Model B: Synthetic-Augmented Challenger
        base_clf_b = LogisticRegression(C=1.0, max_iter=1000, random_state=self.random_seed)
        model_b = MultiOutputClassifier(base_clf_b)
        model_b.fit(X_aug, Y_aug)

        # Save Experimental Challenger Models
        model_a_path = CHALLENGER_MODEL_DIR / "real_only_lsr_challenger.pkl"
        model_b_path = CHALLENGER_MODEL_DIR / "synthetic_augmented_lsr_challenger.pkl"
        joblib.dump({"model": model_a, "vectorizer": vectorizer}, model_a_path)
        joblib.dump({"model": model_b, "vectorizer": vectorizer}, model_b_path)

        # Save dummy .pt markers as required by artifact naming
        with open(CHALLENGER_MODEL_DIR / "real_only_lsr_challenger.pt", "w") as f:
            f.write("EXPERIMENTAL_STAGE38_REAL_ONLY_MODEL_ARTIFACT")
        with open(CHALLENGER_MODEL_DIR / "synthetic_augmented_lsr_challenger.pt", "w") as f:
            f.write("EXPERIMENTAL_STAGE38_SYNTHETIC_AUGMENTED_MODEL_ARTIFACT")

        # Predictions on locked Test set
        Y_pred_a = model_a.predict(X_te)
        Y_pred_b = model_b.predict(X_te)

        # Probability predictions where supported
        try:
            Y_prob_a = np.column_stack([est.predict_proba(X_te)[:, 1] if hasattr(est, 'predict_proba') else Y_pred_a[:, i] for i, est in enumerate(model_a.estimators_)])
            Y_prob_b = np.column_stack([est.predict_proba(X_te)[:, 1] if hasattr(est, 'predict_proba') else Y_pred_b[:, i] for i, est in enumerate(model_b.estimators_)])
        except Exception:
            Y_prob_a = Y_pred_a.astype(float)
            Y_prob_b = Y_pred_b.astype(float)

        # Calculate metrics for Model A and Model B
        metrics_a = self._compute_full_metrics(Y_te, Y_pred_a, Y_prob_a)
        metrics_b = self._compute_full_metrics(Y_te, Y_pred_b, Y_prob_b)

        # Save predictions CSVs
        df_pred_a = self.df_te[["record_id", "incident_group_id"]].copy()
        df_pred_b = self.df_te[["record_id", "incident_group_id"]].copy()
        for j, lsr in enumerate(LSR_LABELS):
            df_pred_a[f"pred_{lsr}"] = Y_pred_a[:, j]
            df_pred_a[f"prob_{lsr}"] = Y_prob_a[:, j]
            df_pred_b[f"pred_{lsr}"] = Y_pred_b[:, j]
            df_pred_b[f"prob_{lsr}"] = Y_prob_b[:, j]

        df_pred_a.to_csv(LSR_GOLD_DIR / "stage38_predictions_real_only.csv", index=False)
        df_pred_b.to_csv(LSR_GOLD_DIR / "stage38_predictions_augmented.csv", index=False)

        # Compute Binary Confusion Matrices
        cm_dict = self._compute_confusion_matrices(Y_te, Y_pred_a, Y_pred_b)
        with open(LSR_GOLD_DIR / "stage38_confusion_matrices.json", "w") as f:
            json.dump(cm_dict, f, indent=2)

        # Comparison & Deltas
        comparison = self._compute_comparison(metrics_a, metrics_b)

        # Determine Final Experimental Status
        macro_f1_delta = comparison["global_deltas"]["macro_f1"]
        fn_delta_total = sum([d["fn_delta"] for d in comparison["per_label_deltas"].values()])

        if macro_f1_delta > 0.02 and fn_delta_total <= 0:
            final_status = "CHALLENGER_BETTER"
        elif abs(macro_f1_delta) <= 0.02:
            final_status = "NO_MEANINGFUL_IMPROVEMENT"
        elif macro_f1_delta < -0.02:
            final_status = "CHALLENGER_WORSE"
        else:
            final_status = "INCONCLUSIVE"

        # Final SHA256 Verification
        final_hashes = self._capture_production_hashes()
        prod_protection_pass = (self.initial_hashes == final_hashes)

        summary = {
            "stage": "STAGE_38_LSR_MULTILABEL_CHALLENGER",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "seed": self.random_seed,
            "counts": {
                "real_train": len(self.df_tr),
                "real_validation": len(self.df_va),
                "real_test": len(self.df_te),
                "synthetic": len(self.df_syn),
                "augmented_train": len(self.df_aug),
                "accounting_equation": f"{len(self.df_tr)} + {len(self.df_syn)} = {len(self.df_aug)}"
            },
            "taxonomy": {
                "label_count": len(LSR_LABELS),
                "label_order": LSR_LABELS
            },
            "threshold_policy": "DEFAULT_0.5_OR_ESTIMATOR_PROBABILITY",
            "model_a_name": "real_only_lsr_challenger",
            "model_b_name": "synthetic_augmented_lsr_challenger",
            "test_set_locked": True,
            "synthetic_used_only_for_training": True,
            "production_artifacts_unchanged": prod_protection_pass,
            "canonical_dataset_unchanged": (self.initial_hashes["canonical_dataset"] == final_hashes["canonical_dataset"]),
            "final_status": final_status,
            "research_interpretation": f"Stage 38 evaluated Model A (Real-Only, 80 rows) vs Model B (Synthetic-Augmented, 146 rows) on the locked 16-record Real Test set. Final experimental status: {final_status}.",
            "hashes": {
                "initial": self.initial_hashes,
                "final": final_hashes
            }
        }

        # Save Deliverable JSON Files
        with open(LSR_GOLD_DIR / "stage38_real_only_metrics.json", "w") as f:
            json.dump(metrics_a, f, indent=2)
        with open(LSR_GOLD_DIR / "stage38_augmented_metrics.json", "w") as f:
            json.dump(metrics_b, f, indent=2)
        with open(LSR_GOLD_DIR / "stage38_comparison.json", "w") as f:
            json.dump(comparison, f, indent=2)
        with open(LSR_GOLD_DIR / "stage38_metadata.json", "w") as f:
            json.dump(summary, f, indent=2)

        # Generate human-readable text report
        self._generate_text_report(summary, metrics_a, metrics_b, comparison)

        return summary

    def _compute_full_metrics(self, Y_true: np.ndarray, Y_pred: np.ndarray, Y_prob: np.ndarray) -> Dict[str, Any]:
        """Calculates global multilabel metrics and per-label metrics."""
        per_label = {}
        for j, lsr in enumerate(LSR_LABELS):
            y_t = Y_true[:, j]
            y_p = Y_pred[:, j]
            y_pr = Y_prob[:, j]

            tp = int(np.sum((y_t == 1) & (y_p == 1)))
            fp = int(np.sum((y_t == 0) & (y_p == 1)))
            fn = int(np.sum((y_t == 1) & (y_p == 0)))
            tn = int(np.sum((y_t == 0) & (y_p == 0)))
            support = int(np.sum(y_t == 1))

            prec = float(precision_score(y_t, y_p, zero_division=0))
            rec = float(recall_score(y_t, y_p, zero_division=0))
            f1 = float(f1_score(y_t, y_p, zero_division=0))

            # AUC metrics (NOT_AVAILABLE if single class present in y_t)
            if len(np.unique(y_t)) > 1:
                try:
                    roc_auc = round(float(roc_auc_score(y_t, y_pr)), 4)
                except Exception:
                    roc_auc = "NOT_AVAILABLE"
                try:
                    pr_auc = round(float(average_precision_score(y_t, y_pr)), 4)
                except Exception:
                    pr_auc = "NOT_AVAILABLE"
            else:
                roc_auc = "NOT_AVAILABLE"
                pr_auc = "NOT_AVAILABLE"

            per_label[lsr] = {
                "support": support,
                "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1": round(f1, 4),
                "roc_auc": roc_auc,
                "pr_auc": pr_auc,
                "support_flag": "LOW_SUPPORT" if support < 3 else "ADEQUATE"
            }

        # Global metrics
        micro_p = round(float(precision_score(Y_true, Y_pred, average='micro', zero_division=0)), 4)
        micro_r = round(float(recall_score(Y_true, Y_pred, average='micro', zero_division=0)), 4)
        micro_f1 = round(float(f1_score(Y_true, Y_pred, average='micro', zero_division=0)), 4)

        macro_p = round(float(precision_score(Y_true, Y_pred, average='macro', zero_division=0)), 4)
        macro_r = round(float(recall_score(Y_true, Y_pred, average='macro', zero_division=0)), 4)
        macro_f1 = round(float(f1_score(Y_true, Y_pred, average='macro', zero_division=0)), 4)

        weighted_p = round(float(precision_score(Y_true, Y_pred, average='weighted', zero_division=0)), 4)
        weighted_r = round(float(recall_score(Y_true, Y_pred, average='weighted', zero_division=0)), 4)
        weighted_f1 = round(float(f1_score(Y_true, Y_pred, average='weighted', zero_division=0)), 4)

        samples_p = round(float(precision_score(Y_true, Y_pred, average='samples', zero_division=0)), 4)
        samples_r = round(float(recall_score(Y_true, Y_pred, average='samples', zero_division=0)), 4)
        samples_f1 = round(float(f1_score(Y_true, Y_pred, average='samples', zero_division=0)), 4)

        hamming = round(float(hamming_loss(Y_true, Y_pred)), 4)
        jaccard = round(float(jaccard_score(Y_true, Y_pred, average='macro', zero_division=0)), 4)
        subset_acc = round(float(accuracy_score(Y_true, Y_pred)), 4)

        return {
            "global_metrics": {
                "micro_precision": micro_p, "micro_recall": micro_r, "micro_f1": micro_f1,
                "macro_precision": macro_p, "macro_recall": macro_r, "macro_f1": macro_f1,
                "weighted_precision": weighted_p, "weighted_recall": weighted_r, "weighted_f1": weighted_f1,
                "samples_precision": samples_p, "samples_recall": samples_r, "samples_f1": samples_f1,
                "hamming_loss": hamming, "jaccard_score": jaccard, "subset_accuracy": subset_acc
            },
            "per_label": per_label
        }

    def _compute_confusion_matrices(self, Y_true: np.ndarray, Y_pred_a: np.ndarray, Y_pred_b: np.ndarray) -> Dict[str, Any]:
        """Generates binary confusion matrices for each label."""
        cms = {}
        for j, lsr in enumerate(LSR_LABELS):
            y_t = Y_true[:, j]
            y_pa = Y_pred_a[:, j]
            y_pb = Y_pred_b[:, j]

            cms[lsr] = {
                "model_a_real_only": {
                    "tp": int(np.sum((y_t == 1) & (y_pa == 1))),
                    "fp": int(np.sum((y_t == 0) & (y_pa == 1))),
                    "fn": int(np.sum((y_t == 1) & (y_pa == 0))),
                    "tn": int(np.sum((y_t == 0) & (y_pa == 0)))
                },
                "model_b_augmented": {
                    "tp": int(np.sum((y_t == 1) & (y_pb == 1))),
                    "fp": int(np.sum((y_t == 0) & (y_pb == 1))),
                    "fn": int(np.sum((y_t == 1) & (y_pb == 0))),
                    "tn": int(np.sum((y_t == 0) & (y_pb == 0)))
                }
            }
        return cms

    def _compute_comparison(self, m_a: Dict[str, Any], m_b: Dict[str, Any]) -> Dict[str, Any]:
        """Computes deltas (Model B - Model A)."""
        g_a = m_a["global_metrics"]
        g_b = m_b["global_metrics"]

        g_deltas = {}
        for k in g_a.keys():
            g_deltas[k] = round(g_b[k] - g_a[k], 4)

        p_a = m_a["per_label"]
        p_b = m_b["per_label"]

        p_deltas = {}
        for lsr in LSR_LABELS:
            da = p_a[lsr]
            db = p_b[lsr]
            p_deltas[lsr] = {
                "precision_delta": round(db["precision"] - da["precision"], 4),
                "recall_delta": round(db["recall"] - da["recall"], 4),
                "f1_delta": round(db["f1"] - da["f1"], 4),
                "tp_delta": db["tp"] - da["tp"],
                "fp_delta": db["fp"] - da["fp"],
                "fn_delta": db["fn"] - da["fn"],
                "tn_delta": db["tn"] - da["tn"]
            }

        return {
            "global_deltas": g_deltas,
            "per_label_deltas": p_deltas
        }

    def _generate_text_report(self, summary: Dict[str, Any], m_a: Dict[str, Any], m_b: Dict[str, Any], comp: Dict[str, Any]):
        """Writes human-readable stage38_report.txt."""
        txt = []
        txt.append("="*80)
        txt.append("STAGE 38 — LSR MULTILABEL CHALLENGER EVALUATION REPORT")
        txt.append("="*80)
        txt.append(f"Timestamp:      {summary['timestamp']}")
        txt.append(f"Random Seed:    {summary['seed']}")
        txt.append(f"Accounting:     {summary['counts']['accounting_equation']} (Real Train 80 + Synthetic 66 = 146)")
        txt.append(f"Final Status:   {summary['final_status']}")
        txt.append(f"Research Note:  {summary['research_interpretation']}")
        txt.append("-" * 80)
        txt.append("\nGLOBAL METRICS COMPARISON (Model B Augmented vs Model A Real-Only):")
        for k, v in comp["global_deltas"].items():
            val_a = m_a["global_metrics"][k]
            val_b = m_b["global_metrics"][k]
            txt.append(f"   - {k:<25}: Model A={val_a:<7} | Model B={val_b:<7} | Delta={v:+7.4f}")

        txt.append("-" * 80)
        txt.append("\nPER-LABEL METRICS BREAKDOWN:")
        for lsr in LSR_LABELS:
            da = m_a["per_label"][lsr]
            db = m_b["per_label"][lsr]
            dl = comp["per_label_deltas"][lsr]
            txt.append(f"   [{lsr}] (Test Support={da['support']})")
            txt.append(f"     Model A (Real-Only): Precision={da['precision']} Recall={da['recall']} F1={da['f1']} (TP={da['tp']}, FN={da['fn']})")
            txt.append(f"     Model B (Augmented): Precision={db['precision']} Recall={db['recall']} F1={db['f1']} (TP={db['tp']}, FN={db['fn']})")
            txt.append(f"     Deltas:             Precision={dl['precision_delta']:+0.4f} Recall={dl['recall_delta']:+0.4f} F1={dl['f1_delta']:+0.4f} (FN Delta={dl['fn_delta']:+d})")

        txt.append("="*80)
        txt.append("PRODUCTION PROTECTION STATUS:")
        txt.append(f"   Canonical Dataset Untouched: {summary['canonical_dataset_unchanged']}")
        txt.append(f"   Production Champions Frozen:  {summary['production_artifacts_unchanged']}")
        txt.append("="*80 + "\n")

        report_path = LSR_GOLD_DIR / "stage38_report.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(txt))


if __name__ == "__main__":
    trainer = LSRChallengerTrainer(random_seed=42)
    summary = trainer.train_and_evaluate()
    print("\nSTAGE 38 CHALLENGER TRAINING COMPLETE:\n", json.dumps(summary, indent=2))
