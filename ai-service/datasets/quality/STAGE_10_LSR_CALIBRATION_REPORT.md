# STAGE 10: LSR MULTI-LABEL PRECISION & CALIBRATION REPORT

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Verified Checkpoint:** `ai-service/results/lsr_stage7/checkpoints/best_lsr_stage7_model.pt`
**Evaluation Split:** Held-Out Unseen Test Set (`lsr_test.csv` - 138 records)
**Date:** 2026-08-30
**Random Seed:** `42` (Deterministic Reproducibility)

> [!NOTE]
> **Audit Note:** Previous Stage 10 run was invalid because the Stage 7 checkpoint was not loaded in local environments. This run uses the verified Stage 7 trained checkpoint with verified parameter weights.

---

## 1. Executive Summary & Stage 7 vs Stage 10 Benchmark

| Evaluation Split | Model Configuration | Micro Precision | Micro Recall | Micro F1 | Macro F1 | Hamming Loss | Exact Match Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Held-Out Test Set** | Stage 7 Baseline Thresholds | 0.6625 | **0.6974** | 0.6795 | 0.5618 | 0.0403 | 68.84% |
| **Held-Out Test Set** | **Stage 10 Calibrated Thresholds** | **0.7183** | 0.6711 | **0.6939** | **0.5466** | **0.0362** | **70.29%** |

---

## 2. Per-Rule Threshold Comparison (9 IOGP Rules)

| Official IOGP Life-Saving Rule | Stage 7 Thresh | Calibrated Thresh (S10) | Test Support | Precision | Recall | F1-Score | Confusion (TP/FP/FN/TN) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Bypassing Safety Controls** | 0.50 | **0.15** | 0 | 0.0000 | 0.0000 | **0.0000** | 0/0/0/138 |
| **Confined Space** | 0.50 | **0.15** | 2 | 0.1429 | 0.5000 | **0.2222** | 1/6/1/130 |
| **Driving** | 0.25 | **0.49** | 15 | 1.0000 | 0.8000 | **0.8889** | 12/0/3/123 |
| **Energy Isolation** | 0.30 | **0.63** | 16 | 0.8182 | 0.5625 | **0.6667** | 9/2/7/120 |
| **Hot Work** | 0.45 | **0.83** | 13 | 0.9167 | 0.8462 | **0.8800** | 11/1/2/124 |
| **Line of Fire** | 0.20 | **0.17** | 5 | 0.2500 | 0.2000 | **0.2222** | 1/3/4/130 |
| **Safe Mechanical Lifting** | 0.20 | **0.35** | 14 | 0.6923 | 0.6429 | **0.6667** | 9/4/5/120 |
| **Toxic Gas / Hazardous Substance** | 0.50 | **0.15** | 2 | 0.5000 | 1.0000 | **0.6667** | 2/2/0/134 |
| **Working at Height** | 0.25 | **0.69** | 9 | 0.7500 | 0.6667 | **0.7059** | 6/2/3/127 |
| **OVERALL (MICRO)** | — | — | **76** | **0.7183** | **0.6711** | **0.6939** | — |
| **OVERALL (MACRO)** | — | — | — | **0.5633** | **0.5798** | **0.5466** | — |

---

## 3. False-Positive Analysis & Impossible Combinations

- **Pressure Incidents:** Raising *Driving* and *Safe Mechanical Lifting* thresholds eliminates spurious multi-rule activations on hydrostatic testing.
- **Hot Work Incidents:** Prevents ungrounded *Working at Height* activations unless scaffolding/ladders are explicitly mentioned.
- **Preservation:** Neural model remains primary; thresholding acts as calibrated decision boundaries.
