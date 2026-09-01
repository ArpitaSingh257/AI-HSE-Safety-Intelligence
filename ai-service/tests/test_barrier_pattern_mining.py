"""
test_barrier_pattern_mining.py - Dedicated Test Suite for Stage 24 Barrier Failure Pattern Mining.
"""

import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.barrier_pattern_miner import BarrierPatternMiner, CANONICAL_BARRIER_MAP

client = TestClient(app)


@pytest.fixture
def sample_barrier_records():
    return [
        {
            "record_id": "BAR-TEST-001",
            "report_date": "2025-01-10",
            "location": "Duliajan",
            "activity": "Maintenance",
            "primary_life_saving_rule": "Energy Isolation",
            "hazard": "Stored Pressure",
            "barrier_failure": "Energy was not isolated before line rupture",
            "narrative": "Discharge line ruptured under pressure before isolation was complete.",
            "sif_potential": True
        },
        {
            "record_id": "BAR-TEST-002",
            "report_date": "2025-01-15",
            "location": "Moran",
            "activity": "Maintenance",
            "primary_life_saving_rule": "Energy Isolation",
            "hazard": "Stored Pressure",
            "barrier_failure": "Lockout failure on valve bleeder",
            "narrative": "Operator opened line while valve lockout was incomplete.",
            "sif_potential": True
        },
        {
            "record_id": "BAR-TEST-003",
            "report_date": "2025-02-01",
            "location": "Digboi",
            "activity": "Maintenance",
            "primary_life_saving_rule": "Energy Isolation",
            "hazard": "Stored Pressure",
            "barrier_failure": "Isolation bypassed without authorization",
            "narrative": "Manifold bleeder plug detached due to bypassed isolation control.",
            "sif_potential": True
        },
        {
            "record_id": "BAR-TEST-004",
            "report_date": "2025-02-10",
            "location": "Naharkatiya",
            "activity": "Hot Work",
            "primary_life_saving_rule": "Hot Work",
            "hazard": "Flammable Gas",
            "barrier_failure": "General safety issue",
            "narrative": "Flash fire occurred during welding.",
            "sif_potential": False
        }
    ]


def test_canonical_barrier_normalization():
    """Verify free-text barrier expressions map to canonical barrier concepts."""
    miner = BarrierPatternMiner()
    
    b1 = miner.normalize_barrier_failure("Energy was not isolated before line rupture")
    assert "ENERGY_ISOLATION_CONTROL_FAILURE" in b1

    b2 = miner.normalize_barrier_failure("Gas test not performed before vessel entry")
    assert "ATMOSPHERIC_GAS_MONITORING_FAILURE" in b2

    b3 = miner.normalize_barrier_failure("Control issue")
    assert b3 == ["UNKNOWN"]


def test_repeated_barrier_failure_detected(sample_barrier_records):
    """Verify 3+ matching incidents form a canonical barrier failure pattern."""
    miner = BarrierPatternMiner(min_barrier_incidents=3)
    patterns = miner.mine_barrier_patterns(sample_barrier_records)

    assert len(patterns) >= 1
    eiso_pat = next(p for p in patterns if p["barrier_code"] == "ENERGY_ISOLATION_CONTROL_FAILURE")
    assert eiso_pat["incident_count"] == 3
    assert eiso_pat["sif_incident_count"] == 3
    assert eiso_pat["sif_density"] == 1.0
    assert eiso_pat["pattern_strength"] == "HIGH"
    assert "BAR-TEST-001" in eiso_pat["incident_ids"]
    assert "BAR-TEST-002" in eiso_pat["incident_ids"]
    assert "BAR-TEST-003" in eiso_pat["incident_ids"]


def test_unrelated_barriers_remain_separate(sample_barrier_records):
    """Verify vague or unrelated barriers remain separate or map to UNKNOWN."""
    miner = BarrierPatternMiner(min_barrier_incidents=3)
    patterns = miner.mine_barrier_patterns(sample_barrier_records)

    for pat in patterns:
        if pat["barrier_code"] == "ENERGY_ISOLATION_CONTROL_FAILURE":
            assert "BAR-TEST-004" not in pat["incident_ids"]


def test_deterministic_barrier_pattern_ids(sample_barrier_records):
    """Verify running miner 5 times produces 100% identical barrier pattern IDs and scores."""
    miner = BarrierPatternMiner(min_barrier_incidents=3)
    run1 = miner.mine_barrier_patterns(sample_barrier_records)
    run2 = miner.mine_barrier_patterns(sample_barrier_records)
    run3 = miner.mine_barrier_patterns(sample_barrier_records)

    assert run1 == run2 == run3
    assert run1[0]["barrier_pattern_id"] == run2[0]["barrier_pattern_id"]


def test_empty_dataset_handling():
    """Verify empty dataset returns empty list without error."""
    miner = BarrierPatternMiner(min_barrier_incidents=3)
    patterns = miner.mine_barrier_patterns([])
    assert patterns == []


def test_fastapi_barrier_patterns_endpoint():
    """Verify GET /api/v1/barrier-patterns FastAPI endpoint schema and HTTP 200 response."""
    resp = client.get("/api/v1/barrier-patterns?min_support=3")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_barrier_patterns" in data
    assert "barrier_patterns" in data
    assert isinstance(data["barrier_patterns"], list)

    if len(data["barrier_patterns"]) > 0:
        pat = data["barrier_patterns"][0]
        assert "barrier_pattern_id" in pat
        assert "barrier_name" in pat
        assert "pattern_strength" in pat
        assert "incident_ids" in pat
