# OILPS Final Data Integrity & Precursor Provenance Audit
**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Audit Focus:** Granular field-by-field provenance audit across the 300 IOGP records and 4,229 OSHA records.
**Date:** 2026-08-30

---

## 1. Granular Precursor Provenance Audit (300 IOGP Records)

We performed a strict audit of the 300 IOGP records to determine whether each precursor field is **explicitly present as a labeled field (`SOURCE_GROUNDED`)**, **inferred/normalized from source sections (`DERIVED_FROM_SOURCE`)**, **human verified (`HUMAN_VERIFIED`)**, or **unannotated (`UNANNOTATED`)**:

| Precursor Field | `SOURCE_GROUNDED` | `DERIVED_FROM_SOURCE` | `HUMAN_VERIFIED` | `UNANNOTATED` | Provenance Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`verified_activity`** | **`300`** | `0` | `0` | `0` | Explicitly present under the labeled header `ACTIVITY:` in both HPE (pp. 5–91) and SPI (pp. 5–152). |
| **`verified_hazard`** | **`0`** | **`300`** | `0` | `0` | IOGP reports do NOT contain a labeled `HAZARD:` field. Physical energy hazards (*85 barg gas*, *33 kV live power*, *1.8-ton drill pipe*) are derived from `CAUSE:`, `POINT OF RELEASE:`, and narrative text. |
| **`verified_barrier`** | **`0`** | **`300`** | `0` | `0` | IOGP reports identify failure categories, not standalone intended barriers. The positive barrier (*Double Block & Bleed*, *5-point Safety Harness*) is derived from control context. |
| **`verified_barrier_failure`**| **`190`** | **`110`** | `0` | `0` | Explicitly present under the labeled section `BARRIERS: Hardware/Human Barrier Failures:...` in SPI Tier 1 (190 records); derived from `WHAT WENT WRONG:` and `CAUSAL FACTORS:` in HPE/Fatal (110 records). |
| **`verified_potential_consequence`**| **`13`** | **`287`** | `0` | `0` | Explicitly present with fatal coroner/HSE findings in `IOGP_FATAL` (13 records); derived as credible worst-case potential from HiPo/LOPC classifications in HPE (97) and SPI (190). |

---

## 2. Complete Corpus Precursor Provenance Summary (4,529 Total Records)

| Precursor Field | `SOURCE_GROUNDED` | `DERIVED_FROM_SOURCE` | `HUMAN_VERIFIED` | `UNANNOTATED` | Total Records |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`verified_activity`** | **300** (IOGP) | 0 | 0 | **4,229** (OSHA) | 4,529 |
| **`verified_hazard`** | **0** | **300** (IOGP) | 0 | **4,229** (OSHA) | 4,529 |
| **`verified_barrier`** | **0** | **300** (IOGP) | 0 | **4,229** (OSHA) | 4,529 |
| **`verified_barrier_failure`** | **190** (IOGP SPI) | **110** (IOGP HPE/Fatal) | 0 | **4,229** (OSHA) | 4,529 |
| **`verified_potential_consequence`** | **13** (IOGP Fatal) | **287** (IOGP HPE/SPI) | 0 | **4,229** (OSHA) | 4,529 |

---

## 3. Separation of Mapped OSHA Regulatory Metadata

To eliminate any ambiguity between genuine verified entities and mapped government codes:
- **`mapped_osha_source_hazard`**: Retains the raw OSHA `SourceTitle` regulatory taxonomy (e.g. *'Valves, nozzles'*, *'Hoisting accessories, n.e.c.'*).
- **`mapped_osha_actual_injury_outcome`**: Retains the raw OSHA `NatureTitle` (e.g. *'Fractures'*, *'Amputations'*), making clear that this is the **actual historical physical injury**, NOT a SIF potential consequence.

---

## 4. Formal Answers to Core Questions

### A. Is the current dataset genuinely source-grounded?
**YES.** 100% of the 4,529 incident narratives, dates, locations, employers, and severity indicators are authentic, non-fabricated text extracted directly from official IOGP reports and OSHA regulatory inspection records.

### B. Which fields are truly source-grounded?
1. **`narrative`** (100% genuine source text across all 4,529 records).
2. **`verified_sif_label = 1` for IOGP_HPE & IOGP_FATAL (110 records)** (`SOURCE_GROUNDED`).
3. **`verified_primary_lsr` & `verified_secondary_lsr` for IOGP (300 records)**.
4. **`verified_activity` for IOGP (300 records)**.
5. **`verified_barrier_failure` for IOGP SPI (190 records)**.
6. **`verified_potential_consequence` for IOGP Fatal (13 records)**.

### C. Which fields are derived from source text?
1. **`verified_sif_label = 1` for IOGP_SPI (190 records)** (`DERIVED_SOURCE_RULE` Tier 1 Process Safety releases).
2. **`verified_hazard` for IOGP (300 records)** (Derived from release points and cause text).
3. **`verified_barrier` for IOGP (300 records)** (Derived from control context).
4. **`verified_barrier_failure` for IOGP HPE (97 records) & Fatal (13 records)**.
5. **`verified_potential_consequence` for IOGP HPE (97 records) & SPI (190 records)**.

### D. Which fields require human annotation?
For all 4,229 OSHA records:
1. **`verified_sif_label`** (1 vs 0 under Energy-Barrier rubric).
2. **`verified_primary_lsr` & `verified_secondary_lsr`** (Confirming or correcting candidate suggestions).
3. **`verified_activity`, `verified_hazard`, `verified_barrier`, `verified_barrier_failure`, `verified_potential_consequence`** (Annotating explicit text spans).

### E. Is the dataset ready for creating the 600-record OSHA annotation sample?
**YES.** With the field-level provenance strictly categorized across all 4 types (`SOURCE_GROUNDED`, `DERIVED_FROM_SOURCE`, `HUMAN_VERIFIED`, `UNANNOTATED`), the dataset is 100% ready for exporting the 600-record stratified OSHA annotation sample.
