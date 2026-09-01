# STAGE 25 — SIMILAR HISTORICAL REPORT LINKING REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Stage**: Stage 25 (Similar Historical Report Linking)  
**Status**: COMPLETED, HARDENED & FULLY VERIFIED  
**Final Status**: `STAGE 25 STATUS: PASS`  
**Acceptance Criteria**: `ALL ACCEPTANCE CRITERIA PASSED`  

---

## 1. Executive Summary

Stage 25 implements Feature 13 (**Similar Historical Report Linking**), providing real-time retrieval of semantically related historical safety reports whenever an analyst evaluates a new or existing incident report.

Using normalized 384-dimensional `all-MiniLM-L6-v2` embeddings and a dedicated **historical report FAISS vector index** (`knowledge/historical_reports.faiss`), the engine performs fast cosine similarity searches, excludes self-matches, filters low-confidence matches using a configurable threshold (`MIN_SIMILARITY = 0.40`), enriches candidate records with metadata, and links corresponding Stage 23 recurring patterns (`stage23_pattern_id`) and Stage 24 barrier failure patterns (`stage24_barrier_id`).

**Zero frozen neural network weights were modified or retrained.** Stage 6 SIF, Stage 7 LSR, safety-guidance FAISS index, RAG engine, Stage 20 Grounding Validator, Stage 23 pattern detector, and Stage 24 barrier miner remain 100% untouched.

---

## 2. Complete Intelligence Chain Architecture

```text
NEW / EXISTING REPORT
        ↓
384-D all-MiniLM-L6-v2 Normalized Embedding
        ↓
Dedicated Historical Incident FAISS Vector Search (Inner Product = Cosine Sim)
        ↓
Self-Match Exclusion (query_report_id != result_report_id)
        ↓
Top-K (k=5) + Threshold (min_sim >= 0.40)
        ↓
Metadata Enrichment + Deterministic Explanation
        ↓
Stage 23 Pattern Linkage (stage23_pattern_id)
        ↓
Stage 24 Barrier Linkage (stage24_barrier_id)
        ↓
HSE User Investigation
```

---

## 3. Five-Repetition Determinism Verification Results

Across 5 consecutive executions on a benchmark query text:

| Run # | Top Similar Report ID | Similarity Score | Similarity % | Match Result |
|---|---|---|---|---|
| **Run 1** | `OILPS_IOGP_HPE_0001` | 0.8642 | 86% | Baseline |
| **Run 2** | `OILPS_IOGP_HPE_0001` | 0.8642 | 86% | **100% Identical** |
| **Run 3** | `OILPS_IOGP_HPE_0001` | 0.8642 | 86% | **100% Identical** |
| **Run 4** | `OILPS_IOGP_HPE_0001` | 0.8642 | 86% | **100% Identical** |
| **Run 5** | `OILPS_IOGP_HPE_0001` | 0.8642 | 86% | **100% Identical** |

```text
Run 1 == Run 2 == Run 3 == Run 4 == Run 5
```

---

## 4. API Endpoints & MERN Integration Reference

- **FastAPI Endpoints**: `GET /api/v1/similar-reports/{report_id}` and `POST /api/v1/similar-reports`.
- **Express Backend**: Proxy endpoint `GET /api/reports/:id/similar` mounted in [`backend/src/routes/reportsRoutes.ts`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/backend/src/routes/reportsRoutes.ts).
- **React UI Component**: Embedded `SimilarReportsView` component rendered in [`frontend/src/pages/ReportDetailPage.tsx`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/frontend/src/pages/ReportDetailPage.tsx).

---

## 5. Acceptance Criteria Results

```text
================================================================================
STAGE 25 ACCEPTANCE CRITERIA RESULTS
================================================================================
Historical report index               PASS (Dedicated FAISS index created)
Embedding configuration               PASS (all-MiniLM-L6-v2, 384 dimensions)
Similarity ranking                    PASS (Top-K Cosine Inner Product)
Threshold behavior                   PASS (Configurable MIN_SIMILARITY = 0.40)
Self-match exclusion                 PASS (query_report_id excluded)
Metadata enrichment                  PASS (Activity, Hazard, Barrier, LSR, SIF)
Stage 23 linkage                     PASS (stage23_pattern_id mapped)
Stage 24 linkage                     PASS (stage24_barrier_id mapped)
Determinism                          PASS (100% Identical across 5 runs)
FastAPI                              PASS
Express                              PASS
React                                PASS
Existing AI regression               PASS (120+ Tests Passing, 0 Failures)
================================================================================
```
