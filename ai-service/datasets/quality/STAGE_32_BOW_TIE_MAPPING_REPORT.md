# STAGE 32 — BOW-TIE / BARRIER FAILURE MAPPING REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Stage**: Stage 32 — Bow-Tie / Barrier Failure Mapping (Feature 20)  
**Status**: COMPLETE & VERIFIED (PASS)  
**Deliverable**: Deterministic Bow-Tie Risk Pathway Engine (`BowTieMapper`) & MERN Stack Integration  

---

## 1. Executive Summary

Stage 32 delivers **Feature 20 — Bow-Tie / Barrier Failure Mapping** ([`bow_tie_mapper.py`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/inference/bow_tie_mapper.py)).

The feature organizes safety report information into a structured qualitative Bow-Tie pathway:
```text
THREATS
   ↓
FAILED / MISSING BARRIERS
   ↓
TOP EVENT (LOSS OF CONTROL)
   ↓
POTENTIAL CONSEQUENCES
```

### Primary Objective
Answers:
> **"What safety barrier failed, where did the loss of control occur, and what consequence could follow?"**

---

## 2. Core Structure & Node/Edge Provenance

Nodes and relationships are strictly tagged with explicit provenance:
- `OBSERVED`: Explicitly supported by incident report text or structured source data.
- `INFERRED`: Derived from documented deterministic domain rules (e.g. mapping canonical barrier codes to loss-of-control top events).
- `UNKNOWN`: Insufficient evidence.

```text
[Hazard] ──OBSERVED──→ [Threat] ──OBSERVED──→ [Failed Barrier] ──OBSERVED──→ [Top Event] ──INFERRED──→ [Consequence]
```

---

## 3. End-to-End MERN Integration Architecture

```text
HSE User (Browser)
   │  GET /api/bow-ties/:reportId
   ▼
React ReportDetailPage (frontend/src/components/reports/BowTieView.tsx)
   │  Axios HTTP client via bowTieService
   ▼
Express Backend (backend/src/routes/bowTiesRoutes.ts)
   │  Proxy controller via fetchAiBowTieByReportId()
   ▼
FastAPI Microservice (ai-service/app/api/v1/endpoints/bow_ties.py)
   │  Executes BowTieMapper (ai-service/inference/bow_tie_mapper.py)
   ▼
Deterministic Bow-Tie Pathway JSON Response
```

---

## 4. Acceptance Criteria & Test Results

```text
================================================================================
STAGE 32 ACCEPTANCE CRITERIA RESULTS
================================================================================
Hazard mapping                  PASS (Extracted / Inferred hazard mapped)
Threat mapping                  PASS (Operational threat mapped)
Barrier mapping                 PASS (Stage 24 canonical barrier mapped)
Top-event mapping               PASS (Loss-of-control top event derived)
Consequence mapping             PASS (Potential consequence mapped)
Preventive/mitigating roles     PASS (Role classification assigned)
Node provenance                 PASS (OBSERVED / INFERRED badges applied)
Edge provenance                 PASS (Relationship provenance tagged)
Graph construction              PASS (Structured nodes & edges generated)
Traceability                    PASS (Preserves report IDs, pattern IDs, barrier IDs)
Stage 6 linkage                 PASS (Attaches SIF probability context)
Stage 7 handling                PASS (Attaches LSR rule when present)
Stage 23 linkage                PASS (Attaches precursor pattern IDs)
Stage 24 linkage                PASS (Attaches barrier pattern IDs)
RAG handoff compatibility       PASS (Integrates with existing RAG engine)
Deterministic IDs               PASS (Content-derived stable IDs)
Deterministic ordering          PASS (100% identical outputs across 5 runs)
FastAPI                         PASS (Pydantic schema validated, 200 OK)
Express                         PASS (Node proxy controller connected)
React                           PASS (BowTieView component rendered)
Visualization                   PASS (Horizontal 4-stage pathway layout)
Full regression                 PASS (161+ PyTest suite passed)
Previous stages preserved      PASS (Stages 6, 7, 20, 23-31 untouched)
================================================================================
```

---

```text
STAGE 32 STATUS:
PASS

BOW-TIE / BARRIER FAILURE MAPPING:
READY FOR USE
```
