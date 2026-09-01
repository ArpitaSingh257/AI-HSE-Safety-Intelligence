"""
site_risk_analyzer.py - Stage 26 Site-Level Risk Intelligence Engine for OILPS.
Aggregates historical incident data, Stage 23 recurring patterns, and Stage 24 barrier failure patterns
to derive volume-normalized site-level risk profiles and priority rankings.
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


class SiteRiskAnalyzer:
    """
    Deterministic site-level safety risk analyzer combining SIF precursor density,
    Stage 23 recurring pattern concentration, and Stage 24 barrier failure concentration.
    """

    def __init__(self, min_site_reports: int = 3):
        self.min_site_reports = max(1, min_site_reports)
        self.pattern_detector = RecurringPatternDetector()
        self.barrier_miner = BarrierPatternMiner()

    def _normalize_site(self, raw_site: Any) -> str:
        if pd.isna(raw_site) or not raw_site:
            return "UNKNOWN_SITE"
        site_str = str(raw_site).strip()
        if not site_str:
            return "UNKNOWN_SITE"
        return site_str

    def calculate_site_risk_profiles(self, records_override: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Calculates volume-normalized site risk profiles and returns a stably ranked list of site profiles.
        """
        records = self.pattern_detector.load_historical_records(records_override)
        if not records:
            return []

        # Load Stage 23 & Stage 24 patterns
        stage23_patterns = self.pattern_detector.detect_patterns(records)
        stage24_barriers = self.barrier_miner.mine_barrier_patterns(records)

        # Map incident_id -> Stage 23 pattern IDs & Stage 24 barrier IDs
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

        # Group unique records by site
        site_groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in records:
            site_name = self._normalize_site(r.get("location") or r.get("site"))
            if site_name not in site_groups:
                site_groups[site_name] = []
            site_groups[site_name].append(r)

        site_profiles = []

        for site_name in sorted(site_groups.keys()):
            group = site_groups[site_name]
            # Deduplicate by record_id
            unique_records_dict = {c["record_id"]: c for c in group}
            unique_records = list(unique_records_dict.values())
            unique_records.sort(key=lambda x: x["record_id"])

            total_cnt = len(unique_records)
            inc_ids = [c["record_id"] for c in unique_records]
            sif_cnt = sum(1 for c in unique_records if c["is_sif"])
            non_sif_cnt = total_cnt - sif_cnt
            sif_density = round(sif_cnt / total_cnt, 4) if total_cnt > 0 else 0.0

            # Collect unique linked Stage 23 and Stage 24 pattern IDs
            linked_s23 = sorted(list(set(p for inc_id in inc_ids for p in inc_to_s23.get(inc_id, []))))
            linked_s24 = sorted(list(set(b for inc_id in inc_ids for b in inc_to_s24.get(inc_id, []))))

            # Top activities with counts & SIF rates
            act_counts: Dict[str, Dict[str, int]] = {}
            for c in unique_records:
                act = c.get("activity") or "General Operations"
                if act not in act_counts:
                    act_counts[act] = {"total": 0, "sif": 0}
                act_counts[act]["total"] += 1
                if c["is_sif"]:
                    act_counts[act]["sif"] += 1

            top_activities = []
            for act_name, counts in sorted(act_counts.items(), key=lambda x: (-x[1]["total"], x[0])):
                rate = round(counts["sif"] / counts["total"], 4) if counts["total"] > 0 else 0.0
                top_activities.append({
                    "name": act_name,
                    "report_count": counts["total"],
                    "sif_count": counts["sif"],
                    "sif_density": rate
                })

            # Top hazards
            hazards = [c.get("hazard") for c in unique_records if c.get("hazard")]
            haz_counts = {}
            for h in hazards:
                haz_counts[h] = haz_counts.get(h, 0) + 1
            top_hazards = [
                {"name": h, "count": cnt}
                for h, cnt in sorted(haz_counts.items(), key=lambda x: (-x[1], x[0]))
            ]

            # Top barrier failures
            barrier_counts: Dict[str, Dict[str, int]] = {}
            for c in unique_records:
                bf = c.get("barrier_failure") or "Control Gap"
                if bf not in barrier_counts:
                    barrier_counts[bf] = {"total": 0, "sif": 0}
                barrier_counts[bf]["total"] += 1
                if c["is_sif"]:
                    barrier_counts[bf]["sif"] += 1

            top_barrier_failures = []
            for b_name, counts in sorted(barrier_counts.items(), key=lambda x: (-x[1]["total"], x[0])):
                rate = round(counts["sif"] / counts["total"], 4) if counts["total"] > 0 else 0.0
                top_barrier_failures.append({
                    "name": b_name,
                    "count": counts["total"],
                    "sif_count": counts["sif"],
                    "sif_density": rate
                })

            # Top Life-Saving Rules
            lsr_rules = [c.get("primary_life_saving_rule") for c in unique_records if c.get("primary_life_saving_rule")]
            lsr_counts = {}
            for r in lsr_rules:
                lsr_counts[r] = lsr_counts.get(r, 0) + 1
            top_lsrs = [
                {"name": r, "count": cnt}
                for r, cnt in sorted(lsr_counts.items(), key=lambda x: (-x[1], x[0]))
            ]

            # Date Range
            dates = [c.get("report_date") for c in unique_records if c.get("report_date")]
            dates_sorted = sorted(dates)
            first_obs = dates_sorted[0] if dates_sorted else "Unknown"
            last_obs = dates_sorted[-1] if dates_sorted else "Unknown"

            # Calculate Deterministic Site Risk Index (R_s) & Risk Classification
            if total_cnt < self.min_site_reports:
                risk_level = "INSUFFICIENT_DATA"
                risk_index = 0.0
                sif_component = 0.0
                pattern_component = 0.0
                barrier_component = 0.0
            else:
                sif_component = round(0.50 * sif_density, 4)
                pattern_component = round(0.30 * min(1.0, len(linked_s23) / 5.0), 4)
                barrier_component = round(0.20 * min(1.0, len(linked_s24) / 5.0), 4)
                risk_index = round(min(1.0, sif_component + pattern_component + barrier_component), 4)

                if risk_index >= 0.60:
                    risk_level = "CRITICAL"
                elif risk_index >= 0.40:
                    risk_level = "HIGH"
                elif risk_index >= 0.20:
                    risk_level = "MEDIUM"
                else:
                    risk_level = "LOW"

            site_id = f"SITE-{site_name.upper().replace(' ', '-')}"

            profile = {
                "site_id": site_id,
                "site_name": site_name,
                "total_reports": total_cnt,
                "sif_reports": sif_cnt,
                "non_sif_reports": non_sif_cnt,
                "sif_density": sif_density,
                "recurring_pattern_count": len(linked_s23),
                "barrier_failure_pattern_count": len(linked_s24),
                "risk_index": risk_index,
                "risk_level": risk_level,
                "sif_component": sif_component,
                "pattern_component": pattern_component,
                "barrier_component": barrier_component,
                "top_activities": top_activities[:3],
                "top_hazards": top_hazards[:3],
                "top_barrier_failures": top_barrier_failures[:3],
                "top_life_saving_rules": top_lsrs[:3],
                "first_observed": first_obs,
                "last_observed": last_obs,
                "report_ids": inc_ids,
                "pattern_ids": linked_s23,
                "barrier_pattern_ids": linked_s24
            }
            site_profiles.append(profile)

        # Sort stably by (-risk_index, -sif_density, site_name)
        site_profiles.sort(key=lambda x: (-x["risk_index"], -x["sif_density"], x["site_name"]))
        return site_profiles


if __name__ == "__main__":
    analyzer = SiteRiskAnalyzer(min_site_reports=3)
    profiles = analyzer.calculate_site_risk_profiles()
    print(f"Calculated risk profiles for {len(profiles)} sites.")
    if profiles:
        import json
        print("Top Ranked Site:\n", json.dumps(profiles[0], indent=2))
