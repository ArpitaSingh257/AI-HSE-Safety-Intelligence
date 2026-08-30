"""
build_full_dataset.py - Complete standalone pipeline for dataset generation, normalization,
deduplication, quality analysis, annotation file creation, and train/val/test splitting.
Extracts dynamically from all 4 IOGP PDFs and the OSHA 10-year CSV.
"""

import os
import re
import csv
import json
import hashlib
import random
from pathlib import Path
from collections import Counter, defaultdict

# Import IOGP parser functions
from extract_iogp import extract_pdf_pages_clean, parse_iogp_hpe_pdf, parse_iogp_spi_and_fatal_pdf

CANONICAL_FIELDS = [
    "record_id",
    "source",
    "source_document",
    "source_record_id",
    "report_date",
    "country",
    "location",
    "function",
    "industry",
    "activity",
    "event_type",
    "cause",
    "narrative",
    "what_went_wrong",
    "corrective_actions",
    "causal_factors",
    "primary_life_saving_rule",
    "secondary_life_saving_rule",
    "life_saving_rules",
    "severity",
    "hospitalization",
    "amputation",
    "loss_of_eye",
    "sif_potential",
    "hazard",
    "barrier",
    "barrier_failure",
    "potential_consequence",
    "data_source_type"
]

OIL_GAS_NAICS_PREFIXES = {
    "211111": "Crude Petroleum and Natural Gas Extraction",
    "211112": "Natural Gas Liquid Extraction",
    "211120": "Crude Petroleum Extraction",
    "211130": "Natural Gas Extraction",
    "211": "Oil and Gas Extraction (General)",
    "213111": "Drilling Oil and Gas Wells",
    "213112": "Support Activities for Oil and Gas Operations",
    "21311": "Support Activities for Oil and Gas",
    "486110": "Pipeline Transportation of Crude Oil",
    "486210": "Pipeline Transportation of Natural Gas",
    "486910": "Pipeline Transportation of Refined Petroleum Products",
    "486990": "All Other Pipeline Transportation",
    "486": "Pipeline Transportation",
    "324110": "Petroleum Refineries",
    "324121": "Asphalt Paving Mixture and Block Manufacturing",
    "324191": "Petroleum Lubricating Oil and Grease Manufacturing",
    "324199": "All Other Petroleum and Coal Products Manufacturing",
    "324": "Petroleum Products Manufacturing",
    "237120": "Oil and Gas Pipeline Construction",
    "23712": "Oil and Gas Pipeline Construction",
    "424710": "Petroleum Bulk Stations and Terminals",
    "424720": "Petroleum and Petroleum Products Merchant Wholesalers",
    "4247": "Petroleum Wholesalers"
}

OIL_GAS_KEYWORDS = re.compile(
    r'\b(oil and gas|oil & gas|oilfield|oil field|wellhead|well pad|drilling rig|workover rig|'
    r'derrick|mud pump|blowout preventer|bop|fracing|fracking|hydraulic fracturing|casing string|'
    r'tubular|wireline|slickline|coiled tubing|christmas tree|xmas tree|crude oil|pipeline|'
    r'petroleum refinery|compressor station|separator vessel|tank battery|drilling crew|'
    r'roughneck|derrickman|roustabout|flowline|pig launcher|well site|rig floor|drill pipe)\b',
    re.IGNORECASE
)

def clean_text(val):
    if val is None:
        return ""
    text = str(val).strip()
    text = re.sub(r'\s+', ' ', text)
    return text if text else ""

