"""
process_osha.py - Extracts and filters Oil & Gas / Petroleum sector records from OSHA Dataset.
Source File: resources/January2015toNovember2025.csv
Output Files:
- datasets/raw/osha/osha_oil_gas_raw.csv
- datasets/processed/osha_relevant.csv
"""

import os
import re
import csv
import json
from pathlib import Path

# NAICS Codes directly relevant to Oil & Gas, Petroleum, and Pipeline Operations
OIL_GAS_NAICS_PREFIXES = {
    # 211: Oil and Gas Extraction
    "211111": "Crude Petroleum and Natural Gas Extraction",
    "211112": "Natural Gas Liquid Extraction",
    "211120": "Crude Petroleum Extraction",
    "211130": "Natural Gas Extraction",
    "211": "Oil and Gas Extraction (General)",
    
    # 213: Support Activities for Mining and Oil/Gas
    "213111": "Drilling Oil and Gas Wells",
    "213112": "Support Activities for Oil and Gas Operations",
    "21311": "Support Activities for Oil and Gas",
    
    # 486: Pipeline Transportation
    "486110": "Pipeline Transportation of Crude Oil",
    "486210": "Pipeline Transportation of Natural Gas",
    "486910": "Pipeline Transportation of Refined Petroleum Products",
    "486990": "All Other Pipeline Transportation",
    "486": "Pipeline Transportation",
    
    # 324: Petroleum and Coal Products Manufacturing
    "324110": "Petroleum Refineries",
    "324121": "Asphalt Paving Mixture and Block Manufacturing",
    "324191": "Petroleum Lubricating Oil and Grease Manufacturing",
    "324199": "All Other Petroleum and Coal Products Manufacturing",
    "324": "Petroleum Products Manufacturing",
    
    # 237120: Oil and Gas Pipeline and Related Structures Construction
    "237120": "Oil and Gas Pipeline Construction",
    "23712": "Oil and Gas Pipeline Construction",
    
    # 4247: Petroleum and Petroleum Products Merchant Wholesalers
    "424710": "Petroleum Bulk Stations and Terminals",
    "424720": "Petroleum and Petroleum Products Merchant Wholesalers",
    "4247": "Petroleum Wholesalers"
}

# Domain keyword regex for narrative/employer identification
OIL_GAS_KEYWORDS = re.compile(
    r'\b(oil and gas|oil & gas|oilfield|oil field|wellhead|well pad|drilling rig|workover rig|'
    r'derrick|mud pump|blowout preventer|bop|fracing|fracking|hydraulic fracturing|casing string|'
    r'tubular|wireline|slickline|coiled tubing|christmas tree|xmas tree|crude oil|pipeline|'
    r'petroleum refinery|compressor station|separator vessel|tank battery|drilling crew|'
    r'roughneck|derrickman|roustabout|flowline|pig launcher|well site|rig floor|drill pipe)\b',
    re.IGNORECASE
)

def matches_oil_gas_naics(naics_str):
    if not naics_str:
        return False, None
    naics_clean = str(naics_str).strip().replace('"', '').replace("'", "")
    for code, desc in OIL_GAS_NAICS_PREFIXES.items():
        if naics_clean.startswith(code):
            return True, desc
    return False, None

def matches_oil_gas_keywords(text):
    if not text:
        return False
    return bool(OIL_GAS_KEYWORDS.search(str(text)))

def process_osha_dataset(source_csv_path, output_raw_dir, output_processed_dir):
    source_csv_path = Path(source_csv_path)
    output_raw_dir = Path(output_raw_dir)
    output_processed_dir = Path(output_processed_dir)
    
    output_raw_dir.mkdir(parents=True, exist_ok=True)
    output_processed_dir.mkdir(parents=True, exist_ok=True)
    
    raw_out_path = output_raw_dir / "osha_oil_gas_raw.csv"
    processed_out_path = output_processed_dir / "osha_relevant.csv"
    stats_out_path = output_processed_dir / "osha_filtering_stats.json"
    
    total_records = 0
    naics_matched = 0
    keyword_matched = 0
    both_matched = 0
    selected_records = []
    
    print(f"Reading OSHA source file: {source_csv_path}...")
    
    with open(source_csv_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            total_records += 1
            naics = row.get("Primary NAICS", "")
            narrative = row.get("Final Narrative", "")
            employer = row.get("Employer", "")
            
            is_naics, naics_desc = matches_oil_gas_naics(naics)
            is_kw = matches_oil_gas_keywords(f"{narrative} {employer}")
            
            if is_naics and is_kw:
                both_matched += 1
                match_reason = "NAICS_AND_KEYWORD"
            elif is_naics:
                naics_matched += 1
                match_reason = "NAICS_CODE"
            elif is_kw:
                keyword_matched += 1
                match_reason = "DOMAIN_KEYWORD"
            else:
                continue
                
            row["Filtering_Match_Reason"] = match_reason
            row["Industry_Description"] = naics_desc if naics_desc else "Oil & Gas / Energy Related"
            selected_records.append(row)
            
    print(f"Total OSHA records inspected: {total_records}")
    print(f"Records matched via NAICS: {naics_matched + both_matched}")
    print(f"Records matched via Keyword: {keyword_matched + both_matched}")
    print(f"Total Oil & Gas relevant records extracted: {len(selected_records)}")
    
    # Save raw filtered dataset
    if selected_records:
        out_fields = list(selected_records[0].keys())
        with open(raw_out_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(selected_records)
            
        with open(processed_out_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_fields)
            writer.writeheader()
            writer.writerows(selected_records)
            
    stats = {
        "total_source_records": total_records,
        "selected_relevant_records": len(selected_records),
        "naics_matched_only": naics_matched,
        "keyword_matched_only": keyword_matched,
        "both_matched": both_matched,
        "percentage_selected": round((len(selected_records) / max(total_records, 1)) * 100, 2),
        "naics_categories": list(OIL_GAS_NAICS_PREFIXES.keys())
    }
    
    with open(stats_out_path, mode="w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
        
    print(f"Saved {len(selected_records)} records to {processed_out_path}")
    print(f"Saved stats to {stats_out_path}")
    return stats

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    src_file = base_dir / "resources" / "January2015toNovember2025.csv"
    raw_dir = base_dir / "ai-service" / "datasets" / "raw" / "osha"
    proc_dir = base_dir / "ai-service" / "datasets" / "processed"
    
    if src_file.exists():
        process_osha_dataset(src_file, raw_dir, proc_dir)
    else:
        print(f"Error: Source file {src_file} not found.")
