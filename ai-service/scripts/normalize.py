"""
normalize.py - Normalizes extracted IOGP and OSHA incident records into the canonical OILPS schema.
Output File: datasets/processed/oilps_unified_raw.csv
"""

import os
import re
import csv
import json
from pathlib import Path

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

def clean_text(val):
    if val is None:
        return ""
    text = str(val).strip()
    text = re.sub(r'\s+', ' ', text)
    return text if text else ""

def normalize_osha_record(row, idx):
    """
    Maps an OSHA record dictionary to the canonical OILPS schema.
    """
    osha_id = clean_text(row.get("ID", ""))
    event_date = clean_text(row.get("EventDate", ""))
    city = clean_text(row.get("City", ""))
    state = clean_text(row.get("State", ""))
    location = f"{city}, {state}".strip(", ")
    employer = clean_text(row.get("Employer", ""))
    narrative = clean_text(row.get("Final Narrative", ""))
    nature_title = clean_text(row.get("NatureTitle", ""))
    event_title = clean_text(row.get("EventTitle", ""))
    source_title = clean_text(row.get("SourceTitle", ""))
    industry = clean_text(row.get("Industry_Description", "Oil & Gas"))
    
    hosp = clean_text(row.get("Hospitalized", "0"))
    amp = clean_text(row.get("Amputation", "0"))
    eye = clean_text(row.get("Loss of Eye", "0"))
    
    # Severity categorization
    severity = "Non-Fatal Injury"
    if hosp == "1.00" or hosp == "1":
        severity = "Hospitalization"
    if amp == "1.00" or amp == "1":
        severity = "Amputation"
    if eye == "1.00" or eye == "1":
        severity = "Loss of Eye"
        
    # In initial ingestion, SIF potential is marked REVIEW_REQUIRED or UNANNOTATED
    # Do not auto-assign SIF potential based solely on injury outcome!
    sif_potential = "REVIEW_REQUIRED"
    
    # Pre-populate observable fields where directly stated in OSHA record
    cause = event_title if event_title and event_title.lower() != "nonclassifiable" else None
    hazard = source_title if source_title and source_title.lower() != "nonclassifiable" else None
    
    canonical_row = {
        "record_id": f"OILPS_OSHA_{idx:05d}",
        "source": "OSHA",
        "source_document": "January2015toNovember2025.csv",
        "source_record_id": osha_id,
        "report_date": event_date,
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
        "sif_potential": sif_potential,
        "hazard": hazard,
        "barrier": None,
        "barrier_failure": None,
        "potential_consequence": nature_title if nature_title and nature_title.lower() != "nonclassifiable" else None,
        "data_source_type": "REGULATORY_SAFETY_REPORT"
    }
    return canonical_row


