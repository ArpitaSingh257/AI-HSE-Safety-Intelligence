# STAGE 36A — SYNTHETIC RARE-SIF DATA GENERATOR & QUALITY PATCH REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Requirement**: Requirement 24 — Step 1: Synthetic Rare-SIF Data Generator & Missing-Value Patch  
**Status**: COMPLETE & VERIFIED (PASS)  
**Deliverable**: Controlled Synthetic Data Generator, Missing-Value Leakage Prevention Engine, Explicit Provenance Tracking & Isolated Storage  

---

## 1. Executive Summary & Problem Addressed

Stage 36A implements the **Synthetic Rare-SIF Data Generation Subsystem** ([`synthetic_sif_generator.py`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/data/synthetic_sif_generator.py)).

Because Serious Injury/Fatality (SIF) precursor events are rare in safety reporting datasets (creating significant class imbalance), Stage 36A builds a controlled generator that derives synthetic candidate SIF records from verified real SIF positive records (`sif_potential == 1`).

### Missing-Value Quality Patch
A synthetic data quality patch was applied to prevent missing or NaN source attributes from leaking into generated narratives as literal strings (`"resulting in nan..."`):
- **Missing Value Helper**: Functions `is_missing_value(val)` and `clean_generation_field(val)` identify `None`, `NaN`, `"nan"`, `"null"`, `"none"`, `""` and normalize missing attributes.
- **Dynamic Clause Omission**: When structured fields (e.g. `barrier_failure`) are missing, the generator omits the clause rather than inserting `nan` or fake placeholder strings like `"unknown"`.
- **Post-Generation Leakage Check**: In `validate_candidates()`, candidates containing literal missing tokens matching `\b(nan|none|null|undefined)\b` are rejected (`MISSING_VALUE_LEAKAGE`).

```text
REAL VERIFIED SIF RECORDS (sif_potential = 1)
          ↓
   Source Selection & Structure Extraction
          ↓
   Missing-Value Normalization (Omit NaN / null clauses)
          ↓
Controlled Synthetic Variation Generator
          ↓
Synthetic Candidates (SYN-SIF-000001 ...)
          ↓
Quality Validation (Missing-Value Leakage Check, Duplicate Detection, Contamination, Schema Checks)
          ↓
Provenance & Metadata Linking
          ↓
ISOLATED SYNTHETIC DATASET (ai-service/datasets/synthetic/)
```

### Critical Architectural Principles & Model Freeze
- **Zero Production Retraining**: Stage 6 SIF and Stage 7 LSR champion model weights remain **100% frozen**.
- **No Production RAG Contamination**: Synthetic records are saved strictly isolated in `ai-service/datasets/synthetic/` and are **NEVER** ingested into the production FAISS vector index or historical database.
- **Explicit Synthetic Provenance**: Every synthetic record contains `synthetic_id` (e.g. `SYN-SIF-000001`), `source_type = "SYNTHETIC"`, `is_synthetic = True`, `sif_potential = 1`, and `synthetic_parent_ids`.

---

## 2. Real Dataset Audit Summary

Audit of `datasets/processed/oilps_unified_deduped.csv`:

- **Total Dataset Records**: $1,554$
- **Verified SIF Positive Records (`sif_potential == 1`)**: $356$ ($22.91\%$)
- **SIF Negative Records (`sif_potential == 0`)**: $1,198$ ($77.09\%$)
- **SIF Class Imbalance Ratio**: $1 : 3.37$

---

## 3. Synthetic Candidate Record Structure

```json
{
  "synthetic_id": "SYN-SIF-000001",
  "source_type": "SYNTHETIC",
  "is_synthetic": true,
  "sif_potential": 1,
  "description": "During hazardous operation, an unexpected high-energy release occurred at process unit, resulting in isolation verification defect and creating severe SIF exposure.",
  "synthetic_parent_ids": "[\"IOGP-REPORT-00123\"]",
  "activity_category": "hazardous operation",
  "primary_hazard": "high-energy release",
  "barrier_failure": "isolation verification defect",
  "site_location": "process unit",
  "generation_method": "CONTROLLED_VARIATION",
  "generation_model": "OILPS_SyntheticSIFGen_v1",
  "generation_version": "1.0.0",
  "created_at": "2026-09-02T11:04:00Z",
  "validation_status": "ACCEPTED",
  "validation_reason": "VALID"
}
```

---

## 4. Acceptance Criteria & Verification Results

```text
================================================================================
STAGE 36A ACCEPTANCE CRITERIA RESULTS
================================================================================
Real-data audit                         PASS (1,554 total, 356 SIF positives audited)
Verified SIF source selection           PASS (Selected exclusively from sif_potential=1)
Controlled generation                   PASS (Template & structure variations applied)
Missing-value leakage prevention        PASS (0 'nan', 'null', 'none' leakage)
Synthetic IDs                           PASS (SYN-SIF-000001 ... format enforced)
Synthetic provenance                    PASS (parent IDs & generation metadata preserved)
Synthetic labels                        PASS (sif_potential=1 with source_type=SYNTHETIC)
Schema validation                       PASS (All required fields verified)
Safety validation                       PASS (Negation contradiction check active)
Duplicate detection                     PASS (Exact & intra-set duplicates checked)
Real-data contamination check           PASS (Rejects matches to real dataset)
Distribution sanity                     PASS (Safety factor proportions aligned)
Synthetic/real separation               PASS (Stored isolated in datasets/synthetic/)
RAG isolation                           PASS (Vector index & FAISS untouched)
Production model freeze                 PASS (SIF & LSR champion weights 100% frozen)
No model training                       PASS (0 training calls executed)
Determinism                             PASS (100% identity across repeated runs)
Security                                PASS (No PII / personal IDs generated)
Full regression                         PASS (All PyTest test suites passed)
Documentation                           PASS (Complete architectural report created)
================================================================================
```

---

```text
================================================================================
STAGE 36A — SYNTHETIC SIF DATA QUALITY PATCH
================================================================================
 Missing-Value Leakage: PASS
 Synthetic Data Quality: PASS
 Provenance:            PASS
 Determinism:           PASS
 Production Models:     FROZEN
 Production RAG:        UNCHANGED
================================================================================
STAGE 36A STATUS: PASS
================================================================================
```
