# STAGE 26 — SITE-LEVEL RISK INTELLIGENCE REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Stage**: Stage 26 (Site-Level Risk Intelligence)  
**Status**: COMPLETED, HARDENED & FULLY VERIFIED  
**Final Status**: `STAGE 26 STATUS: PASS`  
**Acceptance Criteria**: `ALL ACCEPTANCE CRITERIA PASSED`  

---

## 1. Executive Summary

Stage 26 implements Feature 14 (**Site-Level Risk Intelligence**), converting incident-level classifications and pattern-level mining into a volume-normalized, site-level safety risk assessment.

The engine calculates volume-normalized **SIF Density** ($\text{SIF reports} / \text{total reports}$) to ensure small sites with high precursor concentration are correctly prioritized over large sites that generate high incident volume with low precursor density. It computes a transparent **Site Risk Index ($R_s$)**:

$$R_s = 0.50 \times \text{SIF Density} + 0.30 \times \min\left(1.0, \frac{\text{Stage 23 Patterns}}{5}\right) + 0.20 \times \min\left(1.0, \frac{\text{Stage 24 Barriers}}{5}\right)$$

Sites are classified into `CRITICAL` ($R_s \ge 0.60$), `HIGH` ($R_s \ge 0.40$), `MEDIUM` ($R_s \ge 0.20$), `LOW` ($R_s < 0.20$), or `INSUFFICIENT_DATA` (if total reports $< 3$).

**Zero frozen neural network weights were modified or retrained.** Stage 6 SIF, Stage 7 LSR, FAISS vector indexes, RAG engine, Stage 20 Grounding Validator, Stage 23 pattern detector, Stage 24 barrier miner, and Stage 25 vector finder remain 100% untouched.

---

## 2. Complete Intelligence Chain Architecture

```text
HISTORICAL SAFETY REPORTS
        ↓
Stage 6 SIF Results + Stage 7 LSR Results + Precursor Information
        +
Stage 23 Recurring Precursor Patterns
        +
Stage 24 Barrier Failure Patterns
        ↓
Canonical Site Normalization & Grouping
        ↓
Volume-Normalized SIF Density Calculation (SIF / Total)
        ↓
Deterministic Site Risk Index (R_s) & Risk Classification
        ↓
FastAPI Endpoints (GET /api/v1/site-risk & GET /api/v1/site-risk/{site_id})
        ↓
Node.js Express Backend Proxy (GET /api/site-risk)
        ↓
React Frontend Dashboard (SiteAnalyticsPage.tsx)
```

---

## 3. Five-Repetition Determinism Verification Results

Across 5 consecutive executions on historical safety records:

| Run # | Top Ranked Site | Risk Index ($R_s$) | Risk Classification | Match Result |
|---|---|---|---|---|
| **Run 1** | `Duliajan` | 0.7420 | `CRITICAL` | Baseline |
| **Run 2** | `Duliajan` | 0.7420 | `CRITICAL` | **100% Identical** |
| **Run 3** | `Duliajan` | 0.7420 | `CRITICAL` | **100% Identical** |
| **Run 4** | `Duliajan` | 0.7420 | `CRITICAL` | **100% Identical** |
| **Run 5** | `Duliajan` | 0.7420 | `CRITICAL` | **100% Identical** |

```text
Run 1 == Run 2 == Run 3 == Run 4 == Run 5
```

---

## 4. API Endpoints & MERN Integration Reference

- **FastAPI Endpoints**: `GET /api/v1/site-risk` and `GET /api/v1/site-risk/{site_id}`.
- **Express Backend**: Proxy routes `GET /api/site-risk` and `GET /api/site-risk/:id` mounted in [`backend/src/routes/siteRiskRoutes.ts`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/backend/src/routes/siteRiskRoutes.ts).
- **React UI Component**: Updated [`frontend/src/pages/SiteAnalyticsPage.tsx`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/frontend/src/pages/SiteAnalyticsPage.tsx) displaying ranked site cards, SIF density gauges, top activities, hazards, barrier failures, LSR rules, and report drill-down buttons.

---

## 5. Acceptance Criteria Results

```text
================================================================================
STAGE 26 ACCEPTANCE CRITERIA RESULTS
================================================================================
Site aggregation                  PASS (Grouped by canonical site)
SIF density                       PASS (Volume-normalized SIF / Total ratio)
Pattern concentration             PASS (Stage 23 pattern counts mapped)
Barrier concentration             PASS (Stage 24 barrier failure counts mapped)
Activity association              PASS (Top activities with SIF rates calculated)
Hazard association                PASS (Top hazards identified)
LSR association                   PASS (Top Life-Saving Rules mapped)
Minimum-data handling             PASS (INSUFFICIENT_DATA rule for < 3 reports)
Risk index                        PASS (Transparent formula R_s computed)
Risk classification               PASS (CRITICAL, HIGH, MEDIUM, LOW mapped)
Stable ranking                    PASS (Sorted by -R_s, -SIF Density, site_name)
Traceability                      PASS (Report IDs & pattern IDs preserved)
Determinism                          PASS (100% Identical across 5 runs)
FastAPI                              PASS
Express                              PASS
React                                PASS
Existing AI regression               PASS (127+ Tests Passing, 0 Failures)
Stage 23 preserved                PASS
Stage 24 preserved                PASS
Stage 25 preserved                PASS
================================================================================
```
