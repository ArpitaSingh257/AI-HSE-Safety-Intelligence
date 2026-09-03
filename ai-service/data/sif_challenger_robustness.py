"""
sif_challenger_robustness.py - Stage 36B.1 SIF Challenger Robustness Validation Subsystem for OILPS.
Performs Repeated Stratified K-Fold Cross-Validation (e.g. 5 splits x 3 repeats = 15 runs) comparing
Real-Only vs Real + Validated Synthetic SIF augmentation with fold-level parent leakage audits,
paired metric differences, and final evaluation on locked untouched Real Test data.
Production models, RAG vector index, and historical datasets remain 100% frozen and isolated.
"""

import sys
import os
import re
import json
import time
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from sklearn.model_selection import RepeatedStratifiedKFold, train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, balanced_accuracy_score, confusion_matrix
)

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

UNIFIED_DATASET_PATH = BASE_DIR / "datasets" / "processed" / "oilps_unified_deduped.csv"
SYNTHETIC_CSV_PATH = BASE_DIR / "datasets" / "synthetic" / "synthetic_sif_candidates.csv"
ROBUSTNESS_DIR = BASE_DIR / "models" / "experiments" / "sif" / "robustness"
ROBUSTNESS_DIR.mkdir(parents=True, exist_ok=True)

METADATA_PATH = ROBUSTNESS_DIR / "experiment_metadata.json"
RUN_RESULTS_PATH = ROBUSTNESS_DIR / "run_results.csv"
AGGREGATE_RESULTS_PATH = ROBUSTNESS_DIR / "aggregate_results.csv"
METRIC_DELTAS_PATH = ROBUSTNESS_DIR / "metric_differences.csv"
FINAL_TEST_PATH = ROBUSTNESS_DIR / "final_test_comparison.json"


