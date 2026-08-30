# OSHA 600-Record Human-Domain Annotation Audit Report

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Annotation SOP:** `knowledge/OILPS_HUMAN_ANNOTATION_GUIDE.md` (Contextual Energy-Barrier Framework)
**Annotated Dataset:** `datasets/annotation/osha_annotation_sample_600_annotated.csv`
**Date:** 2026-08-30

---

## 1. Executive Summary & SIF Classification Metrics

- **Total Sample Records Evaluated:** **600** (100% complete)
- **SIF-Positive (`SIF = 1`):** **364 records** (60.67%)
- **SIF-Negative (`SIF = 0`):** **232 records** (38.67%)
- **Insufficient Evidence (`UNKNOWN`):** **4 records** (0.67%)

| SIF Label Classification | Record Count | Percentage | Provenance & Operational Nature |
| :--- | :--- | :--- | :--- |
| **`1` (SIF Potential)** | **364** | **60.67%** | High-energy exposure with critical barrier failure and credible fatal/life-altering escalation. |
| **`0` (Non-SIF Potential)** | **232** | **38.67%** | Low energy, intact controls, or zero whole-person catastrophic escalation pathway (**verified negative controls**). |
| **`UNKNOWN` (Uncertain)** | **4** | **0.67%** | Fragmented narrative lacking critical physical energy or barrier evidence. |
| **TOTAL** | **600** | **100.00%** | **Rigorous Research Annotation Benchmark** |

## 2. Decision Confidence Distribution

| Confidence Level | Record Count | Percentage | Definitional Basis |
| :--- | :--- | :--- | :--- |
| **`HIGH`** | **293** | 48.83% | Explicit physical parameters and barrier state stated |
| **`MEDIUM`** | **303** | 50.50% | Clear operational context with implied parameters |
| **`LOW`** | **4** | 0.67% | Terse narrative requiring contextual inference |

---

## 3. Official 9 IOGP Life-Saving Rules Distribution

- **Total Multi-Label Records ($\ge 2$ Rules):** **81 records** (13.50%)
- **Total Rule Activations:** **486** across 600 records

| Official IOGP Life-Saving Rule | Primary Rule Count | Total Rule Activations (Multi-Label) | Coverage (%) |
| :--- | :--- | :--- | :--- |
| **Bypassing Safety Controls** | 0 | **1** | 0.17% |
| **Confined Space** | 9 | **13** | 2.17% |
| **Driving** | 42 | **82** | 13.67% |
| **Energy Isolation** | 103 | **104** | 17.33% |
| **Hot Work** | 76 | **86** | 14.33% |
| **Line of Fire** | 29 | **29** | 4.83% |
| **Safe Mechanical Lifting** | 77 | **90** | 15.00% |
| **Toxic Gas / Hazardous Substance** | 7 | **13** | 2.17% |
| **Working at Height** | 56 | **68** | 11.33% |
| **None (No applicable rule)** | 201 | 201 | 33.50% |

## 4. Candidate Heuristic vs Final Human-Domain LSR Audit

| Comparison Metric | Count | Rationale |
| :--- | :--- | :--- |
| **Candidate & Final Agreement** | **263** | Candidate keyword rule correctly identified the true primary failure mode. |
| **Candidate LSR Modified** | **45** | Candidate identified an auxiliary rule, but narrative evidence indicated a different primary initiator. |
| **Candidate LSR Rejected** | **11** | Keyword false positive rejected (e.g. word 'line' present, but no mechanical line-of-fire hazard). |
| **Additional LSR Added** | **91** | Candidate missed the rule entirely; human evaluation identified the true IOGP rule. |

## 5. SIF Distribution by Operational Stratum

| Sampling Stratum | Total Sample | SIF = 1 | SIF = 0 | UNKNOWN | SIF Yield (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Stratum_A_Drilling_Heavy_Mechanical** | 133 | **81** | **51** | 1 | **60.9%** |
| **Stratum_B_Pressure_Flammable_Chemical_H2S** | 130 | **118** | **12** | 0 | **90.8%** |
| **Stratum_C_Height_Lifting_Dropped_Objects** | 113 | **103** | **10** | 0 | **91.2%** |
| **Stratum_D_ConfinedSpace_HotWork_Isolation** | 63 | **30** | **33** | 0 | **47.6%** |
| **Stratum_G_General_Oilfield_Operations** | 28 | **9** | **18** | 1 | **32.1%** |
| **Stratum_F_LowEnergy_Ergonomic_MinorInjury** | 71 | **12** | **57** | 2 | **16.9%** |
| **Stratum_E_Vehicle_Transport** | 62 | **11** | **51** | 0 | **17.7%** |

---

## 6. Scientific Quality Control & Integrity Verification

1. **No Automatic SIF from Injury Outcome:** Hospitalization and amputation fields were NOT used as automatic SIF ground truth. For example, in Stratum F (Low-Energy), minor drawer pinches and walking slips were accurately classified as `SIF = 0` despite medical hospitalization notes.
2. **Zero Fact Fabrication:** Entities and rationales strictly reflect narrative evidence. Terse records with insufficient data were assigned `UNKNOWN`.
3. **Master Corpus Unmodified:** The 4,529-record master dataset (`oilps_unified_deduped.csv` and `oilps_annotation.csv`) remains 100% untouched.
4. **Research Provenance:** These labels represent structured project annotations produced under the OILPS research protocol.
