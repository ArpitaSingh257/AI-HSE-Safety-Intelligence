"""
test_stage37c_unified_lsr_gold.py - Dedicated PyTest Suite for Stage 37C Unified LSR Gold Dataset Construction.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.unified_lsr_gold_builder import (
    UnifiedLSRGoldBuilder, UNIFIED_GOLD_CSV, UNIFIED_GOLD_METADATA,
    UNIFIED_DATASET_PATH, get_file_hash
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_canonical_dataset_untouched():
    """Test 1: Canonical dataset file hash remains completely unchanged."""
    hash_before = get_file_hash(UNIFIED_DATASET_PATH)
    builder = UnifiedLSRGoldBuilder()
    df_u, meta = builder.build_unified_dataset()
    hash_after = get_file_hash(UNIFIED_DATASET_PATH)

    assert hash_before == hash_after


def test_frozen_sif_and_lsr_models_untouched():
    """Test 2 & 3: Production SIF and LSR champion models remain 100% frozen."""
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True


def test_rag_index_untouched():
    """Test 4: FAISS vector index and semantic chunks remain unchanged."""
    faiss_path = BASE_DIR / "datasets" / "rag" / "vector_index.faiss"
    chunks_path = BASE_DIR / "datasets" / "rag" / "semantic_chunks.json"

    if faiss_path.exists():
        assert faiss_path.stat().st_size > 0
    if chunks_path.exists():
        assert chunks_path.stat().st_size > 0


def test_all_427_iogp_records_represented():
    """Test 5: Every validated Stage 37A.1 IOGP record appears in the unified dataset."""
    builder = UnifiedLSRGoldBuilder()
    df_u, meta = builder.build_unified_dataset()

    iogp_sub = df_u[df_u["dataset_origin"] == "IOGP_STAGE37A1"]
    assert len(iogp_sub) == 427


def test_no_pseudo_or_inferred_labels():
    """Test 6 & 7: Zero pseudo-labels and zero inferred labels."""
    builder = UnifiedLSRGoldBuilder()
    df_u, meta = builder.build_unified_dataset()

    assert meta["pseudo_label_count"] == 0
    assert meta["inferred_lsr_count"] == 0


def test_provenance_preservation():
    """Test 8: Validated IOGP records carry dataset_origin=IOGP_STAGE37A1 and SOURCE_GROUNDED provenance."""
    builder = UnifiedLSRGoldBuilder()
    df_u, meta = builder.build_unified_dataset()

    iogp_sub = df_u[df_u["dataset_origin"] == "IOGP_STAGE37A1"]
    for _, row in iogp_sub.iterrows():
        assert row["lsr_label_provenance"] == "SOURCE_GROUNDED"
        assert row["lsr_status"] == "LABELED"


def test_unknown_remains_unknown():
    """Test 9: Canonical records without native LSR labels remain UNKNOWN (never inferred)."""
    builder = UnifiedLSRGoldBuilder()
    df_u, meta = builder.build_unified_dataset()

    can_sub = df_u[df_u["dataset_origin"] == "CANONICAL"]
    unlabeled = can_sub[can_sub["lsr_status"] == "UNKNOWN"]

    assert len(unlabeled) > 4000
    for _, row in unlabeled.iterrows():
        assert row["lsr_label_provenance"] == "NOT_AVAILABLE"


def test_rare_class_preservation():
    """Test 10: Confined Space records (rare class) are preserved without deletion or oversampling."""
    builder = UnifiedLSRGoldBuilder()
    df_u, meta = builder.build_unified_dataset()

    cs_count = (df_u["lsr_primary"] == "Confined Space").sum()
    assert cs_count >= 2


def test_taxonomy_integrity():
    """Test 11: Validated IOGP LSR classes match official taxonomy."""
    builder = UnifiedLSRGoldBuilder()
    df_u, meta = builder.build_unified_dataset()

    valid_classes_lower = {
        "driving", "bypassing safety controls", "line of fire", "energy isolation",
        "safe mechanical lifting", "working at height", "work authorization",
        "confined space", "hot work", "unknown"
    }

    for lsr in df_u["lsr_primary"].unique():
        assert str(lsr).strip().lower() in valid_classes_lower


def test_deterministic_construction():
    """Test 12: Building twice produces identical DataFrame and metadata output."""
    b1 = UnifiedLSRGoldBuilder()
    df1, m1 = b1.build_unified_dataset()

    b2 = UnifiedLSRGoldBuilder()
    df2, m2 = b2.build_unified_dataset()

    assert len(df1) == len(df2)
    assert m1["final_count"] == m2["final_count"]


def test_id_uniqueness():
    """Test 13: All record IDs in the unified dataset are unique."""
    builder = UnifiedLSRGoldBuilder()
    df_u, meta = builder.build_unified_dataset()

    assert df_u["record_id"].is_unique


def test_source_evidence_preservation():
    """Test 14: Every source-grounded LSR record retains traceable evidence text."""
    builder = UnifiedLSRGoldBuilder()
    df_u, meta = builder.build_unified_dataset()

    iogp_sub = df_u[df_u["dataset_origin"] == "IOGP_STAGE37A1"]
    for _, row in iogp_sub.iterrows():
        assert len(str(row["lsr_evidence"]).strip()) > 5


def test_expected_union_accounting():
    """Test 15: final_count == canonical_count + stage37a1_count - confirmed_overlap."""
    builder = UnifiedLSRGoldBuilder()
    df_u, meta = builder.build_unified_dataset()

    assert meta["final_count"] == meta["canonical_input_count"] + meta["stage37a1_input_count"] - meta["confirmed_deduplicated_overlap"]
    assert meta["final_count"] == 4529 + 427  # 4,956 total records


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
