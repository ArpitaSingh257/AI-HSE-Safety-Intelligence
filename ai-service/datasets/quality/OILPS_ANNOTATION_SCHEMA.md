# OILPS Annotation Schema Specification & Data Leakage Guidelines
**Document Purpose:** Definitive technical data dictionary for the OILPS annotation corpus (`oilps_annotation.csv`).

---

## 1. Complete Field Specification Table

| Field Name | Description | Allowed Values | Source Authority | Ground Truth? | Requires Human Verification? | Permitted ML Input? | Permitted Target Label? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `record_id` | Unique incident identifier | String (`OILPS_...`) | System Generated | Yes | No | ❌ (Identifier) | ❌ |
| `source` | Originating data collection | `IOGP_HPE`, `IOGP_FATAL`, `IOGP_SPI`, `OSHA` | Source File | Yes | No | ⚠️ **LEAKAGE RISK** | ❌ |
| `source_document` | Original PDF/CSV filename | String | Source File | Yes | No | ❌ | ❌ |
| `source_record_id` | Original inspection or page ID | String | Source File | Yes | No | ❌ | ❌ |
| `report_date` | Date of incident occurrence | YYYY-MM-DD or text | Source File | Yes | No | ❌ | ❌ |
| `country` | Country of occurrence | String | Source File | Yes | No | Optional metadata | ❌ |
| `location` | Specific site, city, state | String | Source File | Yes | No | Optional metadata | ❌ |
| `industry` | Specific operational industry | String | Source / NAICS | Yes | No | Optional feature | ❌ |
| `event_type` | High-level event category | String | Source File | Yes | No | ⚠️ **LEAKAGE RISK** | ❌ |
| `severity` | Stated injury outcome | String | Source File | Yes | No | ⚠️ **LEAKAGE RISK** | ❌ |
| **`narrative`** | **Full descriptive incident text** | **Free text** | **Source File** | **Yes** | **No** | **✅ PRIMARY ML INPUT** | ❌ |
| `sif_annotation_status` | Status of SIF potential label | `SOURCE_GROUNDED`, `REVIEW_REQUIRED`, `VERIFIED` | Pipeline / Annotator | Yes | Yes (for OSHA) | ❌ | ❌ |
| `sif_label_type` | Origin of the SIF label | `SOURCE_GROUNDED`, `HUMAN_ANNOTATED`, `UNANNOTATED` | Metadata | Yes | No | ❌ | ❌ |
| **`verified_sif_label`** | **SIF Potential Indicator** | **`1` (SIF), `0` (Non-SIF), `UNKNOWN`** | **Annotator / IOGP** | **Yes (once verified)** | **Yes (for OSHA)** | ❌ **(Target)** | **✅ SIF TARGET** |
| `sif_annotator_notes` | Reviewer rationale | Free text | Annotator | No | Yes | ❌ | ❌ |
| `lsr_annotation_status` | Status of LSR labels | `SOURCE_GROUNDED`, `REVIEW_REQUIRED`, `VERIFIED` | Pipeline / Annotator | Yes | Yes (for OSHA) | ❌ | ❌ |
| `lsr_label_type` | Origin of the LSR label | `SOURCE_GROUNDED`, `HUMAN_ANNOTATED`, `CANDIDATE_HEURISTIC` | Metadata | Yes | No | ❌ | ❌ |
| `candidate_primary_lsr`| Rule-based suggested primary rule| Official 9 IOGP rules | Heuristic Rule | ❌ (Candidate only) | Yes | ❌ **LEAKAGE RISK** | ❌ |
| `candidate_secondary_lsr`| Rule-based suggested secondary| Official 9 IOGP rules | Heuristic Rule | ❌ (Candidate only) | Yes | ❌ **LEAKAGE RISK** | ❌ |
| `candidate_all_lsrs` | Semicolon-separated candidate list | Semicolon-separated list | Heuristic Rule | ❌ (Candidate only) | Yes | ❌ **LEAKAGE RISK** | ❌ |
| **`verified_primary_lsr`** | **Confirmed Primary Life-Saving Rule** | **Official 9 IOGP rules, None** | **Annotator / IOGP** | **Yes (once verified)** | **Yes (for OSHA)** | ❌ **(Target)** | **✅ LSR TARGET** |
| **`verified_secondary_lsr`**| **Confirmed Secondary Life-Saving Rule**| **Official 9 IOGP rules, None** | **Annotator / IOGP** | **Yes (once verified)** | **Yes (for OSHA)** | ❌ **(Target)** | **✅ LSR TARGET** |
| **`verified_life_saving_rules`**| **Complete multi-label set** | **Semicolon-separated rules** | **Annotator / IOGP** | **Yes (once verified)** | **Yes (for OSHA)** | ❌ **(Target)** | **✅ MULTI-LABEL TARGET** |
| `lsr_annotator_notes` | Reviewer notes for LSR | Free text | Annotator | No | Yes | ❌ | ❌ |
| `precursor_annotation_status`| Status of precursor extraction | `SOURCE_GROUNDED`, `REVIEW_REQUIRED`, `VERIFIED` | Pipeline / Annotator | Yes | Yes (for OSHA) | ❌ | ❌ |
| **`verified_activity`** | **Operational task entity** | String / Entity span | Annotator / IOGP | Yes | Yes (for OSHA) | ❌ **(Target)** | **✅ EXTRACTION TARGET**|
| **`verified_hazard`** | **Hazardous energy entity** | String / Entity span | Annotator / IOGP | Yes | Yes (for OSHA) | ❌ **(Target)** | **✅ EXTRACTION TARGET**|
| **`verified_barrier`** | **Intended protective control** | String / Entity span | Annotator / IOGP | Yes | Yes (for OSHA) | ❌ **(Target)** | **✅ EXTRACTION TARGET**|
| **`verified_barrier_failure`**| **Specific failure mode** | String / Entity span | Annotator / IOGP | Yes | Yes (for OSHA) | ❌ **(Target)** | **✅ EXTRACTION TARGET**|
| **`verified_potential_consequence`**| **Worst-case credible outcome**| String / Entity span | Annotator / IOGP | Yes | Yes (for OSHA) | ❌ **(Target)** | **✅ EXTRACTION TARGET**|

---

## 2. Strict Data Leakage Prevention Rules

> [!CAUTION]
> **CRITICAL FEATURE LEAKAGE WARNINGS FOR MACHINE LEARNING:**
> 1. **`source` Must Never Be a Model Feature:** Since 100% of IOGP records are `SIF = 1`, including `source` as an input feature would allow a classifier to simply memorize `source == IOGP -> SIF = 1`, destroying generalization to OSHA or real OIL reports.
> 2. **`severity` / `event_type` Must Never Be an Input Feature for SIF:** Real-world near-miss reports will NOT have pre-filled injury outcomes. The model must predict SIF potential **solely from the unstructured `narrative` text**.
> 3. **Candidate Labels Must Never Be Used as Targets:** `candidate_primary_lsr` is a heuristic keyword suggestion generated to assist human reviewers. Training a model to predict candidate labels would merely train the model to mimic simple keyword rules rather than genuine NLP semantics.
