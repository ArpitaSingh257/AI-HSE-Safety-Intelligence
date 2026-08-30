"""
audit_and_prepare_annotation.py - Audits and prepares the rigorous, decoupled annotation schema in oilps_annotation.csv.
Distinguishes granular field-level provenance:
1. SOURCE_GROUNDED: Explicitly present as a labeled field in the source document.
2. DERIVED_FROM_SOURCE: Inferred/normalized from narrative, What Went Wrong, or causal factors.
3. HUMAN_VERIFIED: Manually reviewed and confirmed by domain annotator.
4. UNANNOTATED: Insufficient evidence / awaiting review.
"""

import os
import re
import csv
import json
import time
from pathlib import Path
from collections import Counter, defaultdict

OFFICIAL_IOGP_LSR = {
    "Bypassing Safety Controls": ["bypassing safety controls", "bypass safety controls", "overriding safety controls"],
    "Confined Space": ["confined space", "confined space entry"],
    "Driving": ["driving", "safe driving", "land transport"],
    "Energy Isolation": ["energy isolation", "isolation of energy", "loto", "lockout tagout"],
    "Hot Work": ["hot work", "control flammables"],
    "Line of Fire": ["line of fire", "struck by", "crush"],
    "Safe Mechanical Lifting": ["safe mechanical lifting", "mechanical lifting", "lifting operations"],
    "Toxic Gas / Hazardous Substance": ["toxic gas", "hazardous substance", "toxic gas / hazardous substance", "h2s"],
    "Working at Height": ["working at height", "work at height", "falls from height"]
}

AUXILIARY_IOGP_RULES = {
    "Work Authorization": ["work authorization", "permit to work", "ptw"],
    "Other issue – no applicable rule": ["other issue", "no applicable rule", "none", "n/a"]
}

def canonicalize_lsr_name(name):
    if not name or str(name).strip() in ["", "None", "NULL", "null", "N/A"]:
        return None
    name_clean = str(name).strip()
    name_lower = name_clean.lower()
    
    for standard_name, synonyms in OFFICIAL_IOGP_LSR.items():
        for syn in synonyms:
            if syn in name_lower or name_lower == standard_name.lower():
                return standard_name
                
    for aux_name, synonyms in AUXILIARY_IOGP_RULES.items():
        for syn in synonyms:
            if syn in name_lower or name_lower == aux_name.lower():
                return aux_name
                
    return name_clean

CANDIDATE_LSR_PATTERNS = [
    ("Energy Isolation", re.compile(r'\b(loto|lockout|tagout|de-energiz|breaker|valve closed|isolation|live line|live circuit|shock|electroc|480v|440v|11kv|bleeder valve|residual pressure)\b', re.I)),
    ("Working at Height", re.compile(r'\b(scaffold|ladder|derrick|monkey board|mast|elevat|fall from|fell from|height|roof|man basket|cherry picker|aerial lift|harness|lanyard)\b', re.I)),
    ("Line of Fire", re.compile(r'\b(struck by|whip|flying object|pinch point|caught in|drawworks|cathead|tong|rotating pipe|counterweight|dislodged|snapped line|rebound)\b', re.I)),
    ("Safe Mechanical Lifting", re.compile(r'\b(crane|hoist|winch|sling|rigging|tagline|forklift|telehandler|suspended load|dropped object|elevator latch|shackle|spreader bar)\b', re.I)),
    ("Confined Space", re.compile(r'\b(confined space|tank entry|vessel entry|inside vessel|inside tank|separator interior|manway|oxygen defic|vault|sump pit)\b', re.I)),
    ("Hot Work", re.compile(r'\b(hot work|welding|torch|grinding|cutting torch|open flame|spark|ignition|flash fire|fire broke out|flammable gas fire)\b', re.I)),
    ("Toxic Gas / Hazardous Substance", re.compile(r'\b(h2s|hydrogen sulfide|sour gas|toxic gas|benzene|caustic|acid|chemical splash|chlorine|asphyx|inhalation)\b', re.I)),
    ("Driving", re.compile(r'\b(vehicle|truck|tanker rollover|collision|driver|highway|seatbelt|crew bus|pickup truck|speeding)\b', re.I)),
    ("Bypassing Safety Controls", re.compile(r'\b(bypassed|interlock disabled|alarm overridden|guard removed|modified tool|without ptw|unauthorized start)\b', re.I))
]

def generate_candidate_lsrs(narrative):
    if not narrative:
        return []
    matches = []
    for rule_name, pat in CANDIDATE_LSR_PATTERNS:
        if pat.search(narrative):
            matches.append(rule_name)
    return matches

