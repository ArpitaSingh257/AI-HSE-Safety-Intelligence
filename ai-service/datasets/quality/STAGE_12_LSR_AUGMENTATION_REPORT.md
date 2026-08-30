# STAGE 12: TARGETED LSR DATA AUGMENTATION & DOMAIN-AWARE TRAINING REPORT

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Evaluation Split:** Held-Out Unseen Test Set (`lsr_test.csv` - 138 records)
**Date:** 2026-08-30
**Random Seed:** `42` (Deterministic Reproducibility)

---

## 1. Executive Summary & Benchmark Comparison

| Model Phase | Architecture | Training Data Strategy | Test Micro-F1 | Test Macro-F1 | Test Hamming Loss | Test Exact Match Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 7 Champion** | Bidirectional GRU + Attention | Original Split Only | 0.6928 | 0.5723 | 0.0378 | 71.74% |
| **Stage 12 Candidate** | **Domain-Aware BiGRU+Attn** | **Targeted Domain Augmentation (Train Only)** | **0.6853** | **0.5352** | **0.0362** | **73.19%** |

### Final Selection Decision: **`STAGE 7 REMAINS LSR CHAMPION`**

---

## 2. Stage 12 Per-Rule Performance Breakdown (9 IOGP Rules)

| Official IOGP Life-Saving Rule | Validation Threshold | Test Support | Precision | Recall | F1-Score | Confusion (TP/FP/FN/TN) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bypassing Safety Controls** | 0.35 | 0 | 0.0000 | 0.0000 | **0.0000** | 0/0/0/138 |
| **Confined Space** | 0.35 | 2 | 1.0000 | 0.5000 | **0.6667** | 1/0/1/136 |
| **Driving** | 0.35 | 15 | 0.8000 | 0.8000 | **0.8000** | 12/3/3/120 |
| **Energy Isolation** | 0.27 | 16 | 0.7692 | 0.6250 | **0.6897** | 10/3/6/119 |
| **Hot Work** | 0.23 | 13 | 0.8000 | 0.9231 | **0.8571** | 12/3/1/122 |
| **Line of Fire** | 0.15 | 5 | 0.0000 | 0.0000 | **0.0000** | 0/4/5/129 |
| **Safe Mechanical Lifting** | 0.81 | 14 | 0.8750 | 0.5000 | **0.6364** | 7/1/7/123 |
| **Toxic Gas / Hazardous Substance** | 0.35 | 2 | 0.5000 | 0.5000 | **0.5000** | 1/1/1/135 |
| **Working at Height** | 0.69 | 9 | 0.6667 | 0.6667 | **0.6667** | 6/3/3/126 |
| **OVERALL (MICRO)** | — | **76** | **0.7313** | **0.6447** | **0.6853** | — |
| **OVERALL (MACRO)** | — | — | **0.6012** | **0.5016** | **0.5352** | — |

---

## 3. Demo Scenario Verification Audit

### Hydrotest Pressure Fitting Failure:
- **Triggered Rules:** `['Energy Isolation']`
- **Key Probabilities:** Energy Isolation: 74.3%

### Crane Lifting Tubular Handling:
- **Triggered Rules:** `[]`
- **Key Probabilities:** 

### Confined Space Vessel Entry with H2S:
- **Triggered Rules:** `[]`
- **Key Probabilities:** 

### Minor Slip on Ice in Yard:
- **Triggered Rules:** `[]`
- **Key Probabilities:** 

