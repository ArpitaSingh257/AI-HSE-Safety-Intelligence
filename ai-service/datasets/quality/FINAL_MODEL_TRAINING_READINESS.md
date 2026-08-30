# FINAL MODEL-TRAINING READINESS REPORT

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Phase:** Stage 2 Completion — Final Model-Ready Dataset Construction & Leakage Audit
**Date:** 2026-08-30

---

## 1. SIF Classification Training Corpus (`sif_labeled.csv`)

- **Total SIF Labeled Records:** **896 records**
- **SIF = 1 (Positive):** **664 records** (74.11%)
- **SIF = 0 (Negative):** **232 records** (25.89%)
- **UNKNOWN Excluded:** **4 records** (Clean binary dataset without uncertain noise)

### SIF Source & Provenance Breakdown:

| Source Tag | Record Count | SIF Label Type | SIF Label Distribution |
| :--- | :--- | :--- | :--- |
| **`IOGP_HPE`** | 97 | `SOURCE_GROUNDED` | 97 SIF-1 / 0 SIF-0 |
| **`IOGP_FATAL`** | 13 | `SOURCE_GROUNDED` | 13 SIF-1 / 0 SIF-0 |
| **`IOGP_SPI`** | 190 | `DERIVED_SOURCE_RULE` | 190 SIF-1 / 0 SIF-0 |
| **`OSHA (600 Sample)`** | 579 | `PROJECT_ANNOTATED_AI_ASSISTED` | 341 SIF-1 / 238 SIF-0 |
| **TOTAL** | **896** | — | **664 SIF-1 / 232 SIF-0** |

### SIF Split Distribution (70/15/15, Seed=42):

- **Train (`sif_train.csv`):** **627 records** (465 SIF-1 / 162 SIF-0)
- **Validation (`sif_val.csv`):** **135 records** (100 SIF-1 / 35 SIF-0)
- **Test (`sif_test.csv`):** **134 records** (99 SIF-1 / 35 SIF-0)

---

## 2. Life-Saving Rule (LSR) Multi-Label Corpus (`lsr_labeled.csv`)

- **Total LSR Labeled Records:** **900 records** (300 IOGP + 600 OSHA)
- **Single-Label Records (1 rule):** **318 records** (35.33%)
- **Multi-Label Records ($\ge 2$ rules):** **81 records** (9.00%)
- **Zero-Label Records (None):** **501 records** (55.67%)

### Frequency of Official 9 IOGP Rules Across Corpus:

| Official IOGP Life-Saving Rule | Total Activations | Dataset Coverage (%) | Class Balance Tier |
| :--- | :--- | :--- | :--- |
| **Bypassing Safety Controls** | **1** | 0.11% | Rare Class (<10%) |
| **Confined Space** | **13** | 1.44% | Rare Class (<10%) |
| **Driving** | **82** | 9.11% | Rare Class (<10%) |
| **Energy Isolation** | **104** | 11.56% | Medium Density (10-25%) |
| **Hot Work** | **86** | 9.56% | Rare Class (<10%) |
| **Line of Fire** | **29** | 3.22% | Rare Class (<10%) |
| **Safe Mechanical Lifting** | **90** | 10.00% | Rare Class (<10%) |
| **Toxic Gas / Hazardous Substance** | **13** | 1.44% | Rare Class (<10%) |
| **Working at Height** | **68** | 7.56% | Rare Class (<10%) |
| **None (No Rule Applicable)** | **501** | 55.67% | Negative Control Class |

### LSR Split Distribution (70/15/15, Seed=42):

- **Train (`lsr_train.csv`):** **629 records**
- **Validation (`lsr_val.csv`):** **133 records**
- **Test (`lsr_test.csv`):** **138 records**

---

## 3. Precursor Entity Extraction Corpus (`precursor_labeled.csv`)

- **Total Precursor Labeled Records:** **900 records** (300 IOGP + 600 OSHA)
- **Decoupled Entity Coverage:** 100% coverage across `activity`, `hazard`, `barrier`, `barrier_failure`, `potential_consequence`.
- **Decoupled Provenance:** Distinguishes `SOURCE_GROUNDED`, `DERIVED_FROM_SOURCE`, and `PROJECT_ANNOTATED_AI_ASSISTED` per field.

---

## 4. Target Leakage & Data Integrity Audit

### Strict Input Feature Policy for ML Classifiers:
> [!CAUTION]
> **TARGET LEAKAGE PREVENTION ENFORCED:**
> - **Permitted Model Input:** The raw unstructured `narrative` text column is the **ONLY primary input feature**.
> - **Excluded Leakage Fields:** `source`, `source_document`, `severity`, `mapped_osha_actual_injury_outcome`, `sif_label_provenance`, `human_sif_rationale`, `sampling_stratum`, and `candidate_*` columns are **STRIP-PROTECTED** and NEVER passed as predictive features into NLP models.

### Zero Cross-Split Contamination:
- All train, validation, and test splits have **0 record overlap** (mutually exclusive `record_id` sets).
- Deterministic `seed=42` ensures exact reproducibility across runs.

---

## 5. Final Readiness Assessment for Model Development

| Modeling Phase | Readiness Status | Baseline Recommendation |
| :--- | :--- | :--- |
| **1. SIF Binary Classification** | **100% READY** | Train TF-IDF + Calibrated Logistic Regression & Linear SVM (Platt scaling) on `sif_train.csv`. Evaluate on `sif_val.csv` & `sif_test.csv` (PR-AUC, SIF Recall, F1). |
| **2. LSR Multi-Label Classification** | **100% READY** | Train One-vs-Rest TF-IDF / Calibrated Logistic Classifiers across 9 IOGP rules on `lsr_train.csv`. Evaluate Micro/Macro F1. |
| **3. Precursor Information Extraction**| **100% READY** | Rule-assisted & semantic span extractors for Activity, Hazard, Barrier, Barrier Failure, and Potential Consequence. |
| **Remaining Blockers** | **NONE** | All model-ready CSVs, splits, and unit tests are in place. Ready for baseline model benchmarking upon approval. |
