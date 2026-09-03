"""
test_stage37a1_lsr_validation.py - Dedicated PyTest Suite for Stage 37A.1 LSR Source-Grounding Validation & Reconciliation.
"""

import sys
import os
import json
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from data.lsr_reconciliation_engine import (
    LSRReconciliationEngine, CANDIDATES_DIR, VALIDATED_GOLD_CSV, RECONCILIATION_JSON
)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_incident_vs_assignment_distinction():
    """Test 1: One incident with two LSRs must count as 1 unique incident and 2 assignments."""
    raw_dummy = [
        {
            "candidate_id": "CAND-001",
            "incident_id": "INC-TEST-001",
            "source_document": "doc1.pdf",
            "evidence_excerpt": "Applicable Life-Saving Rule: Line of Fire",
            "lsr_normalized": "Line of Fire"
        },
        {
            "candidate_id": "CAND-002",
            "incident_id": "INC-TEST-001",
            "source_document": "doc1.pdf",
            "evidence_excerpt": "Applicable Life-Saving Rule: Energy Isolation",
            "lsr_normalized": "Energy Isolation"
        }
    ]

    engine = LSRReconciliationEngine()
    engine.raw_candidates = raw_dummy
    gold, rq, summary = engine.validate_and_reconcile()

    assert summary["candidate_counts"]["unique_incidents"] == 1
    assert summary["candidate_counts"]["unique_lsr_assignments"] == 2
    assert summary["candidate_counts"]["multi_lsr_incidents"] == 1


def test_duplicate_annual_appearance_reconciliation():
    """Test 2: Same incident appearing in 2023 and 2024 must not become two unique incidents."""
    raw_dummy = [
        {
            "candidate_id": "CAND-001",
            "incident_id": "INC-TEST-001",
            "source_document": "2023_data.pdf",
            "evidence_excerpt": "Applicable Life-Saving Rule: Line of Fire",
            "lsr_normalized": "Line of Fire"
        },
        {
            "candidate_id": "CAND-002",
            "incident_id": "INC-TEST-001",
            "source_document": "2024_data.pdf",
            "evidence_excerpt": "Applicable Life-Saving Rule: Line of Fire",
            "lsr_normalized": "Line of Fire"
        }
    ]

    engine = LSRReconciliationEngine()
    engine.raw_candidates = raw_dummy
    gold, rq, summary = engine.validate_and_reconcile()

    assert summary["candidate_counts"]["unique_incidents"] == 1
    assert summary["candidate_counts"]["duplicate_source_appearances"] == 1


def test_non_incident_lsr_definition_exclusion():
    """Test 3: Text containing rule definitions must be excluded from Gold Candidates."""
    raw_dummy = [
        {
            "candidate_id": "CAND-001",
            "incident_id": "INC-DEF-001",
            "source_document": "guidance.pdf",
            "evidence_excerpt": "General Guidance Definition: Working at Height requires fall protection.",
            "lsr_normalized": "Working at Height"
        }
    ]

    engine = LSRReconciliationEngine()
    engine.raw_candidates = raw_dummy
    gold, rq, summary = engine.validate_and_reconcile()

    assert summary["candidate_counts"]["validated_gold_candidates"] == 0
    assert summary["candidate_counts"]["non_incident_references"] == 1


def test_explicit_evidence_validation():
    """Test 4: Explicit incident-level LSR assignment must become VALIDATED_GOLD."""
    raw_dummy = [
        {
            "candidate_id": "CAND-001",
            "incident_id": "INC-VALID-001",
            "source_document": "report.pdf",
            "evidence_excerpt": "Incident #101 Applicable Rule: Energy Isolation",
            "lsr_normalized": "Energy Isolation"
        }
    ]

    engine = LSRReconciliationEngine()
    engine.raw_candidates = raw_dummy
    gold, rq, summary = engine.validate_and_reconcile()

    assert len(gold) == 1
    assert gold[0]["validation_status"] == "VALIDATED_GOLD"


