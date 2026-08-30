# STAGE 11: MULTI-LABEL LSR SEMANTIC ERROR ANALYSIS & TARGETED IMPROVEMENT REPORT

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Evaluation Split:** Held-Out Unseen Test Set (`lsr_test.csv` - 138 records)
**Date:** 2026-08-30
**Random Seed:** `42` (Deterministic Reproducibility)

---

## 1. Executive Summary & Cross-Stage LSR Comparison

| Model Phase | Architecture | Loss / Calibration Strategy | Test Micro-F1 | Test Macro-F1 | Test Hamming Loss | Test Exact Match Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 7 Baseline** | Bidirectional GRU + Attention | Smooth Pos-Weighted BCE | 0.6795 | 0.5618 | 0.0403 | 68.84% |
| **Stage 10 Calibration** | Stage 7 Frozen Model | Post-Hoc F0.7 Grid Search | 0.6939 | 0.5466 | 0.0362 | 70.29% |
| **Stage 11 Enhanced** | **Asymmetric Multi-Head GRU+Attn** | **Asymmetric Focal Loss + Dynamic Multi-Head** | **0.6977** | **0.5253** | **0.0419** | **67.39%** |

---

## 2. Stage 11 Per-Rule Performance Breakdown (9 IOGP Rules)

| Official IOGP Life-Saving Rule | Validation Threshold | Test Support | Precision | Recall | F1-Score | Confusion (TP/FP/FN/TN) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bypassing Safety Controls** | 0.40 | 0 | 0.0000 | 0.0000 | **0.0000** | 0/0/0/138 |
| **Confined Space** | 0.40 | 2 | 0.3333 | 0.5000 | **0.4000** | 1/2/1/134 |
| **Driving** | 0.73 | 15 | 0.9286 | 0.8667 | **0.8966** | 13/1/2/122 |
| **Energy Isolation** | 0.47 | 16 | 0.7059 | 0.7500 | **0.7273** | 12/5/4/117 |
| **Hot Work** | 0.27 | 13 | 0.9231 | 0.9231 | **0.9231** | 12/1/1/124 |
| **Line of Fire** | 0.39 | 5 | 0.0000 | 0.0000 | **0.0000** | 0/2/5/131 |
| **Safe Mechanical Lifting** | 0.38 | 14 | 0.6190 | 0.9286 | **0.7429** | 13/8/1/116 |
| **Toxic Gas / Hazardous Substance** | 0.40 | 2 | 0.4000 | 1.0000 | **0.5714** | 2/3/0/133 |
| **Working at Height** | 0.51 | 9 | 0.3333 | 0.7778 | **0.4667** | 7/14/2/115 |
| **OVERALL (MICRO)** | — | **76** | **0.6250** | **0.7895** | **0.6977** | — |
| **OVERALL (MACRO)** | — | — | **0.4715** | **0.6385** | **0.5253** | — |

