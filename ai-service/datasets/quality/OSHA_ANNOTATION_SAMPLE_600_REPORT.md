# OSHA 600-Record Human-Annotation Sample Report

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Sample Purpose:** Dedicated, reproducible stratified sample of 600 OSHA records exclusively for human domain annotation.
**Random Seed:** `42` (Deterministic and 100% reproducible)
**Master Source:** `datasets/annotation/oilps_annotation.csv` (4,229 OSHA records)
**Output Target:** `datasets/annotation/osha_annotation_sample_600.csv`

---

## 1. Executive Summary & Verification Check

| Integrity Requirement | Status | Verification Detail |
| :--- | :--- | :--- |
| **Exact Sample Size** | **Passed** | Exactly **600 records** |
| **Record Uniqueness** | **Passed** | **600 unique `record_id`s** (0 duplicates) |
| **Source Purity** | **Passed** | 100% `source = OSHA` (0 IOGP records included) |
| **Corpus Origin** | **Passed** | All 600 records exist in the 4,229 OSHA master dataset |
| **Human Fields Blank** | **Passed** | 100% of `human_*` fields are blank (0 fabricated labels) |
| **Status Setting** | **Passed** | 100% set to `annotation_status = PENDING_HUMAN_REVIEW` |
| **Candidate Distinction** | **Passed** | Candidate LSRs preserved as suggestions only |
| **Deterministic Seed** | **Passed** | `random.seed(42)` produces identical sample on every run |

## 2. Stratification Breakdown & Representation

The 600 records were sampled across 6 domain strata to ensure maximum operational diversity without pre-determining SIF labels:

| Sampling Stratum | Sample Count | Sample (%) | Operational Scope |
| :--- | :--- | :--- | :--- |
| **Stratum_A_Drilling_Heavy_Mechanical** | **133** | 22.17% | Drilling rig floor, casing, tubulars, BOP, drawworks, tongs |
| **Stratum_B_Pressure_Flammable_Chemical_H2S** | **130** | 21.67% | High pressure releases, flammable gases, flash fires, H2S, acids |
| **Stratum_C_Height_Lifting_Dropped_Objects** | **113** | 18.83% | Mobile cranes, rigging, slings, suspended loads, scaffolding, falls >1.8m |
| **Stratum_F_LowEnergy_Ergonomic_MinorInjury** | **71** | 11.83% | Slips on same level, lifting boxes, insect stings, tool drawer pinches |
| **Stratum_D_ConfinedSpace_HotWork_Isolation** | **63** | 10.5% | Vessel entry, tanks, separators, welding/cutting, LOTO, electrical arc |
| **Stratum_E_Vehicle_Transport** | **62** | 10.33% | Heavy haul trucks, tanker rollovers, oilfield access roads, collisions |
| **Stratum_G_General_Oilfield_Operations** | **28** | 4.67% | General well pad maintenance and miscellaneous operations |

## 3. Industry / Operational Function Distribution

| Industry Description | Sample Count | Percentage |
| :--- | :--- | :--- |
| Support Activities for Oil and Gas Operations | 269 | 44.83% |
| Oil and Gas Pipeline Construction | 74 | 12.33% |
| Oil & Gas / Energy Related | 63 | 10.5% |
| Drilling Oil and Gas Wells | 63 | 10.5% |
| Petroleum Refineries | 28 | 4.67% |
| Asphalt Paving Mixture and Block Manufacturing | 17 | 2.83% |
| Petroleum Bulk Stations and Terminals | 15 | 2.5% |
| Petroleum and Petroleum Products Merchant Wholesalers | 14 | 2.33% |
| Crude Petroleum and Natural Gas Extraction | 13 | 2.17% |
| Petroleum Products Manufacturing | 8 | 1.33% |
| All Other Petroleum and Coal Products Manufacturing | 8 | 1.33% |
| Natural Gas Liquid Extraction | 7 | 1.17% |
| Petroleum Lubricating Oil and Grease Manufacturing | 7 | 1.17% |
| All Other Pipeline Transportation | 3 | 0.5% |
| Pipeline Transportation of Natural Gas | 3 | 0.5% |
| Pipeline Transportation of Crude Oil | 2 | 0.33% |
| Natural Gas Extraction | 2 | 0.33% |
| Crude Petroleum Extraction | 2 | 0.33% |
| Oil and Gas Extraction (General) | 1 | 0.17% |
| Support Activities for Oil and Gas | 1 | 0.17% |

## 4. Candidate Life-Saving Rule (LSR) Suggestions Distribution

> [!NOTE]
> These candidate rules are **heuristic suggestions** to assist human annotators and are **NOT ground truth**.

| Candidate Primary Rule | Suggested Count | Percentage |
| :--- | :--- | :--- |
| None suggested | 281 | 46.83% |
| Safe Mechanical Lifting | 74 | 12.33% |
| Hot Work | 64 | 10.67% |
| Working at Height | 61 | 10.17% |
| Driving | 50 | 8.33% |
| Energy Isolation | 27 | 4.5% |
| Line of Fire | 26 | 4.33% |
| Toxic Gas / Hazardous Substance | 12 | 2.0% |
| Confined Space | 5 | 0.83% |

## 5. OSHA Severity & Outcome Distribution (Context Only)

> [!IMPORTANT]
> Actual injury outcomes do **NOT** determine SIF potential. They are preserved solely as historical context.

| Stated OSHA Severity Indicator | Sample Count | Percentage |
| :--- | :--- | :--- |
| Hospitalization | 471 | 78.5% |
| Amputation | 113 | 18.83% |
| Non-Fatal Injury | 15 | 2.5% |
| Loss of Eye | 1 | 0.17% |

## 6. Scientific Sampling Integrity Confirmation

1. **Zero Pre-Determined SIF Labels:** No SIF potential labels (`1` or `0`) were assigned to any of the 600 sampled records.
2. **Zero Pre-Determined Human Fields:** All `human_*` fields (`human_sif_label`, `human_sif_confidence`, `human_sif_rationale`, `human_primary_lsr`, `human_activity`, `human_hazard`, `human_barrier`, `human_barrier_failure`, `human_potential_consequence`) are 100% blank.
3. **Complete Provenance:** Every record retains its unique `record_id`, original OSHA report ID, event date, employer, location, and full unmodified narrative text.
4. **Exact Reproducibility:** Running `python ai-service/scripts/create_annotation_sample.py` with `seed=42` deterministically reproduces this exact 600-record sample.
