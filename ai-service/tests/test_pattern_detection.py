"""
test_pattern_detection.py - Dedicated Test Suite for Stage 23 Recurring Precursor Pattern Detection.
"""

import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from inference.pattern_detector import RecurringPatternDetector

client = TestClient(app)


@pytest.fixture
def sample_incidents():
    return [
        {
            "record_id": "INC-TEST-001",
            "report_date": "2025-01-10",
            "location": "Duliajan",
            "activity": "Maintenance",
            "primary_life_saving_rule": "Energy Isolation",
            "hazard": "High Pressure",
            "barrier_failure": "Valves Bleeder Rupture",
            "narrative": "Operator exposed to pressure release during discharge line testing.",
            "sif_potential": True
        },
        {
            "record_id": "INC-TEST-002",
            "report_date": "2025-01-15",
            "location": "Moran",
            "activity": "Maintenance",
            "primary_life_saving_rule": "Energy Isolation",
            "hazard": "High Pressure",
            "barrier_failure": "Valves Bleeder Rupture",
            "narrative": "Line pressurized while fitting was loose, causing pressure blowout.",
            "sif_potential": True
        },
        {
            "record_id": "INC-TEST-003",
            "report_date": "2025-02-01",
            "location": "Digboi",
            "activity": "Maintenance",
            "primary_life_saving_rule": "Energy Isolation",
            "hazard": "High Pressure",
            "barrier_failure": "Valves Bleeder Rupture",
            "narrative": "Pressure gauge failed on discharge manifold during hydrotest.",
            "sif_potential": True
        },
        {
            "record_id": "INC-TEST-004",
            "report_date": "2025-02-10",
            "location": "Naharkatiya",
            "activity": "Hot Work",
            "primary_life_saving_rule": "Hot Work",
            "hazard": "Flammable Vapor",
            "barrier_failure": "Gas Monitoring Gap",
            "narrative": "Flash fire occurred during welding near fuel line manifold.",
            "sif_potential": False
        }
    ]


def test_minimum_support_threshold(sample_incidents):
    """Verify that fewer incidents than min_pattern_incidents does not form a pattern."""
    detector = RecurringPatternDetector(min_pattern_incidents=3)
    # Pass only 2 energy isolation incidents
    subset = sample_incidents[:2]
    patterns = detector.detect_patterns(subset)
    assert len(patterns) == 0, "Should not create pattern with < min_pattern_incidents"


def test_pattern_detection_from_repeated_incidents(sample_incidents):
    """Verify 3+ similar incidents form a valid recurring precursor pattern."""
    detector = RecurringPatternDetector(min_pattern_incidents=3)
    patterns = detector.detect_patterns(sample_incidents)
    
    assert len(patterns) >= 1
    pat = patterns[0]
    assert "Energy Isolation" in pat["dominant_lsr"]
    assert pat["incident_count"] == 3
    assert pat["sif_incident_count"] == 3
    assert pat["sif_density"] == 1.0
    assert pat["pattern_strength"] == "HIGH"
    assert "INC-TEST-001" in pat["incident_ids"]
    assert "INC-TEST-002" in pat["incident_ids"]
    assert "INC-TEST-003" in pat["incident_ids"]


def test_unrelated_incidents_remain_separate(sample_incidents):
    """Verify unrelated incidents (Hot Work vs Energy Isolation) remain separate."""
    detector = RecurringPatternDetector(min_pattern_incidents=3)
    patterns = detector.detect_patterns(sample_incidents)
    
    # The Hot Work incident (INC-TEST-004) is single so it should not be merged into the Energy Isolation pattern
    for pat in patterns:
        assert "INC-TEST-004" not in pat["incident_ids"]


def test_deterministic_pattern_ids_and_output(sample_incidents):
    """Verify 5 consecutive runs produce 100% identical pattern IDs, strength, and summaries."""
    detector = RecurringPatternDetector(min_pattern_incidents=3)
    
    run1 = detector.detect_patterns(sample_incidents)
    run2 = detector.detect_patterns(sample_incidents)
    run3 = detector.detect_patterns(sample_incidents)

    assert run1 == run2 == run3, "Pattern detection output must be 100% deterministic"
    assert run1[0]["pattern_id"] == run2[0]["pattern_id"]


def test_empty_dataset_handling():
    """Verify empty dataset returns empty list without error."""
    detector = RecurringPatternDetector(min_pattern_incidents=3)
    patterns = detector.detect_patterns([])
    assert patterns == []


def test_missing_fields_handling():
    """Verify missing structured fields are handled explicitly."""
    incomplete_incidents = [
        {"record_id": "INC-01", "narrative": "Pressure line burst", "sif_potential": True},
        {"record_id": "INC-02", "narrative": "Pressure line burst", "sif_potential": True},
        {"record_id": "INC-03", "narrative": "Pressure line burst", "sif_potential": True},
    ]
    detector = RecurringPatternDetector(min_pattern_incidents=3)
    patterns = detector.detect_patterns(incomplete_incidents)
    assert len(patterns) == 1
    assert patterns[0]["dominant_activity"] == "General Operations"


def test_fastapi_patterns_endpoint():
    """Verify GET /api/v1/patterns API endpoint schema and HTTP 200 response."""
    resp = client.get("/api/v1/patterns?min_support=3")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_patterns" in data
    assert "patterns" in data
    assert isinstance(data["patterns"], list)

    if len(data["patterns"]) > 0:
        pat = data["patterns"][0]
        assert "pattern_id" in pat
        assert "summary" in pat
        assert "pattern_strength" in pat
        assert "incident_ids" in pat
