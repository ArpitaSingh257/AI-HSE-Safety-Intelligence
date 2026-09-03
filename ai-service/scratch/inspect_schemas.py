"""
inspect_schemas.py - Scratch script to inspect dataset schemas for Stage 39B.
"""

import sys
import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CANONICAL_CSV = BASE_DIR / "datasets" / "processed" / "oilps_unified_deduped.csv"
GOLD_CSV = BASE_DIR / "datasets" / "lsr_gold" / "iogp_incident_level_gold_v1.csv"
REC_CSV = BASE_DIR / "datasets" / "lsr_gold" / "iogp_reconstructed_lsr_v1.csv"

def inspect():
    print("="*80)
    print("CANONICAL DATASET SCHEMA:")
    df_can = pd.read_csv(CANONICAL_CSV)
    print(f"Row count: {len(df_can)}")
    print(f"Columns ({len(df_can.columns)}): {list(df_can.columns)}")
    print(f"Sources unique: {df_can['source'].value_counts().to_dict() if 'source' in df_can.columns else 'N/A'}")
    print(f"Data source types: {df_can['data_source_type'].value_counts().to_dict() if 'data_source_type' in df_can.columns else 'N/A'}")
    print("Sample canonical row:")
    print(df_can.head(2).to_dict(orient="records"))

    print("\n" + "="*80)
    print("IOGP GOLD DATASET SCHEMA:")
    df_gold = pd.read_csv(GOLD_CSV)
    print(f"Row count: {len(df_gold)}")
    print(f"Columns ({len(df_gold.columns)}): {list(df_gold.columns)}")
    print(f"Unique incident groups: {df_gold['incident_group_id'].nunique() if 'incident_group_id' in df_gold.columns else 'N/A'}")
    print("Sample gold row:")
    print(df_gold.head(2).to_dict(orient="records"))

    if REC_CSV.exists():
        print("\n" + "="*80)
        print("IOGP RECONSTRUCTED DATASET SCHEMA:")
        df_rec = pd.read_csv(REC_CSV)
        print(f"Row count: {len(df_rec)}")
        print(f"Columns ({len(df_rec.columns)}): {list(df_rec.columns)}")
        print("Sample rec row:")
        print(df_rec.head(2).to_dict(orient="records"))

if __name__ == "__main__":
    inspect()
