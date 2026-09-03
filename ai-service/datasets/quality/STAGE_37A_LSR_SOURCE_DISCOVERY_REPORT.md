# STAGE 37A — LOCAL IOGP LSR GROUND-TRUTH DISCOVERY & AUDIT REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Requirement**: Requirement 24 — Step 3: Local IOGP LSR Ground-Truth Discovery & Audit (Stage 37A)  
**Status**: COMPLETE & VERIFIED (PASS)  
**Stage 37B Status**: HSE Expert Annotation Required (`stage37b_annotation_required = true`)  

---

## 1. Executive Summary & Audit Purpose

Stage 37A performs a **Data Discovery & Audit** of all local files inside `ai-service/resources/` (and subfolders) to extract explicit, source-grounded IOGP Life-Saving Rule (LSR) labels.

### Strict Principles & Restrictions
- **Zero Retraining**: No models were trained or modified.
- **Zero Label Guessing**: Implicit narrative text (e.g. *"worker contacted energized line"*) is **NEVER** assigned an LSR label unless explicitly linked in the source document.
- **Zero Production Overwrites**: Production SIF champion (`models/sif/sif_model.pt`), production LSR champion (`models/lsr/lsr_model.pt`), canonical dataset (`datasets/processed/oilps_unified_deduped.csv`), and production RAG index (`datasets/rag/vector_index.faiss`) remain **100% frozen and untouched**.

```text
                  RESOURCES FOLDER (ai-service/resources/)
                                   │
                 ┌─────────────────┴─────────────────┐
                 ↓                                   ↓
        PDF Resource Scanner                Resource Inventory CSV
                 │
   Explicit-Only Parsing (Regex + Metadata)
                 │
  ┌──────────────┼──────────────┬────────────────┐
  ↓              ↓              ↓                ↓
Explicit       Rule          General         Ambiguous
Incidents   Definitions    Discussions      Candidates
  │
  └──────────────────────────────┬─────────────────┘
                                 ↓
                     STAGE 37A AUDIT & REPORT
```

---

## 2. Resources Discovered & Inventory Summary

Inspected Files under `ai-service/resources/`:
1. `safety-recommendation-engine/IOGP Life-Saving Rules.pdf` ($1,100,603$ bytes, Page Count: $12$, Relevance: **HIGH**)
2. `safety-recommendation-engine/Process Safety Fundamentals.pdf` ($8,873,875$ bytes, Page Count: $28$, Relevance: **MEDIUM**)
3. `safety-recommendation-engine/Safety performance indicators – 2023 data.pdf` ($539,114$ bytes, Page Count: $48$, Relevance: **HIGH**)
4. `safety-recommendation-engine/Safety performance indicators – 2024 data.pdf` ($547,140$ bytes, Page Count: $52$, Relevance: **HIGH**)
5. `safety-recommendation-engine/Safety performance indicators – 2025 data.pdf` ($454,731$ bytes, Page Count: $44$, Relevance: **HIGH**)

- **Total Resources Inspected**: $5$ PDF documents ($184$ total pages scanned).

---

## 3. Textual Mentions & Evidence Classification

- **Incident-Level Explicit Assignments (`INCIDENT_ASSIGNMENT`)**: $0$ new explicit incident-level labels in local PDFs (all occurrences in these PDFs represent rule definitions, general safety metrics, or process safety fundamentals).
- **Rule Definitions Identified (`RULE_DEFINITION`)**: $14$ (General guidance on rules such as *Working at Height*, *Energy Isolation*, *Line of Fire*).
- **General Safety Discussions (`GENERAL_DISCUSSION`)**: $32$ (Annual performance statistics and safety indicator overviews).
- **Ambiguous Candidates**: $0$.

---

## 4. Ground-Truth Discovery Totals

- **Previously Known Native LSR Incidents**: $10$ records (in historical IOGP positive subset).
- **New Explicit Native LSR Incidents Found**: $0$ (Current local PDF source material contains rule guidance and statistics, but zero additional explicitly labelled incident rows).
- **Total Unique Source-Grounded Incidents**: $10$ records.

---

## 5. Recommendation for Stage 37B

Since local resource inspection confirmed that current PDFs contain rule guidance rather than additional explicit incident-level LSR rows:

> **Proceed to Stage 37B — Human HSE Expert Annotation** to acquire high-confidence, domain-validated IOGP Life-Saving Rule labels.

---

## 6. Acceptance Criteria Results

```text
================================================================================
STAGE 37A ACCEPTANCE CRITERIA RESULTS
================================================================================
Resource discovery scanner                   PASS (5 PDF resources scanned, 184 pages)
Explicit-only rule validation               PASS (0 label guessing from implicit text)
Rule definition exclusion                    PASS (14 definitions classified separately)
Provenance completeness                      PASS (resource_inventory.csv generated)
Deduplication integrity                      PASS (0 duplicate inflation)
Determinism                                  PASS (100% output identity)
Production SIF model unchanged               PASS (models/sif/sif_model.pt 100% frozen)
Production LSR model unchanged               PASS (models/lsr/lsr_model.pt 100% frozen)
Production RAG unchanged                     PASS (vector_index.faiss untouched)
Historical dataset unchanged                 PASS (oilps_unified_deduped.csv untouched)
Stage 37B HSE Annotation recommendation       PASS (stage37b_annotation_required = true)
Documentation                                PASS (Complete audit report created)
================================================================================
```

---

```text
================================================================================
STAGE 37A STATUS: PASS
STAGE 37B REQUIRED: TRUE (Proceed to HSE Expert Annotation)
================================================================================
```
