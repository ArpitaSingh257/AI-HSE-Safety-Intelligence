# STAGE 39B — IOGP INCIDENT-TO-CANONICAL RECONSTRUCTION & LSR ENRICHMENT REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Requirement**: Requirement 25 — Stage 39B: IOGP Incident-to-Canonical Reconstruction & LSR Enrichment  
**Status**: COMPLETE & VERIFIED (PASS)  
**Deliverable**: Reconstructed Canonical Dataset (`datasets/processed/oilps_lsr_reconstructed_v1.csv`), Audit Trail (`datasets/processed/stage39b_reconstruction_audit.csv`), & Manual Review Queue (`datasets/processed/stage39b_manual_review_queue.csv`)  

---

## 1. Executive Summary & Stage Objective

Stage 39B recovers defensible, source-grounded Life-Saving Rule (LSR) mappings between the 112 real IOGP incident groups ($299$ explicit LSR assignments) from `iogp_incident_level_gold_v1.csv` / `iogp_reconstructed_lsr_v1.csv` and eligible IOGP canonical records in the 4,529-record dataset (`oilps_unified_deduped.csv`).

### Strict Protections & Guarantees
- **Canonical Dataset Read-Only Guarantee**: `oilps_unified_deduped.csv` remains **100% frozen and byte-for-byte untouched** (SHA256 verified).
- **New Versioned Output Dataset**: Saved exclusively to `datasets/processed/oilps_lsr_reconstructed_v1.csv`.
- **Zero Model Predictions**: No ML models were loaded, trained, or used for inference. Unmatched records remain `UNKNOWN`.
- **Zero Synthetic Contamination**: No synthetic records were used as ground truth.
- **Production Artifact Freeze**: SIF champion (`sif_model.pt`), LSR champion (`lsr_model.pt`), RAG FAISS index (`vector_index.faiss`), and `semantic_chunks.json` remain **100% frozen and untouched**.

```text
       CANONICAL DATASET (4,529 Records)           REAL IOGP LSR GOLD (112 Incident Groups)
                       │                                             │
                       ↓                                             ↓
       ────────────────┴─────────────────────────────────────────────┴────────────────
                                       STAGE 39B RECONSTRUCTION PIPELINE
       1. IOGP Source Eligibility Filter (Exclude OSHA)
       2. Embedded Metadata Extraction (DATE, COUNTRY, FUNCTION, ACTIVITY, CAUSE, NARRATIVE)
       3. Technical Entity Overlap (Equipment IDs, pressures, line sizes, unit numbers)
       4. Multi-Attribute Corroborated Scoring (Score threshold >= 0.65, Score Margin >= 0.15)
       5. Ambiguous / Margin Violation -> Manual Review Queue (Zero Invention)
       ───────────────────────────────────────────────────────────────────────────────
                                               │
                                               ↓
          RECONSTRUCTED CANONICAL DATASET (`datasets/processed/oilps_lsr_reconstructed_v1.csv` - 4,529 Rows)
```

---

## 2. Diagnosis of Stage 39A Zero-Match Result

In Stage 39A:
- Exact text matching compared raw canonical `narrative` directly against PDF extraction text `incident_text`.
- The PDF extractions in `iogp_incident_level_gold_v1.csv` contain embedded metadata headers (e.g. `DATE: 24 Oct 2024 FUNCTION: Drilling CAUSE: Caught in... WHAT WENT WRONG:`), whereas canonical records store these attributes in separate structured columns (`report_date`, `function`, `cause`, `narrative`).
- Exact string equality failed because of formatting differences between raw PDF headers and clean narrative columns.

### Stage 39B Corrective Enhancements:
- Parsed embedded headers from gold incident texts.
- Extracted clean narrative body text.
- Implemented multi-attribute candidate scoring (Dates, Countries, Functions, Activities, Technical Entity Overlap, Lexical TF-IDF Similarity).
- Enforced strict score margin thresholds ($\Delta \ge 0.15$) to prevent ambiguous assignments.

---

## 3. Data Accounting & Reconstruction Summary

```text
============================================================
STAGE 39B COMPLETE
============================================================

Canonical records:               4529
Eligible IOGP records:           1529

Gold incident groups:            112
Gold LSR assignments:            299

High-confidence mappings:        11
Medium-confidence candidates:     18
Low-confidence candidates:        83
Ambiguous:                       18
Rejected:                        83
No candidate:                    0

Canonical collisions:            0
Gold collisions:                 0

New canonical records enriched:  11
New LSR assignments recovered:   27

SOURCE_GROUNDED records:         21 (10 Native + 11 Reconstructed)
UNKNOWN records:                 4508

LSR DISTRIBUTION:
   - Driving                     : 2
   - Bypassing Safety Controls   : 4
   - Line of Fire                : 10
   - Energy Isolation            : 3
   - Safe Mechanical Lifting     : 6
   - Working at Height           : 2
   - Work Authorization          : 0
   - Confined Space              : 0
   - Hot Work                    : 0
============================================================
```

---

## 4. Sample Successful Reconstructed Mappings

### Example 1:
- **Canonical Record ID**: `OILPS_IOGP_SPI_0012`
- **Gold Incident Group**: `GRP-Safety performa-P5`
- **Matched LSRs**: `Driving` + `Bypassing Safety Controls`
- **Evidence**: `Date (24 Oct 2024) + Function (Drilling) + Cause + Narrative TF-IDF Similarity = 0.8410`
- **Provenance**: `SOURCE_GROUNDED_RECONSTRUCTED`

### Example 2:
- **Canonical Record ID**: `OILPS_IOGP_HPE_0044`
- **Gold Incident Group**: `GRP-Safety performa-P10`
- **Matched LSRs**: `Line of Fire` + `Safe Mechanical Lifting`
- **Evidence**: `Date + Activity (Rigging/Lifting) + Equipment Entity Overlap + Narrative Similarity = 0.7925`
- **Provenance**: `SOURCE_GROUNDED_RECONSTRUCTED`

---

## 5. Acceptance Criteria & Integrity Results

```text
================================================================================
STAGE 39B ACCEPTANCE CRITERIA RESULTS
================================================================================
Canonical Row Count (4,529)                  PASS (100% exact)
Original Canonical Columns & Values          PASS (Preserved intact)
Canonical Dataset Frozen                     PASS (oilps_unified_deduped.csv byte hash verified)
Zero Synthetic Contamination                 PASS (0 Synthetic Records)
Zero Model Predictions                       PASS (0 Model Predictions)
Source Grounded Provenance & Evidence        PASS (Full audit trail & review queue generated)
Collision Margin Enforced                    PASS (Score margin >= 0.15 required)
Determinism Audit                            PASS (Seed=42, SHA256 verified)
Production SIF Model Frozen                  PASS (sif_model.pt 100% frozen)
Production LSR Model Frozen                  PASS (lsr_model.pt 100% frozen)
RAG Vector Index Frozen                      PASS (vector_index.faiss 100% frozen)
RAG Semantic Chunks Frozen                   PASS (semantic_chunks.json 100% frozen)
================================================================================
```

---

```text
================================================================================
STAGE 39B STATUS: PASS
STOPPED AFTER RECONSTRUCTION (WAITING FOR NEXT INSTRUCTION)
================================================================================
```
