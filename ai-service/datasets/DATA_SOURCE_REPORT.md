# OILPS Dataset Source & Data Provenance Report
**Problem Statement:** SIH26165 — Oil India Limited (AI/NLP Precursor Engine)
**Report Date:** 2026-08-30
**Scope:** Strict AI/NLP Dataset Preparation and Source Provenance Verification

---

## 1. Overview & Data Integrity Principles

In compliance with the SIH26165 problem statement and strict safety research guidelines:
- **No Fabrication:** No fictional or unverified "OIL dataset" is fabricated.
- **Traceable Provenance:** Every single extracted record retains its original document, page/record identifier, and source tag.
- **Dual-Domain Corpus:** The dataset combines international upstream/midstream benchmarks from the International Association of Oil & Gas Producers (**IOGP**) with extensive empirical operational incident records from the Occupational Safety and Health Administration (**OSHA**) filtered for energy and petroleum operations.

---

## 2. Comprehensive Inventory of Source Documents

### Source 1: IOGP High Potential Event Reports
- **Filename:** `resources/IAOGP - High Potential Event Reports.pdf`
- **Source Type:** Industry Safety Association Benchmark & Case Narrative Compilation (PDF).
- **Source Tag:** `IOGP_HPE`
- **Data Nature:** Incident-level case studies detailing high potential near-misses and precursor incidents where fatal consequences were narrowly avoided.
- **Key Fields Available:**
  - Incident Narrative / What Happened
  - What Went Wrong / Causal Factors
  - Corrective Actions / Lessons Learned
  - Associated Operational Activity
  - Applicable IOGP Life-Saving Rules
- **Relevant OILPS Tasks:**
  - SIF-Potential Classification (Ground-truth SIF = 1 due to high-energy barrier failure)
  - Life-Saving Rule Multi-Label Detection
  - Barrier & Failure Mode Extraction
  - Precursor Pattern Discovery
- **Limitations:** Limited sample size relative to tabular government datasets; narratives focus on severe/escalated scenarios.
- **Extraction Method:** Section-delimited PDF extraction parsing incident narratives, causal headers, and corrective action blocks.

---

### Source 2: IOGP Safety Performance Indicators / Fatal Incident Reports
- **Filename:** `resources/IAOGP - Safety performance indicators.pdf`
- **Source Type:** Industry Safety Association Global Report & Fatal Incident Case Registry (PDF).
- **Source Tag:** `IOGP_FATAL`
- **Data Nature:** Global upstream fatal incident descriptions, fatal event mechanisms, activity breakdowns, and causal factor distributions.
- **Key Fields Available:**
  - Fatal Event Description & Mechanism
  - Operational Function / Activity (Drilling, Production, Rig Move, Maintenance)
  - Direct Cause / Failure Mode
  - Potential Consequence (Fatal / Catastrophic)
  - Primary Life-Saving Rule breach
- **Relevant OILPS Tasks:**
  - Fatal-event language modeling and consequence mapping
  - Precursor severity weighting and risk intelligence
  - Multi-label Life-Saving Rule mapping
- **Limitations:** Fatal incident narratives are concise summaries focused on actual fatalities rather than near-miss observations.
- **Extraction Method:** Page-by-page incident narrative extraction with table and non-incident filter masking.

---

### Source 3: IOGP Safety Performance Indicators — 2025 Data
- **Filename:** `resources/IAOGP-Safety performance indicators - 2025 data.pdf`
- **Source Type:** Latest Global Annual Safety Data Report (PDF).
- **Source Tag:** `IOGP_SPI`
- **Data Nature:** Comprehensive global safety metrics, process safety tier classifications, high potential incident distributions, and regional incident trends.
- **Key Fields Available:**
  - Regional and activity incident frequencies
  - Process safety event descriptions (Tier 1 & Tier 2 releases)
  - Equipment/system failure categories
- **Relevant OILPS Tasks:**
  - Domain terminology dictionary & vocabulary grounding
  - Causal taxonomy verification
  - Contextual statistical calibration for risk priority support
- **Limitations:** Contains extensive statistical aggregate charts and macro benchmarks alongside specific case vignettes.
- **Extraction Method:** Selective narrative case extraction avoiding pure numerical benchmarking tables.

