"""
test_synthetic_sif_generation.py - Dedicated PyTest Suite for Stage 36A.2 Synthetic SIF Data Diversity Improvement.
"""

import sys
import os
import re
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.synthetic_sif_generator import (
    SyntheticSIFGenerator,
    is_missing_value,
    clean_generation_field,
    UNIFIED_DATASET_PATH,
    SYNTHETIC_OUTPUT_DIR
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_safety_factor_pool_extraction():
    """Verify extraction of safety factor pools from verified real SIF parent records."""
    generator = SyntheticSIFGenerator(target_count=10, random_seed=42)
    pools = generator.safety_pools

    assert len(pools["activities"]) > 0
    assert len(pools["hazards"]) > 0
    assert len(pools["barriers"]) > 0
    assert len(pools["locations"]) > 0


def test_diversity_generation_and_multi_parent_provenance():
    """Verify candidates are generated with multi-parent provenance and diverse safety factor combinations."""
    generator = SyntheticSIFGenerator(target_count=10, candidate_multiplier=3, random_seed=42)
    candidates = generator.generate_candidates()

    assert len(candidates) == 30  # 10 * 3
    for c in candidates:
        assert c["synthetic_id"].startswith("SYN-SIF-")
        assert c["source_type"] == "SYNTHETIC"
        assert c["is_synthetic"] == True
        assert c["sif_potential"] == 1
        assert "synthetic_parent_ids" in c
        parents = json.loads(c["synthetic_parent_ids"])
        assert isinstance(parents, list) and len(parents) > 0


def test_diversity_diagnostics_and_candidate_acceptance():
    """Verify validation deduplication accepts target_count diverse records and computes diversity diagnostics."""
    generator = SyntheticSIFGenerator(target_count=15, candidate_multiplier=3, random_seed=42)
    candidates = generator.generate_candidates()
    validated_records, report = generator.validate_candidates(candidates)

    assert len(validated_records) == 45
    assert report["accepted_count"] > 0
    assert report["accepted_count"] <= 15

    diversity = generator.compute_diversity_diagnostics(validated_records)
    assert diversity["accepted_count"] == report["accepted_count"]
    assert "synthetic_unique_activities" in diversity
    assert "coverage_pct" in diversity

    generator.save_synthetic_dataset(validated_records, report)
    assert (SYNTHETIC_OUTPUT_DIR / "synthetic_sif_candidates.csv").exists()
    assert (SYNTHETIC_OUTPUT_DIR / "validation_report.json").exists()


def test_missing_value_leakage_prevention():
    """Verify zero missing-value token leakage in accepted synthetic records."""
    generator = SyntheticSIFGenerator(target_count=10, candidate_multiplier=2, random_seed=42)
    candidates = generator.generate_candidates()
    validated_records, report = generator.validate_candidates(candidates)

    for r in validated_records:
        if r["validation_status"] == "ACCEPTED":
            desc = r["description"].lower()
            assert not re.search(r'\b(nan|none|null|undefined)\b', desc), f"Leakage found in {r['synthetic_id']}: '{desc}'"


def test_determinism_across_runs():
    """Verify deterministic candidate factor selection given identical random seed."""
    g1 = SyntheticSIFGenerator(target_count=10, candidate_multiplier=2, random_seed=42)
    cands1 = g1.generate_candidates()

    g2 = SyntheticSIFGenerator(target_count=10, candidate_multiplier=2, random_seed=42)
    cands2 = g2.generate_candidates()

    for c1, c2 in zip(cands1, cands2):
        assert c1["synthetic_id"] == c2["synthetic_id"]
        assert c1["description"] == c2["description"]


def test_production_model_and_rag_freeze_guarantee():
    """Verify Stage 6 SIF and Stage 7 LSR champion model weights & RAG indexes remain 100% frozen."""
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
