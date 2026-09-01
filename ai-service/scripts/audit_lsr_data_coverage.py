"""
audit_lsr_data_coverage.py - STAGE 28D Full Pipeline & LSR Coverage Audit Script.
Traces historical dataset, Stage 7 prediction outputs, field mappings, and Stage 28 trend analyzer.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from inference.lsr_predictor import LSRPredictor, OFFICIAL_9_LSR
from inference.pattern_detector import RecurringPatternDetector
from inference.lsr_trend_analyzer import LsrTrendAnalyzer


def run_full_lsr_audit():
    print("="*80)
    print("STAGE 28D — LIFE-SAVING RULE (LSR) DATA-COVERAGE AUDIT")
    print("="*80)

    # ---------------------------------------------------------
    # STEP 1: HISTORICAL SOURCE DATASET AUDIT
    # ---------------------------------------------------------
    csv_path = BASE_DIR / "datasets" / "processed" / "oilps_unified_deduped.csv"
    print(f"\n[1] Inspecting Source CSV: {csv_path}")
    if not csv_path.exists():
        print(" ERROR: oilps_unified_deduped.csv not found!")
        return

    df_csv = pd.read_csv(csv_path)
    total_csv_records = len(df_csv)
    print(f" Total records in oilps_unified_deduped.csv: {total_csv_records:,}")
    print(f" CSV Columns ({len(df_csv.columns)}):", df_csv.columns.tolist())

    lsr_candidate_cols = [c for c in df_csv.columns if any(kw in c.lower() for kw in ['lsr', 'life', 'rule', 'saving'])]
    print(f" Candidate LSR Columns Found: {lsr_candidate_cols}")

    for col in lsr_candidate_cols:
        non_nulls = df_csv[col].dropna().tolist()
        non_empty = [str(x).strip() for x in non_nulls if str(x).strip() and str(x).strip().upper() not in ["UNKNOWN", "NAN", "NONE", ""]]
        print(f"\n --- Column '{col}' ---")
        print(f"   Non-null count: {len(non_nulls)} / {total_csv_records} ({len(non_nulls)/total_csv_records*100:.2f}%)")
        print(f"   Non-empty/valid label count: {len(non_empty)} / {total_csv_records} ({len(non_empty)/total_csv_records*100:.2f}%)")
        print(f"   Top 10 raw values:")
        print(df_csv[col].value_counts(dropna=False).head(10))

    # ---------------------------------------------------------
    # STEP 2: RECURRING PATTERN DETECTOR LOADED RECORDS AUDIT
    # ---------------------------------------------------------
    detector = RecurringPatternDetector()
    loaded_records = detector.load_historical_records()
    total_loaded = len(loaded_records)
    print(f"\n[2] Inspecting RecurringPatternDetector.load_historical_records()")
    print(f" Total records loaded: {total_loaded:,}")

    lsr_in_loaded = Counter(r.get("primary_life_saving_rule") for r in loaded_records)
    print(" Value distribution for 'primary_life_saving_rule' in loaded records:")
    for k, v in lsr_in_loaded.most_common(15):
        print(f"   - {k!r}: {v} ({v/total_loaded*100:.2f}%)")

    # ---------------------------------------------------------
    # STEP 3: STAGE 7 LSR PREDICTOR INFERENCE AUDIT
    # ---------------------------------------------------------
    print(f"\n[3] Inspecting Stage 7 LSR Predictor Inference (LSRPredictor)")
    lsr_predictor = LSRPredictor()
    print(f" Stage 7 Trained Weights Loaded? {lsr_predictor.has_trained_weights}")
    print(f" Checkpoint Path: {lsr_predictor.checkpoint_loaded_from}")
    print(f" Official 9 IOGP LSR Vocab: {lsr_predictor.rule_names}")
    print(" Per-Rule Thresholds:", json.dumps(lsr_predictor.rule_thresholds, indent=2))

    narratives = [r.get("narrative") or r.get("description") or "" for r in loaded_records]
    print(f" Running Stage 7 inference on {len(narratives):,} historical narrative descriptions...")

    predictions = []
    has_at_least_one = 0
    zero_predictions = 0
    pred_label_counts = Counter()

    for idx, narrative in enumerate(narratives):
        if idx % 1000 == 0 and idx > 0:
            print(f"   Processed {idx}/{len(narratives)} records...")
        pred = lsr_predictor.predict(narrative)
        matched_rules = pred.get("predicted_lsrs", [])
        if matched_rules:
            has_at_least_one += 1
            pred_label_counts.update(matched_rules)
        else:
            zero_predictions += 1

    print(f"\n Stage 7 Inference Results:")
    print(f"   Total records evaluated: {len(narratives):,}")
    print(f"   Records with at least one positive LSR predicted: {has_at_least_one:,} ({has_at_least_one/len(narratives)*100:.2f}%)")
    print(f"   Records with ZERO predicted LSRs (below threshold): {zero_predictions:,} ({zero_predictions/len(narratives)*100:.2f}%)")
    print("\n   Predicted LSR Label Counts across Historical Dataset:")
    for rule, count in pred_label_counts.most_common():
        print(f"     - {rule}: {count:,} ({count/len(narratives)*100:.2f}%)")

    # ---------------------------------------------------------
    # STEP 4: STAGE 28 DATA INTEGRATION / MERGE VERIFICATION
    # ---------------------------------------------------------
    print(f"\n[4] Stage 28 LSR Trend Analyzer Integration Verification")
    analyzer = LsrTrendAnalyzer()
    summary = analyzer.get_lsr_analytics_summary()
    print(f" Total records analyzed by Stage 28: {summary['total_reports']}")
    print(f" Unknown/missing LSR records: {summary['unknown_lsr_records']} ({summary['unknown_lsr_rate']*100:.2f}%)")
    print(f" Official IOGP LSR Profiles Returned: {len(summary['official_lsr_profiles'])}")
    for p in summary["official_lsr_profiles"]:
        print(f"   - {p['lsr_rule']}: {p['total_reports']} reports ({p['sif_reports']} SIF), trend={p['trend']}")

    # ---------------------------------------------------------
    # STEP 5: VOCABULARY MATCHING AUDIT
    # ---------------------------------------------------------
    print(f"\n[5] Official LSR Vocabulary Alignment Audit")
    s7_vocab = set(lsr_predictor.rule_names)
    loaded_vocab = set(lsr_in_loaded.keys())

    print(" Stage 7 Official 9 IOGP Vocabulary:", sorted(list(s7_vocab)))
    print(" Loaded Dataset LSR Vocabulary:", sorted(list(loaded_vocab)))
    print(" Overlap:", sorted(list(s7_vocab.intersection(loaded_vocab))))
    print(" Labels in dataset but not in Stage 7 vocab:", sorted(list(loaded_vocab - s7_vocab)))

    print("\n" + "="*80)
    print("AUDIT COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_full_lsr_audit()
