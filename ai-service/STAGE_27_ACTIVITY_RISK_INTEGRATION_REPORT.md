# STAGE 27 — ACTIVITY-LEVEL RISK INTELLIGENCE REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Stage**: Stage 27 (Activity-Level Risk Intelligence)  
**Status**: COMPLETED, HARDENED & FULLY VERIFIED  
**Final Status**: `STAGE 27 STATUS: PASS`  
**Acceptance Criteria**: `ALL ACCEPTANCE CRITERIA PASSED`  

---

## 1. Executive Summary

Stage 27 implements Feature 15 (**Activity-Level Risk Intelligence**), converting incident-level classifications, pattern-level mining, and site risk profiles into a volume-normalized, task-level safety risk assessment.

The engine calculates volume-normalized **SIF Density** ($\text{SIF reports} / \text{total reports}$) to ensure activities with high precursor concentration (e.g., *Maintenance*, *Lifting / Crane*, *Hot Work*, *Drilling*) are correctly prioritized over high-volume routine tasks with low precursor density. It computes a transparent **Activity Risk Index ($R_a$)**:

$$R_a = 0.50 \times \text{SIF Density} + 0.30 \times \min\left(1.0, \frac{\text{Stage 23 Patterns}}{5}\right) + 0.20 \times \min\left(1.0, \frac{\text{Stage 24 Barriers}}{5}\right)$$

Activities are classified into `CRITICAL` ($R_a \ge 0.60$), `HIGH` ($R_a \ge 0.40$), `MEDIUM` ($R_a \ge 0.20$), `LOW` ($R_a < 0.20$), or `INSUFFICIENT_DATA` (if total reports $< 3$).

**Zero frozen neural network weights were modified or retrained.** Stage 6 SIF, Stage 7 LSR, FAISS vector indexes, RAG engine, Stage 20 Grounding Validator, Stage 23 pattern detector, Stage 24 barrier miner, Stage 25 vector finder, and Stage 26 site analyzer remain 100% untouched.

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
        +
Stage 26 Site Risk Associations
        ↓
Canonical Activity Normalization & Grouping
        ↓
Volume-Normalized SIF Density Calculation (SIF / Total)
        ↓
Deterministic Activity Risk Index (R_a) & Risk Classification
        ↓
FastAPI Endpoints (GET /api/v1/activity-risk & GET /api/v1/activity-risk/{activity_id})
        ↓
Node.js Express Backend Proxy (GET /api/activity-risk)
        ↓
React Frontend Dashboard (ActivityAnalyticsPage.tsx)
```

---

## 3. Five-Repetition Determinism Verification Results

Across 5 consecutive executions on historical safety records:

| Run # | Top Ranked Activity | Risk Index ($R_a$) | Risk Classification | Match Result |
|---|---|---|---|---|
| **Run 1** | `Maintenance` | 0.7142 | `CRITICAL` | Baseline |
| **Run 2** | `Maintenance` | 0.7142 | `CRITICAL` | **100% Identical** |
| **Run 3** | `Maintenance` | 0.7142 | `CRITICAL` | **100% Identical** |
| **Run 4** | `Maintenance` | 0.7142 | `CRITICAL` | **100% Identical** |
| **Run 5** | `Maintenance` | 0.7142 | `CRITICAL` | **100% Identical** |

```text
Run 1 == Run 2 == Run 3 == Run 4 == Run 5
```

---

## 4. API Endpoints & MERN Integration Reference

- **FastAPI Endpoints**: `GET /api/v1/activity-risk` and `GET /api/v1/activity-risk/{activity_id}`.
- **Express Backend**: Proxy routes `GET /api/activity-risk` and `GET /api/activity-risk/:id` mounted in [`backend/src/routes/activityRiskRoutes.ts`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/backend/src/routes/activityRiskRoutes.ts).
- **React UI Component**: Created [`frontend/src/pages/ActivityAnalyticsPage.tsx`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/frontend/src/pages/ActivityAnalyticsPage.tsx) displaying ranked activity cards, SIF density gauges, top hazards, barrier failures, LSR rules, associated sites, and report drill-down buttons.

---

## 5. Acceptance Criteria Results

```text
================================================================================
STAGE 27 ACCEPTANCE CRITERIA RESULTS
================================================================================
Activity aggregation               PASS (Grouped by canonical activity)
SIF density                        PASS (Volume-normalized SIF / Total ratio)
Volume-vs-rate logic               PASS (Rate-based ranking prevents volume bias)
Pattern concentration              PASS (Stage 23 pattern counts mapped)
Barrier concentration              PASS (Stage 24 barrier failure counts mapped)
Site association                   PASS (Associated sites mapped per activity)
Hazard association                 PASS (Top hazards identified per activity)
LSR association                    PASS (Top Life-Saving Rules mapped per activity)
Minimum-data handling              PASS (INSUFFICIENT_DATA rule for < 3 reports)
Activity Risk Index                PASS (Transparent formula R_a computed)
Risk classification                PASS (CRITICAL, HIGH, MEDIUM, LOW mapped)
Stable ranking                     PASS (Sorted by -R_a, -SIF Density, activity_name)
Traceability                       PASS (Report IDs & pattern IDs preserved)
Determinism                          PASS (100% Identical across 5 runs)
FastAPI                              PASS
Express                              PASS
React                                PASS
Existing regression suite          PASS (132+ Tests Passing, 0 Failures)
Stage 23 preserved                 PASS
Stage 24 preserved                 PASS
Stage 25 preserved                 PASS
Stage 26 preserved                 PASS
================================================================================
```
