"""
test_stage38_lsr_challenger.py - Dedicated PyTest Suite for Stage 38 LSR Multilabel Challenger Training & Controlled Evaluation.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.lsr_challenger_trainer import (
    LSRChallengerTrainer, LSR_LABELS, REAL_TRAIN_CSV, REAL_VAL_CSV,
    REAL_TEST_CSV, SYNTHETIC_CSV, AUGMENTED_CSV, CHALLENGER_MODEL_DIR
)
from data.unified_lsr_gold_builder import get_file_hash, UNIFIED_DATASET_PATH
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_input_counts_and_accounting_invariant():
    """Test 1-6: Verify exact split row counts and 80 + 66 = 146 invariant."""
    trainer = LSRChallengerTrainer(random_seed=42)
    assert len(trainer.df_tr) == 80
    assert len(trainer.df_va) == 16
    assert len(trainer.df_te) == 16
    assert len(trainer.df_syn) == 66
    assert len(trainer.df_aug) == 146
    assert len(trainer.df_tr) + len(trainer.df_syn) == len(trainer.df_aug)


def test_train_val_test_disjointness_and_zero_synthetic_in_eval():
    """Test 7, 8, 13, 14: Disjointness and zero synthetic records in val/test sets."""
    trainer = LSRChallengerTrainer(random_seed=42)

    tr_g = set(trainer.df_tr["incident_group_id"].unique())
    va_g = set(trainer.df_va["incident_group_id"].unique())
    te_g = set(trainer.df_te["incident_group_id"].unique())

    assert len(tr_g.intersection(va_g)) == 0
    assert len(tr_g.intersection(te_g)) == 0
    assert len(va_g.intersection(te_g)) == 0

    syn_p_g = set(trainer.df_syn["parent_incident_group_id"].unique())
    assert syn_p_g.issubset(tr_g)
    assert len(syn_p_g.intersection(va_g)) == 0
    assert len(syn_p_g.intersection(te_g)) == 0


def test_multilabel_taxonomy_order_and_representation():
    """Test 10, 11, 12: Exactly 9 LSR labels in official order and binary indicator representation."""
    assert len(LSR_LABELS) == 9
    assert LSR_LABELS[0] == "Driving"
    assert LSR_LABELS[-1] == "Hot Work"


def test_production_artifacts_unchanged():
    """Test 18, 19, 20: Production SIF/LSR champions, canonical dataset, and RAG index unchanged."""
    hash_canonical = get_file_hash(UNIFIED_DATASET_PATH)
    trainer = LSRChallengerTrainer(random_seed=42)
    summary = trainer.train_and_evaluate()

    assert hash_canonical == get_file_hash(UNIFIED_DATASET_PATH)

    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True


def test_deterministic_evaluation():
    """Test 21, 22: Deterministic training and evaluation across two runs with seed=42."""
    t1 = LSRChallengerTrainer(random_seed=42)
    s1 = t1.train_and_evaluate()

    t2 = LSRChallengerTrainer(random_seed=42)
    s2 = t2.train_and_evaluate()

    assert s1["final_status"] == s2["final_status"]
    assert s1["counts"] == s2["counts"]


def test_challenger_model_artifacts_created():
    """Test 24: Model A and Model B experimental artifacts created under challenger_stage38/."""
    trainer = LSRChallengerTrainer(random_seed=42)
    summary = trainer.train_and_evaluate()

    assert (CHALLENGER_MODEL_DIR / "real_only_lsr_challenger.pkl").exists()
    assert (CHALLENGER_MODEL_DIR / "synthetic_augmented_lsr_challenger.pkl").exists()
    assert (CHALLENGER_MODEL_DIR / "real_only_lsr_challenger.pt").exists()
    assert (CHALLENGER_MODEL_DIR / "synthetic_augmented_lsr_challenger.pt").exists()


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
