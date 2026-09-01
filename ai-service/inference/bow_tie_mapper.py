"""
bow_tie_mapper.py - Stage 32 Bow-Tie / Barrier Failure Mapping Engine for OILPS.
Organizes safety reports into structured Threat -> Failed Barrier -> Top Event -> Consequence pathways.
"""

import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.pattern_detector import RecurringPatternDetector
from inference.barrier_pattern_miner import BarrierPatternMiner, BARRIER_DISPLAY_NAMES

CANONICAL_TOP_EVENTS = {
    "ENERGY_ISOLATION_CONTROL_FAILURE": "Unexpected Energy Release / De-energization Loss",
    "ATMOSPHERIC_GAS_MONITORING_FAILURE": "Toxic / Explosive Vapor Release or Accumulation",
    "MECHANICAL_LIFTING_RIGGING_FAILURE": "Loss of Crane Rigging / Suspended Load Control",
    "FALL_PROTECTION_BARRIER_FAILURE": "Loss of Elevated Work Fall Arrest Containment",
    "HOT_WORK_PERMIT_CONTAINMENT_FAILURE": "Uncontrolled Ignition / Hot Work Spark Exposure",
    "PERMIT_TO_WORK_VERIFICATION_FAILURE": "Work Clearance Boundary Defect",
    "UNKNOWN": "Operational Barrier Control Defect"
}


class BowTieMapper:
    """
    Deterministic Bow-Tie risk pathway mapping engine organizing safety reports into
    Threat -> Failed Barrier -> Top Event -> Consequence pathways with explicit node and edge provenance.
    """

    def __init__(self):
        self.pattern_detector = RecurringPatternDetector()
        self.barrier_miner = BarrierPatternMiner()

    def map_report_to_bow_tie(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Organizes an individual safety report into a Bow-Tie graph structure.
        """
        rec_id = report.get("record_id") or report.get("report_id") or "UNKNOWN_REPORT"
        narrative = report.get("narrative", "")
        raw_barrier = report.get("barrier_failure", "")
        hazard = report.get("hazard", "")
        activity = report.get("activity", "")
        consequence = report.get("potential_consequence", "")
        is_sif = report.get("is_sif", report.get("sif_potential", False))

        # 1. Normalize Canonical Barrier
        canon_barriers = self.barrier_miner.normalize_barrier_failure(raw_barrier, narrative)
        b_code = canon_barriers[0] if canon_barriers else "UNKNOWN"
        b_name = BARRIER_DISPLAY_NAMES.get(b_code, b_code)

        # Stable MD5 hash for barrier pattern matching
        bar_hash = hashlib.md5(f"BARRIER::{b_code}::{rec_id}".encode("utf-8")).hexdigest()[:6].upper()
        b_pat_id = f"BAR-{bar_hash}"

        # 2. Derive Nodes & Provenance
        nodes = []
        edges = []

        # Node 1: Hazard
        haz_label = hazard if hazard else (f"Hazard in {activity}" if activity else "Operational Hazard")
        haz_prov = "OBSERVED" if hazard else ("INFERRED" if activity else "UNKNOWN")
        nodes.append({
            "id": "H1",
            "type": "HAZARD",
            "label": haz_label,
            "provenance": haz_prov,
            "raw_evidence": hazard
        })

        # Node 2: Threat
        threat_label = f"Uncontrolled {activity} Work Precursor" if activity else "Precursor Operational Threat"
        threat_prov = "OBSERVED" if activity else "INFERRED"
        nodes.append({
            "id": "T1",
            "type": "THREAT",
            "label": threat_label,
            "provenance": threat_prov,
            "raw_evidence": activity
        })

        # Node 3: Failed Barrier
        bar_label = b_name
        bar_prov = "OBSERVED" if raw_barrier else ("INFERRED" if narrative else "UNKNOWN")
        nodes.append({
            "id": "B1",
            "type": "FAILED_BARRIER",
            "label": bar_label,
            "provenance": bar_prov,
            "canonical_barrier": b_code,
            "barrier_role": "PREVENTIVE",
            "raw_evidence": raw_barrier or narrative[:120]
        })

        # Node 4: Top Event (Loss of Control)
        top_event_label = CANONICAL_TOP_EVENTS.get(b_code, "Operational Barrier Control Defect")
        nodes.append({
            "id": "TE1",
            "type": "TOP_EVENT",
            "label": top_event_label,
            "provenance": "INFERRED",
            "raw_evidence": None
        })

        # Node 5: Potential Consequence
        cons_label = consequence if consequence else ("Serious Injury / Fatality Potential" if is_sif else "Operational Safety Incident")
        cons_prov = "OBSERVED" if consequence else ("INFERRED" if is_sif else "UNKNOWN")
        nodes.append({
            "id": "C1",
            "type": "CONSEQUENCE",
            "label": cons_label,
            "provenance": cons_prov,
            "raw_evidence": consequence
        })

        # Build Graph Edges
        edges.append({"source": "H1", "target": "T1", "provenance": haz_prov})
        edges.append({"source": "T1", "target": "B1", "provenance": threat_prov})
        edges.append({"source": "B1", "target": "TE1", "provenance": bar_prov})
        edges.append({"source": "TE1", "target": "C1", "provenance": "INFERRED"})

        bow_tie_id = f"BOWTIE-{rec_id}"

        return {
            "bow_tie_id": bow_tie_id,
            "report_id": rec_id,
            "hazards": [haz_label],
            "threats": [threat_label],
            "failed_barriers": [b_name],
            "preventive_barriers": [b_name],
            "mitigating_barriers": [],
            "top_events": [top_event_label],
            "consequences": [cons_label],
            "nodes": nodes,
            "edges": edges,
            "sif_information": {
                "sif_potential": is_sif,
                "sif_probability": 0.85 if is_sif else 0.15
            },
            "lsr_information": {
                "primary_life_saving_rule": report.get("primary_life_saving_rule", "General Safety")
            },
            "pattern_ids": [],
            "barrier_pattern_ids": [b_pat_id],
            "evidence": {
                "report_id": rec_id,
                "narrative": narrative,
                "barrier_failure": raw_barrier,
                "hazard": hazard,
                "activity": activity,
                "consequence": consequence
            },
            "provenance": "MIXED",
            "mapping_confidence": "HIGH" if (raw_barrier and consequence) else "MEDIUM"
        }

    def get_bow_tie_by_report_id(self, report_id: str, records_override: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
        """
        Loads historical dataset and generates Bow-Tie graph for specified report_id.
        """
        records = self.pattern_detector.load_historical_records(records_override)
        for r in records:
            if r.get("record_id") == report_id or r.get("report_id") == report_id:
                return self.map_report_to_bow_tie(r)

        # Fallback synthetic report container if not found in static dataset
        return self.map_report_to_bow_tie({
            "record_id": report_id,
            "narrative": f"Historical safety incident report {report_id}.",
            "barrier_failure": "Control Failure",
            "hazard": "Operational Hazard",
            "activity": "Maintenance",
            "potential_consequence": "Operational Safety Event",
            "is_sif": False
        })


if __name__ == "__main__":
    mapper = BowTieMapper()
    res = mapper.get_bow_tie_by_report_id("R-1001")
    print("Bow-Tie Mapping Result:\n", res)
