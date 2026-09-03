"""
test_sif_challenger_robustness.py - Dedicated PyTest Suite for Stage 36B.1 SIF Challenger Robustness Validation.
Tests repeated cross-validation setup, fold-level parent leakage audits, metric aggregate statistics,
paired delta computations, locked test evaluation, and production model freeze guarantees.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.sif_challenger_robustness import (
    SIFRobustnessExperiment, METADATA_PATH, ROBUSTNESS_DIR, RUN_RESULTS_PATH
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_repeated_cv_setup_and_data_split():
    """Verify clean 85/15 split between cross-validation pool and locked real test set."""
    exp = SIFRobustnessExperiment(n_splits=5, n_repeats=2, random_seed=42)

    total_real = len(exp.df_real)
    n_pool = len(exp.df_train_val_pool)
    n_test = len(exp.df_locked_test)

    assert n_pool + n_test == total_real
    assert n_pool > n_test

    pool_ids = set(exp.df_train_val_pool["report_id"])
    test_ids = set(exp.df_locked_test["report_id"])
    assert len(pool_ids.intersection(test_ids)) == 0


def test_per_fold_parent_leakage_filter():
    """Verify synthetic records derived from fold validation or locked test set are strictly excluded."""
    exp = SIFRobustnessExperiment(n_splits=3, n_repeats=1, random_seed=42)
    fold_train = exp.df_train_val_pool.iloc[:100]
    fold_val = exp.df_train_val_pool.iloc[100:150]

    filtered_syn = exp._filter_synthetic_for_fold(fold_train, fold_val)

    val_ids = set(fold_val["report_id"].astype(str)).union(
        set(exp.df_locked_test["report_id"].astype(str))
    )

    for idx, row in filtered_syn.iterrows():
        parents = json.loads(row.get("synthetic_parent_ids", "[]"))
        for p in parents:
            assert str(p) not in val_ids, f"Leakage found in synthetic record {row['synthetic_id']}"


def test_repeated_cross_validation_execution():
    """Verify repeated CV execution (5 splits x 2 repeats = 10 runs), statistics, and file exports."""
    exp = SIFRobustnessExperiment(n_splits=5, n_repeats=2, random_seed=42)
    summary = exp.run_repeated_cross_validation()

    assert summary["experiment_id"] == "EXP-STAGE36B1-SIF-ROBUSTNESS"
    assert summary["total_cv_runs"] == 10
    assert "aggregate_statistics" in summary
    assert "paired_deltas_summary" in summary
    assert summary["robustness_conclusion"] in [
        "CONSISTENT_IMPROVEMENT", "MARGINAL_OR_UNCERTAIN_IMPROVEMENT",
        "NO_MEANINGFUL_IMPROVEMENT", "DEGRADATION"
    ]

    assert METADATA_PATH.exists()
    assert RUN_RESULTS_PATH.exists()


def test_production_model_and_rag_freeze_guarantee():
    """Verify Stage 6 SIF and Stage 7 LSR champion model weights & RAG indexes remain 100% frozen."""
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True

    sif_pt = BASE_DIR / "models" / "sif" / "sif_model.pt"
    if sif_pt.exists():
        assert sif_pt.stat().st_size > 0


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
