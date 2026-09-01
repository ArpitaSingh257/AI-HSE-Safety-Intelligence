"""
risk_matrix_engine.py - Stage 31 Severity vs Recurrence Risk Matrix Engine for OILPS.
Calculates 2D coordinates (Severity vs Recurrence) and classifies safety entities into 4 matrix quadrants.
"""

import sys
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.pattern_detector import RecurringPatternDetector
from inference.barrier_pattern_miner import BarrierPatternMiner
from inference.site_risk_analyzer import SiteRiskAnalyzer
from inference.activity_risk_analyzer import ActivityRiskAnalyzer


class RiskMatrixEngine:
    """
    Deterministic 2D Risk Matrix Engine placing safety entities (Barrier Failures, Precursor Patterns,
    Operational Sites, Operational Activities) onto a 2D coordinate grid (Recurrence vs Severity).
    """

    def __init__(
        self,
        min_matrix_incidents: int = 3,
        severity_threshold: float = 0.50,
        recurrence_threshold: float = 0.50
    ):
        self.min_matrix_incidents = max(1, min_matrix_incidents)
        self.sev_thresh = severity_threshold
        self.rec_thresh = recurrence_threshold

        self.pattern_detector = RecurringPatternDetector()
        self.barrier_miner = BarrierPatternMiner()
        self.site_analyzer = SiteRiskAnalyzer()
        self.activity_analyzer = ActivityRiskAnalyzer()

    def _classify_quadrant(self, sev_score: float, rec_score: float, inc_cnt: int) -> Dict[str, str]:
        if inc_cnt < self.min_matrix_incidents:
            return {
                "severity_level": "INSUFFICIENT_DATA",
                "recurrence_level": "INSUFFICIENT_DATA",
                "quadrant": "INSUFFICIENT_DATA",
                "classification": "INSUFFICIENT_DATA"
            }

        sev_lvl = "HIGH" if sev_score >= self.sev_thresh else "LOW"
        rec_lvl = "HIGH" if rec_score >= self.rec_thresh else "LOW"

        if sev_lvl == "HIGH" and rec_lvl == "HIGH":
            quad = "HIGH_SEVERITY_HIGH_RECURRENCE"
            cls = "CRITICAL_PRIORITY"
        elif sev_lvl == "HIGH" and rec_lvl == "LOW":
            quad = "HIGH_SEVERITY_LOW_RECURRENCE"
            cls = "HIGH_POTENTIAL_RARE"
        elif sev_lvl == "LOW" and rec_lvl == "HIGH":
            quad = "LOW_SEVERITY_HIGH_RECURRENCE"
            cls = "FREQUENT_LOWER_POTENTIAL"
        else:
            quad = "LOW_SEVERITY_LOW_RECURRENCE"
            cls = "LOW_PRIORITY_MONITOR"

        return {
            "severity_level": sev_lvl,
            "recurrence_level": rec_lvl,
            "quadrant": quad,
            "classification": cls
        }

    def calculate_risk_matrix(self, records_override: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Evaluates historical safety records and generates 2D matrix coordinates & classifications.
        """
        records = self.pattern_detector.load_historical_records(records_override)
        if not records:
            return []

        patterns = self.pattern_detector.detect_patterns(records)
        barriers = self.barrier_miner.mine_barrier_patterns(records)
        sites = self.site_analyzer.calculate_site_risk_profiles(records)
        activities = self.activity_analyzer.calculate_activity_risk_profiles(records)

        matrix_items = []

        # ---------------------------------------------------------
        # 1. BARRIER FAILURE PATTERNS
        # ---------------------------------------------------------
        for b in barriers:
            b_code = b["barrier_code"]
            b_name = b.get("barrier_name") or b.get("barrier_failure") or b_code
            inc_cnt = b["incident_count"]
            sif_density = b["sif_density"]

            sev_score = round(min(1.0, sif_density), 4)
            rec_score = round(min(1.0, inc_cnt / 15.0), 4)

            quad_info = self._classify_quadrant(sev_score, rec_score, inc_cnt)
            item_id = f"MATRIX-BARRIER-{b_code.upper().replace('_', '-')}"

            reason = (
                f"Barrier failure '{b_name}' has severity score {sev_score:.2f} ({int(sev_score*100)}% SIF density) "
                f"and recurrence score {rec_score:.2f} ({inc_cnt} incidents). Classified as {quad_info['classification']}."
            )

            dates = [r["report_date"] for r in records if r["record_id"] in b["incident_ids"] and r.get("report_date")]
            dates_sorted = sorted(dates)

            matrix_items.append({
                "matrix_item_id": item_id,
                "entity_type": "BARRIER_FAILURE",
                "entity_id": b["barrier_pattern_id"],
                "entity_name": b_name,
                "severity_score": sev_score,
                "recurrence_score": rec_score,
                "severity_level": quad_info["severity_level"],
                "recurrence_level": quad_info["recurrence_level"],
                "quadrant": quad_info["quadrant"],
                "classification": quad_info["classification"],
                "supporting_report_ids": b["incident_ids"],
                "pattern_ids": b.get("stage23_pattern_ids", []),
                "barrier_pattern_ids": [b["barrier_pattern_id"]],
                "site_ids": [s for s in b.get("locations", [])],
                "activity_ids": [b.get("dominant_activity")] if b.get("dominant_activity") else [],
                "first_observed": dates_sorted[0] if dates_sorted else "Unknown",
                "last_observed": dates_sorted[-1] if dates_sorted else "Unknown",
                "reason": reason
            })

        # ---------------------------------------------------------
        # 2. RECURRING PRECURSOR PATTERNS
        # ---------------------------------------------------------
        for p in patterns:
            p_id_raw = p["pattern_id"]
            p_name = p["pattern_name"]
            inc_cnt = p["incident_count"]
            sif_density = p["sif_density"]

            sev_score = round(min(1.0, sif_density), 4)
            rec_score = round(min(1.0, inc_cnt / 15.0), 4)

            quad_info = self._classify_quadrant(sev_score, rec_score, inc_cnt)
            item_id = f"MATRIX-PATTERN-{p_id_raw}"

            reason = (
                f"Recurring pattern '{p_name}' has severity score {sev_score:.2f} ({int(sev_score*100)}% SIF density) "
                f"and recurrence score {rec_score:.2f} ({inc_cnt} incidents). Classified as {quad_info['classification']}."
            )

            dates = [r["report_date"] for r in records if r["record_id"] in p["incident_ids"] and r.get("report_date")]
            dates_sorted = sorted(dates)

            matrix_items.append({
                "matrix_item_id": item_id,
                "entity_type": "RECURRING_PATTERN",
                "entity_id": p_id_raw,
                "entity_name": p_name,
                "severity_score": sev_score,
                "recurrence_score": rec_score,
                "severity_level": quad_info["severity_level"],
                "recurrence_level": quad_info["recurrence_level"],
                "quadrant": quad_info["quadrant"],
                "classification": quad_info["classification"],
                "supporting_report_ids": p["incident_ids"],
                "pattern_ids": [p_id_raw],
                "barrier_pattern_ids": [],
                "site_ids": [s for s in p.get("locations", [])],
                "activity_ids": [p.get("activity")] if p.get("activity") else [],
                "first_observed": dates_sorted[0] if dates_sorted else "Unknown",
                "last_observed": dates_sorted[-1] if dates_sorted else "Unknown",
                "reason": reason
            })

        # ---------------------------------------------------------
        # 3. OPERATIONAL SITES
        # ---------------------------------------------------------
        for st in sites:
            st_name = st["site_name"]
            st_id = st["site_id"]
            inc_cnt = st["total_reports"]
            sif_density = st["sif_density"]

            sev_score = round(min(1.0, sif_density), 4)
            rec_score = round(min(1.0, inc_cnt / 25.0), 4)

            quad_info = self._classify_quadrant(sev_score, rec_score, inc_cnt)
            item_id = f"MATRIX-SITE-{st_id}"

            reason = (
                f"Site '{st_name}' has severity score {sev_score:.2f} ({int(sev_score*100)}% SIF density) "
                f"and recurrence score {rec_score:.2f} ({inc_cnt} reports). Classified as {quad_info['classification']}."
            )

            matrix_items.append({
                "matrix_item_id": item_id,
                "entity_type": "SITE",
                "entity_id": st_id,
                "entity_name": st_name,
                "severity_score": sev_score,
                "recurrence_score": rec_score,
                "severity_level": quad_info["severity_level"],
                "recurrence_level": quad_info["recurrence_level"],
                "quadrant": quad_info["quadrant"],
                "classification": quad_info["classification"],
                "supporting_report_ids": st.get("report_ids", []),
                "pattern_ids": st.get("recurring_pattern_ids", []),
                "barrier_pattern_ids": st.get("barrier_pattern_ids", []),
                "site_ids": [st_name],
                "activity_ids": [],
                "first_observed": st.get("first_observed", "Unknown"),
                "last_observed": st.get("last_observed", "Unknown"),
                "reason": reason
            })

        # ---------------------------------------------------------
        # 4. OPERATIONAL ACTIVITIES
        # ---------------------------------------------------------
        for act in activities:
            act_name = act["activity_name"]
            act_id = act["activity_id"]
            inc_cnt = act["total_reports"]
            sif_density = act["sif_density"]

            sev_score = round(min(1.0, sif_density), 4)
            rec_score = round(min(1.0, inc_cnt / 25.0), 4)

            quad_info = self._classify_quadrant(sev_score, rec_score, inc_cnt)
            item_id = f"MATRIX-ACTIVITY-{act_id}"

            reason = (
                f"Activity '{act_name}' has severity score {sev_score:.2f} ({int(sev_score*100)}% SIF density) "
                f"and recurrence score {rec_score:.2f} ({inc_cnt} reports). Classified as {quad_info['classification']}."
            )

            matrix_items.append({
                "matrix_item_id": item_id,
                "entity_type": "ACTIVITY",
                "entity_id": act_id,
                "entity_name": act_name,
                "severity_score": sev_score,
                "recurrence_score": rec_score,
                "severity_level": quad_info["severity_level"],
                "recurrence_level": quad_info["recurrence_level"],
                "quadrant": quad_info["quadrant"],
                "classification": quad_info["classification"],
                "supporting_report_ids": act.get("report_ids", []),
                "pattern_ids": act.get("recurring_pattern_ids", []),
                "barrier_pattern_ids": act.get("barrier_pattern_ids", []),
                "site_ids": [],
                "activity_ids": [act_name],
                "first_observed": act.get("first_observed", "Unknown"),
                "last_observed": act.get("last_observed", "Unknown"),
                "reason": reason
            })

        # Sort stably by (-severity_score, -recurrence_score, entity_name)
        matrix_items.sort(key=lambda x: (-x["severity_score"], -x["recurrence_score"], x["entity_name"]))
        return matrix_items


if __name__ == "__main__":
    engine = RiskMatrixEngine()
    items = engine.calculate_risk_matrix()
    print(f"Calculated {len(items)} 2D risk matrix items.")
    if items:
        import json
        print("Top #1 Risk Matrix Item:\n", json.dumps(items[0], indent=2))
