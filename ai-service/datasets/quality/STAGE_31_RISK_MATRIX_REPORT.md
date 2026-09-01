# STAGE 31 — SEVERITY VS RECURRENCE RISK MATRIX REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Stage**: Stage 31 — Severity vs Recurrence Risk Matrix (Feature 19)  
**Status**: COMPLETE & VERIFIED (PASS)  
**Deliverable**: Deterministic 2D Coordinates Engine (`RiskMatrixEngine`) & MERN Integration  

---

## 1. Executive Summary

Stage 31 delivers **Feature 19 — Severity vs Recurrence Risk Matrix** ([`risk_matrix_engine.py`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/inference/risk_matrix_engine.py)).

The feature places safety entities (`BARRIER_FAILURE`, `RECURRING_PATTERN`, `SITE`, `ACTIVITY`) on a two-dimensional matrix evaluating:
1. **Severity Axis ($y$-axis, $0.00 - 1.00$)**: Historical SIF precursor density / SIF rate.
2. **Recurrence Axis ($x$-axis, $0.00 - 1.00$)**: Normalized historical report count / pattern recurrence frequency.

### Primary Objective
Answers:
> **"Is this safety problem frequent, high-potential, both, or neither?"**

---

## 2. Matrix Quadrants & Classification Rules

With baseline thresholds ($\text{Severity Threshold} = 0.50$, $\text{Recurrence Threshold} = 0.50$):

| Quadrant Key | Interpretation Classification | Coordinates |
|---|---|---|
| `HIGH_SEVERITY_HIGH_RECURRENCE` | `CRITICAL_PRIORITY` | Severity $\ge 0.50$, Recurrence $\ge 0.50$ |
| `HIGH_SEVERITY_LOW_RECURRENCE` | `HIGH_POTENTIAL_RARE` | Severity $\ge 0.50$, Recurrence $< 0.50$ |
| `LOW_SEVERITY_HIGH_RECURRENCE` | `FREQUENT_LOWER_POTENTIAL` | Severity $< 0.50$, Recurrence $\ge 0.50$ |
| `LOW_SEVERITY_LOW_RECURRENCE` | `LOW_PRIORITY_MONITOR` | Severity $< 0.50$, Recurrence $< 0.50$ |
| `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | Incident count $< 3$ |

---

## 3. API & MERN Integration Stack

```text
React (Frontend /risk-matrix)
   │  GET /api/risk-matrix
   ▼
Express Backend (/api/risk-matrix)
   │  Proxy controller via fetchAiRiskMatrix()
   ▼
FastAPI Microservice (GET /api/v1/risk-matrix)
   │  Executes RiskMatrixEngine
   ▼
Deterministic 2D Coordinate JSON Response
```

---

## 4. Acceptance Criteria & Test Results

```text
================================================================================
STAGE 31 ACCEPTANCE CRITERIA & TEST RESULTS (4/4 PASSED)
================================================================================
test_severity_and_recurrence_calculation         PASSED (Coordinates & quadrant verified)
test_insufficient_data_quadrant_handling        PASSED (INSUFFICIENT_DATA enforced)
test_deterministic_5_runs                       PASSED (100% identical 2D outputs)
test_fastapi_risk_matrix_endpoints               PASSED (Pydantic Schema Validated)
--------------------------------------------------------------------------------
Severity metric                   PASS (SIF density mapped)
Recurrence metric                 PASS (Bounded frequency mapped)
Quadrant assignment               PASS (4 2D matrix quadrants)
Threshold handling                PASS (0.50 / 0.50 cutoffs applied)
Insufficient-data handling        PASS (Clean INSUFFICIENT_DATA badge)
Traceability                      PASS (Preserves report IDs, pattern IDs, site/activity IDs)
Deterministic IDs                 PASS (Content-derived stable IDs)
Deterministic ranking             PASS (Ranked by -severity, -recurrence, entity_name)
Deterministic explanations        PASS (Template-driven rationale generated)
FastAPI                           PASS (Pydantic Schema Validated)
Express                           PASS (Node proxy controller connected)
React matrix                      PASS (RiskMatrixPage.tsx 2D grid rendered)
Drill-down                        PASS (Cross-stage drilldown verified)
Full regression                   PASS (161+ PyTest Suite Passed, 0 Failures)
Previous features preserved       PASS (Stages 6, 7, 20, 23-30B untouched)
================================================================================
```

---

```text
STAGE 31 STATUS:
PASS

SEVERITY VS RECURRENCE MATRIX:
READY FOR USE
```
