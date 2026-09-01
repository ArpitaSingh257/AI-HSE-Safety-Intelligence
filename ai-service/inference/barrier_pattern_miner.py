"""
barrier_pattern_miner.py - Stage 24 Barrier Failure Pattern Mining Engine for OILPS.
Extracts, normalizes, and groups repeated safety barrier failure patterns across historical incident data.
"""

import sys
import re
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.pattern_detector import RecurringPatternDetector


CANONICAL_BARRIER_MAP = {
    "ENERGY_ISOLATION_CONTROL_FAILURE": [
        "isolation", "isolated", "isolate", "isolating", "isolat", "lockout", "tagout", "loto",
        "zero energy", "de-energize", "de-energised", "electrical isolation", "valve bleeder",
        "plug rupture", "pressurized line", "pressure release", "fitting loose", "discharge line"
    ],
    "ATMOSPHERIC_GAS_MONITORING_FAILURE": [
        "gas test", "gas monitor", "h2s", "toxic gas", "explosimeter", "stratification",
        "oxygen deficiency", "hazardous atmosphere", "gas detector", "vapor testing"
    ],
    "MECHANICAL_LIFTING_RIGGING_FAILURE": [
        "crane", "sling", "rigging", "suspended load", "hoist", "tag line",
        "load drop", "lifting gear", "rig floor", "shackle"
    ],
    "FALL_PROTECTION_BARRIER_FAILURE": [
        "harness", "lanyard", "lifeline", "scaffold", "guardrail", "anchor point",
        "height work", "elevated platform", "fall arrest"
    ],
    "HOT_WORK_PERMIT_CONTAINMENT_FAILURE": [
        "hot work", "welding", "cutting", "fire watch", "sparks", "combustible gas",
        "fire blanket", "flash fire", "fuel manifold"
    ],
    "PERMIT_TO_WORK_VERIFICATION_FAILURE": [
        "ptw", "permit to work", "job safety analysis", "jsa", "pre-job brief",
        "toolbox talk", "work clearance", "authorization"
    ]
}

BARRIER_DISPLAY_NAMES = {
    "ENERGY_ISOLATION_CONTROL_FAILURE": "Energy Isolation Control Failure",
    "ATMOSPHERIC_GAS_MONITORING_FAILURE": "Atmospheric & Toxic Gas Monitoring Control Failure",
    "MECHANICAL_LIFTING_RIGGING_FAILURE": "Mechanical Lifting & Rigging Barrier Failure",
    "FALL_PROTECTION_BARRIER_FAILURE": "Working at Height & Fall Protection Barrier Failure",
    "HOT_WORK_PERMIT_CONTAINMENT_FAILURE": "Hot Work Spark Containment & Ignition Control Failure",
    "PERMIT_TO_WORK_VERIFICATION_FAILURE": "Permit-to-Work & Job Safety Analysis Barrier Failure",
    "UNKNOWN": "Unspecified Barrier Failure"
}


