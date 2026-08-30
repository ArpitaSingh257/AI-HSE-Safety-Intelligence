# STAGE 9: PRODUCTION MODEL PACKAGING & INFERENCE PIPELINE REPORT

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence  
**Component:** AI/NLP Service Model Packaging & Production Inference System  
**Date:** 2026-08-30  
**Status:** Packaged, Verified, and Production-Ready for Backend API Integration  

---

## 1. Executive Summary & Packaged Champions

The OILPS AI Safety Intelligence Engine has finalized and packaged the top-performing champion architectures from the research and optimization phases into an isolated, reusable production inference pipeline (`ai-service/inference/`):

1. **SIF Precursor Binary Classifier:**
   - **Champion Architecture:** **`Stage 6 Bidirectional GRU + Softmax Sequence Attention (SIF_Cfg3_MidBi)`**
   - **Verified Performance on Held-Out Test Set:** **`96.97% SIF Recall`**, **`0.9231 F1-Score`**, **`0.9715 PR-AUC`**, with only 3 false negatives.
   - **Validation-Derived Decision Threshold:** **`0.30`** (Prioritizing high sensitivity on life-threatening precursors).
   - **Packaged Path:** `ai-service/models/sif/sif_model.pt`

2. **Life-Saving Rules (LSR) Multi-Label Classifier:**
   - **Champion Architecture:** **`Stage 7 Robust Bidirectional GRU + Scaled-Dot-Product Attention with LayerNorm (Stage7_Norm_Base)`**
   - **Verified Performance on Held-Out Test Set:** **`0.7020 Micro-F1`**, **`71.74% Exact Match Ratio`**, **`0.0362 Hamming Loss`**.
   - **Validation-Derived Decision Thresholds:** 9 independent per-rule thresholds (*Hot Work: 0.20, Working at Height: 0.35, Driving: 0.40, Confined Space: 0.50, Toxic Gas: 0.50, Bypassing Controls: 0.50, Line of Fire: 0.55, Safe Mechanical Lifting: 0.60, Energy Isolation: 0.70*).
   - **Packaged Path:** `ai-service/models/lsr/lsr_model.pt`

---

## 2. Directory Structure & Architecture

```text
ai-service/
├── models/
│   ├── sif/
│   │   ├── sif_model.pt               ── Stage 6 Champion PyTorch State Dict
│   │   ├── sif_vocab.json             ── Production Vocabulary (1,682 tokens)
│   │   └── sif_config.json            ── Embedding/Hidden dimensions & Threshold (0.30)
│   ├── lsr/
│   │   ├── lsr_model.pt               ── Stage 7 Champion PyTorch State Dict
│   │   ├── lsr_vocab.json             ── Production Vocabulary (1,682 tokens)
│   │   └── lsr_config.json            ── Architecture Config & 9 Per-Rule Thresholds
│   └── MODEL_MANIFEST.json            ── Reproducibility & Provenance Metadata
│
├── inference/
│   ├── __init__.py                    ── Package Exports
│   ├── preprocessing.py               ── Tokenization, Vocabulary Indexing, Padding
│   ├── sif_predictor.py               ── SIFPredictor (Standalone SIF Inference)
│   ├── lsr_predictor.py               ── LSRPredictor (Standalone 9-Rule Multi-Label Inference)
│   └── safety_pipeline.py             ── SafetyPipeline (Unified Single-Call Analysis Endpoint)
│
└── scripts/
    ├── package_final_models.py        ── Automated Packager & Manifest Generator
    └── run_inference_demo.py          ── Interactive Demonstration Script
```

---

## 3. Preprocessing & Device Compatibility

- **Tokenization & Cleaning:** Case-folding and alphanumeric token extraction (`clean_and_tokenize`), handling punctuation, whitespace, and special characters cleanly.
- **Out-of-Vocabulary (OOV) Protection:** Any unseen domain token is mapped to `<UNK>` (Index 1) without crashing.
- **Fixed Max Sequence Length:** 120 tokens (capturing 95% of full incident reports with zero truncation of core hazard descriptions).
- **CPU / CUDA Auto-Detection:** Automatically executes on CUDA GPU if present, with transparent fallback to local CPU.

---

## 4. Example End-to-End Inference Payload

Calling `pipeline.analyze_incident(narrative)` produces a structured JSON output:

```json
{
  "narrative": "During hydrostatic testing of the 6-inch high pressure discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting while the line remained pressurized. The bleeder plug ruptured and struck the worker in the chest.",
  "risk_tier": "CRITICAL_SIF_PRECURSOR",
  "sif": {
    "label": 1,
    "probability": 0.9842,
    "threshold": 0.30,
    "model": "optimized_bigru_attention",
    "salient_tokens": [
      {"token": "pressure", "weight": 0.2410},
      {"token": "ruptured", "weight": 0.1980},
      {"token": "hydrostatic", "weight": 0.1740},
      {"token": "bleeder", "weight": 0.1420},
      {"token": "struck", "weight": 0.1150}
    ]
  },
  "life_saving_rules": {
    "predicted_rules": [
      "Energy Isolation",
      "Line of Fire"
    ],
    "probabilities": {
      "Energy Isolation": 0.8920,
      "Line of Fire": 0.7410,
      "Hot Work": 0.0410,
      "Safe Mechanical Lifting": 0.0820,
      "Working at Height": 0.0120,
      "Driving": 0.0030,
      "Toxic Gas / Hazardous Substance": 0.0620,
      "Confined Space": 0.0050,
      "Bypassing Safety Controls": 0.1240
    },
    "thresholds": {
      "Energy Isolation": 0.70,
      "Line of Fire": 0.55,
      "Hot Work": 0.20,
      "Safe Mechanical Lifting": 0.60,
      "Working at Height": 0.35,
      "Driving": 0.40,
      "Toxic Gas / Hazardous Substance": 0.50,
      "Confined Space": 0.50,
      "Bypassing Safety Controls": 0.50
    },
    "salient_tokens": [
      {"token": "pressurized", "weight": 0.2310},
      {"token": "fitting", "weight": 0.1850},
      {"token": "bleeder", "weight": 0.1540}
    ]
  }
}
```

---

## 5. Scope Boundaries & Important Notes

- **Task-Specific Domain Models:** These models are trained strictly on verified IOGP & contextual OSHA energy datasets; they are **NOT** generic off-the-shelf transformers.
- **Precursor Extraction Status:** Precursor fields remain structured text attributes; sequence token NER is deferred pending character-offset annotation.
- **MERN Integration Boundary:** The AI inference system is fully standalone and ready for backend API integration in **Stage 10**.
