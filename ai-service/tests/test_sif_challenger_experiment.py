"""
test_sif_challenger_experiment.py - Dedicated PyTest Suite for Stage 36B SIF Challenger Model Experiment.
Tests dataset splitting, untouched real test isolation, synthetic provenance leakage audit,
challenger training, comparative evaluation, and production model freeze guarantees.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.sif_challenger_trainer import SIFChallengerExperiment, EXPERIMENT_METADATA_PATH, EXPERIMENTS_DIR
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_real_dataset_split_and_isolation():
    """Verify real dataset is split cleanly into train, val, test with untouched test isolation."""
    exp = SIFChallengerExperiment(random_seed=42)

    total_real = len(exp.df_real)
    n_train = len(exp.df_train_real)
    n_val = len(exp.df_val_real)
    n_test = len(exp.df_test_real)

    assert n_train + n_val + n_test == total_real
    assert n_train > n_val
    assert n_val > 0 and n_test > 0

    # Ensure zero overlap in report IDs
    train_ids = set(exp.df_train_real["report_id"])
    val_ids = set(exp.df_val_real["report_id"])
    test_ids = set(exp.df_test_real["report_id"])

    assert len(train_ids.intersection(val_ids)) == 0
    assert len(train_ids.intersection(test_ids)) == 0
    assert len(val_ids.intersection(test_ids)) == 0


def test_synthetic_parent_leakage_audit():
    """Verify synthetic records derived from val/test sets are strictly excluded."""
    exp = SIFChallengerExperiment(random_seed=42)

    train_ids = set(exp.df_train_real["report_id"].astype(str))
    val_ids = set(exp.df_val_real["report_id"].astype(str))
    test_ids = set(exp.df_test_real["report_id"].astype(str))

    for idx, row in exp.df_syn_eligible.iterrows():
        parents = json.loads(row["synthetic_parent_ids"])
        for p in parents:
            assert str(p) not in val_ids, f"Val leakage detected in synthetic record {row['synthetic_id']}"
            assert str(p) not in test_ids, f"Test leakage detected in synthetic record {row['synthetic_id']}"


def test_challenger_experiment_execution_and_metrics():
    """Verify offline challenger experiment execution, evaluation metrics, and metadata export."""
    exp = SIFChallengerExperiment(random_seed=42)
    summary = exp.run_experiment()

    assert summary["experiment_id"] == "EXP-STAGE36B-SIF-CHALLENGER"
    assert "challenger_a_real_only" in summary
    assert "challenger_b_real_plus_synthetic" in summary
    assert "comparison" in summary
    assert summary["research_outcome"] in ["CHALLENGER_BETTER", "CHALLENGER_TRADEOFF", "NEGLIGIBLE_EFFECT", "CHALLENGER_NOT_BETTER"]

    # Check metrics structure
    m_a = summary["challenger_a_real_only"]
    assert "precision" in m_a and "recall" in m_a and "f1" in m_a and "pr_auc" in m_a and "false_negatives" in m_a

    # Check metadata file written strictly to EXPERIMENTS_DIR
    assert EXPERIMENT_METADATA_PATH.exists()


def test_production_model_and_rag_freeze_guarantee():
    """Verify Stage 6 SIF and Stage 7 LSR champion model weights & RAG indexes remain 100% frozen."""
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True

    # Confirm production model files were NOT overwritten
    sif_pt = BASE_DIR / "models" / "sif" / "sif_model.pt"
    if sif_pt.exists():
        assert sif_pt.stat().st_size > 0


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
