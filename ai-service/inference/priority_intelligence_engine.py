"""
priority_intelligence_engine.py - Stage 30 Risk / Priority Intelligence Engine for OILPS.
Synthesizes Stage 6/23/24/26/27/29 safety intelligence into a unified, deterministic HSE prioritization layer.
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
from inference.early_warning_detector import EarlyWarningDetector

PRIORITY_LEVEL_RANK = {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4,
    "INSUFFICIENT_DATA": 5
}

EARLY_WARNING_SCORE_MAP = {
    "HIGH_PRIORITY": 1.00,
    "EARLY_WARNING": 0.67,
    "WATCH": 0.33,
    "NORMAL": 0.00,
    "INSUFFICIENT_DATA": 0.00
}


class PriorityIntelligenceEngine:
    """
    Unified deterministic HSE priority ranking engine combining SIF impact, recurrence,
    barrier failure severity, site/activity risk indices, and early-warning signals.
    """

    def __init__(
        self,
        min_priority_incidents: int = 3,
        weight_sif: float = 0.35,
        weight_recurrence: float = 0.25,
        weight_barrier: float = 0.20,
        weight_site_activity: float = 0.10,
        weight_early_warning: float = 0.10
    ):
        self.min_priority_incidents = max(1, min_priority_incidents)
        self.w_sif = weight_sif
        self.w_rec = weight_recurrence
        self.w_bar = weight_barrier
        self.w_sa = weight_site_activity
        self.w_ew = weight_early_warning

        self.pattern_detector = RecurringPatternDetector()
        self.barrier_miner = BarrierPatternMiner()
        self.site_analyzer = SiteRiskAnalyzer()
        self.activity_analyzer = ActivityRiskAnalyzer()
        self.early_warning_detector = EarlyWarningDetector()

    def _classify_level(self, score: float, count: int) -> str:
        if count < self.min_priority_incidents:
            return "INSUFFICIENT_DATA"
        if score >= 0.75:
            return "CRITICAL"
        if score >= 0.55:
            return "HIGH"
        if score >= 0.35:
            return "MEDIUM"
        return "LOW"

    def calculate_priorities(self, records_override: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Evaluates historical dataset and Stage 23-29 outputs to generate ranked HSE priority entities.
        """
        records = self.pattern_detector.load_historical_records(records_override)
        if not records:
            return []

        # Load upstream Stage 23 - 29 outputs
        patterns = self.pattern_detector.detect_patterns(records)
        barriers = self.barrier_miner.mine_barrier_patterns(records)
        sites = self.site_analyzer.calculate_site_risk_profiles(records)
        activities = self.activity_analyzer.calculate_activity_risk_profiles(records)
        warnings = self.early_warning_detector.detect_early_warnings(records)

        # Build index maps for cross-stage context
        warning_by_name = {w["signal_name"].lower(): w for w in warnings}
        warning_by_pat = {p_id: w for w in warnings for p_id in w.get("pattern_ids", [])}
        warning_by_bpat = {b_id: w for w in warnings for b_id in w.get("barrier_pattern_ids", [])}

        priorities = []

        # ---------------------------------------------------------
        # ENTITY TYPE 1: BARRIER FAILURE PATTERNS
        # ---------------------------------------------------------
        for b in barriers:
            b_code = b["barrier_code"]
            b_name = b.get("barrier_name") or b.get("barrier_failure") or b_code
            inc_cnt = b["incident_count"]
            sif_density = b["sif_density"]

            # Normalized Components
            c_sif = round(min(1.0, sif_density), 4)
            c_rec = round(min(1.0, inc_cnt / 15.0), 4)
            c_bar = round(min(1.0, (sif_density * 0.6) + (inc_cnt / 20.0)), 4)
            c_sa = 0.50  # Average site/activity concentration baseline

            ew_match = warning_by_bpat.get(b["barrier_pattern_id"]) or warning_by_name.get(b_name.lower())
            ew_level = ew_match["warning_level"] if ew_match else "NORMAL"
            c_ew = EARLY_WARNING_SCORE_MAP.get(ew_level, 0.0)

            score = round((
                self.w_sif * c_sif +
                self.w_rec * c_rec +
                self.w_bar * c_bar +
                self.w_sa * c_sa +
                self.w_ew * c_ew
            ), 4)

            p_level = self._classify_level(score, inc_cnt)
            p_id = f"PRI-BARRIER-{b_code.upper().replace('_', '-')}"

            reason = (
                f"{p_level} priority because SIF impact ({int(c_sif*100)}%) and barrier recurrence ({inc_cnt} incidents) "
                f"are elevated, with early-warning status '{ew_level}'."
            )

            dates = [r["report_date"] for r in records if r["record_id"] in b["incident_ids"] and r.get("report_date")]
            dates_sorted = sorted(dates)

            priorities.append({
                "priority_id": p_id,
                "entity_type": "BARRIER_FAILURE",
                "entity_id": b["barrier_pattern_id"],
                "entity_name": b_name,
                "priority_score": score,
                "priority_level": p_level,
                "components": {
                    "sif_impact": c_sif,
                    "recurrence": c_rec,
                    "barrier_impact": c_bar,
                    "site_activity": c_sa,
                    "early_warning": c_ew
                },
                "supporting_report_ids": b["incident_ids"],
                "pattern_ids": b.get("stage23_pattern_ids", []),
                "barrier_pattern_ids": [b["barrier_pattern_id"]],
                "site_ids": [s for s in b.get("locations", [])],
                "activity_ids": [b.get("dominant_activity")] if b.get("dominant_activity") else [],
                "warning_ids": [ew_match["warning_id"]] if ew_match else [],
                "first_observed": dates_sorted[0] if dates_sorted else "Unknown",
                "last_observed": dates_sorted[-1] if dates_sorted else "Unknown",
                "reason": reason
            })

        # ---------------------------------------------------------
        # ENTITY TYPE 2: RECURRING PRECURSOR PATTERNS
        # ---------------------------------------------------------
        for p in patterns:
            p_id_raw = p["pattern_id"]
            p_name = p["pattern_name"]
            inc_cnt = p["incident_count"]
            sif_density = p["sif_density"]

            c_sif = round(min(1.0, sif_density), 4)
            c_rec = round(min(1.0, inc_cnt / 15.0), 4)
            c_bar = 0.50
            c_sa = 0.50

            ew_match = warning_by_pat.get(p_id_raw) or warning_by_name.get(p_name.lower())
            ew_level = ew_match["warning_level"] if ew_match else "NORMAL"
            c_ew = EARLY_WARNING_SCORE_MAP.get(ew_level, 0.0)

            score = round((
                self.w_sif * c_sif +
                self.w_rec * c_rec +
                self.w_bar * c_bar +
                self.w_sa * c_sa +
                self.w_ew * c_ew
            ), 4)

            p_level = self._classify_level(score, inc_cnt)
            p_id = f"PRI-PATTERN-{p_id_raw}"

            reason = (
                f"{p_level} priority due to recurring precursor pattern ({inc_cnt} incidents, "
                f"{int(sif_density*100)}% SIF density) and early-warning state '{ew_level}'."
            )

            dates = [r["report_date"] for r in records if r["record_id"] in p["incident_ids"] and r.get("report_date")]
            dates_sorted = sorted(dates)

            priorities.append({
                "priority_id": p_id,
                "entity_type": "RECURRING_PATTERN",
                "entity_id": p_id_raw,
                "entity_name": p_name,
                "priority_score": score,
                "priority_level": p_level,
                "components": {
                    "sif_impact": c_sif,
                    "recurrence": c_rec,
                    "barrier_impact": c_bar,
                    "site_activity": c_sa,
                    "early_warning": c_ew
                },
                "supporting_report_ids": p["incident_ids"],
                "pattern_ids": [p_id_raw],
                "barrier_pattern_ids": [],
                "site_ids": [s for s in p.get("locations", [])],
                "activity_ids": [p.get("activity")] if p.get("activity") else [],
                "warning_ids": [ew_match["warning_id"]] if ew_match else [],
                "first_observed": dates_sorted[0] if dates_sorted else "Unknown",
                "last_observed": dates_sorted[-1] if dates_sorted else "Unknown",
                "reason": reason
            })

        # ---------------------------------------------------------
        # ENTITY TYPE 3: OPERATIONAL SITES
        # ---------------------------------------------------------
        for st in sites:
            st_name = st["site_name"]
            st_id = st["site_id"]
            inc_cnt = st["total_reports"]
            sif_density = st["sif_density"]
            site_index = st.get("risk_index") if st.get("risk_index") is not None else st.get("site_risk_index", 0.0)

            c_sif = round(min(1.0, sif_density), 4)
            c_rec = round(min(1.0, inc_cnt / 25.0), 4)
            c_bar = 0.50
            c_sa = round(min(1.0, site_index), 4)
            c_ew = 0.0

            score = round((
                self.w_sif * c_sif +
                self.w_rec * c_rec +
                self.w_bar * c_bar +
                self.w_sa * c_sa +
                self.w_ew * c_ew
            ), 4)

            p_level = self._classify_level(score, inc_cnt)
            p_id = f"PRI-SITE-{st_id}"

            reason = (
                f"{p_level} priority for operational site {st_name} (Site Risk Index: {site_index:.2f}, "
                f"SIF density: {int(sif_density*100)}% across {inc_cnt} reports)."
            )

            priorities.append({
                "priority_id": p_id,
                "entity_type": "SITE",
                "entity_id": st_id,
                "entity_name": st_name,
                "priority_score": score,
                "priority_level": p_level,
                "components": {
                    "sif_impact": c_sif,
                    "recurrence": c_rec,
                    "barrier_impact": c_bar,
                    "site_activity": c_sa,
                    "early_warning": c_ew
                },
                "supporting_report_ids": st.get("report_ids", []),
                "pattern_ids": st.get("recurring_pattern_ids", []),
                "barrier_pattern_ids": st.get("barrier_pattern_ids", []),
                "site_ids": [st_name],
                "activity_ids": [],
                "warning_ids": [],
                "first_observed": st.get("first_observed", "Unknown"),
                "last_observed": st.get("last_observed", "Unknown"),
                "reason": reason
            })

        # ---------------------------------------------------------
        # ENTITY TYPE 4: OPERATIONAL ACTIVITIES
        # ---------------------------------------------------------
        for act in activities:
            act_name = act["activity_name"]
            act_id = act["activity_id"]
            inc_cnt = act["total_reports"]
            sif_density = act["sif_density"]
            act_index = act.get("risk_index") if act.get("risk_index") is not None else act.get("activity_risk_index", 0.0)

            c_sif = round(min(1.0, sif_density), 4)
            c_rec = round(min(1.0, inc_cnt / 25.0), 4)
            c_bar = 0.50
            c_sa = round(min(1.0, act_index), 4)
            c_ew = 0.0

            score = round((
                self.w_sif * c_sif +
                self.w_rec * c_rec +
                self.w_bar * c_bar +
                self.w_sa * c_sa +
                self.w_ew * c_ew
            ), 4)

            p_level = self._classify_level(score, inc_cnt)
            p_id = f"PRI-ACTIVITY-{act_id}"

            reason = (
                f"{p_level} priority for activity {act_name} (Activity Risk Index: {act_index:.2f}, "
                f"SIF density: {int(sif_density*100)}% across {inc_cnt} reports)."
            )

            priorities.append({
                "priority_id": p_id,
                "entity_type": "ACTIVITY",
                "entity_id": act_id,
                "entity_name": act_name,
                "priority_score": score,
                "priority_level": p_level,
                "components": {
                    "sif_impact": c_sif,
                    "recurrence": c_rec,
                    "barrier_impact": c_bar,
                    "site_activity": c_sa,
                    "early_warning": c_ew
                },
                "supporting_report_ids": act.get("report_ids", []),
                "pattern_ids": act.get("recurring_pattern_ids", []),
                "barrier_pattern_ids": act.get("barrier_pattern_ids", []),
                "site_ids": [],
                "activity_ids": [act_name],
                "warning_ids": [],
                "first_observed": act.get("first_observed", "Unknown"),
                "last_observed": act.get("last_observed", "Unknown"),
                "reason": reason
            })

        # Deterministic Ranking Order: -priority_score, entity_type, entity_name
        priorities.sort(key=lambda x: (-x["priority_score"], x["entity_type"], x["entity_name"]))
        return priorities


if __name__ == "__main__":
    engine = PriorityIntelligenceEngine()
    priorities = engine.calculate_priorities()
    print(f"Calculated {len(priorities)} HSE priority items.")
    if priorities:
        import json
        print("Top #1 Priority Item:\n", json.dumps(priorities[0], indent=2))
