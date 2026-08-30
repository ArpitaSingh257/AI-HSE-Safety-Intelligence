# OILPS Final Annotation Readiness & Pre-Training Audit Report
**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Phase:** Final Annotation Audit & Pipeline Readiness Assessment
**Date:** 2026-08-30 (Updated with Strict SIF Provenance Grounding)

---

## 1. Executive Summary & Strict Provenance SIF Breakdown

| SIF Classification Provenance | Count | Proportion | Exact Source Justification & Handling |
| :--- | :--- | :--- | :--- |
| **Explicitly Source-Grounded SIF Positives** | **110** | **2.43%** | **`IOGP_HPE` (97)** + **`IOGP_FATAL` (13)**.<br>Directly established by official IOGP standards (HiPo definition: credible fatality/disabling injury potential; Fatal incident outcome). `sif_label_type = 'SOURCE_GROUNDED'`. |
| **Derived SIF Positives** | **190** | **4.20%** | **`IOGP_SPI` (190)**.<br>Reported by IOGP as Tier 1 Process Safety Events (LOPC). SIF equivalence is derived via OILPS rule `RULE_SPI_TIER1_SIF` based on high-energy chemical/pressure barrier failures. `sif_label_type = 'DERIVED_SOURCE_RULE'`. |
| **Records Requiring Review** | **4,229** | **93.38%** | **`OSHA` (4,229)**.<br>Workplace incident filings with intact injury/severity data. Kept as `REVIEW_REQUIRED` (not assuming `Hospitalization = SIF`). `sif_label_type = 'UNANNOTATED'`. |
| **Verified SIF Negatives** | **0** | **0.00%** | To be obtained through the 600-record stratified OSHA sampling review. |
| **TOTAL CORPUS** | **4,529** | **100.00%** | **ML-Ready Corpus** |

---

## 2. Source-by-Source Breakdown

| Originating Source | Source Document | Record Count | SIF Label Type | LSR Label Type |
| :--- | :--- | :--- | :--- | :--- |
| **`IOGP_HPE`** | `IAOGP - High Potential Event Reports.pdf` | **97** | **`SOURCE_GROUNDED`** (`SIF = 1`) | **`SOURCE_GROUNDED`** |
| **`IOGP_FATAL`** | `IAOGP - Safety performance indicators.pdf` | **13** | **`SOURCE_GROUNDED`** (`SIF = 1`) | **`SOURCE_GROUNDED`** |
| **`IOGP_SPI`** | `IAOGP - Safety performance indicators.pdf` | **190** | **`DERIVED_SOURCE_RULE`** (`SIF = 1`) | **`SOURCE_GROUNDED`** |
| **`OSHA`** | `January2015toNovember2025.csv` | **4,229** | **`UNANNOTATED`** (`REVIEW_REQUIRED`) | **`CANDIDATE_HEURISTIC`** |
| **TOTAL** | **All 5 Sources** | **4,529** | — | — |

---

## 3. Life-Saving Rule (LSR) Label Audit

- **Source-Grounded LSR Records:** **300 records** (100% of IOGP records with official primary/secondary rules).
- **Multi-Label Ground-Truth Cases ($\ge 2$ LSRs):** **73 records** (e.g. *Safe Mechanical Lifting* + *Line of Fire*; *Energy Isolation* + *Line of Fire*).
- **Candidate Suggestions:** **4,229 OSHA records** populated with `candidate_primary_lsr` and `candidate_secondary_lsr` for human review without claiming ground truth.

---

## 4. Precursor Annotation Coverage & Consistency

- **`activity`:** 300 source-grounded; 4,229 unannotated (high entity density in text).
- **`hazard`:** 300 source-grounded; 4,229 mapped from source energy metadata.
- **`barrier` vs `barrier_failure` Decoupling:**
  - `barrier` = Intended protective control (e.g. *Double Block and Bleed Isolation*, *5-point Safety Harness*).
  - `barrier_failure` = Specific failure mechanism (e.g. *Bleed valve unverified before flange unbolting*, *Lanyard unclipped during transition*).
- **`potential_consequence`:** 300 verified; mapped from OSHA nature metadata.

---

## 5. Sampling Plan & Training Readiness Assessment

1. **Recommended Human Annotation Sample:** **600 stratified OSHA records** (yielding ~300 verified SIF-1 / ~300 verified SIF-0).
2. **Supervised SIF Training Readiness:** **Partially Ready.** High-quality positive anchors exist (110 source-grounded + 190 derived), but non-biased binary supervised training requires the 600-sample negative class review.
3. **Supervised LSR Training Readiness:** **Ready for Semantic Embeddings / Few-Shot; Ready for Supervised Classifiers upon sample verification.** All 9 official rules have ground-truth prototypes.
4. **Precursor Extraction Readiness:** **Ready for Rule-Assisted & Semantic Span Extraction.**

---

## 6. Exact Next Step

1. **Review and approve this final scientifically grounded audit.**
2. **Execute the Stratified Annotation Sample (600 records) or proceed to Stage 3: Baseline Classifier Benchmarking (TF-IDF + Calibrated Logistic Regression / Linear SVM) on the verified corpus.**
