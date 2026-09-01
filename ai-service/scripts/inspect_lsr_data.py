"""
inspect_lsr_data.py - Stage 28D Data Pipeline & LSR Coverage Audit Script.
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def inspect_lsr():
    csv_path = BASE_DIR / "datasets" / "processed" / "oilps_unified_deduped.csv"
    print("CSV Path:", csv_path)
    print("CSV Exists?", csv_path.exists())

    if not csv_path.exists():
        # Check other dataset paths
        processed_dir = BASE_DIR / "datasets" / "processed"
        print("Files in datasets/processed:")
        for f in processed_dir.glob("*"):
            print(" -", f.name)
        return

    df = pd.read_csv(csv_path)
    print("\nTotal Records in CSV:", len(df))
    print("\nColumns in CSV:\n", df.columns.tolist())

    lsr_cols = [c for c in df.columns if 'lsr' in c.lower() or 'life' in c.lower() or 'rule' in c.lower()]
    print("\nLSR-related columns:", lsr_cols)

    for col in df.columns:
        # Check unique values and value counts for candidate LSR columns
        if any(kw in col.lower() for kw in ['lsr', 'life', 'rule', 'category', 'type', 'precursor']):
            print(f"\n--- Column: '{col}' ---")
            print("Null count:", df[col].isnull().sum(), f"({df[col].isnull().sum()/len(df)*100:.2f}%)")
            print("Top 10 Value Counts:")
            print(df[col].value_counts(dropna=False).head(10))

if __name__ == "__main__":
    inspect_lsr()
