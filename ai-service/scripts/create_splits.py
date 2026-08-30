"""
create_splits.py - Creates leakage-safe, reproducible Train (70%), Validation (15%), and Test (15%) splits.
Outputs:
- datasets/splits/train.csv
- datasets/splits/val.csv
- datasets/splits/test.csv
- datasets/splits/splits_metadata.json
"""

import os
import csv
import json
import random
from pathlib import Path
from collections import defaultdict

def create_dataset_splits(input_csv, output_splits_dir, seed=42):
    input_csv = Path(input_csv)
    output_splits_dir = Path(output_splits_dir)
    output_splits_dir.mkdir(parents=True, exist_ok=True)
    
    random.seed(seed)
    
    records = []
    with open(input_csv, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            records.append(r)
            
    total = len(records)
    print(f"Creating splits from {total} records with random seed = {seed}...")
    
    # Group by source to ensure stratified representation across splits
    source_groups = defaultdict(list)
    for r in records:
        source_groups[r.get("source", "OTHER")].append(r)
        
    train_records = []
    val_records = []
    test_records = []
    
    for src, group in source_groups.items():
        random.shuffle(group)
        n = len(group)
        n_train = int(n * 0.70)
        n_val = int(n * 0.15)
        # Remaining goes to test
        train_records.extend(group[:n_train])
        val_records.extend(group[n_train:n_train + n_val])
        test_records.extend(group[n_train + n_val:])
        
    # Shuffle each split
    random.shuffle(train_records)
    random.shuffle(val_records)
    random.shuffle(test_records)
    
    # Save CSV files
    train_path = output_splits_dir / "train.csv"
    val_path = output_splits_dir / "val.csv"
    test_path = output_splits_dir / "test.csv"
    meta_path = output_splits_dir / "splits_metadata.json"
    
    for path, data in [(train_path, train_records), (val_path, val_records), (test_path, test_records)]:
        with open(path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
            
    meta = {
        "random_seed": seed,
        "total_records": total,
        "train_count": len(train_records),
        "train_pct": round((len(train_records) / max(total, 1)) * 100, 2),
        "val_count": len(val_records),
        "val_pct": round((len(val_records) / max(total, 1)) * 100, 2),
        "test_count": len(test_records),
        "test_pct": round((len(test_records) / max(total, 1)) * 100, 2),
        "stratification_sources": list(source_groups.keys())
    }
    
    with open(meta_path, mode="w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        
    print(f"Splits generated successfully:")
    print(f"  Train: {len(train_records)} ({meta['train_pct']}%)")
    print(f"  Val:   {len(val_records)} ({meta['val_pct']}%)")
    print(f"  Test:  {len(test_records)} ({meta['test_pct']}%)")
    return meta

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent
    in_csv = base_dir / "ai-service" / "datasets" / "processed" / "oilps_unified_deduped.csv"
    out_dir = base_dir / "ai-service" / "datasets" / "splits"
    
    if in_csv.exists():
        create_dataset_splits(in_csv, out_dir)