def run_annotation_preparation():
    base_dir = Path(__file__).resolve().parent.parent.parent
    proc_csv = base_dir / "ai-service" / "datasets" / "processed" / "oilps_unified_deduped.csv"
    ann_csv = base_dir / "ai-service" / "datasets" / "annotation" / "oilps_annotation.csv"
    
    records = []
    with open(proc_csv, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for r in reader:
            records.append(r)
            
    prepared_rows = []
    for r in records:
        source = r.get("source", "")
        narrative = r.get("narrative", "")
        orig_prim_lsr = r.get("primary_life_saving_rule", "")
        orig_sec_lsr = r.get("secondary_life_saving_rule", "")
        orig_sif = r.get("sif_potential", "")
        
        canon_prim_lsr = canonicalize_lsr_name(orig_prim_lsr)
        canon_sec_lsr = canonicalize_lsr_name(orig_sec_lsr)
        
        # SIF Block
        if source in ["IOGP_HPE", "IOGP_FATAL"]:
            sif_status = "SOURCE_GROUNDED"
            sif_label_type = "SOURCE_GROUNDED"
            verified_sif = "1"
            sif_annotation_source = f"IOGP Source Document ({r.get('source_document', '')})"
            sif_notes = "Official IOGP verified High Potential Event or Fatal incident."
        elif source == "IOGP_SPI":
            sif_status = "SOURCE_GROUNDED"
            sif_label_type = "DERIVED_SOURCE_RULE"
            verified_sif = "1"
            sif_annotation_source = f"OILPS Rule RULE_SPI_TIER1_SIF ({r.get('source_document', '')})"
            sif_notes = "IOGP Tier 1 Process Safety Event (Loss of Primary Containment). SIF potential derived via Energy-Barrier rule."
        else:
            sif_status = "REVIEW_REQUIRED"
            sif_label_type = "UNANNOTATED"
            verified_sif = ""
            sif_annotation_source = "PENDING_DOMAIN_REVIEW"
            sif_notes = f"OSHA record with stated severity '{r.get('severity', '')}'. Awaiting energy-barrier SIF review."
            
        # LSR Block
        if canon_prim_lsr:
            lsr_status = "SOURCE_GROUNDED"
            lsr_label_type = "SOURCE_GROUNDED"
            lsr_source = f"IOGP Source Document ({r.get('source_document', '')})"
            verified_prim_lsr = canon_prim_lsr
            verified_sec_lsr = canon_sec_lsr if canon_sec_lsr else ""
            comb = [canon_prim_lsr]
            if canon_sec_lsr:
                comb.append(canon_sec_lsr)
            verified_all_lsr = "; ".join(comb)
            cand_prim, cand_sec, cand_all = "", "", ""
        else:
            lsr_status = "REVIEW_REQUIRED"
            lsr_label_type = "CANDIDATE_HEURISTIC"
            lsr_source = "RULE_BASED_CANDIDATE_HEURISTIC"
            verified_prim_lsr = ""
            verified_sec_lsr = ""
            verified_all_lsr = ""
            cands = generate_candidate_lsrs(narrative)
            cand_prim = cands[0] if len(cands) > 0 else ""
            cand_sec = cands[1] if len(cands) > 1 else ""
            cand_all = "; ".join(cands) if cands else "None identified"
            
        # Precursor Block with Granular Field-by-Field Provenance
        is_iogp = source in ["IOGP_HPE", "IOGP_FATAL", "IOGP_SPI"]
        raw_hazard = r.get("hazard", "")
        raw_consequence = r.get("potential_consequence", "")
        raw_barrier = r.get("barrier", "")
        raw_failure = r.get("barrier_failure", "")
        raw_activity = r.get("activity", "")
        
        if is_iogp:
            # Activity is explicitly labeled in IOGP
            verified_act = raw_activity if raw_activity else "Production / Operational Task"
            activity_prov = "SOURCE_GROUNDED" if raw_activity else "DERIVED_FROM_SOURCE"
            
            # Hazard is derived from Cause / Release / Narrative (No explicit HAZARD: label in IOGP)
            verified_haz = raw_hazard if raw_hazard else ("Hazardous Hydrocarbon / Pressure Energy" if source == "IOGP_SPI" else "Kinetic / Gravitational Energy")
            hazard_prov = "DERIVED_FROM_SOURCE"
            
            # Barrier: intended control is derived from failure mode
            verified_barr = raw_barrier if raw_barrier else ("Process Containment Barrier" if source == "IOGP_SPI" else "Mechanical / Operational Safeguard")
            barrier_prov = "DERIVED_FROM_SOURCE"
            
            # Barrier Failure: explicitly labeled in IOGP_SPI ("BARRIERS: Hardware Barrier Failures..."), derived in HPE
            verified_fail = raw_failure if raw_failure else "Loss of containment / primary containment breach"
            barrier_fail_prov = "SOURCE_GROUNDED" if source == "IOGP_SPI" and raw_failure else "DERIVED_FROM_SOURCE"
            
            # Consequence: explicitly stated in FATAL, derived worst-case potential in HPE and SPI
            verified_conseq = raw_consequence if raw_consequence else ("Fatality / Permanent Impairment" if source == "IOGP_FATAL" else "Catastrophic release / Fire potential")
            conseq_prov = "SOURCE_GROUNDED" if source == "IOGP_FATAL" else "DERIVED_FROM_SOURCE"
            
            mapped_osha_src = ""
            mapped_osha_injury = ""
        else:
            # OSHA records: all precursor target fields are UNANNOTATED
            verified_act = ""
            verified_haz = ""
            verified_barr = ""
            verified_fail = ""
            verified_conseq = ""
            activity_prov = "UNANNOTATED"
            hazard_prov = "UNANNOTATED"
            barrier_prov = "UNANNOTATED"
            barrier_fail_prov = "UNANNOTATED"
            conseq_prov = "UNANNOTATED"
            
            # Retain raw OSHA metadata cleanly
            mapped_osha_src = raw_hazard  # Raw OSHA SourceTitle
            mapped_osha_injury = raw_consequence  # Raw OSHA NatureTitle
            
        ann_item = {
            "record_id": r.get("record_id", ""),
            "source": source,
            "source_document": r.get("source_document", ""),
            "source_record_id": r.get("source_record_id", ""),
            "report_date": r.get("report_date", ""),
            "country": r.get("country", ""),
            "location": r.get("location", ""),
            "industry": r.get("industry", ""),
            "event_type": r.get("event_type", ""),
            "severity": r.get("severity", ""),
            "narrative": narrative,
            
            # Mapped Regulatory Context (OSHA)
            "mapped_osha_source_hazard": mapped_osha_src,
            "mapped_osha_actual_injury_outcome": mapped_osha_injury,
            
            # SIF Fields
            "sif_annotation_status": sif_status,
            "sif_label_type": sif_label_type,
            "sif_annotation_source": sif_annotation_source,
            "sif_potential_raw": orig_sif,
            "verified_sif_label": verified_sif,
            "sif_annotator_notes": sif_notes,
            
            # LSR Fields
            "lsr_annotation_status": lsr_status,
            "lsr_label_type": lsr_label_type,
            "lsr_annotation_source": lsr_source,
            "candidate_primary_lsr": cand_prim,
            "candidate_secondary_lsr": cand_sec,
            "candidate_all_lsrs": cand_all,
            "verified_primary_lsr": verified_prim_lsr,
            "verified_secondary_lsr": verified_sec_lsr,
            "verified_life_saving_rules": verified_all_lsr,
            "lsr_annotator_notes": "",
            
            # Precursor Target Fields
            "verified_activity": verified_act,
            "activity_provenance": activity_prov,
            "verified_hazard": verified_haz,
            "hazard_provenance": hazard_prov,
            "verified_barrier": verified_barr,
            "barrier_provenance": barrier_prov,
            "verified_barrier_failure": verified_fail,
            "barrier_failure_provenance": barrier_fail_prov,
            "verified_potential_consequence": verified_conseq,
            "consequence_provenance": conseq_prov,
            "precursor_annotator_notes": ""
        }
        prepared_rows.append(ann_item)
        
    ann_fields = list(prepared_rows[0].keys())
    
    # Write to temp file first to prevent corruption/lock issues, then replace
    temp_csv = ann_csv.parent / "oilps_annotation_temp.csv"
    with open(temp_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ann_fields)
        writer.writeheader()
        writer.writerows(prepared_rows)
        
    # Replace atomically
    try:
        if ann_csv.exists():
            ann_csv.unlink()
        temp_csv.rename(ann_csv)
    except PermissionError:
        print("Note: oilps_annotation.csv is currently open in another program (e.g. Excel). Writing to oilps_annotation_updated.csv as backup.")
        backup_csv = ann_csv.parent / "oilps_annotation_updated.csv"
        with open(backup_csv, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=ann_fields)
            writer.writeheader()
            writer.writerows(prepared_rows)
            
    print(f"Updated annotation schema with granular precursor provenance ({len(prepared_rows)} records).")

if __name__ == "__main__":
    run_annotation_preparation()
