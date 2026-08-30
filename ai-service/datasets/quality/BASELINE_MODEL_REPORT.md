# OILPS Stage 3: Baseline Model Training & Benchmark Report

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Phase:** Stage 3 Baseline Model Benchmarking
**Date:** 2026-08-30
**Random Seed:** `42` (Deterministic Reproducibility)

---

## 1. Dataset & Experimental Setup

| Task | Training Records | Validation Records | Test Records | Input Feature | Target Schema |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SIF Binary Classification** | 627 | 135 | 134 | Raw Narrative Text | `sif_label` (1 = SIF, 0 = Non-SIF) |
| **LSR Multi-Label Classification** | 629 | 133 | 138 | Raw Narrative Text | 9 Official IOGP Rules (Multi-Hot) |
| **Precursor Information Extraction** | 900 Total Records | — | — | Raw Narrative Text | 5 Decoupled Entity Fields |

## 2. Task 1: SIF Binary Classification Performance

### Model Selection on Validation Set:

| Model Architecture | Accuracy | Precision | SIF=1 Recall | F1-Score | ROC-AUC | PR-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TF-IDF + Logistic Regression** | 0.8444 | 0.9438 | 0.8400 | 0.8889 | 0.9169 | 0.9720 |
| **TF-IDF + Calibrated Linear SVM** | 0.8667 | 0.9184 | **0.9000** | **0.9091** | **0.9386** | **0.9793** |

**Selected Best SIF Baseline:** **`Calibrated Linear SVM`**.

### Final Held-Out Test Set Performance (Evaluated ONCE):

| Test Metric | Value | Safety Interpretation |
| :--- | :--- | :--- |
| **Accuracy** | **79.85%** | Overall binary correctness on unseen incidents. |
| **SIF=1 Recall** | **89.90%** | **Primary Safety Metric:** Captures 89 of 99 true SIF precursors. |
| **SIF=1 Precision** | **83.96%** | Precision of flagged SIF precursor alerts. |
| **F1-Score (SIF=1)** | **0.8683** | Harmonic mean of precision and recall. |
| **PR-AUC** | **0.9586** | Area Under Precision-Recall Curve. |
| **ROC-AUC** | **0.8782** | Area Under ROC Curve. |

### Test Confusion Matrix:

```text
                     Predicted Non-SIF (0)    Predicted SIF (1)
Actual Non-SIF (0)        TN = 18                   FP = 17
Actual SIF (1)            FN = 10                   TP = 89
```

## 3. Task 2: IOGP Life-Saving Rule Multi-Label Performance

### Model Selection on Validation Set:

| Model Architecture | Micro Precision | Micro Recall | Micro F1 | Macro F1 | Hamming Loss | Exact Match |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **One-vs-Rest Logistic Regression** | 0.9038 | 0.6620 | **0.7642** | **0.5247** | **0.0242** | **0.7970** |
| **One-vs-Rest Linear SVM** | 0.9535 | 0.5775 | 0.7193 | 0.4779 | 0.0267 | 0.7895 |

### Final Held-Out Test Set Performance for All 9 IOGP Rules:

| Official IOGP Life-Saving Rule | Test Support | Test Precision | Test Recall | Test F1-Score |
| :--- | :--- | :--- | :--- | :--- |
| **Bypassing Safety Controls** | 0 | 0.0000 | 0.0000 | **0.0000** |
| **Confined Space** | 2 | 1.0000 | 0.5000 | **0.6667** |
| **Driving** | 15 | 0.9167 | 0.7333 | **0.8148** |
| **Energy Isolation** | 16 | 0.5882 | 0.6250 | **0.6061** |
| **Hot Work** | 13 | 0.9167 | 0.8462 | **0.8800** |
| **Line of Fire** | 5 | 0.0000 | 0.0000 | **0.0000** |
| **Safe Mechanical Lifting** | 14 | 0.6667 | 0.5714 | **0.6154** |
| **Toxic Gas / Hazardous Substance** | 2 | 1.0000 | 0.5000 | **0.6667** |
| **Working at Height** | 9 | 0.5556 | 0.5556 | **0.5556** |
| **OVERALL (MICRO)** | **76** | **0.7344** | **0.6184** | **0.6714** |
| **OVERALL (MACRO)** | — | **0.6271** | **0.4813** | **0.5339** |

## 4. Task 3: Precursor Information Extraction Baseline

- **`activity`**: Mean Token Overlap = **6.4%**, High Grounding Rate = **4.3%**
- **`hazard`**: Mean Token Overlap = **2.9%**, High Grounding Rate = **0.6%**
- **`barrier`**: Mean Token Overlap = **1.8%**, High Grounding Rate = **0.0%**
- **`barrier_failure`**: Mean Token Overlap = **5.0%**, High Grounding Rate = **0.0%**
- **`potential_consequence`**: Mean Token Overlap = **1.8%**, High Grounding Rate = **0.0%**
