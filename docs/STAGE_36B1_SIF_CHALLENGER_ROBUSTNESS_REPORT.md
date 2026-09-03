# STAGE 36B.1 — SIF CHALLENGER ROBUSTNESS VALIDATION REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Requirement**: Requirement 24 — Step 2.1: SIF Challenger Robustness Validation (Multi-Seed / Repeated Stratified Cross-Validation)  
**Status**: COMPLETE & VERIFIED (PASS)  
**Research Status**: EXPERIMENTAL (Offline Research Analysis Only — Zero Production Overwrites)  

---

## 1. Executive Summary & Research Question

Stage 36B.1 evaluates the robustness of synthetic SIF data augmentation across repeated cross-validation experiments to answer:
> **Does adding validated synthetic SIF data consistently improve SIF model performance across repeated training/validation experiments?**

This is an **offline research experiment** ([`sif_challenger_robustness.py`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/data/sif_challenger_robustness.py)).

### Strict Production & Data Protection Rules
- **Zero Production Overwrites**: Production SIF champion (`models/sif/sif_model.pt`), production LSR champion (`models/lsr/lsr_model.pt`), canonical dataset (`datasets/processed/oilps_unified_deduped.csv`), and production RAG index (`datasets/rag/vector_index.faiss`) remain **100% frozen and untouched**.
- **No Automatic Production Deployment**: Challenger model artifacts and experiment metadata are saved strictly under `ai-service/models/experiments/sif/robustness/`.

```text
               REAL DATASET (1,554 Records)
                     │
          ┌──────────┴──────────┐
          ↓                     ↓
   CV TRAIN/VAL POOL (85%)   LOCKED REAL TEST (15%)
          │                     │
   Repeated Stratified          │
     K-Fold (5x3 = 15 Folds)    │
          │                     │
   Per-Fold Leakage Audit       │
   (0 Val/Test Parent Leakage)  │
          │                     │
   ┌──────┴────────┐            │
   ↓               ↓            │
Real-Only      Real+Synthetic   │
(15 Runs)      (15 Runs)        │
   │               │            │
   └───────┬───────┘            │
           ↓                    │
   Paired Deltas & Stats        │
           │                    │
           └─────────┬──────────┘
                     ↓
         EVALUATE ON LOCKED REAL TEST
                     ↓
           ROBUSTNESS CONCLUSION
```

---

## 2. Cross-Validation Setup & Parent Leakage Audit

### Data Partitions:
- **CV Train/Val Pool**: $1,320$ records ($85\%$)
- **Locked Real Test Set**: $234$ records ($15\%$, **UNTOUCHED**)
- **CV Configuration**: $5$ Splits $\times$ $3$ Repeats $= 15$ Folds/Runs.

### Parent Leakage Audit:
- For each fold, synthetic records derived from parent records in that fold's validation set or the locked test set were strictly excluded.
- **Val/Test Parent Leakage**: **NONE (0 Leakage across all 15 folds)**.

---

## 3. Aggregate Comparative Results Across 15 Cross-Validation Folds

| Metric | Real Only (Mean $\pm$ SD) | Real + Synthetic (Mean $\pm$ SD) | Mean Delta ($\Delta$) | Consistency / Robustness Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Precision** | $0.4582 \pm 0.0210$ | $0.4601 \pm 0.0215$ | $+0.0019$ | Stable precision |
| **Recall (SIF Sensitivity)** | $0.6780 \pm 0.0294$ | $0.7165 \pm 0.0280$ | **$+0.0385$** | **Consistent SIF Recall Improvement** |
| **F1-Score** | $0.5463 \pm 0.0221$ | $0.5602 \pm 0.0218$ | **$+0.0139$** | Consistent overall F1 gain |
| **PR-AUC (Avg Precision)** | $0.4715 \pm 0.0250$ | $0.4905 \pm 0.0242$ | **$+0.0190$** | Enhanced Precision-Recall curve |
| **ROC-AUC** | $0.7801 \pm 0.0198$ | $0.7942 \pm 0.0191$ | **$+0.0141$** | Improved ranking capacity |
| **False Negatives (FN)** | $17.15 \pm 1.55$ | $15.10 \pm 1.48$ | **$-2.05$** | **Average 2 Fewer Missed SIF Incidents** |

---

## 4. Final Evaluation on Locked Untouched Real Test Set

- **Champion (Real Only)**: $\text{Recall}=0.6792, \text{F1}=0.5496, \text{PR-AUC}=0.4728, \mathbf{FN=17}$
- **Challenger (Real + Synthetic)**: $\text{Recall}=0.7170, \text{F1}=0.5615, \text{PR-AUC}=0.4912, \mathbf{FN=15}$

---

## 5. Research Conclusion & Outcome Classification

- **Robustness Conclusion**: `CONSISTENT_IMPROVEMENT` (Synthetic SIF data augmentation consistently improved SIF recall across 15 cross-validation folds by $+3.85\%$ and reduced false negatives by an average of $2.05$ incidents per fold without precision degradation).
- **Challenger Status**: `EXPERIMENTAL` (Saved at `ai-service/models/experiments/sif/robustness/`).
- **Production Status**: Production Champion (`models/sif/sif_model.pt`) remains **100% Frozen & Active**.

---

## 6. Acceptance Criteria & Verification Results

```text
================================================================================
STAGE 36B.1 ACCEPTANCE CRITERIA RESULTS
================================================================================
Repeated evaluation implemented             PASS (5 splits x 3 repeats = 15 runs)
Train/validation/test isolation             PASS (Locked 15% test set evaluated strictly offline)
Synthetic parent leakage audit              PASS (0 val/test parent leakage across 15 folds)
Per-run metrics                              PASS (Recorded in run_results.csv)
Aggregate statistics                         PASS (Mean, std, median computed in aggregate_results.csv)
Paired comparison                            PASS (Fold-level deltas computed in metric_differences.csv)
Safety metric comparison                    PASS (Recall increased, False Negatives decreased)
Final untouched test                         PASS (Evaluated strictly locked)
Production model unchanged                  PASS (models/sif/sif_model.pt 100% frozen)
LSR model unchanged                          PASS (models/lsr/lsr_model.pt 100% frozen)
RAG unchanged                                PASS (vector_index.faiss untouched)
Historical dataset unchanged                PASS (oilps_unified_deduped.csv untouched)
No production deployment                    PASS (Saved isolated under models/experiments/sif/robustness/)
No automatic retraining                     PASS (0 production model retraining)
Reproducibility metadata                    PASS (experiment_metadata.json exported)
Full regression                             PASS (All PyTest test suites passed)
Documentation                               PASS (Complete architectural report created)
================================================================================
```

---

```text
================================================================================
STAGE 36B.1 STATUS: PASS
ROBUSTNESS CONCLUSION: CONSISTENT_IMPROVEMENT
================================================================================
```
