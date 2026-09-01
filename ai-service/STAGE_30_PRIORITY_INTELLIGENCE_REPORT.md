# STAGE 30 — RISK / PRIORITY INTELLIGENCE REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Stage**: Stage 30 — Risk / Priority Intelligence (Feature 18)  
**Status**: COMPLETE & VERIFIED (PASS)  
**Deliverable**: Deterministic Risk & Priority Intelligence Engine (`PriorityIntelligenceEngine`) & MERN Integration  

---

## 1. Executive Summary

Stage 30 delivers **Feature 18 — Risk / Priority Intelligence** ([`priority_intelligence_engine.py`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/inference/priority_intelligence_engine.py)).

The system creates a unified, transparent HSE prioritization layer that synthesizes intelligence outputs across Stage 6 SIF, Stage 23 precursor patterns, Stage 24 barrier failure patterns, Stage 26 site risk profiles, Stage 27 activity risk profiles, and Stage 29 early-warning signals.

### Primary Objective
Answers:
> **"Among the detected safety problems, recurring patterns, barrier failures, sites, and activities, what should HSE focus on first?"**

---

## 2. Priority Score Formula & Weights

The Priority Score is calculated using a transparent, normalized component formula ($0.00 - 1.00$):

$$\text{Priority Score} = 0.35 \times SIF + 0.25 \times Recurrence + 0.20 \times Barrier + 0.10 \times Site/Activity + 0.10 \times Early Warning$$

- **SIF Impact ($35\%$)**: Normalized SIF precursor density for the entity.
- **Recurrence ($25\%$)**: Normalized recurrence count / pattern strength.
- **Barrier Impact ($20\%$)**: Barrier failure severity & SIF concentration.
- **Site / Activity Index ($10\%$)**: Stage 26 Site Risk Index $R_s$ or Stage 27 Activity Risk Index $R_a$.
- **Early-Warning Signal ($10\%$)**: Stage 29 early warning status (`HIGH_PRIORITY`: 1.0, `EARLY_WARNING`: 0.67, `WATCH`: 0.33, `NORMAL`: 0.0).

---

## 3. Priority Classification Levels

- **`CRITICAL`**: Priority Score $\ge 0.75$
- **`HIGH`**: Priority Score $\ge 0.55$
- **`MEDIUM`**: Priority Score $\ge 0.35$
- **`LOW`**: Priority Score $< 0.35$
- **`INSUFFICIENT_DATA`**: Supporting incident count $< 3$.

---

## 4. API & MERN Integration Stack

```text
React (Frontend /priorities)
   │  GET /api/priorities
   ▼
Express Backend (/api/priorities)
   │  Proxy controller via fetchAiPriorities()
   ▼
FastAPI Microservice (GET /api/v1/priorities)
   │  Executes PriorityIntelligenceEngine
   ▼
Deterministic Ranked JSON Response
```

---

## 5. Acceptance Criteria & Test Results

```text
================================================================================
STAGE 30 ACCEPTANCE CRITERIA & TEST RESULTS (4/4 PASSED)
================================================================================
test_priority_calculation_and_components        PASSED (Score & components verified)
test_insufficient_data_priority_handling        PASSED (INSUFFICIENT_DATA enforced)
test_deterministic_5_runs                       PASSED (100% identical outputs)
test_fastapi_priorities_endpoints               PASSED (Pydantic Schema Validated)
--------------------------------------------------------------------------------
Entity evaluation                 PASS (BARRIER_FAILURE, RECURRING_PATTERN, SITE, ACTIVITY)
SIF component                     PASS (SIF density normalized)
Recurrence component              PASS (Recurrence strength mapped)
Barrier component                 PASS (Barrier severity mapped)
Site/activity component           PASS (Stage 26/27 risk indices mapped)
Early-warning component           PASS (Stage 29 warning state mapped)
Normalization                     PASS (0.0 - 1.0 bounded components)
Priority formula                  PASS (0.35/0.25/0.20/0.10/0.10 weights applied)
Priority classification           PASS (CRITICAL, HIGH, MEDIUM, LOW, INSUFFICIENT_DATA)
Insufficient-data handling        PASS (Clean INSUFFICIENT_DATA badge)
No-double-counting                PASS (Operates on normalized component metrics)
Traceability                      PASS (Preserves report IDs, pattern IDs, site/activity/warning IDs)
Deterministic IDs                 PASS (Content-derived stable IDs)
Deterministic ranking             PASS (Ranked by -score, entity_type, entity_name)
Deterministic explanations        PASS (Template-driven rationale generated)
FastAPI                           PASS (Pydantic Schema Validated)
Express                           PASS (Node proxy controller connected)
React                             PASS (PriorityIntelligencePage.tsx rendered)
Full regression                   PASS (157+ Tests Passing, 0 Failures)
Previous stages preserved         PASS (Stages 6, 7, 20, 23-29B untouched)
================================================================================
```

---

```text
STAGE 30 STATUS:
PASS

RISK / PRIORITY INTELLIGENCE:
READY FOR USE
```
