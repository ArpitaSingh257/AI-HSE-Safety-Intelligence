# OILPS Human Annotation Protocol Audit & Readiness Verification
**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Audit Focus:** Verification of human annotation guidelines, contextual Energy-Barrier framework, reference examples, quality control procedures, and dataset safety.
**Date:** 2026-08-30 (Rev 2 — Contextual SIF Framework)

---

## 1. Executive Protocol Audit & Compliance Checklist

| Protocol Requirement | Compliance Status | Evidence & Verification Detail |
| :--- | :--- | :--- |
| **Comprehensive SOP Created** | **VERIFIED** | [`knowledge/OILPS_HUMAN_ANNOTATION_GUIDE.md`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/knowledge/OILPS_HUMAN_ANNOTATION_GUIDE.md) contains the complete operational workflow. |
| **Contextual Energy + Barrier Framework** | **VERIFIED** | Enforces SIF potential based on holistic evaluation of **Hazardous Energy + Worker Exposure + Critical Barrier Failure + Credible Catastrophic Escalation**. Explicitly establishes that numerical values are contextual examples, NOT rigid SIF boundaries. |
| **No Numerical Threshold Fallacy** | **VERIFIED** | Explicitly prohibits automatic `SIF = 1` from numbers alone, and prohibits automatic `SIF = 0` from the absence of numbers. |
| **Confidence & Rationale Rules** | **VERIFIED** | Mandatory structured rationale (`Energy | Exposure | Barrier Failure | Escalation`) and 3-tier confidence criteria (`HIGH`, `MEDIUM`, `LOW`). |
| **Official 9 IOGP LSR Schema** | **VERIFIED** | Restricted strictly to the 9 official IOGP rules with candidate suggestions kept as non-ground-truth suggestions. |
| **Precursor Entity Decoupling** | **VERIFIED** | Strict decoupling of `barrier` (defense) vs `barrier_failure` (mode), and `hazard` vs actual injury outcome. |
| **10 Realistic Domain Examples** | **VERIFIED** | 10 end-to-end Oil & Gas incident walkthroughs spanning drilling, pressure, height, hot work, confined space, transport, and low-energy non-SIF baselines. |
| **Double-Review QA Procedure** | **VERIFIED** | Defined 20% double-annotation sample, Cohen's Kappa threshold ($>0.85$), and formal adjudication dispute logging. |
| **Zero Auto-Annotation Check** | **VERIFIED** | All 600 records in `osha_annotation_sample_600.csv` have blank `human_*` fields with `annotation_status = PENDING_HUMAN_REVIEW`. |
| **Zero Model Training Check** | **VERIFIED** | No machine learning / NLP models have been trained or instantiated. |
| **Master Dataset Protection** | **VERIFIED** | The 4,529-record master corpus (`oilps_unified_deduped.csv` and `oilps_annotation.csv`) remains 100% intact and unmodified. |

---

## 2. Review of Reference Annotation Examples Across Strata

| Example # | Domain Activity & Hazard Context | True SIF Potential | Primary Life-Saving Rule | Key Barrier Breakdown |
| :--- | :--- | :--- | :--- | :--- |
| **Ex 1** | Rig floor casing pickup (Suspended heavy load) | **`1` (SIF)** | `Safe Mechanical Lifting` | Tugger operated without signal; red zone breached |
| **Ex 2** | Pipeline hydrotesting (High-pressure test plug) | **`1` (SIF)** | `Energy Isolation` | Fitting tightened while under pressure |
| **Ex 3** | Scaffolding dismantling on column (Elevated deck)| **`1` (SIF)** | `Working at Height` | Harness lanyard unclipped during transition |
| **Ex 4** | Torch cutting on crude storage tank | **`1` (SIF)** | `Hot Work` | 0% LEL unverified; open drain nozzle unsealed |
| **Ex 5** | Production separator sludge removal | **`1` (SIF)** | `Confined Space` | Entered without verifying safe O2 levels (>19.5%) |
| **Ex 6** | Crude oil tanker highway transport | **`1` (SIF)** | `Driving` | Excessive speed on wet unpaved road shoulder |
| **Ex 7** | MCC electrical breaker troubleshooting | **`1` (SIF)** | `Energy Isolation` | Live circuit worked on without LOTO isolation |
| **Ex 8** | Walking across parking lot (slip on ice) | **`0` (Non-SIF)** | `None` | Low kinetic energy; zero fatal/life-altering potential |
| **Ex 9** | Sorting parts in warehouse (tool drawer pinch) | **`0` (Non-SIF)** | `None` | Manually closed drawer; minor localized pinch |
| **Ex 10** | Perimeter fence clearing (wasp sting) | **`0` (Non-SIF)** | `None` | Isolated biological sting; no systemic collapse |

---

## 3. Human Review Operational Readiness

With the contextual energy-barrier framework formalized and numerical threshold boundaries clarified as non-rigid indicators, human annotators can now evaluate [`ai-service/datasets/annotation/osha_annotation_sample_600.csv`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/datasets/annotation/osha_annotation_sample_600.csv) according to [`knowledge/OILPS_HUMAN_ANNOTATION_GUIDE.md`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/knowledge/OILPS_HUMAN_ANNOTATION_GUIDE.md).
