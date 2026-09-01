# STAGE 31B — MERN INTEGRATION OF SEVERITY VS RECURRENCE RISK MATRIX REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Stage**: Stage 31B (MERN Stack Integration of Severity vs Recurrence Risk Matrix)  
**Status**: COMPLETE & VERIFIED (PASS)  
**Integration Stack**: React 18 (Vite) → Express.js (Node) → FastAPI (Python 3.11)  

---

## 1. Executive Summary

Stage 31B connects the Stage 31 **Severity vs Recurrence Risk Matrix Engine** into the MERN web application.

### End-to-End Architecture
```text
HSE User (Browser)
   │  GET /api/risk-matrix
   ▼
React RiskMatrixPage (frontend/src/pages/RiskMatrixPage.tsx)
   │  Axios HTTP client via riskMatrixService
   ▼
Express Backend (backend/src/routes/riskMatrixRoutes.ts)
   │  Proxy controller via fetchAiRiskMatrix()
   ▼
FastAPI Microservice (ai-service/app/api/v1/endpoints/risk_matrix.py)
   │  Executes RiskMatrixEngine (ai-service/inference/risk_matrix_engine.py)
   ▼
Deterministic JSON Response (~1,554 2D Coordinate Items)
```

---

## 2. API Endpoints & Route Definitions

| Layer | Endpoint | Method | Response Model / Handler | Status |
|---|---|---|---|---|
| **FastAPI** | `/api/v1/risk-matrix` | GET | `RiskMatrixListResponse` | **200 OK** |
| **FastAPI** | `/api/v1/risk-matrix/{id}` | GET | `RiskMatrixItemSchema` | **200 OK / 404** |
| **Express** | `/api/risk-matrix` | GET | `getRiskMatrix()` controller | **200 OK** |
| **Express** | `/api/risk-matrix/:id` | GET | `getRiskMatrixItemById()` controller | **200 OK / 404** |

---

## 3. UI Component & 2D Visualization ([`RiskMatrixPage.tsx`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/frontend/src/pages/RiskMatrixPage.tsx))

1. **Interactive 4-Quadrant Visual Grid Layout**:
   - **High Severity + High Recurrence**: `CRITICAL PRIORITY` (Red container).
   - **High Severity + Low Recurrence**: `HIGH-POTENTIAL / RARE` (Amber container).
   - **Low Severity + High Recurrence**: `FREQUENT / LOWER-POTENTIAL` (Blue container).
   - **Low Severity + Low Recurrence**: `LOW PRIORITY MONITOR` (Emerald container).
2. **Governance & Decision-Support Notice**:
   - Explicitly clarifies: *"Severity (y-axis) represents historical SIF precursor density; Recurrence (x-axis) represents historical report frequency. Quadrant placements classify preventative focus and do not predict accident probabilities."*
3. **Traceability & Cross-Stage Links**:
   - Stage 30 Priorities (`/priorities`).
   - Stage 24 Barrier Failure patterns (`/barrier-patterns`).
   - Stage 23 Precursor patterns (`/patterns`).
   - Affected Site Risk profiles (`/sites`) and Activity Risk profiles (`/activities`).
   - Supporting Historical Report drill-down (`/reports/:id`).

---

## 4. Acceptance Criteria & Test Results

```text
================================================================================
STAGE 31B INTEGRATION ACCEPTANCE CRITERIA RESULTS
================================================================================
FastAPI integration             PASS (Schema validated, 200 OK)
Express integration             PASS (Node proxy controller connected)
React integration               PASS (RiskMatrixPage.tsx rendered)
2D matrix                       PASS (4-quadrant visual layout)
Severity axis                   PASS (Historical SIF precursor rate mapped)
Recurrence axis                 PASS (Historical report frequency mapped)
Quadrant assignment             PASS (Critical, High-Pot Rare, Frequent, Monitor)
Threshold display               PASS (0.50 / 0.50 cutoffs communicated)
Filters                         PASS (Quadrant & entity type filters)
Search                          PASS (Search query input for name/ID)
Detail view                     PASS (Detailed coordinates & rationale inspect panel)
Traceability                    PASS (Preserves report IDs, pattern IDs, site/activity IDs)
Priority navigation             PASS (Navigates to /priorities)
Pattern navigation             PASS (Navigates to /patterns)
Barrier navigation             PASS (Navigates to /barrier-patterns)
Site navigation                PASS (Navigates to /sites)
Activity navigation            PASS (Navigates to /activities)
Report drill-down               PASS (Navigates to /reports/:id)
Insufficient-data handling      PASS (Clean INSUFFICIENT_DATA badge)
Error handling                  PASS (Graceful 404 & service fallback)
RBAC                            PASS (Authenticated session protection)
Large-result handling           PASS (Scrollable quadrant list over ~1,554 items)
AI regression                  PASS (161+ PyTest suite passed)
Previous stages preserved      PASS (Stages 6, 7, 20, 23-31 untouched)
================================================================================
```

---

```text
STAGE 31B STATUS:
PASS

SEVERITY VS RECURRENCE RISK MATRIX:
READY FOR USE
```
