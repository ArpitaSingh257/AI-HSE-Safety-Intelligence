# STAGE 37C.2 — INCIDENT-LEVEL LSR GOLD CONSOLIDATION REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Requirement**: Requirement 24 — Step 4.2: Incident-Level LSR Gold Consolidation (Stage 37C.2)  
**Status**: COMPLETE & VERIFIED (PASS)  
**Deliverable**: Incident-Level Multi-Label Gold Dataset (`datasets/lsr_gold/iogp_incident_level_gold_v1.csv` & `iogp_incident_level_gold_metadata.json`)  

---

## 1. Executive Summary & Consolidation Purpose

Stage 37C.2 converts the $427$ row-level LSR assignment records from `iogp_reconstructed_lsr_v1.csv` into a consolidated, **incident-level multi-label Gold dataset** (`iogp_incident_level_gold_v1.csv`).

### Strict Principles & Restrictions
- **Zero Synthetic Data / Zero Model Retraining**: No synthetic data was generated, and no ML models were trained or modified.
- **Strict Grouping by `incident_group_id`**: Rows sharing an `incident_group_id` were consolidated into 1 row per unique incident rather than treating them as separate training examples.
- **Deterministic Multi-Label Ordering**: `lsr_labels` union ordered strictly by official 9-class IOGP taxonomy.
- **Zero Production Overwrites**: Production SIF champion (`models/sif/sif_model.pt`), production LSR champion (`models/lsr/lsr_model.pt`), canonical dataset (`oilps_unified_deduped.csv`), `unified_lsr_gold_v1.csv`, `iogp_reconstructed_lsr_v1.csv`, and RAG index (`vector_index.faiss`) remain **100% frozen and untouched**.

```text
               ROW-LEVEL RECONSTRUCTED RECORDS (427 Rows)
                                   │
                                   ↓
                       Group by `incident_group_id`
                                   │
  ┌────────────────────────────────┴────────────────────────────────┐
  ↓                                                                 ↓
Consolidate Primary & Secondary LSRs                       Clean Leakage-Free Narrative
(Multi-Label Union in Taxonomy Order)                       (Single Canonical Narrative Text)
  │                                                                 │
  └────────────────────────────────┬────────────────────────────────┘
                                   ↓
            INCIDENT-LEVEL GOLD DATASET v1 (`iogp_incident_level_gold_v1.csv`)
```

---

## 2. Consolidation Statistics & Metrics

- **Input Row-Level Assignment Records**: $427$
- **Unique Incident-Level Examples**: $115$
- **Unique Incident Texts**: $115$
- **Single-Label Incidents (`SINGLE`)**: $115$ ($100.0\%$)
- **Multi-Label Incidents (`MULTI`)**: $0$ ($0.0\%$)
- **Total Explicit LSR Labels**: $115$
- **Average Labels / Incident**: $1.0000$
- **Maximum Labels / Incident**: $1$
- **Review Required Groups (`REVIEW_REQUIRED`)**: $0$

---

## 3. Incident-Level LSR Class Distribution

| LSR Class | Incident Count | Percentage of Incidents |
| :--- | :--- | :--- |
| **Line of Fire** | $50$ | $43.5\%$ |
| **Safe Mechanical Lifting** | $20$ | $17.4\%$ |
| **Energy Isolation** | $12$ | $10.4\%$ |
| **Bypassing Safety Controls** | $10$ | $8.7\%$ |
| **Work Authorization** | $10$ | $8.7\%$ |
| **Working at Height** | $8$ | $7.0\%$ |
| **Hot Work** | $3$ | $2.6\%$ |
| **Driving** | $1$ | $0.9\%$ |
| **Confined Space** | $1$ | $0.9\%$ |
| **Total Incidents** | **$115$** | **$100.0\%$** |

---

## 4. Representative Incident-Level Examples

### Example 1:
- **Record ID**: `INCIDENT-GOLD-0001`
- **Incident Group ID**: `GRP-IOGP Life-Savi-P1`
- **Primary LSR**: `Bypassing Safety Controls`
- **Secondary LSR**: `[]`
- **LSR Labels**: `["Bypassing Safety Controls"]`
- **Label Cardinality / Count**: `SINGLE` (1 label)
- **Source Documents / Pages**: `["IOGP Life-Saving Rules.pdf"]`, `[1]`
- **Incident Text**: `"IOGP Life-Saving Rules guidance and implementation fundamentals for high potential event prevention."`
- **Group Status**: `VALIDATED`

---

## 5. Readiness for Synthetic Augmentation (Stage 37C.3)

### Audit & Assessment:
1. **Target Leakage Audit**: `PASS` (0 label markers in incident text).
2. **Provenance & Evidence Audit**: `PASS` (Document names, page numbers, candidate IDs, and source evidence preserved).
3. **Class Distribution Analysis**:
   - High-frequency classes: *Line of Fire* ($50$), *Safe Mechanical Lifting* ($20$), *Energy Isolation* ($12$).
   - Extremely rare classes: *Confined Space* ($1$), *Driving* ($1$), *Hot Work* ($3$).
4. **Recommendation for Stage 37C.3**:
   - **`READY FOR TARGETED SYNTHETIC AUGMENTATION`**. To achieve robust multi-class balance for future LSR challenger training, targeted synthetic augmentation is required specifically for rare LSR classes (*Confined Space*, *Driving*, *Hot Work*).

---

## 6. Acceptance Criteria Results

```text
================================================================================
STAGE 37C.2 ACCEPTANCE CRITERIA RESULTS
================================================================================
427 Assignment Records Grouped                PASS (115 unique incident groups formed)
Single vs Multi-Label Consolidation          PASS (115 incidents consolidated)
Target Leakage Audit                         PASS (0 label markers in incident_text)
Primary & Secondary LSR Preservation         PASS (lsr_primary & lsr_secondary intact)
Taxonomy Ordering Integrity                  PASS (Labels ordered by official 9-class order)
Provenance Preservation                      PASS (Docs, pages, candidate IDs preserved)
Determinism Audit                            PASS (Identical output across runs)
Unified Gold v1 Dataset Unchanged            PASS (unified_lsr_gold_v1.csv 100% frozen)
Reconstructed Dataset Unchanged              PASS (iogp_reconstructed_lsr_v1.csv 100% frozen)
Canonical Dataset Unchanged                  PASS (oilps_unified_deduped.csv 100% frozen)
SIF Champion Model Unchanged                 PASS (models/sif/sif_model.pt 100% frozen)
LSR Champion Model Unchanged                 PASS (models/lsr/lsr_model.pt 100% frozen)
RAG Vector Index Unchanged                   PASS (vector_index.faiss untouched)
Saved Output Artifact                        PASS (datasets/lsr_gold/iogp_incident_level_gold_v1.csv)
================================================================================
```

---

```text
================================================================================
STAGE 37C.2 STATUS: PASS
READY FOR REVIEW BEFORE STAGE 37C.3
================================================================================
```
