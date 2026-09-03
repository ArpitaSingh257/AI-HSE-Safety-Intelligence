# STAGE 37C — UNIFIED LSR GOLD DATASET CONSTRUCTION REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Requirement**: Requirement 24 — Step 4: Unified LSR Gold Dataset Construction (Stage 37C)  
**Status**: COMPLETE & VERIFIED (PASS)  
**Deliverable**: Versioned Unified LSR Gold Dataset v1 (`datasets/lsr_gold/unified_lsr_gold_v1.csv` & `unified_lsr_gold_v1_metadata.json`)  

---

## 1. Executive Summary & Construction Purpose

Stage 37C constructs the versioned **Unified LSR Gold Dataset v1** by performing a **dataset-level union with provenance preservation** between:
1. The canonical $4,529$ historical incident records ([`oilps_unified_deduped.csv`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/datasets/processed/oilps_unified_deduped.csv)).
2. The $427$ validated, source-grounded IOGP LSR incidents produced by Stage 37A.1 ([`lsr_evidence_candidates.json`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/datasets/lsr_gold_candidates/lsr_evidence_candidates.json)).

### Strict Principles & Restrictions
- **Zero Retraining**: No models were trained or modified.
- **Zero Production Overwrites**: Production SIF champion (`models/sif/sif_model.pt`), production LSR champion (`models/lsr/lsr_model.pt`), canonical dataset (`datasets/processed/oilps_unified_deduped.csv`), and production RAG index (`datasets/rag/vector_index.faiss`) remain **100% frozen and untouched**.
- **Zero Pseudo-Labels & Zero Inferred Labels**: `inferred_lsr_count = 0`, `pseudo_label_count = 0`. Unlabeled canonical records ($4,519$ records) remain with `lsr_status = UNKNOWN` and `lsr_label_provenance = NOT_AVAILABLE`. `UNKNOWN` is never converted into a negative label or inferred label.
- **Dataset-Level Union**: Because Stage 37A.1 found zero incident-level matches between the $427$ IOGP records and the canonical dataset, the $427$ records were appended cleanly with `dataset_origin = IOGP_STAGE37A1` and `canonical_match_status = UNMAPPED_IOGP` rather than attaching them to arbitrary unlabeled rows.

```text
                  CANONICAL DATASET (4,529 Records)
                                 +
              VALIDATED STAGE 37A.1 IOGP (427 Records)
                                 │
   ┌─────────────────────────────┴─────────────────────────────┐
   ↓                                                           ↓
Dataset-Level Union with Provenance                Deterministic Sorting & Audit
(Canonical + IOGP_STAGE37A1)                       (4,956 Final Dataset Rows)
   │                                                           │
   └─────────────────────────────┬─────────────────────────────┘
                                 ↓
           UNIFIED LSR GOLD DATASET v1 (datasets/lsr_gold/)
```

---

## 2. Dataset Accounting & Union Summary

- **Canonical Input Records (`oilps_unified_deduped.csv`)**: $4,529$
- **Stage 37A.1 Validated Records (IOGP Candidates)**: $427$
- **Raw Union Count**: $4,956$
- **Confirmed Deduplicated Overlap**: $0$
- **Final Unified Gold Dataset Count**: $4,956$ records

### Provenance & Origin Breakdown:
- **CANONICAL Origin Records**: $4,529$ ($4,519$ `UNKNOWN`, $10$ native labeled)
- **IOGP_STAGE37A1 Origin Records**: $427$ ($427$ `SOURCE_GROUNDED`)
- **Total Source-Grounded Labeled Records**: $437$ ($427$ IOGP + $10$ native canonical)
- **Total UNKNOWN LSR Records**: $4,519$
- **Inferred LSR Labels**: $0$ (Strictly 0)
- **Pseudo-Labeled Records**: $0$ (Strictly 0)

---

## 3. LSR Class Distribution (Source-Grounded Labeled Records)

| LSR Class | Labeled Record Count | Percentage of Labeled |
| :--- | :--- | :--- |
| **Line of Fire** | $199$ | $45.5\%$ |
| **Safe Mechanical Lifting** | $70$ | $16.0\%$ |
| **Energy Isolation** | $38$ | $8.7\%$ |
| **Bypassing Safety Controls** | $35$ | $8.0\%$ |
| **Work Authorization** | $35$ | $8.0\%$ |
| **Working at Height** | $31$ | $7.1\%$ |
| **Hot Work** | $12$ | $2.7\%$ |
| **Driving** | $11$ | $2.5\%$ |
| **Confined Space** | $6$ | $1.4\%$ |
| **Total Source-Grounded Labeled** | **$437$** | **$100.0\%$** |

*Note: Rare classes such as Confined Space ($6$ records) are preserved intact without oversampling or synthetic duplication.*

---

## 4. Acceptance Criteria & Verification Results

```text
================================================================================
STAGE 37C ACCEPTANCE CRITERIA RESULTS
================================================================================
427 Validated IOGP Records Represented       PASS (427 records added with IOGP_STAGE37A1 origin)
Canonical Dataset Unchanged                  PASS (oilps_unified_deduped.csv 100% frozen)
SIF Model Unchanged                          PASS (models/sif/sif_model.pt 100% frozen)
LSR Model Unchanged                          PASS (models/lsr/lsr_model.pt 100% frozen)
RAG Unchanged                                PASS (vector_index.faiss & chunks untouched)
Zero Pseudo-Labels                           PASS (pseudo_label_count = 0)
Zero Inferred LSR Labels                     PASS (inferred_lsr_count = 0)
Provenance & Evidence Preserved              PASS (lsr_evidence & reference fields populated)
Rare Classes Preserved                       PASS (Confined Space & rare classes intact)
Unique Record IDs                            PASS (4,956 unique IDs verified)
Deterministic Construction                   PASS (Identical output on repeated builds)
Saved Output Artifacts                       PASS (datasets/lsr_gold/unified_lsr_gold_v1.csv)
================================================================================
```

---

```text
================================================================================
STAGE 37C STATUS: PASS
UNIFIED LSR GOLD DATASET v1: COMPLETE & ISOLATED
================================================================================
```