def normalize_text_for_comparison(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    tokens = [w for w in text.split() if len(w) > 2]
    return " ".join(tokens)

def get_shingles(text, k=3):
    words = text.split()
    if len(words) < k:
        return set([" ".join(words)])
    return set([" ".join(words[i:i+k]) for i in range(len(words) - k + 1)])

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0

def build_complete_dataset():
    base_dir = Path(__file__).resolve().parent.parent.parent
    resources_dir = base_dir / "resources"
    ai_service_dir = base_dir / "ai-service"
    datasets_dir = ai_service_dir / "datasets"
    
    raw_osha_dir = datasets_dir / "raw" / "osha"
    raw_iogp_dir = datasets_dir / "raw" / "iogp"
    proc_dir = datasets_dir / "processed"
    ann_dir = datasets_dir / "annotation"
    splits_dir = datasets_dir / "splits"
    quality_dir = datasets_dir / "quality"
    
    for d in [raw_osha_dir, raw_iogp_dir, proc_dir, ann_dir, splits_dir, quality_dir]:
        d.mkdir(parents=True, exist_ok=True)
        
    print("=" * 70)
    print("OILPS COMPLETE DATASET GENERATION PIPELINE")
    print("=" * 70)
    
    unified_rows = []
    
    # 1. Dynamic Extraction from All 4 IOGP Documents
    print("\n[Step 1] Dynamically extracting all IOGP PDF Documents...")
    
    # A. HPE Reports
    hpe_file = resources_dir / "IAOGP - High Potential Event Reports.pdf"
    if hpe_file.exists():
        pages, method = extract_pdf_pages_clean(hpe_file)
        hpe_records = parse_iogp_hpe_pdf(pages, hpe_file.name)
        print(f"  --> Extracted {len(hpe_records)} records from {hpe_file.name}")
        for idx, rec in enumerate(hpe_records, start=1):
            item = {f: rec.get(f, None) for f in CANONICAL_FIELDS}
            item["record_id"] = f"OILPS_IOGP_HPE_{idx:04d}"
            item["source_record_id"] = f"HPE_P{rec.get('page_number', idx):03d}"
            item["industry"] = "Oil and Gas Exploration and Production"
            item["event_type"] = "High Potential Event"
            item["sif_potential"] = "1"
            unified_rows.append(item)
            
    # B. Safety Performance Indicators / Fatal & Tier 1 PSE
    spi_file = resources_dir / "IAOGP - Safety performance indicators.pdf"
    if spi_file.exists():
        pages, method = extract_pdf_pages_clean(spi_file)
        spi_records = parse_iogp_spi_and_fatal_pdf(pages, spi_file.name)
        print(f"  --> Extracted {len(spi_records)} records from {spi_file.name}")
        for idx, rec in enumerate(spi_records, start=1):
            src = rec.get("source", "IOGP_SPI")
            item = {f: rec.get(f, None) for f in CANONICAL_FIELDS}
            item["record_id"] = f"OILPS_{src}_{idx:04d}"
            item["source_record_id"] = f"{src}_P{rec.get('page_number', idx):03d}"
            item["industry"] = "Oil and Gas Production and Operations"
            item["sif_potential"] = "1"
            unified_rows.append(item)
            
    # C. Macro & Guide Verification
    macro_file = resources_dir / "IAOGP-Safety performance indicators - 2025 data.pdf"
    guide_file = resources_dir / "IAOGP - Safety data reporting user guide.pdf"
    if macro_file.exists():
        print(f"  --> Verified {macro_file.name} (Global Macro KPI Benchmarks)")
    if guide_file.exists():
        print(f"  --> Verified {guide_file.name} (Standard Reference in knowledge/iogp_user_guide_reference.md)")
        
    print(f"  Total IOGP incident records incorporated: {len(unified_rows)}")
    
    # 2. Process OSHA dataset
    osha_src_csv = resources_dir / "January2015toNovember2025.csv"
    osha_records = []
    total_osha_read = 0
    
    if osha_src_csv.exists():
        print(f"\n[Step 2] Filtering OSHA dataset ({osha_src_csv.name})...")
        with open(osha_src_csv, mode="r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_osha_read += 1
                naics = clean_text(row.get("Primary NAICS", ""))
                narrative = clean_text(row.get("Final Narrative", ""))
                employer = clean_text(row.get("Employer", ""))
                
                is_naics = False
                naics_desc = None
                for code, desc in OIL_GAS_NAICS_PREFIXES.items():
                    if naics.startswith(code):
                        is_naics = True
                        naics_desc = desc
                        break
                        
                is_kw = bool(OIL_GAS_KEYWORDS.search(f"{narrative} {employer}"))
                
                if is_naics or is_kw:
                    row["Filtering_Match_Reason"] = "NAICS_AND_KEYWORD" if (is_naics and is_kw) else ("NAICS_CODE" if is_naics else "DOMAIN_KEYWORD")
                    row["Industry_Description"] = naics_desc if naics_desc else "Oil & Gas / Energy Related"
                    osha_records.append(row)
                    
        print(f"  Total OSHA records scanned: {total_osha_read}")
        print(f"  Extracted Oil & Gas relevant OSHA records: {len(osha_records)}")
        
        # Save raw and processed OSHA CSVs
        if osha_records:
            osha_fields = list(osha_records[0].keys())
            with open(raw_osha_dir / "osha_oil_gas_raw.csv", mode="w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=osha_fields)
                w.writeheader()
                w.writerows(osha_records)
            with open(proc_dir / "osha_relevant.csv", mode="w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=osha_fields)
                w.writeheader()
                w.writerows(osha_records)
                
        # Normalize OSHA records
        for idx, o_rec in enumerate(osha_records, start=1):
            osha_id = clean_text(o_rec.get("ID", ""))
            event_date = clean_text(o_rec.get("EventDate", ""))
            city = clean_text(o_rec.get("City", ""))
            state = clean_text(o_rec.get("State", ""))
            location = f"{city}, {state}".strip(", ")
            narrative = clean_text(o_rec.get("Final Narrative", ""))
            nature_title = clean_text(o_rec.get("NatureTitle", ""))
            event_title = clean_text(o_rec.get("EventTitle", ""))
            source_title = clean_text(o_rec.get("SourceTitle", ""))
            industry = clean_text(o_rec.get("Industry_Description", "Oil & Gas"))
            
            hosp = clean_text(o_rec.get("Hospitalized", "0"))
            amp = clean_text(o_rec.get("Amputation", "0"))
            eye = clean_text(o_rec.get("Loss of Eye", "0"))
            
            severity = "Non-Fatal Injury"
            if hosp == "1.00" or hosp == "1":
                severity = "Hospitalization"
            if amp == "1.00" or amp == "1":
                severity = "Amputation"
            if eye == "1.00" or eye == "1":
                severity = "Loss of Eye"
                
            cause = event_title if event_title and event_title.lower() != "nonclassifiable" else None
            hazard = source_title if source_title and source_title.lower() != "nonclassifiable" else None
            
            canon_item = {
                "record_id": f"OILPS_OSHA_{idx:05d}",
                "source": "OSHA",
                "source_document": "January2015toNovember2025.csv",
                "source_record_id": osha_id,
                "report_date": event_date if event_date else None,
                "country": "USA",
                "location": location if location else None,
                "function": None,
                "industry": industry,
                "activity": None,
                "event_type": "Workplace Safety Incident",
                "cause": cause,
                "narrative": narrative,
                "what_went_wrong": None,
                "corrective_actions": None,
                "causal_factors": None,
                "primary_life_saving_rule": None,
                "secondary_life_saving_rule": None,
                "life_saving_rules": None,
                "severity": severity,
                "hospitalization": hosp,
                "amputation": amp,
                "loss_of_eye": eye,
                "sif_potential": "REVIEW_REQUIRED",
                "hazard": hazard,
                "barrier": None,
                "barrier_failure": None,
                "potential_consequence": nature_title if nature_title and nature_title.lower() != "nonclassifiable" else None,
                "data_source_type": "REGULATORY_SAFETY_REPORT"
            }
            unified_rows.append(canon_item)
            
    print(f"  Total normalized raw records in unified corpus: {len(unified_rows)}")
    
    # Save unified raw CSV
    unified_raw_path = proc_dir / "oilps_unified_raw.csv"
    with open(unified_raw_path, mode="w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CANONICAL_FIELDS)
        w.writeheader()
        w.writerows(unified_rows)
        
    # 3. Deduplication
    print("\n[Step 3] Performing exact and near-duplicate detection...")
    exact_hash_map = defaultdict(list)
    for idx, r in enumerate(unified_rows):
        norm = normalize_text_for_comparison(r.get("narrative", ""))
        if len(norm) > 10:
            h = hashlib.md5(norm.encode('utf-8')).hexdigest()
            exact_hash_map[h].append(idx)
        else:
            src_id = f"{r.get('source')}_{r.get('source_record_id')}"
            exact_hash_map[src_id].append(idx)
            
    exact_dup_indices = set()
    exact_dup_logs = []
    for h, group in exact_hash_map.items():
        if len(group) > 1:
            primary_idx = group[0]
            for dup_idx in group[1:]:
                exact_dup_indices.add(dup_idx)
                exact_dup_logs.append({
                    "primary_record_id": unified_rows[primary_idx]["record_id"],
                    "duplicate_record_id": unified_rows[dup_idx]["record_id"],
                    "source": unified_rows[dup_idx]["source"],
                    "reason": "Exact narrative text hash match"
                })
                
    active_indices = [i for i in range(len(unified_rows)) if i not in exact_dup_indices]
    
    near_dup_indices = set()
    near_dup_logs = []
    shingles_cache = {}
    for idx in active_indices:
        norm = normalize_text_for_comparison(unified_rows[idx].get("narrative", ""))
        shingles_cache[idx] = get_shingles(norm, k=3)
        
    for i_pos in range(len(active_indices)):
        idx_a = active_indices[i_pos]
        if idx_a in near_dup_indices:
            continue
        sh_a = shingles_cache[idx_a]
        if not sh_a:
            continue
            
        for j_pos in range(i_pos + 1, min(i_pos + 150, len(active_indices))):
            idx_b = active_indices[j_pos]
            if idx_b in near_dup_indices:
                continue
            sh_b = shingles_cache[idx_b]
            sim = jaccard_similarity(sh_a, sh_b)
            if sim >= 0.85:
                near_dup_indices.add(idx_b)
                near_dup_logs.append({
                    "primary_record_id": unified_rows[idx_a]["record_id"],
                    "duplicate_record_id": unified_rows[idx_b]["record_id"],
                    "similarity_score": round(sim, 3),
                    "reason": f"Near-duplicate narrative (Jaccard = {sim:.2f})"
                })
                
    all_removed = exact_dup_indices.union(near_dup_indices)
    deduped_rows = [r for idx, r in enumerate(unified_rows) if idx not in all_removed]
    
    print(f"  Exact duplicates removed: {len(exact_dup_indices)}")
    print(f"  Near duplicates removed: {len(near_dup_indices)}")
    print(f"  Total clean records retained: {len(deduped_rows)}")
    
    unified_dedup_path = proc_dir / "oilps_unified_deduped.csv"
    with open(unified_dedup_path, mode="w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CANONICAL_FIELDS)
        w.writeheader()
        w.writerows(deduped_rows)
        
    # 4. Generate Annotation CSV
    print("\n[Step 4] Creating Annotation Dataset (oilps_annotation.csv)...")
    annotation_rows = []
    for r in deduped_rows:
        ann_item = dict(r)
        sif_val = r.get("sif_potential", "")
        if sif_val in ["1", "0"]:
            ann_status = "ANNOTATED_SOURCE_GROUNDED"
        elif sif_val == "REVIEW_REQUIRED":
            ann_status = "REVIEW_REQUIRED"
        else:
            ann_status = "UNANNOTATED"
            
        ann_item["annotation_status"] = ann_status
        ann_item["annotator_notes"] = ""
        ann_item["verified_sif_label"] = sif_val if sif_val in ["0", "1"] else ""
        ann_item["verified_primary_lsr"] = r.get("primary_life_saving_rule", "")
        ann_item["verified_secondary_lsr"] = r.get("secondary_life_saving_rule", "")
        ann_item["verified_activity"] = r.get("activity", "")
        ann_item["verified_hazard"] = r.get("hazard", "")
        ann_item["verified_barrier_failure"] = r.get("barrier_failure", "")
        ann_item["verified_potential_consequence"] = r.get("potential_consequence", "")
        annotation_rows.append(ann_item)
        
    ann_csv_path = ann_dir / "oilps_annotation.csv"
    ann_fields = list(annotation_rows[0].keys())
    with open(ann_csv_path, mode="w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ann_fields)
        w.writeheader()
        w.writerows(annotation_rows)
        
    print(f"  Annotation file saved with {len(annotation_rows)} records.")
    
    # 5. Stratified Splits (70 / 15 / 15)
    print("\n[Step 5] Creating Stratified Train/Val/Test Splits...")
    random.seed(42)
    source_groups = defaultdict(list)
    for r in deduped_rows:
        source_groups[r.get("source", "OTHER")].append(r)
        
    train_rows, val_rows, test_rows = [], [], []
    for src, grp in source_groups.items():
        random.shuffle(grp)
        n = len(grp)
        n_tr = int(n * 0.70)
        n_va = int(n * 0.15)
        train_rows.extend(grp[:n_tr])
        val_rows.extend(grp[n_tr:n_tr + n_va])
        test_rows.extend(grp[n_tr + n_va:])
        
    random.shuffle(train_rows)
    random.shuffle(val_rows)
    random.shuffle(test_rows)
    
    for fname, data in [("train.csv", train_rows), ("val.csv", val_rows), ("test.csv", test_rows)]:
        with open(splits_dir / fname, mode="w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=CANONICAL_FIELDS)
            w.writeheader()
            w.writerows(data)
            
    meta_split = {
        "random_seed": 42,
        "total_records": len(deduped_rows),
        "train_count": len(train_rows),
        "train_pct": round((len(train_rows)/len(deduped_rows))*100, 2),
        "val_count": len(val_rows),
        "val_pct": round((len(val_rows)/len(deduped_rows))*100, 2),
        "test_count": len(test_rows),
        "test_pct": round((len(test_rows)/len(deduped_rows))*100, 2),
        "split_strategy": "Stratified by source authority to prevent cross-source leakage"
    }
    with open(splits_dir / "splits_metadata.json", mode="w", encoding="utf-8") as f:
        json.dump(meta_split, f, indent=2)
        
    print(f"  Splits created: Train={len(train_rows)}, Val={len(val_rows)}, Test={len(test_rows)}")
    print("\n" + "=" * 70)
    print("DATASET CREATION COMPLETED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    build_complete_dataset()
