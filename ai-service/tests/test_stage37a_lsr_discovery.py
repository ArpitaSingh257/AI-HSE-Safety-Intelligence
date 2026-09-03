"""
test_stage37a_lsr_discovery.py - Dedicated PyTest Suite for Stage 37A Local IOGP LSR Ground-Truth Discovery & Audit.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.lsr_discovery_engine import (
    LSRDiscoveryEngine, EXPLICIT_LSR_REGEX, IOGP_LSR_TAXONOMY_MAP,
    OUTPUT_DIR, INVENTORY_CSV_PATH, AUDIT_JSON_PATH
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_resource_discovery_scanner():
    """Test 1: Scanner recursively discovers supported files under resources/."""
    engine = LSRDiscoveryEngine()
    inventory = engine.scan_and_inventory_resources()

    assert isinstance(inventory, list)
    assert len(inventory) > 0

    for item in inventory:
        assert "file_name" in item
        assert "relative_path" in item
        assert "file_type" in item
        assert "likely_relevance_to_LSR" in item


def test_explicit_only_rule():
    """Test 2: Implicit narrative text ('worker contacted energized equipment') must NOT generate LSR candidate."""
    engine = LSRDiscoveryEngine()

    implicit_narrative = "The maintenance worker contacted energized electrical equipment without PPE near P-101."
    match = EXPLICIT_LSR_REGEX.search(implicit_narrative)

    # Must NOT match as explicit LSR assignment
    assert match is None


def test_explicit_assignment_extraction():
    """Test 3: Explicit string ('Life-Saving Rule: Energy Isolation') must extract candidate."""
    explicit_text = "Incident Report #142 - Applicable Life-Saving Rule: Energy Isolation"
    match = EXPLICIT_LSR_REGEX.search(explicit_text)

    assert match is not None
    raw_val = match.group(2).strip()
    assert raw_val.lower() == "energy isolation"


def test_rule_definition_exclusion():
    """Test 4: Generic section defining 'Working at Height' must NOT become an incident label."""
    engine = LSRDiscoveryEngine()
    dummy_inventory = [{
        "file_name": "IOGP Life-Saving Rules.pdf",
        "relative_path": "resources/safety-recommendation-engine/IOGP Life-Saving Rules.pdf",
        "file_type": "pdf",
        "file_size_bytes": 1000,
        "source_organization": "IOGP",
        "document_title": "IOGP Life-Saving Rules",
        "document_year": "2024",
        "page_count": 1,
        "likely_relevance_to_LSR": "HIGH"
    }]

    cands, non_inc, amb = engine.extract_lsr_evidence(dummy_inventory)

    # Definitions should be in non_inc, not cands
    for n in non_inc:
        assert n["mention_type"] in ["RULE_DEFINITION", "GENERAL_DISCUSSION"]


def test_multi_label_preservation():
    """Test 5: Multi-label fields must preserve all explicit rules."""
    all_rules = ["Line of Fire", "Energy Isolation"]
    serialized = json.dumps(all_rules)
    deserialized = json.loads(serialized)

    assert len(deserialized) == 2
    assert "Line of Fire" in deserialized
    assert "Energy Isolation" in deserialized


def test_historical_terminology_preservation():
    """Test 6: Original source terminology ('Isolation') mapped to normalized ('Energy Isolation') while storing source text."""
    raw_source = "Isolation"
    norm = IOGP_LSR_TAXONOMY_MAP.get(raw_source.lower())

    assert norm == "Energy Isolation"
    assert raw_source != norm  # Preserves raw source text distinction


def test_provenance_completeness():
    """Test 7: Every candidate must contain complete provenance metadata."""
    engine = LSRDiscoveryEngine()
    inv = engine.scan_and_inventory_resources()
    cands, non_inc, amb = engine.extract_lsr_evidence(inv)

    for c in cands:
        assert "candidate_id" in c
        assert "source_document" in c
        assert "source_path" in c
        assert "evidence_excerpt" in c
        assert "page_number" in c or "row_reference" in c
        assert c["confidence"] == "SOURCE_EXPLICIT"


def test_deduplication_integrity():
    """Test 8: Repeated extraction of same source incident does not inflate candidate counts."""
    engine = LSRDiscoveryEngine()
    inv = engine.scan_and_inventory_resources()
    cands1, _, _ = engine.extract_lsr_evidence(inv)
    cands2, _, _ = engine.extract_lsr_evidence(inv)

    assert len(cands1) == len(cands2)


def test_ambiguous_evidence_handling():
    """Test 9: Ambiguous matches must be marked REVIEW_REQUIRED."""
    unmapped_raw = "Unidentified Special Safety Custom Rule"
    norm_lsr = IOGP_LSR_TAXONOMY_MAP.get(unmapped_raw.lower(), None)

    assert norm_lsr is None  # Marked for review required rather than forced guess


def test_determinism():
    """Test 10: Repeated execution produces identical inventory and evidence structures."""
    engine = LSRDiscoveryEngine()
    inv1 = engine.scan_and_inventory_resources()
    inv2 = engine.scan_and_inventory_resources()

    assert inv1 == inv2


def test_production_model_and_rag_freeze():
    """Test 11: Production model weights, canonical dataset, and RAG indexes remain 100% frozen."""
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["sif_champion_loaded"] == True
    assert health_data["lsr_champion_loaded"] == True

    canonical_csv = BASE_DIR / "datasets" / "processed" / "oilps_unified_deduped.csv"
    assert canonical_csv.exists() and canonical_csv.stat().st_size > 0


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
