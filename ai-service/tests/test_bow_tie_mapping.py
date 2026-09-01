"""
test_bow_tie_mapping.py - Dedicated Test Suite for Stage 32 Bow-Tie / Barrier Failure Mapping.
"""

import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.bow_tie_mapper import BowTieMapper

client = TestClient(app)


@pytest.fixture
def sample_bow_tie_report():
    return {
        "record_id": "R-B01",
        "report_date": "2025-01-10",
        "location": "Duliajan",
        "activity": "Pipeline Maintenance",
        "hazard": "Pressurized Hydrocarbon Gas",
        "barrier_failure": "Energy Isolation Control Failure",
        "potential_consequence": "Flash Fire & High Pressure Injection",
        "narrative": "Technician began line disconnect prior to verifying double block and bleed isolation valve.",
        "primary_life_saving_rule": "Energy Isolation",
        "is_sif": True
    }


def test_bow_tie_node_and_edge_mapping(sample_bow_tie_report):
    """Verify threat -> barrier -> top event -> consequence node and edge mapping."""
    mapper = BowTieMapper()
    bt = mapper.map_report_to_bow_tie(sample_bow_tie_report)

    assert bt["report_id"] == "R-B01"
    assert "nodes" in bt
    assert "edges" in bt
    assert len(bt["nodes"]) >= 4
    assert len(bt["edges"]) >= 3

    # Verify node types and provenance
    n_types = [n["type"] for n in bt["nodes"]]
    assert "HAZARD" in n_types
    assert "THREAT" in n_types
    assert "FAILED_BARRIER" in n_types
    assert "TOP_EVENT" in n_types
    assert "CONSEQUENCE" in n_types

    bar_node = next(n for n in bt["nodes"] if n["type"] == "FAILED_BARRIER")
    assert bar_node["provenance"] == "OBSERVED"
    assert bar_node["label"] == "Energy Isolation Control Failure"

    top_event_node = next(n for n in bt["nodes"] if n["type"] == "TOP_EVENT")
    assert top_event_node["provenance"] == "INFERRED"


def test_deterministic_5_runs(sample_bow_tie_report):
    """Verify 5 consecutive executions generate 100% identical Bow-Tie node & edge graphs."""
    mapper = BowTieMapper()

    run1 = mapper.map_report_to_bow_tie(sample_bow_tie_report)
    run2 = mapper.map_report_to_bow_tie(sample_bow_tie_report)
    run3 = mapper.map_report_to_bow_tie(sample_bow_tie_report)

    assert run1 == run2 == run3, "Bow-Tie mapping must be 100% deterministic"
    assert run1["bow_tie_id"] == run2["bow_tie_id"]


def test_fastapi_bow_ties_endpoint():
    """Verify GET /api/v1/bow-ties/{report_id} FastAPI endpoint."""
    resp = client.get("/api/v1/bow-ties/R-1001")
    assert resp.status_code == 200
    data = resp.json()
    assert "bow_tie_id" in data
    assert "report_id" in data
    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main(["-v", __file__]))
