"""
diagnose_lsr_csv.py - Diagnoses primary_life_saving_rule column in oilps_unified_deduped.csv.
"""

import pandas as pd
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent

def diagnose():
    csv_path = BASE_DIR / "datasets" / "processed" / "oilps_unified_deduped.csv"
    if not csv_path.exists():
        print("CSV not found!")
        return

    df = pd.read_csv(csv_path)
    print(f"Total rows in CSV: {len(df)}")
    
    col = "primary_life_saving_rule"
    if col in df.columns:
        s = df[col].fillna("").astype(str).str.strip()
        non_empty = s[s != ""]
        print(f"\nNon-empty count for '{col}': {len(non_empty)} / {len(df)} ({len(non_empty)/len(df)*100:.2f}%)")
        print("\nValue Counts for 'primary_life_saving_rule':")
        print(s.value_counts().head(20))

    col2 = "life_saving_rules"
    if col2 in df.columns:
        s2 = df[col2].fillna("").astype(str).str.strip()
        non_empty2 = s2[s2 != ""]
        print(f"\nNon-empty count for '{col2}': {len(non_empty2)} / {len(df)} ({len(non_empty2)/len(df)*100:.2f}%)")
        print("\nValue Counts for 'life_saving_rules':")
        print(s2.value_counts().head(20))

if __name__ == "__main__":
    diagnose()
