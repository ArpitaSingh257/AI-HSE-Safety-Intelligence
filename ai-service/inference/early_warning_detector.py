"""
early_warning_detector.py - Stage 29 Temporal Trend / Early-Warning Detection Engine for OILPS.
Detects persistent worsening safety precursor signals across time buckets to generate deterministic early-warning alerts.
"""

import sys
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

WARNING_LEVEL_RANK = {
    "HIGH_PRIORITY": 1,
    "EARLY_WARNING": 2,
    "WATCH": 3,
    "NORMAL": 4,
    "INSUFFICIENT_DATA": 5
}


class EarlyWarningDetector:
    """
    Deterministic early-warning intelligence layer detecting sustained worsening safety signals.
    """

    def __init__(
        self,
        min_warning_reports: int = 3,
        min_warning_periods: int = 3,
        min_consecutive_increasing_periods: int = 3
    ):
        self.min_warning_reports = max(1, min_warning_reports)
        self.min_warning_periods = max(1, min_warning_periods)
        self.min_consecutive_increasing_periods = max(1, min_consecutive_increasing_periods)
        self.pattern_detector = RecurringPatternDetector()
        self.barrier_miner = BarrierPatternMiner()

    def _parse_period(self, date_str: Any) -> str:
        if pd.isna(date_str) or not date_str:
            return "UNKNOWN_PERIOD"
        d = str(date_str).strip()
        if len(d) >= 7 and d[:4].isdigit() and d[4] == '-' and d[5:7].isdigit():
            return d[:7]  # YYYY-MM
        return "UNKNOWN_PERIOD"

    def detect_early_warnings(self, records_override: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Evaluates historical safety records across Stage 23/24/26/27 signals to generate early warnings.
        """
        records = self.pattern_detector.load_historical_records(records_override)
        if not records:
            return []

        # Load Stage 23 & Stage 24 patterns
        stage23_patterns = self.pattern_detector.detect_patterns(records)
        stage24_barriers = self.barrier_miner.mine_barrier_patterns(records)

        inc_to_s23: Dict[str, List[str]] = {}
        for pat in stage23_patterns:
            for inc_id in pat["incident_ids"]:
                if inc_id not in inc_to_s23:
                    inc_to_s23[inc_id] = []
                inc_to_s23[inc_id].append(pat["pattern_id"])

        inc_to_s24: Dict[str, List[str]] = {}
        for bpat in stage24_barriers:
            for inc_id in bpat["incident_ids"]:
                if inc_id not in inc_to_s24:
                    inc_to_s24[inc_id] = []
                inc_to_s24[inc_id].append(bpat["barrier_pattern_id"])

        warnings = []

        # ---------------------------------------------------------
        # SIGNAL TYPE 1: BARRIER FAILURE PATTERNS
        # ---------------------------------------------------------
        for bpat in stage24_barriers:
            b_name = bpat.get("barrier_name") or bpat.get("barrier_failure") or bpat.get("barrier_code") or "Barrier Failure"
            b_inc_ids = set(bpat["incident_ids"])
            b_recs = [r for r in records if r["record_id"] in b_inc_ids]

            period_groups: Dict[str, List[Dict[str, Any]]] = {}
            for r in b_recs:
                p_key = self._parse_period(r.get("report_date"))
                if p_key not in period_groups:
                    period_groups[p_key] = []
                period_groups[p_key].append(r)

            valid_periods = [p for p in sorted(period_groups.keys()) if p != "UNKNOWN_PERIOD"]
            time_series = []
            for p_key in valid_periods:
                p_recs = period_groups[p_key]
                p_cnt = len(p_recs)
                p_sif = sum(1 for x in p_recs if x["is_sif"])
                p_rate = round(p_sif / p_cnt, 4) if p_cnt > 0 else 0.0
                time_series.append({
                    "period": p_key,
                    "report_count": p_cnt,
                    "sif_count": p_sif,
                    "sif_density": p_rate
                })

            num_periods = len(valid_periods)

            # Calculate consecutive increasing periods
            consec_inc = 0
            if num_periods >= 2:
                for i in range(num_periods - 1, 0, -1):
                    if time_series[i]["report_count"] > time_series[i-1]["report_count"] or (
                        time_series[i]["report_count"] == time_series[i-1]["report_count"] and time_series[i]["sif_density"] > time_series[i-1]["sif_density"]
                    ):
                        consec_inc += 1
                    else:
                        break

            # Baseline vs Recent Window
            if num_periods < self.min_warning_periods or len(b_recs) < self.min_warning_reports:
                w_level = "INSUFFICIENT_DATA"
                baseline_val = 0.0
                recent_val = 0.0
                delta = 0.0
            else:
                mid = num_periods // 2
                earlier = time_series[:mid]
                recent = time_series[mid:]

                baseline_val = round(sum(x["report_count"] for x in earlier) / len(earlier), 2)
                recent_val = round(sum(x["report_count"] for x in recent) / len(recent), 2)
                delta = round(recent_val - baseline_val, 2)

                if consec_inc >= self.min_consecutive_increasing_periods and delta >= 1.0 and bpat["sif_density"] >= 0.40:
                    w_level = "HIGH_PRIORITY"
                elif consec_inc >= self.min_consecutive_increasing_periods:
                    w_level = "EARLY_WARNING"
                elif consec_inc >= 1 or delta > 0:
                    w_level = "WATCH"
                else:
                    w_level = "NORMAL"

            # Affected Sites & Activities
            sites = [r.get("location") or r.get("site") for r in b_recs if (r.get("location") or r.get("site"))]
            site_cnts = {}
            for s in sites:
                s_norm = str(s).strip()
                if s_norm:
                    site_cnts[s_norm] = site_cnts.get(s_norm, 0) + 1
            affected_sites = [{"site_name": s, "count": c} for s, c in sorted(site_cnts.items(), key=lambda x: (-x[1], x[0]))]

            acts = [r.get("activity") for r in b_recs if r.get("activity")]
            act_cnts = {}
            for a in acts:
                a_norm = str(a).strip()
                if a_norm:
                    act_cnts[a_norm] = act_cnts.get(a_norm, 0) + 1
            affected_activities = [{"activity_name": a, "count": c} for a, c in sorted(act_cnts.items(), key=lambda x: (-x[1], x[0]))]

            w_id = f"EW-BARRIER-{b_name.upper().replace(' ', '-').replace('/', '-')}"
            latest_p = valid_periods[-1] if valid_periods else "Unknown"

            reason = (
                f"Barrier failure '{b_name}' frequency increased for {consec_inc} consecutive monthly periods "
                f"(baseline: {baseline_val}, recent: {recent_val}, delta: {delta:+.2f}). Requires HSE attention."
            )

            dates = [r.get("report_date") for r in b_recs if r.get("report_date")]
            dates_sorted = sorted(dates)

            warnings.append({
                "warning_id": w_id,
                "signal_type": "BARRIER_FAILURE",
                "signal_name": b_name,
                "warning_level": w_level,
                "period": latest_p,
                "baseline_value": baseline_val,
                "recent_value": recent_val,
                "delta": delta,
                "consecutive_increasing_periods": consec_inc,
                "affected_sites": affected_sites[:3],
                "affected_activities": affected_activities[:3],
                "pattern_ids": sorted(list(set(p for inc in b_inc_ids for p in inc_to_s23.get(inc, [])))),
                "barrier_pattern_ids": [bpat["barrier_pattern_id"]],
                "supporting_incident_ids": sorted(list(b_inc_ids)),
                "reason": reason,
                "first_observed": dates_sorted[0] if dates_sorted else "Unknown",
                "last_observed": dates_sorted[-1] if dates_sorted else "Unknown",
                "time_series": time_series
            })

        # ---------------------------------------------------------
        # SIGNAL TYPE 2: RECURRING PRECURSOR PATTERNS
        # ---------------------------------------------------------
        for pat in stage23_patterns:
            p_name = pat["pattern_name"]
            p_inc_ids = set(pat["incident_ids"])
            p_recs = [r for r in records if r["record_id"] in p_inc_ids]

            period_groups: Dict[str, List[Dict[str, Any]]] = {}
            for r in p_recs:
                p_key = self._parse_period(r.get("report_date"))
                if p_key not in period_groups:
                    period_groups[p_key] = []
                period_groups[p_key].append(r)

            valid_periods = [p for p in sorted(period_groups.keys()) if p != "UNKNOWN_PERIOD"]
            time_series = []
            for p_key in valid_periods:
                p_recs_p = period_groups[p_key]
                p_cnt = len(p_recs_p)
                p_sif = sum(1 for x in p_recs_p if x["is_sif"])
                p_rate = round(p_sif / p_cnt, 4) if p_cnt > 0 else 0.0
                time_series.append({
                    "period": p_key,
                    "report_count": p_cnt,
                    "sif_count": p_sif,
                    "sif_density": p_rate
                })

            num_periods = len(valid_periods)

            consec_inc = 0
            if num_periods >= 2:
                for i in range(num_periods - 1, 0, -1):
                    if time_series[i]["report_count"] > time_series[i-1]["report_count"]:
                        consec_inc += 1
                    else:
                        break

            if num_periods < self.min_warning_periods or len(p_recs) < self.min_warning_reports:
                w_level = "INSUFFICIENT_DATA"
                baseline_val = 0.0
                recent_val = 0.0
                delta = 0.0
            else:
                mid = num_periods // 2
                earlier = time_series[:mid]
                recent = time_series[mid:]

                baseline_val = round(sum(x["report_count"] for x in earlier) / len(earlier), 2)
                recent_val = round(sum(x["report_count"] for x in recent) / len(recent), 2)
                delta = round(recent_val - baseline_val, 2)

                if consec_inc >= self.min_consecutive_increasing_periods and delta >= 1.0:
                    w_level = "HIGH_PRIORITY"
                elif consec_inc >= self.min_consecutive_increasing_periods:
                    w_level = "EARLY_WARNING"
                elif consec_inc >= 1 or delta > 0:
                    w_level = "WATCH"
                else:
                    w_level = "NORMAL"

            sites = [r.get("location") or r.get("site") for r in p_recs if (r.get("location") or r.get("site"))]
            site_cnts = {}
            for s in sites:
                s_norm = str(s).strip()
                if s_norm:
                    site_cnts[s_norm] = site_cnts.get(s_norm, 0) + 1
            affected_sites = [{"site_name": s, "count": c} for s, c in sorted(site_cnts.items(), key=lambda x: (-x[1], x[0]))]

            acts = [r.get("activity") for r in p_recs if r.get("activity")]
            act_cnts = {}
            for a in acts:
                a_norm = str(a).strip()
                if a_norm:
                    act_cnts[a_norm] = act_cnts.get(a_norm, 0) + 1
            affected_activities = [{"activity_name": a, "count": c} for a, c in sorted(act_cnts.items(), key=lambda x: (-x[1], x[0]))]

            w_id = f"EW-PATTERN-{pat['pattern_id']}"
            latest_p = valid_periods[-1] if valid_periods else "Unknown"

            reason = (
                f"Recurring precursor pattern '{p_name}' frequency increased for {consec_inc} consecutive monthly periods "
                f"(baseline: {baseline_val}, recent: {recent_val}, delta: {delta:+.2f}). Requires HSE attention."
            )

            dates = [r.get("report_date") for r in p_recs if r.get("report_date")]
            dates_sorted = sorted(dates)

            warnings.append({
                "warning_id": w_id,
                "signal_type": "RECURRING_PATTERN",
                "signal_name": p_name,
                "warning_level": w_level,
                "period": latest_p,
                "baseline_value": baseline_val,
                "recent_value": recent_val,
                "delta": delta,
                "consecutive_increasing_periods": consec_inc,
                "affected_sites": affected_sites[:3],
                "affected_activities": affected_activities[:3],
                "pattern_ids": [pat["pattern_id"]],
                "barrier_pattern_ids": sorted(list(set(b for inc in p_inc_ids for b in inc_to_s24.get(inc, [])))),
                "supporting_incident_ids": sorted(list(p_inc_ids)),
                "reason": reason,
                "first_observed": dates_sorted[0] if dates_sorted else "Unknown",
                "last_observed": dates_sorted[-1] if dates_sorted else "Unknown",
                "time_series": time_series
            })

        # Sort stably by (warning_level_rank, -delta, -recent_value, warning_id)
        warnings.sort(key=lambda x: (WARNING_LEVEL_RANK.get(x["warning_level"], 99), -x["delta"], -x["recent_value"], x["warning_id"]))
        return warnings


if __name__ == "__main__":
    detector = EarlyWarningDetector()
    warnings = detector.detect_early_warnings()
    print(f"Calculated {len(warnings)} early warning signals.")
    if warnings:
        import json
        print("Top Early Warning Signal:\n", json.dumps(warnings[0], indent=2))
