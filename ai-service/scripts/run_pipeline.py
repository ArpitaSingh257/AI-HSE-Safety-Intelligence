"""
run_pipeline.py - Master pipeline runner for OILPS Safety Dataset Creation.
Executes all stages in sequence:
1. IOGP extraction
2. OSHA extraction & domain filtering
3. Canonical schema normalization
4. Exact & near deduplication
5. Quality validation & annotation dataset generation
6. Stratified train/val/test splitting
"""

import sys
import time
from pathlib import Path

# Add scripts directory to path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from extract_iogp import main as run_extract_iogp
from process_osha import process_osha_dataset
from normalize import normalize_all_datasets
from deduplicate import run_deduplication
from validate_dataset import analyze_dataset_quality
from create_splits import create_dataset_splits

def run_master_pipeline():
    start_time = time.time()
    base_dir = current_dir.parent.parent
    resources_dir = base_dir / "resources"
    ai_service_dir = base_dir / "ai-service"
    
    datasets_dir = ai_service_dir / "datasets"
    raw_osha_dir = datasets_dir / "raw" / "osha"
    raw_iogp_dir = datasets_dir / "raw" / "iogp"
    processed_dir = datasets_dir / "processed"
    annotation_dir = datasets_dir / "annotation"
    splits_dir = datasets_dir / "splits"
    quality_dir = datasets_dir / "quality"
    
    osha_src_csv = resources_dir / "January2015toNovember2025.csv"
    osha_relevant_csv = processed_dir / "osha_relevant.csv"
    unified_raw_csv = processed_dir / "oilps_unified_raw.csv"
    unified_deduped_csv = processed_dir / "oilps_unified_deduped.csv"
    annotation_csv = annotation_dir / "oilps_annotation.csv"
    dedup_report_md = quality_dir / "deduplication_report.md"
    quality_report_md = quality_dir / "DATASET_QUALITY_REPORT.md"
    
    print("=" * 70)
    print("OILPS AI/NLP SERVICE — DATASET CREATION PIPELINE")
    print("=" * 70)
    
    # Stage 1: IOGP PDF Extraction
    print("\n[Stage 1/6] Extracting IOGP PDF Reports...")
    run_extract_iogp()
    
    # Stage 2: OSHA Extraction & Filtering
    print("\n[Stage 2/6] Processing and Filtering OSHA Workplace Safety Records...")
    if osha_src_csv.exists():
        process_osha_dataset(osha_src_csv, raw_osha_dir, processed_dir)
    else:
        print(f"Warning: OSHA source file {osha_src_csv} not found.")
        
    # Stage 3: Normalization
    print("\n[Stage 3/6] Normalizing Records to Canonical OILPS Schema...")
    normalize_all_datasets(osha_relevant_csv, raw_iogp_dir, unified_raw_csv)
    
    # Stage 4: Deduplication
    print("\n[Stage 4/6] Running Exact and Near-Duplicate Detection...")
    run_deduplication(unified_raw_csv, unified_deduped_csv, dedup_report_md)
    
    # Stage 5: Quality Validation & Annotation Preparation
    print("\n[Stage 5/6] Validating Dataset Quality & Generating Annotation CSV...")
    analyze_dataset_quality(unified_deduped_csv, annotation_csv, quality_report_md)
    
    # Stage 6: Train/Val/Test Splits
    print("\n[Stage 6/6] Generating Leakage-Safe Stratified Splits (70/15/15)...")
    create_dataset_splits(unified_deduped_csv, splits_dir, seed=42)
    
    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 70)
    print(f"DATASET CREATION PIPELINE COMPLETED SUCCESSFULLY in {elapsed}s")
    print("=" * 70)

if __name__ == "__main__":
    run_master_pipeline()