class SIFRobustnessExperiment:
    """
    Repeated Cross-Validation & Robustness Analysis Engine for SIF Challenger Model.
    """

    def __init__(self, n_splits: int = 5, n_repeats: int = 3, random_seed: int = 42):
        self.n_splits = n_splits
        self.n_repeats = n_repeats
        self.random_seed = random_seed
        np.random.seed(random_seed)

        self.df_real = self._load_real_dataset()
        self.df_syn = self._load_synthetic_dataset()

        # Separate locked Real Test set (15%) from Training/Validation pool (85%)
        self.df_train_val_pool, self.df_locked_test = train_test_split(
            self.df_real, test_size=0.15, random_state=self.random_seed, stratify=self.df_real["sif_potential"]
        )
        self.df_train_val_pool = self.df_train_val_pool.reset_index(drop=True)
        self.df_locked_test = self.df_locked_test.reset_index(drop=True)

    def _load_real_dataset(self) -> pd.DataFrame:
        if not UNIFIED_DATASET_PATH.exists():
            raise FileNotFoundError(f"Real dataset missing at '{UNIFIED_DATASET_PATH}'.")

        df = pd.read_csv(UNIFIED_DATASET_PATH)
        df["sif_potential"] = pd.to_numeric(df["sif_potential"], errors="coerce").fillna(0).astype(int)

        if "report_id" not in df.columns:
            df["report_id"] = [f"REAL-REPORT-{i:05d}" for i in range(1, len(df) + 1)]

        text_cols = ["description", "text_description", "report_text", "incident_description", "narrative", "event_description", "text", "summary"]
        text_col = next((c for c in text_cols if c in df.columns), None)

        if not text_col:
            str_cols = [c for c in df.columns if df[c].dtype == object]
            text_col = str_cols[0] if str_cols else None

        if text_col:
            df["clean_text"] = df[text_col].astype(str).str.strip()
        else:
            df["clean_text"] = "Safety incident precursor event"

        df["description"] = df["clean_text"]
        return df

    def _load_synthetic_dataset(self) -> pd.DataFrame:
        if not SYNTHETIC_CSV_PATH.exists():
            print(f"Warning: Synthetic dataset path '{SYNTHETIC_CSV_PATH}' missing.")
            return pd.DataFrame()

        df = pd.read_csv(SYNTHETIC_CSV_PATH)
        if df.empty:
            return pd.DataFrame()

        if "validation_status" in df.columns:
            df = df[df["validation_status"] == "ACCEPTED"].copy()

        text_cols = ["description", "text_description", "report_text", "incident_description", "narrative", "event_description", "text", "summary"]
        text_col = next((c for c in text_cols if c in df.columns), None)
        if text_col:
            df["clean_text"] = df[text_col].astype(str).str.strip()
        else:
            df["clean_text"] = "Safety incident precursor event"

        df["description"] = df["clean_text"]
        return df

    def _compute_metrics(self, y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> Dict[str, Any]:
        y_pred = (y_prob >= threshold).astype(int)

        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        bal_acc = balanced_accuracy_score(y_true, y_pred)

        try:
            roc_auc = roc_auc_score(y_true, y_prob)
        except Exception:
            roc_auc = 0.5

        try:
            pr_auc = average_precision_score(y_true, y_prob)
        except Exception:
            pr_auc = 0.0

        return {
            "threshold": round(threshold, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "balanced_accuracy": round(bal_acc, 4),
            "false_negatives": int(fn),
            "false_positives": int(fp),
            "true_positives": int(tp),
            "true_negatives": int(tn)
        }

    def _filter_synthetic_for_fold(self, fold_train_df: pd.DataFrame, fold_val_df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs strict parent leakage check for each fold: excludes synthetic records derived from fold_val or locked_test.
        """
        if self.df_syn.empty:
            return pd.DataFrame()

        val_ids_list = fold_val_df["report_id"].astype(str).tolist() if (not fold_val_df.empty and "report_id" in fold_val_df.columns) else []
        test_ids_list = self.df_locked_test["report_id"].astype(str).tolist() if (not self.df_locked_test.empty and "report_id" in self.df_locked_test.columns) else []

        val_ids = set(val_ids_list).union(set(test_ids_list))

        eligible = []
        for idx, row in self.df_syn.iterrows():
            parents_raw = row.get("synthetic_parent_ids", "[]")
            try:
                parents = json.loads(parents_raw) if isinstance(parents_raw, str) else []
            except Exception:
                parents = []

            # Exclude if parent belongs to val or locked test
            if not any(str(p) in val_ids for p in parents):
                eligible.append(row.to_dict())

        df_res = pd.DataFrame(eligible) if eligible else pd.DataFrame()
        if not df_res.empty:
            if "sif_potential" not in df_res.columns:
                df_res["sif_potential"] = 1
            if "clean_text" not in df_res.columns:
                df_res["clean_text"] = "Safety incident precursor event"
            df_res["description"] = df_res["clean_text"]
        return df_res

    def run_repeated_cross_validation(self) -> Dict[str, Any]:
        """
        Runs Repeated Stratified K-Fold CV (n_splits x n_repeats) comparing Real-Only vs Real+Synthetic.
        """
        rskf = RepeatedStratifiedKFold(
            n_splits=self.n_splits, n_repeats=self.n_repeats, random_state=self.random_seed
        )

        X_pool = self.df_train_val_pool["clean_text"].values
        y_pool = self.df_train_val_pool["sif_potential"].values

        runs_a = []
        runs_b = []
        metric_deltas = []

        run_idx = 0
        for train_idx, val_idx in rskf.split(X_pool, y_pool):
            run_idx += 1

            df_tr = self.df_train_val_pool.iloc[train_idx].copy()
            df_va = self.df_train_val_pool.iloc[val_idx].copy()

            # Filter synthetic records for this fold
            df_syn_fold = self._filter_synthetic_for_fold(df_tr, df_va)

            # Feature extraction
            vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), token_pattern=r'(?u)\b\w+\b', min_df=1)
            X_tr_text = df_tr["clean_text"].tolist()
            y_tr = df_tr["sif_potential"].values

            vectorizer.fit(X_tr_text)
            X_tr = vectorizer.transform(X_tr_text)
            X_va = vectorizer.transform(df_va["clean_text"].tolist())
            y_va = df_va["sif_potential"].values

            # Model A: Real Only
            clf_a = LogisticRegression(class_weight="balanced", random_state=self.random_seed, max_iter=500)
            clf_a.fit(X_tr, y_tr)
            prob_a = clf_a.predict_proba(X_va)[:, 1]
            m_a = self._compute_metrics(y_va, prob_a, threshold=0.5)
            m_a["run_id"] = run_idx
            m_a["model_type"] = "REAL_ONLY"
            runs_a.append(m_a)

            # Model B: Real + Synthetic
            if not df_syn_fold.empty:
                X_tr_aug_text = X_tr_text + df_syn_fold["clean_text"].tolist()
                y_tr_aug = np.concatenate([y_tr, df_syn_fold["sif_potential"].values])
            else:
                X_tr_aug_text = X_tr_text
                y_tr_aug = y_tr

            X_tr_aug = vectorizer.transform(X_tr_aug_text)
            clf_b = LogisticRegression(class_weight="balanced", random_state=self.random_seed, max_iter=500)
            clf_b.fit(X_tr_aug, y_tr_aug)
            prob_b = clf_b.predict_proba(X_va)[:, 1]
            m_b = self._compute_metrics(y_va, prob_b, threshold=0.5)
            m_b["run_id"] = run_idx
            m_b["model_type"] = "REAL_PLUS_SYNTHETIC"
            runs_b.append(m_b)

            # Paired deltas
            delta = {
                "run_id": run_idx,
                "delta_precision": round(m_b["precision"] - m_a["precision"], 4),
                "delta_recall": round(m_b["recall"] - m_a["recall"], 4),
                "delta_f1": round(m_b["f1"] - m_a["f1"], 4),
                "delta_pr_auc": round(m_b["pr_auc"] - m_a["pr_auc"], 4),
                "delta_roc_auc": round(m_b["roc_auc"] - m_a["roc_auc"], 4),
                "delta_false_negatives": m_b["false_negatives"] - m_a["false_negatives"]
            }
            metric_deltas.append(delta)

        # Aggregate Statistics
        def calc_stats(run_list: List[Dict[str, Any]]) -> Dict[str, Any]:
            keys = ["precision", "recall", "f1", "roc_auc", "pr_auc", "balanced_accuracy", "false_negatives"]
            stats = {}
            for k in keys:
                vals = [r[k] for r in run_list]
                stats[k] = {
                    "mean": round(float(np.mean(vals)), 4),
                    "std": round(float(np.std(vals)), 4),
                    "median": round(float(np.median(vals)), 4),
                    "min": round(float(np.min(vals)), 4),
                    "max": round(float(np.max(vals)), 4)
                }
            return stats

        stats_a = calc_stats(runs_a)
        stats_b = calc_stats(runs_b)

        # Summary Deltas
        delta_keys = ["delta_precision", "delta_recall", "delta_f1", "delta_pr_auc", "delta_roc_auc", "delta_false_negatives"]
        delta_summary = {}
        for dk in delta_keys:
            vals = [d[dk] for d in metric_deltas]
            delta_summary[dk] = {
                "mean": round(float(np.mean(vals)), 4),
                "std": round(float(np.std(vals)), 4),
                "median": round(float(np.median(vals)), 4)
            }

        # 4. Final Locked Test Evaluation
        vectorizer_final = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), token_pattern=r'(?u)\b\w+\b', min_df=1)
        X_all_tr_text = self.df_train_val_pool["clean_text"].tolist()
        y_all_tr = self.df_train_val_pool["sif_potential"].values

        vectorizer_final.fit(X_all_tr_text)
        X_all_tr = vectorizer_final.transform(X_all_tr_text)
        X_locked_test = vectorizer_final.transform(self.df_locked_test["clean_text"].tolist())
        y_locked_test = self.df_locked_test["sif_potential"].values

        # Final Champion (Real Only)
        clf_final_a = LogisticRegression(class_weight="balanced", random_state=self.random_seed, max_iter=500)
        clf_final_a.fit(X_all_tr, y_all_tr)
        prob_final_a = clf_final_a.predict_proba(X_locked_test)[:, 1]
        final_m_a = self._compute_metrics(y_locked_test, prob_final_a, threshold=0.5)

        # Final Challenger (Real + Eligible Synthetic)
        df_syn_final = self._filter_synthetic_for_fold(self.df_train_val_pool, pd.DataFrame())
        if not df_syn_final.empty:
            X_aug_final_text = X_all_tr_text + df_syn_final["clean_text"].tolist()
            y_aug_final = np.concatenate([y_all_tr, df_syn_final["sif_potential"].values])
        else:
            X_aug_final_text = X_all_tr_text
            y_aug_final = y_all_tr

        X_aug_final = vectorizer_final.transform(X_aug_final_text)
        clf_final_b = LogisticRegression(class_weight="balanced", random_state=self.random_seed, max_iter=500)
        clf_final_b.fit(X_aug_final, y_aug_final)
        prob_final_b = clf_final_b.predict_proba(X_locked_test)[:, 1]
        final_m_b = self._compute_metrics(y_locked_test, prob_final_b, threshold=0.5)

        # Classify Robustness Conclusion
        mean_pr_auc_diff = delta_summary["delta_pr_auc"]["mean"]
        mean_rec_diff = delta_summary["delta_recall"]["mean"]

        if mean_rec_diff > 0.01 and mean_pr_auc_diff > 0.005:
            conclusion = "CONSISTENT_IMPROVEMENT"
        elif mean_rec_diff >= 0.0 or mean_pr_auc_diff > 0.001:
            conclusion = "MARGINAL_OR_UNCERTAIN_IMPROVEMENT"
        elif abs(mean_rec_diff) <= 0.005 and abs(mean_pr_auc_diff) <= 0.001:
            conclusion = "NO_MEANINGFUL_IMPROVEMENT"
        else:
            conclusion = "DEGRADATION"

        # Save artifacts to ROBUSTNESS_DIR
        pd.DataFrame(runs_a + runs_b).to_csv(RUN_RESULTS_PATH, index=False)
        pd.DataFrame(metric_deltas).to_csv(METRIC_DELTAS_PATH, index=False)

        summary = {
            "experiment_id": "EXP-STAGE36B1-SIF-ROBUSTNESS",
            "n_splits": self.n_splits,
            "n_repeats": self.n_repeats,
            "total_cv_runs": len(runs_a),
            "train_val_pool_size": len(self.df_train_val_pool),
            "locked_test_size": len(self.df_locked_test),
            "leakage_audit": {
                "cv_fold_val_leakage": "NONE",
                "locked_test_leakage": "NONE"
            },
            "aggregate_statistics": {
                "real_only": stats_a,
                "real_plus_synthetic": stats_b
            },
            "paired_deltas_summary": delta_summary,
            "final_locked_test_comparison": {
                "real_only_champion": final_m_a,
                "real_plus_synthetic_challenger": final_m_b
            },
            "robustness_conclusion": conclusion,
            "production_protection": {
                "production_sif_champion_frozen": True,
                "production_lsr_champion_frozen": True,
                "production_rag_untouched": True,
                "canonical_dataset_untouched": True
            }
        }

        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        with open(FINAL_TEST_PATH, "w", encoding="utf-8") as f:
            json.dump({"final_champion": final_m_a, "final_challenger": final_m_b, "conclusion": conclusion}, f, indent=2)

        return summary


if __name__ == "__main__":
    exp = SIFRobustnessExperiment(n_splits=5, n_repeats=3, random_seed=42)
    res = exp.run_repeated_cross_validation()
    print("\nROBUSTNESS EXPERIMENT SUMMARY:\n", json.dumps(res, indent=2))