---

### Source 4: IOGP Safety Data Reporting User Guide
- **Filename:** `resources/IAOGP - Safety data reporting user guide.pdf`
- **Source Type:** Technical Standard & Reporting Methodology Specification (PDF).
- **Source Tag:** `IOGP_GUIDE`
- **Data Nature:** Standardized definitions of High Potential Events, barriers, barrier failures, causal factor categories, and reporting rules.
- **Role in Project:** **Reference & Domain Knowledge Document ONLY** (NOT treated as training rows).
- **Deliverable Created:** `knowledge/iogp_user_guide_reference.md`
- **Relevant OILPS Tasks:**
  - Establishes canonical taxonomy for information extraction (Activity, Hazard, Barrier, Barrier Failure, Consequence)
  - Ground-truth Life-Saving Rules reference definitions
  - SIF annotation criteria documentation
- **Limitations:** Contains normative reporting guidance, not individual incident events.

---

### Source 5: OSHA Severe Workplace Safety Dataset
- **Filename:** `resources/January2015toNovember2025.csv`
- **Source Type:** Federal Workplace Incident Dataset (Tabular CSV).
- **Source Tag:** `OSHA`
- **Total Source Records:** 106,489 incident records (covering 2015 to November 2025).
- **Key Fields Available:**
  - `ID`: Unique OSHA inspection/report ID
  - `EventDate`: Incident date
  - `Employer`: Company name
  - `Primary NAICS`: 6-digit North American Industry Classification System code
  - `Final Narrative`: Detailed factual description of the incident sequence and equipment
  - `Hospitalized`, `Amputation`, `Loss of Eye`: Physical injury outcome indicators
  - `EventTitle` & `SourceTitle`: Standardized incident type and hazardous energy source
  - `NatureTitle`: Nature of injury / consequence
- **Filtering Methodology:**
  - Filtered by Oil & Gas NAICS codes (`211111`, `211112`, `211120`, `211130`, `213111`, `213112`, `486110`, `486210`, `486910`, `324110`, `237120`, `424710`, `424720`).
  - Supplemented by domain keyword matching on employer/narrative (`drilling rig`, `wellhead`, `blowout preventer`, `frac`, `casing`, `oilfield`, `refinery`, `compressor station`).
- **Relevant OILPS Tasks:**
  - High-volume empirical training data for semantic similarity and precursor entity extraction
  - Near-miss and unsafe condition/act pattern detection across drilling, servicing, pipeline, and refinery operations
- **Critical SIF Precaution:** Hospitalization/Amputation indicators do NOT automatically equal SIF potential. SIF potential is marked as `REVIEW_REQUIRED` pending systematic annotation.

---

## 3. Provenance & Traceability Matrix

| Field | Description | Example Values |
| :--- | :--- | :--- |
| `record_id` | Unified unique primary key | `OILPS_OSHA_00023`, `OILPS_IOGP_HPE_0005` |
| `source` | Primary originating authority | `IOGP_HPE`, `IOGP_FATAL`, `IOGP_SPI`, `OSHA` |
| `source_document` | Exact filename of source file | `January2015toNovember2025.csv`, `IAOGP - High Potential Event Reports.pdf` |
| `source_record_id` | Original source-assigned ID or page | `2015010023`, `HPE_P012` |
| `data_source_type` | Nature of the source data | `REGULATORY_SAFETY_REPORT`, `INDUSTRY_HPE_REPORT` |

---

## 4. Pipeline Execution Summary

```
   resources/ (5 Raw Source Files)
        │
        ├── extract_iogp.py ─────────> datasets/raw/iogp/
        │
        ├── process_osha.py ─────────> datasets/raw/osha/ & datasets/processed/osha_relevant.csv
        │
        ├── normalize.py ────────────> datasets/processed/oilps_unified_raw.csv
        │
        ├── deduplicate.py ──────────> datasets/processed/oilps_unified_deduped.csv
        │                              datasets/quality/deduplication_report.md
        │
        ├── validate_dataset.py ─────> datasets/annotation/oilps_annotation.csv
        │                              datasets/quality/DATASET_QUALITY_REPORT.md
        │
        └── create_splits.py ────────> datasets/splits/ (train.csv, val.csv, test.csv)
```
