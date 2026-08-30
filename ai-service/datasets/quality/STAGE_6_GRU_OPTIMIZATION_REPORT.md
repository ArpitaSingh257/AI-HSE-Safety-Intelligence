# STAGE 6: GRU + ATTENTION OPTIMIZATION & BENCHMARK REPORT

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Execution Runtime:** `cuda` (Tesla T4)
**Date:** 2026-08-30
**Random Seed:** `42` (Deterministic Reproducibility)

---

## 1. Executive Summary & Master Cross-Stage Benchmark

### SIF Binary Classification Master Benchmark:

| Model Paradigm | Architecture | SIF Test F1 | SIF Recall (SIF=1) | SIF PR-AUC | SIF Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 3 Classical** | TF-IDF + Calibrated Linear SVM | 0.8683 | 89.90% | 0.9586 | 79.85% |
| **Stage 4 Neural** | Baseline GRU + Attention | 0.8750 | 91.92% | 0.9620 | 81.34% |
| **Stage 5 Transformer** | DistilBERT (Fine-Tuned) | 0.8942 | 93.94% | 0.9514 | 83.58% |
| **Stage 6 Optimized Neural** | **Optimized GRU + Attention** | **0.9231** | **96.97%** | **0.9715** | **88.06%** |

### LSR Multi-Label Classification Master Benchmark:

| Model Paradigm | Architecture | Micro-F1 | Macro-F1 | Hamming Loss | Exact Match Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 3 Classical** | TF-IDF + OneVsRest Logistic | 0.6714 | 0.5339 | 0.0370 | 0.7174 |
| **Stage 4 Neural** | Baseline GRU + Attention | 0.6945 | 0.5620 | 0.0352 | 0.7318 |
| **Stage 5 Transformer** | DistilBERT Multi-Label | 0.3198 | 0.1823 | 0.0650 | 0.5217 |
| **Stage 6 Optimized Neural** | **Optimized GRU + Attention (Per-Rule Thresh)** | **0.6514** | **0.5597** | **0.0491** | **63.04%** |

---

## 2. Optimization Grid Search Results (Validation Split)

| Task | Configuration Tag | Embed Dim | Hidden Dim | Dropout | Learning Rate | Best Validation F1 | Tuned Threshold / Metric |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SIF** | SIF_Cfg1_Base | 100 | 128 | 0.3 | 0.001 | **0.9495** (Recall: 94.0%) | Thresh = 0.50 |
| **SIF** | SIF_Cfg2_LargeBi | 200 | 256 | 0.3 | 0.0005 | **0.9286** (Recall: 91.0%) | Thresh = 0.30 |
| **SIF** | SIF_Cfg3_MidBi | 200 | 128 | 0.2 | 0.0005 | **0.9557** (Recall: 97.0%) | Thresh = 0.30 |
| **SIF** | SIF_Cfg4_RegBi | 100 | 128 | 0.5 | 0.0005 | **0.9215** (Recall: 88.0%) | Thresh = 0.35 |
| **SIF** | SIF_Cfg5_DeepBi | 200 | 256 | 0.2 | 0.0002 | **0.9223** (Recall: 89.0%) | Thresh = 0.35 |
| **LSR** | LSR_Cfg1_Base | 100 | 128 | 0.3 | 0.001 | **Micro-F1: 0.6714** | Macro-F1: 0.4596 |
| **LSR** | LSR_Cfg2_LargeBi | 200 | 256 | 0.3 | 0.0005 | **Micro-F1: 0.7287** | Macro-F1: 0.4876 |
| **LSR** | LSR_Cfg3_MidBi | 200 | 128 | 0.2 | 0.0005 | **Micro-F1: 0.6406** | Macro-F1: 0.4345 |
| **LSR** | LSR_Cfg4_RegBi | 100 | 128 | 0.4 | 0.0005 | **Micro-F1: 0.5605** | Macro-F1: 0.3982 |
| **LSR** | LSR_Cfg5_DeepBi | 200 | 256 | 0.2 | 0.0002 | **Micro-F1: 0.6122** | Macro-F1: 0.4304 |

---

## 3. Independent Per-Rule LSR Thresholds & Test Breakdown

| Official IOGP Life-Saving Rule | Learned Threshold | Test Support | Test Precision | Test Recall | Test F1-Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Bypassing Safety Controls** | 0.50 | 0 | 0.0000 | 0.0000 | **0.0000** |
| **Confined Space** | 0.50 | 2 | 1.0000 | 0.5000 | **0.6667** |
| **Driving** | 0.40 | 15 | 0.8125 | 0.8667 | **0.8387** |
| **Energy Isolation** | 0.70 | 16 | 0.7857 | 0.6875 | **0.7333** |
| **Hot Work** | 0.20 | 13 | 0.5238 | 0.8462 | **0.6471** |
| **Line of Fire** | 0.55 | 5 | 0.1429 | 0.2000 | **0.1667** |
| **Safe Mechanical Lifting** | 0.60 | 14 | 0.5789 | 0.7857 | **0.6667** |
| **Toxic Gas / Hazardous Substance** | 0.50 | 2 | 0.6667 | 1.0000 | **0.8000** |
| **Working at Height** | 0.35 | 9 | 0.3889 | 0.7778 | **0.5185** |
| **OVERALL (MICRO)** | — | **76** | **0.5758** | **0.7500** | **0.6514** |
| **OVERALL (MACRO)** | — | — | **0.5444** | **0.6293** | **0.5597** |

---

## 4. Google Colab GPU Execution Instructions

To run this optimization experiment on Google Colab with free T4 GPU acceleration:

```python
# 1. Check GPU
!nvidia-smi

# 2. Verify CUDA in PyTorch
import torch
print('CUDA Available:', torch.cuda.is_available())
print('Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')

# 3. Clone or Upload the repository
# %cd /content/AI-HSE-Safety-Intelligence

# 4. Run Stage 6 Optimization
!python ai-service/scripts/optimize_gru_attention.py

# 5. Run Verification Tests
!python ai-service/tests/test_gru_optimization.py

# 6. Zip and Download Results
!zip -r gru_optimization_results.zip ai-service/results/gru_optimization ai-service/datasets/quality/STAGE_6_GRU_OPTIMIZATION_REPORT.md
from google.colab import files
files.download('gru_optimization_results.zip')
```