class BarrierPatternMiner:
    """
    Deterministic miner that extracts canonical repeated barrier failure patterns
    from historical safety incident records and Stage 23 recurring precursor patterns.
    """

    def __init__(self, min_barrier_incidents: int = 3):
        self.min_barrier_incidents = max(2, min_barrier_incidents)
        self.pattern_detector = RecurringPatternDetector(min_pattern_incidents=3)

    def normalize_barrier_failure(self, raw_barrier: str, narrative: str = "") -> List[str]:
        """
        Deterministically normalizes free-text barrier expressions to canonical barrier concepts.
        Supports multi-barrier matching per incident.
        """
        combined = f"{raw_barrier} {narrative}".lower()

        # Reject overgeneralized vague phrases without specific barrier evidence
        vague_phrases = ["control issue", "unsafe procedure", "safety problem", "general gap"]
        if any(vp == combined.strip() for vp in vague_phrases):
            return ["UNKNOWN"]

        matched = []
        for canonical, keywords in CANONICAL_BARRIER_MAP.items():
            if any(kw in combined for kw in keywords):
                matched.append(canonical)

        if not matched:
            return ["UNKNOWN"]
        return matched

    def mine_barrier_patterns(self, records_override: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Mines recurring barrier failure patterns across historical incidents.
        Returns a stably sorted list of barrier failure pattern objects.
        """
        records = self.pattern_detector.load_historical_records(records_override)
        stage23_patterns = self.pattern_detector.detect_patterns(records)

        if not records:
            return []

        # Map incident_id -> Stage 23 pattern_ids
        inc_to_patterns: Dict[str, List[str]] = {}
        for pat in stage23_patterns:
            for inc_id in pat["incident_ids"]:
                if inc_id not in inc_to_patterns:
                    inc_to_patterns[inc_id] = []
                inc_to_patterns[inc_id].append(pat["pattern_id"])

        # Group records by canonical barrier concept
        barrier_groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in records:
            raw_b = r.get("barrier_failure", "")
            narrative = r.get("narrative", "")
            canon_barriers = self.normalize_barrier_failure(raw_b, narrative)

            for b_code in canon_barriers:
                if b_code not in barrier_groups:
                    barrier_groups[b_code] = []
                barrier_groups[b_code].append(r)

        mined_patterns = []

        for b_code in sorted(barrier_groups.keys()):
            cluster = barrier_groups[b_code]
            # Deduplicate by record_id
            unique_records_dict = {c["record_id"]: c for c in cluster}
            unique_records = list(unique_records_dict.values())
            unique_records.sort(key=lambda x: x["record_id"])

            inc_count = len(unique_records)
            if inc_count < self.min_barrier_incidents and b_code != "UNKNOWN":
                continue
            if b_code == "UNKNOWN" and inc_count < 1:
                continue

            inc_ids = [c["record_id"] for c in unique_records]
            sif_count = sum(1 for c in unique_records if c["is_sif"])
            sif_density = round(sif_count / inc_count, 4) if inc_count > 0 else 0.0

            activities = [c["activity"] for c in unique_records if c.get("activity")]
            locations = [c["location"] for c in unique_records if c.get("location")]
            hazards = [c["hazard"] for c in unique_records if c.get("hazard")]
            lsr_rules = [c["primary_life_saving_rule"] for c in unique_records if c.get("primary_life_saving_rule")]
            consequences = [c["potential_consequence"] for c in unique_records if c.get("potential_consequence")]

            dom_activity = max(set(activities), key=activities.count) if activities else "General Operations"
            dom_lsr = max(set(lsr_rules), key=lsr_rules.count) if lsr_rules else "General Safety"
            dom_hazard = max(set(hazards), key=hazards.count) if hazards else "Operational Hazard"
            unique_locations = sorted(list(set(locations)))
            unique_consequences = sorted(list(set(consequences)))

            # Collect linked Stage 23 pattern IDs
            linked_patterns = set()
            for inc_id in inc_ids:
                for p_id in inc_to_patterns.get(inc_id, []):
                    linked_patterns.add(p_id)
            sorted_pattern_ids = sorted(list(linked_patterns))

            dates = [c["report_date"] for c in unique_records if c.get("report_date")]
            dates_sorted = sorted(dates)
            first_obs = dates_sorted[0] if dates_sorted else "Unknown"
            last_obs = dates_sorted[-1] if dates_sorted else "Unknown"

            # Determine Barrier Pattern Strength
            if (inc_count >= 5 and sif_density >= 0.40) or (inc_count >= 3 and sif_density >= 0.75):
                strength = "HIGH"
            elif inc_count >= 3 and (sif_density >= 0.25 or len(unique_locations) >= 2):
                strength = "MEDIUM"
            else:
                strength = "LOW"

            # Stable content-derived pattern ID
            hash_src = f"BARRIER::{b_code}::{inc_ids[0]}"
            bar_hash = hashlib.md5(hash_src.encode("utf-8")).hexdigest()[:6].upper()
            barrier_pattern_id = f"BAR-{bar_hash}"
            barrier_name = BARRIER_DISPLAY_NAMES.get(b_code, b_code)

            evidence_quotes = [c["narrative"][:160] + "..." for c in unique_records[:3] if c.get("narrative")]

            barrier_pattern = {
                "barrier_pattern_id": barrier_pattern_id,
                "barrier_code": b_code,
                "barrier_name": barrier_name,
                "incident_count": inc_count,
                "sif_incident_count": sif_count,
                "sif_density": sif_density,
                "pattern_strength": strength,
                "dominant_activity": dom_activity,
                "dominant_lsr": dom_lsr,
                "dominant_hazard": dom_hazard,
                "locations": unique_locations,
                "potential_consequences": unique_consequences[:3],
                "stage23_pattern_ids": sorted_pattern_ids,
                "incident_ids": inc_ids,
                "first_observed": first_obs,
                "last_observed": last_obs,
                "supporting_evidence": evidence_quotes
            }
            mined_patterns.append(barrier_pattern)

        # Sort stably by (-incident_count, -sif_density, barrier_pattern_id)
        mined_patterns.sort(key=lambda x: (-x["incident_count"], -x["sif_density"], x["barrier_pattern_id"]))

        # Assign clean display code
        for idx, pat in enumerate(mined_patterns, 1):
            pat["barrier_code_prefix"] = f"B{idx:03d}"

        return mined_patterns


if __name__ == "__main__":
    miner = BarrierPatternMiner(min_barrier_incidents=3)
    pats = miner.mine_barrier_patterns()
    print(f"Mined {len(pats)} recurring barrier failure patterns.")
    if pats:
        import json
        print("Top Barrier Pattern:\n", json.dumps(pats[0], indent=2))