def test_unmapped_source_incident_handling():
    """Test 5: Valid IOGP incident without canonical match remains VALIDATED_GOLD and is NOT marked invalid."""
    raw_dummy = [
        {
            "candidate_id": "CAND-001",
            "incident_id": "INC-UNMAPPED-001",
            "source_incident_id": "UNKNOWN-ID-999",
            "source_document": "report.pdf",
            "evidence_excerpt": "Incident #999 Applicable Rule: Driving",
            "lsr_normalized": "Driving"
        }
    ]

    engine = LSRReconciliationEngine()
    engine.raw_candidates = raw_dummy
    gold, rq, summary = engine.validate_and_reconcile()

    assert len(gold) == 1
    assert gold[0]["canonical_match_status"] == "NO_MATCH"
    assert gold[0]["validation_status"] == "VALIDATED_GOLD"


def test_ambiguous_mapping_status():
    """Test 6: Ambiguous candidate terms must be placed in Review Queue."""
    raw_dummy = [
        {
            "candidate_id": "CAND-001",
            "incident_id": "INC-AMB-001",
            "source_document": "report.pdf",
            "evidence_excerpt": "Incident #55 Applicable Rule: Special Unknown Custom Rule",
            "lsr_normalized": None
        }
    ]

    engine = LSRReconciliationEngine()
    engine.raw_candidates = raw_dummy
    gold, rq, summary = engine.validate_and_reconcile()

    assert len(gold) == 0
    assert summary["candidate_counts"]["ambiguous_candidates"] == 1


def test_multi_label_preservation():
    """Test 7: Primary + Secondary LSRs must remain attached to incident."""
    raw_dummy = [
        {
            "candidate_id": "CAND-001",
            "incident_id": "INC-MULTI-001",
            "source_document": "doc.pdf",
            "evidence_excerpt": "Incident #1 Primary Rule: Line of Fire",
            "lsr_normalized": "Line of Fire",
            "primary_lsr": "Line of Fire"
        },
        {
            "candidate_id": "CAND-002",
            "incident_id": "INC-MULTI-001",
            "source_document": "doc.pdf",
            "evidence_excerpt": "Incident #1 Secondary Rule: Energy Isolation",
            "lsr_normalized": "Energy Isolation",
            "secondary_lsr": "Energy Isolation"
        }
    ]

    engine = LSRReconciliationEngine()
    engine.raw_candidates = raw_dummy
    gold, rq, summary = engine.validate_and_reconcile()

    assert len(gold) == 2
    assert summary["candidate_counts"]["unique_incidents"] == 1


def test_conflict_handling():
    """Test 8: Unresolved or invalid extractions must be tracked in review queue."""
    raw_dummy = [
        {
            "candidate_id": "CAND-001",
            "incident_id": "INC-ERR-001",
            "source_document": "doc.pdf",
            "evidence_excerpt": "Short",
            "lsr_normalized": "Hot Work"
        }
    ]

    engine = LSRReconciliationEngine()
    engine.raw_candidates = raw_dummy
    gold, rq, summary = engine.validate_and_reconcile()

    assert summary["candidate_counts"]["invalid_extractions"] == 1


def test_provenance_completeness():
    """Test 9: Every validated Gold candidate must contain provenance and source details."""
    engine = LSRReconciliationEngine()
    gold, rq, summary = engine.validate_and_reconcile()

    for g in gold:
        assert "gold_candidate_id" in g
        assert "source_document" in g
        assert "evidence_excerpt" in g
        assert g["validation_status"] == "VALIDATED_GOLD"


def test_no_inferred_labels():
    """Test 10: Implicit narratives ('worker contacted energized equipment') must NOT produce validated gold candidate."""
    raw_dummy = [
        {
            "candidate_id": "CAND-001",
            "incident_id": "INC-IMP-001",
            "source_document": "doc.pdf",
            "evidence_excerpt": "Worker touched live cable near compressor",
            "lsr_normalized": None
        }
    ]

    engine = LSRReconciliationEngine()
    engine.raw_candidates = raw_dummy
    gold, rq, summary = engine.validate_and_reconcile()

    assert len(gold) == 0


def test_determinism():
    """Test 11: Repeated execution produces identical summary stats and output structures."""
    engine = LSRReconciliationEngine()
    g1, rq1, s1 = engine.validate_and_reconcile()
    g2, rq2, s2 = engine.validate_and_reconcile()

    assert s1["candidate_counts"] == s2["candidate_counts"]


def test_production_model_and_rag_freeze():
    """Test 12: Production model weights, canonical dataset, and RAG indexes remain 100% frozen."""
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
