# STAGE 24 — BARRIER FAILURE PATTERN MINING REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Stage**: Stage 24 (Barrier Failure Pattern Mining)  
**Status**: COMPLETED, HARDENED & FULLY VERIFIED  
**Final Status**: `STAGE 24 STATUS: PASS`  
**Acceptance Criteria**: `ALL ACCEPTANCE CRITERIA PASSED`  

---

## 1. Executive Summary

Stage 24 transitions the system from general precursor pattern detection (Stage 23) to **specific repeated safety barrier failure mining**. Using a deterministic canonical normalization layer, free-text barrier descriptions across historical incidents are mapped to canonical safety control failure categories (e.g., `ENERGY_ISOLATION_CONTROL_FAILURE`, `ATMOSPHERIC_GAS_MONITORING_FAILURE`, `MECHANICAL_LIFTING_RIGGING_FAILURE`).

Unmapped or ambiguous descriptions explicitly map to `UNKNOWN`. Every mined pattern maintains full traceability to underlying `incident_ids`, associated activities, hazards, locations, and Life-Saving Rules.

**Zero frozen neural network weights were modified or retrained.** Stage 6 SIF, Stage 7 LSR, FAISS vector index, RAG engine, and Stage 20 Grounding Validator remain 100% untouched.

---

## 2. Canonical Normalization Mapping Table

| Canonical Barrier Concept | Keywords / Mappings | Display Name |
|---|---|---|
| `ENERGY_ISOLATION_CONTROL_FAILURE` | `isolation`, `lockout`, `tagout`, `loto`, `de-energize`, `valve bleeder`, `pressurized line` | Energy Isolation Control Failure |
| `ATMOSPHERIC_GAS_MONITORING_FAILURE` | `gas test`, `gas monitor`, `h2s`, `toxic gas`, `explosimeter`, `stratification` | Atmospheric & Toxic Gas Monitoring Control Failure |
| `MECHANICAL_LIFTING_RIGGING_FAILURE` | `crane`, `sling`, `rigging`, `suspended load`, `hoist`, `tag line`, `load drop` | Mechanical Lifting & Rigging Barrier Failure |
| `FALL_PROTECTION_BARRIER_FAILURE` | `harness`, `lanyard`, `lifeline`, `scaffold`, `guardrail`, `anchor point` | Working at Height & Fall Protection Barrier Failure |
| `HOT_WORK_PERMIT_CONTAINMENT_FAILURE` | `hot work`, `welding`, `cutting`, `fire watch`, `sparks`, `flash fire` | Hot Work Spark Containment & Ignition Control Failure |
| `PERMIT_TO_WORK_VERIFICATION_FAILURE` | `ptw`, `permit to work`, `jsa`, `job safety analysis`, `toolbox talk` | Permit-to-Work & Job Safety Analysis Barrier Failure |
| `UNKNOWN` | Unspecified, ambiguous, or generic control statements | Unspecified Barrier Failure |

---

## 3. General → Specific Architecture

```text
Stage 23 Recurring Precursor Pattern
        ↓
Stage 24 Repeated Safety Barrier Failure
        ↓
Associated Dimensions (Activity, Hazard, LSR, Site, SIF Rate)
        ↓
Traceable Incident Report IDs & Evidence Quotes
```

---

## 4. Five-Repetition Determinism Verification Results

Across 5 consecutive executions on the historical dataset:

| Run # | Discovered Barrier Patterns | Top Barrier Code | SIF Density | Match Result |
|---|---|---|---|---|
| **Run 1** | 6 Barrier Patterns | `BAR-7E9A12` (`ENERGY_ISOLATION_CONTROL_FAILURE`) | 100.0% | Baseline |
| **Run 2** | 6 Barrier Patterns | `BAR-7E9A12` (`ENERGY_ISOLATION_CONTROL_FAILURE`) | 100.0% | **100% Identical** |
| **Run 3** | 6 Barrier Patterns | `BAR-7E9A12` (`ENERGY_ISOLATION_CONTROL_FAILURE`) | 100.0% | **100% Identical** |
| **Run 4** | 6 Barrier Patterns | `BAR-7E9A12` (`ENERGY_ISOLATION_CONTROL_FAILURE`) | 100.0% | **100% Identical** |
| **Run 5** | 6 Barrier Patterns | `BAR-7E9A12` (`ENERGY_ISOLATION_CONTROL_FAILURE`) | 100.0% | **100% Identical** |

```text
Run 1 == Run 2 == Run 3 == Run 4 == Run 5
```

---

## 5. API & MERN Integration Reference

- **FastAPI Endpoints**: `GET /api/v1/barrier-patterns` and `GET /api/v1/barrier-patterns/{barrier_pattern_id}`.
- **Express Backend**: Mounted at `GET /api/barrier-patterns` and `GET /api/barrier-patterns/:id` in [`backend/src/routes/barrierPatternsRoutes.ts`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/backend/src/routes/barrierPatternsRoutes.ts).
- **React UI**: Rendered in [`frontend/src/pages/BarrierFailureExplorerPage.tsx`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/frontend/src/pages/BarrierFailureExplorerPage.tsx) accessible from the main navigation sidebar.

---

## 6. Acceptance Criteria Results

```text
================================================================================
STAGE 24 ACCEPTANCE CRITERIA RESULTS
================================================================================
Barrier failure detection          PASS
Barrier normalization              PASS
Minimum support                    PASS
Multi-barrier handling             PASS
Traceability                       PASS
SIF association                    PASS
Activity/Hazard/Site association   PASS
LSR association                    PASS
Determinism                        PASS
FastAPI                            PASS
Express                            PASS
React                              PASS
Existing regression suite          PASS (114+ Tests Passing, 0 Failures)
Stage 23 preserved                 PASS
================================================================================
```
