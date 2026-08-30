# STAGE 7: LSR GRU + ATTENTION ROBUSTNESS OPTIMIZATION REPORT

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Execution Runtime:** `cuda` (Tesla T4)
**Date:** 2026-08-30
**Random Seed:** `42` (Deterministic Reproducibility)

---

## 1. Executive Summary & Stage-over-Stage LSR Comparison

| Model Paradigm | Model Architecture | Micro-F1 | Macro-F1 | Weighted-F1 | Hamming Loss | Exact Match Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 3 Classical** | TF-IDF + OneVsRest Logistic | 0.6714 | 0.5339 | 0.6820 | 0.0370 | 71.74% |
| **Stage 4 Neural** | Baseline GRU + Attention | 0.6945 | 0.5620 | 0.7010 | 0.0352 | 73.18% |
| **Stage 5 Transformer** | DistilBERT Multi-Label | 0.3198 | 0.1823 | 0.3410 | 0.0650 | 52.17% |
| **Stage 6 Neural Opt** | LSR_Cfg2_LargeBi (GRU+Attn) | 0.6514 | 0.5597 | 0.6612 | 0.0491 | 63.04% |
| **Stage 7 Robust Neural** | **Stage7_Norm_Base (Enhanced Attention)** | **0.7020** | **0.5774** | **0.7042** | **0.0362** | **71.74%** |

---

## 2. Per-Rule Thresholds & Held-Out Test Breakdown (9 IOGP Rules)

| Official IOGP Life-Saving Rule | Learned Threshold | Test Support | Test Precision | Test Recall | Test F1-Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Bypassing Safety Controls** | 0.50 | 0 | 0.0000 | 0.0000 | **0.0000** |
| **Confined Space** | 0.50 | 2 | 0.5000 | 0.5000 | **0.5000** |
| **Driving** | 0.25 | 15 | 0.9286 | 0.8667 | **0.8966** |
| **Energy Isolation** | 0.30 | 16 | 0.5882 | 0.6250 | **0.6061** |
| **Hot Work** | 0.45 | 13 | 0.9167 | 0.8462 | **0.8800** |
| **Line of Fire** | 0.20 | 5 | 0.2500 | 0.2000 | **0.2222** |
| **Safe Mechanical Lifting** | 0.20 | 14 | 0.8182 | 0.6429 | **0.7200** |
| **Toxic Gas / Hazardous Substance** | 0.50 | 2 | 0.6667 | 1.0000 | **0.8000** |
| **Working at Height** | 0.25 | 9 | 0.5000 | 0.6667 | **0.5714** |
| **OVERALL (MICRO)** | — | **76** | **0.7067** | **0.6974** | **0.7020** |
| **OVERALL (MACRO)** | — | — | **0.5743** | **0.5941** | **0.5774** |

---

## 3. Key Findings & Architectural Decision

1. **Did Stage 7 improve over Stage 6?**
   - **YES.** Smooth class weighting (square-root scaling) combined with LayerNorm and Scaled-Dot-Product Attention stabilized gradient flow, boosting Micro-F1 from 0.6514 to **0.7020** and reducing Hamming Loss from 0.0491 to **0.0362**.
2. **Production Candidate Retention:**
   - **Champion SIF Model:** Stage 6 `SIF_Cfg3_MidBi` (Test Recall = 96.97%, F1 = 0.9231, PR-AUC = 0.9715).
   - **Champion LSR Model:** Stage 7 `Stage7_Norm_Base` (Micro-F1 = 0.7020, Exact Match = 71.74%).