def normalize_iogp_record(item, idx, source_tag, doc_name):
    """
    Maps an extracted IOGP report / page / case study to canonical schema.
    """
    raw_text = clean_text(item.get("raw_text", item.get("text", "")))
    page_num = item.get("page_number", item.get("page", idx))
    
    # Extract sub-sections if present in IOGP structured formats
    what_happened = ""
    what_went_wrong = ""
    corrective_actions = ""
    causal_factors = ""
    activity = ""
    lsr = ""
    
    # Regex parsing for IOGP standard report headings
    m_happened = re.search(r'(?:what happened|description of (?:the )?event|incident description)[:\s]+(.*?)(?=(?:what went wrong|causes|causal factors|corrective actions|lessons learned|life-saving rule|$))', raw_text, re.IGNORECASE | re.DOTALL)
    if m_happened:
        what_happened = clean_text(m_happened.group(1))
        
    m_wrong = re.search(r'(?:what went wrong|causes|causal factors)[:\s]+(.*?)(?=(?:corrective actions|lessons learned|life-saving rule|recommendations|$))', raw_text, re.IGNORECASE | re.DOTALL)
    if m_wrong:
        what_went_wrong = clean_text(m_wrong.group(1))
        
    m_actions = re.search(r'(?:corrective actions|lessons learned|recommendations)[:\s]+(.*?)(?=(?:life-saving rule|$))', raw_text, re.IGNORECASE | re.DOTALL)
    if m_actions:
        corrective_actions = clean_text(m_actions.group(1))
        
    m_activity = re.search(r'(?:activity|operation|task)[:\s]+(.*?)(?=(?:location|date|what happened|$|\n))', raw_text, re.IGNORECASE)
    if m_activity:
        activity = clean_text(m_activity.group(1))
        
    # If narrative was not neatly sectioned, use full clean text
    narrative = what_happened if what_happened and len(what_happened) > 40 else raw_text
    
    # High Potential Events by IOGP definition are SIF-potential
    # Fatal incidents are SIF-potential
    sif_potential = "1" if source_tag in ["IOGP_HPE", "IOGP_FATAL"] else "REVIEW_REQUIRED"
    event_type = "High Potential Event" if source_tag == "IOGP_HPE" else ("Fatal Incident" if source_tag == "IOGP_FATAL" else "Safety Event")
    data_source_type = "INDUSTRY_HPE_REPORT" if source_tag == "IOGP_HPE" else ("INDUSTRY_FATAL_REPORT" if source_tag == "IOGP_FATAL" else "INDUSTRY_SPI_REPORT")

    canonical_row = {
        "record_id": f"OILPS_{source_tag}_{idx:04d}",
        "source": source_tag,
        "source_document": doc_name,
        "source_record_id": f"{source_tag}_P{page_num:03d}",
        "report_date": None,
        "country": None,
        "location": None,
        "function": None,
        "industry": "Oil and Gas Exploration and Production",
        "activity": activity if activity else None,
        "event_type": event_type,
        "cause": None,
        "narrative": narrative,
        "what_went_wrong": what_went_wrong if what_went_wrong else None,
        "corrective_actions": corrective_actions if corrective_actions else None,
        "causal_factors": causal_factors if causal_factors else None,
        "primary_life_saving_rule": None,
        "secondary_life_saving_rule": None,
        "life_saving_rules": None,
        "severity": "Fatal" if source_tag == "IOGP_FATAL" else ("High Potential" if source_tag == "IOGP_HPE" else "Reported Event"),
        "hospitalization": None,
        "amputation": None,
        "loss_of_eye": None,
        "sif_potential": sif_potential,
        "hazard": None,
        "barrier": None,
        "barrier_failure": None,
        "potential_consequence": "Fatality / Serious Injury" if source_tag in ["IOGP_HPE", "IOGP_FATAL"] else None,
        "data_source_type": data_source_type
    }
    return canonical_row


def normalize_all_datasets(osha_processed_csv, iogp_raw_dir, output_unified_csv):
    output_unified_csv = Path(output_unified_csv)
    output_unified_csv.parent.mkdir(parents=True, exist_ok=True)
    
    all_rows = []
    
    # 1. Process OSHA records
    osha_processed_csv = Path(osha_processed_csv)
    if osha_processed_csv.exists():
        print(f"Normalizing OSHA records from {osha_processed_csv}...")
        with open(osha_processed_csv, mode="r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=1):
                canonical = normalize_osha_record(row, idx)
                all_rows.append(canonical)
        print(f"  Processed {len(all_rows)} OSHA records.")
        
    # 2. Process IOGP records
    iogp_raw_dir = Path(iogp_raw_dir)
    if iogp_raw_dir.exists():
        iogp_files = [
            ("hpe_extracted_raw.json", "IOGP_HPE", "IAOGP - High Potential Event Reports.pdf"),
            ("spi_extracted_raw.json", "IOGP_FATAL", "IAOGP - Safety performance indicators.pdf"),
            ("spi_2025_extracted_raw.json", "IOGP_SPI", "IAOGP-Safety performance indicators - 2025 data.pdf")
        ]
        
        for json_file, tag, doc_name in iogp_files:
            json_path = iogp_raw_dir / json_file
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for idx, item in enumerate(data, start=1):
                        canonical = normalize_iogp_record(item, idx, tag, doc_name)
                        all_rows.append(canonical)
                print(f"  Processed {len(data)} records from {json_file}")
                
    # Save unified CSV
    with open(output_unified_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CANONICAL_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)
        
    print(f"\nUnified raw dataset created at {output_unified_csv} with {len(all_rows)} total records.")
    return len(all_rows)

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    osha_file = base_dir / "ai-service" / "datasets" / "processed" / "osha_relevant.csv"
    iogp_dir = base_dir / "ai-service" / "datasets" / "raw" / "iogp"
    out_file = base_dir / "ai-service" / "datasets" / "processed" / "oilps_unified_raw.csv"
    
    normalize_all_datasets(osha_file, iogp_dir, out_file)
