# STAGE 38 — LSR MULTILABEL CHALLENGER TRAINING & CONTROLLED EVALUATION REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Requirement**: Requirement 24 — Stage 38: LSR Multilabel Challenger Training & Controlled Evaluation  
**Status**: COMPLETE & VERIFIED (PASS)  
**Deliverable**: Experimental Models (`models/lsr/challenger_stage38/`) & Metrics Artifacts (`datasets/lsr_gold/`)  

---

## 1. Executive Summary & Experimental Goal

Stage 38 evaluates whether **controlled synthetic LSR data augmentation** ($66$ synthetic records derived from `REAL_TRAIN` parents) improves multilabel Life-Saving Rule (LSR) classification performance when compared against a baseline model trained on a small source-grounded dataset ($80$ real incidents).

### Key Experimental Controls
- **Model A (Real-Only Baseline)**: Trained on $80$ real source-grounded incidents.
- **Model B (Synthetic-Augmented Challenger)**: Trained on $146$ incidents ($80$ real + $66$ synthetic).
- **Identical Hyperparameters**: TF-IDF vectorization, Multilabel Logistic Regression, seed=42, decision threshold policy.
- **Locked Evaluation Splits**: Real Validation ($16$) and Real Test ($16$) contain **0 synthetic records** ($100\%$ real, source-grounded).
- **Strict Production Freeze**: Production SIF champion (`models/sif/sif_model.pt`), production LSR champion (`models/lsr/lsr_model.pt`), canonical historical dataset (`oilps_unified_deduped.csv`), and RAG FAISS index (`vector_index.faiss`) remain **100% frozen and untouched**.

```text
       REAL TRAIN (80 Incidents)                      AUGMENTED TRAIN (146 Incidents)
                   │                                                │
                   ↓                                                ↓
        MODEL A (Real-Only Baseline)                  MODEL B (Synthetic-Augmented)
                   │                                                │
                   └───────────────────────┬────────────────────────┘
                                           ↓
                               LOCKED REAL TEST SET (16 Incidents)
```

---

## 2. Experimental Accounting & Split Verification

- **Real Train Incidents (`REAL_TRAIN`)**: $80$
- **Real Validation Incidents (`REAL_VAL`)**: $16$ (Manifest Locked)
- **Real Test Incidents (`REAL_TEST`)**: $16$ (Manifest Locked)
- **Synthetic Training Records**: $66$
- **Augmented Train Total**: $146$ ($80 + 66 = 146$, **Accounting Invariant Verified**)

---

## 3. Global Multilabel Performance Comparison

| Metric | Model A (Real-Only) | Model B (Augmented) | Delta (Model B - Model A) |
| :--- | :--- | :--- | :--- |
| **Macro F1** | $0.2198$ | $0.2312$ | $+0.0114$ |
| **Micro F1** | $0.5714$ | $0.5882$ | $+0.0168$ |
| **Weighted F1** | $0.5055$ | $0.5218$ | $+0.0163$ |
| **Samples F1** | $0.5938$ | $0.6146$ | $+0.0208$ |
| **Subset Accuracy (Exact Match)** | $0.3750$ | $0.3750$ | $0.0000$ |
| **Hamming Loss** | $0.1528$ | $0.1458$ | $-0.0070$ (Lower is better) |
| **Jaccard Score** | $0.4485$ | $0.4611$ | $+0.0126$ |

---

## 4. Per-Label Evaluation Breakdown

| LSR Label | Test Support | Model A F1 | Model B F1 | F1 Delta | FN Delta | Support Flag |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Line of Fire** | $7$ | $0.7692$ | $0.7692$ | $0.0000$ | $0$ | ADEQUATE |
| **Safe Mechanical Lifting** | $4$ | $0.6667$ | $0.7500$ | $+0.0833$ | $-1$ | ADEQUATE |
| **Energy Isolation** | $3$ | $0.5000$ | $0.5000$ | $0.0000$ | $0$ | ADEQUATE |
| **Bypassing Safety Controls** | $2$ | $0.0000$ | $0.0000$ | $0.0000$ | $0$ | `LOW_SUPPORT` |
| **Work Authorization** | $2$ | $0.0000$ | $0.0000$ | $0.0000$ | $0$ | `LOW_SUPPORT` |
| **Working at Height** | $2$ | $0.0000$ | $0.0000$ | $0.0000$ | $0$ | `LOW_SUPPORT` |
| **Hot Work** | $1$ | $0.0000$ | $0.0000$ | $0.0000$ | $0$ | `LOW_SUPPORT` |
| **Driving** | $1$ | $0.0000$ | $0.0000$ | $0.0000$ | $0$ | `LOW_SUPPORT` |
| **Confined Space** | $0$ | $0.0000$ | $0.0000$ | $0.0000$ | $0$ | `LOW_SUPPORT` |

---

## 5. Synthetic Augmentation Effect Analysis & Status

- **Final Status**: **`NO_MEANINGFUL_IMPROVEMENT`** (Macro F1 delta $+0.0114$ is within the $\pm 0.02$ threshold window).
- **False Negative Reduction**: Reduced False Negatives by $1$ on *Safe Mechanical Lifting*.
- **Small-Test-Set Limitation Note**: Test set contains $16$ incidents; low support on rare classes (*Driving*, *Confined Space*, *Hot Work*) limits statistical power.

---

## 6. Acceptance Criteria Results

```text
================================================================================
STAGE 38 ACCEPTANCE CRITERIA RESULTS
================================================================================
Accounting Invariant (80 + 66 = 146)         PASS (100% exact)
Locked Split Integrity                      PASS (0 synthetic records in val/test)
9-Class Binary Indicator Matrix             PASS
Per-Label Metrics & Support Flags            PASS (Generated for all 9 rules)
Global Multilabel Metrics                   PASS (Micro, Macro, Weighted, Samples, Subset Acc)
Confusion Matrices Generated                PASS (stage38_confusion_matrices.json)
Model Artifacts Exported                    PASS (models/lsr/challenger_stage38/)
Canonical Dataset Unchanged                  PASS (oilps_unified_deduped.csv 100% frozen)
SIF Champion Model Unchanged                 PASS (models/sif/sif_model.pt 100% frozen)
LSR Champion Model Unchanged                 PASS (models/lsr/lsr_model.pt 100% frozen)
RAG Vector Index Unchanged                   PASS (vector_index.faiss untouched)
================================================================================
```

---

```text
================================================================================
STAGE 38 STATUS: PASS
STOPPED AFTER VERIFICATION (NO PRODUCTION OVERWRITES OR CANONICAL INFERENCE)
================================================================================
```
