"""
lsr_trend_analyzer.py - Stage 28 Life-Saving Rule (LSR) Trend Analytics Engine for OILPS.
Aggregates historical incident data across monthly time buckets to evaluate repeat occurrences,
SIF precursor densities, and temporal trend trajectories (INCREASING, STABLE, DECREASING, INSUFFICIENT_DATA).
Excludes UNKNOWN/missing LSR labels from official IOGP trend analytics while tracking them for data quality.
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.pattern_detector import RecurringPatternDetector
from inference.barrier_pattern_miner import BarrierPatternMiner
from inference.site_risk_analyzer import SiteRiskAnalyzer
from inference.activity_risk_analyzer import ActivityRiskAnalyzer

INVALID_LSR_LABELS = {"UNKNOWN", "MISSING", "N/A", "NONE", "UNCLASSIFIED", "NULL"}


class LsrTrendAnalyzer:
    """
    Deterministic Life-Saving Rule (LSR) trend analyzer evaluating temporal SIF concentration
    and cross-stage site, activity, barrier, and pattern associations.
    """

    def __init__(self, min_lsr_reports: int = 3, min_trend_periods: int = 2):
        self.min_lsr_reports = max(1, min_lsr_reports)
        self.min_trend_periods = max(1, min_trend_periods)
        self.pattern_detector = RecurringPatternDetector()
        self.barrier_miner = BarrierPatternMiner()

    def _normalize_lsr(self, raw_lsr: Any) -> str:
        if pd.isna(raw_lsr) or not raw_lsr:
            return "UNKNOWN"
        lsr_str = str(raw_lsr).strip()
        if not lsr_str:
            return "UNKNOWN"
        return lsr_str

    def _parse_period(self, date_str: Any) -> str:
        if pd.isna(date_str) or not date_str:
            return "UNKNOWN_PERIOD"
        d = str(date_str).strip()
        if len(d) >= 7 and d[:4].isdigit() and d[4] == '-' and d[5:7].isdigit():
            return d[:7]  # YYYY-MM
        return "UNKNOWN_PERIOD"

    def get_lsr_analytics_summary(self, records_override: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Returns official valid IOGP LSR trend profiles and metadata including unknown LSR record counts and rates.
        """
        records = self.pattern_detector.load_historical_records(records_override)
        if not records:
            return {
                "total_reports": 0,
                "unknown_lsr_records": 0,
                "unknown_lsr_rate": 0.0,
                "official_lsr_profiles": []
            }

        # Deduplicate records by record_id
        unique_records_dict = {c["record_id"]: c for c in records}
        all_unique_records = list(unique_records_dict.values())
        total_reports_count = len(all_unique_records)

        # Count UNKNOWN / missing LSR records
        unknown_recs_cnt = sum(
            1 for c in all_unique_records
            if self._normalize_lsr(c.get("primary_life_saving_rule")).upper() in INVALID_LSR_LABELS
        )
        unknown_rate = round(unknown_recs_cnt / total_reports_count, 4) if total_reports_count > 0 else 0.0

        # Load Stage 23 & Stage 24 pattern lookup maps
        stage23_patterns = self.pattern_detector.detect_patterns(all_unique_records)
        stage24_barriers = self.barrier_miner.mine_barrier_patterns(all_unique_records)

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

        # Group unique records by canonical LSR rule
        lsr_groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in all_unique_records:
            lsr_name = self._normalize_lsr(r.get("primary_life_saving_rule"))
            if lsr_name not in lsr_groups:
                lsr_groups[lsr_name] = []
            lsr_groups[lsr_name].append(r)

        lsr_profiles = []

        for lsr_name in sorted(lsr_groups.keys()):
            # EXCLUDE UNKNOWN / invalid labels from official LSR trend profiles
            if lsr_name.upper() in INVALID_LSR_LABELS:
                continue

            group = lsr_groups[lsr_name]
            unique_records = sorted(group, key=lambda x: x["record_id"])

            total_cnt = len(unique_records)
            inc_ids = [c["record_id"] for c in unique_records]
            sif_cnt = sum(1 for c in unique_records if c["is_sif"])
            sif_density = round(sif_cnt / total_cnt, 4) if total_cnt > 0 else 0.0

            # Monthly Time Series Aggregation
            period_groups: Dict[str, List[Dict[str, Any]]] = {}
            for c in unique_records:
                p_key = self._parse_period(c.get("report_date"))
                if p_key not in period_groups:
                    period_groups[p_key] = []
                period_groups[p_key].append(c)

            time_series = []
            valid_periods = [p for p in sorted(period_groups.keys()) if p != "UNKNOWN_PERIOD"]

            for p_key in valid_periods:
                p_recs = period_groups[p_key]
                p_total = len(p_recs)
                p_sif = sum(1 for x in p_recs if x["is_sif"])
                p_density = round(p_sif / p_total, 4) if p_total > 0 else 0.0
                time_series.append({
                    "period": p_key,
                    "report_count": p_total,
                    "sif_count": p_sif,
                    "sif_density": p_density
                })

            # Trend Calculation (Recent vs Earlier window)
            num_periods = len(valid_periods)
            if total_cnt < self.min_lsr_reports or num_periods < self.min_trend_periods:
                trend_state = "INSUFFICIENT_DATA"
                trend_delta = 0.0
            else:
                mid = num_periods // 2
                earlier_periods = valid_periods[:mid]
                recent_periods = valid_periods[mid:]

                earlier_recs = [r for p in earlier_periods for r in period_groups[p]]
                recent_recs = [r for p in recent_periods for r in period_groups[p]]

                e_total = len(earlier_recs)
                e_sif = sum(1 for x in earlier_recs if x["is_sif"])
                e_density = e_sif / e_total if e_total > 0 else 0.0

                r_total = len(recent_recs)
                r_sif = sum(1 for x in recent_recs if x["is_sif"])
                r_density = r_sif / r_total if r_total > 0 else 0.0

                trend_delta = round(r_density - e_density, 4)

                if trend_delta >= 0.05:
                    trend_state = "INCREASING"
                elif trend_delta <= -0.05:
                    trend_state = "DECREASING"
                else:
                    trend_state = "STABLE"

            # Top Sites
            sites = [c.get("location") or c.get("site") for c in unique_records if (c.get("location") or c.get("site"))]
            site_counts = {}
            for s in sites:
                s_norm = str(s).strip()
                if s_norm:
                    site_counts[s_norm] = site_counts.get(s_norm, 0) + 1
            top_sites = [
                {"site_name": s_name, "count": cnt}
                for s_name, cnt in sorted(site_counts.items(), key=lambda x: (-x[1], x[0]))
            ]

            # Top Activities
            activities = [c.get("activity") for c in unique_records if c.get("activity")]
            act_counts = {}
            for a in activities:
                a_norm = str(a).strip()
                if a_norm:
                    act_counts[a_norm] = act_counts.get(a_norm, 0) + 1
            top_activities = [
                {"activity_name": a_name, "count": cnt}
                for a_name, cnt in sorted(act_counts.items(), key=lambda x: (-x[1], x[0]))
            ]

            # Top Barrier Failures
            barrier_counts = {}
            for c in unique_records:
                bf = c.get("barrier_failure") or "Control Gap"
                barrier_counts[bf] = barrier_counts.get(bf, 0) + 1
            top_barrier_failures = [
                {"name": b_name, "count": cnt}
                for b_name, cnt in sorted(barrier_counts.items(), key=lambda x: (-x[1], x[0]))
            ]

            # Linked Stage 23 & Stage 24 Pattern IDs
            linked_s23 = sorted(list(set(p for inc_id in inc_ids for p in inc_to_s23.get(inc_id, []))))
            linked_s24 = sorted(list(set(b for inc_id in inc_ids for b in inc_to_s24.get(inc_id, []))))

            # Dates
            dates = [c.get("report_date") for c in unique_records if c.get("report_date")]
            dates_sorted = sorted(dates)
            first_obs = dates_sorted[0] if dates_sorted else "Unknown"
            last_obs = dates_sorted[-1] if dates_sorted else "Unknown"

            profile = {
                "lsr_rule": lsr_name,
                "total_reports": total_cnt,
                "sif_reports": sif_cnt,
                "sif_density": sif_density,
                "trend": trend_state,
                "trend_delta": trend_delta,
                "time_series": time_series,
                "top_sites": top_sites[:3],
                "top_activities": top_activities[:3],
                "top_barrier_failures": top_barrier_failures[:3],
                "recurring_pattern_ids": linked_s23,
                "barrier_pattern_ids": linked_s24,
                "first_observed": first_obs,
                "last_observed": last_obs,
                "report_ids": inc_ids
            }
            lsr_profiles.append(profile)

        # Sort stably by (-total_reports, -sif_density, lsr_rule)
        lsr_profiles.sort(key=lambda x: (-x["total_reports"], -x["sif_density"], x["lsr_rule"]))

        return {
            "total_reports": total_reports_count,
            "unknown_lsr_records": unknown_recs_cnt,
            "unknown_lsr_rate": unknown_rate,
            "official_lsr_profiles": lsr_profiles
        }

    def calculate_lsr_trend_profiles(self, records_override: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Backward compatible helper returning list of official valid IOGP LSR profiles."""
        summary = self.get_lsr_analytics_summary(records_override)
        return summary["official_lsr_profiles"]


if __name__ == "__main__":
    analyzer = LsrTrendAnalyzer(min_lsr_reports=3)
    summary = analyzer.get_lsr_analytics_summary()
    print(f"Total reports: {summary['total_reports']}")
    print(f"Unknown LSR records: {summary['unknown_lsr_records']} ({summary['unknown_lsr_rate']*100:.2f}%)")
    print(f"Official IOGP LSR Profiles: {len(summary['official_lsr_profiles'])}")
    for p in summary["official_lsr_profiles"]:
        print(f" - {p['lsr_rule']}: {p['total_reports']} reports, trend={p['trend']}")
