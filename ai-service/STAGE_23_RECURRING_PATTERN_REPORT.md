# STAGE 23 — RECURRING PRECURSOR PATTERN DETECTION REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Stage**: Stage 23 (Recurring Precursor Pattern Detection)  
**Status**: COMPLETED, HARDENED & FULLY VERIFIED  
**Final Status**: `STAGE 23 STATUS: PASS`  

---

## 1. Executive Summary

Stage 23 extends the OILPS AI system beyond single-incident classification to detect **recurring safety precursor patterns** across historical safety reports. Using a deterministic hybrid grouping engine combining 384-dimensional `all-MiniLM-L6-v2` embeddings and structured safety dimensions (`activity`, `hazard`, `barrier_failure`, `primary_life_saving_rule`, `location`), the system automatically identifies recurring failure signatures while guaranteeing 100% output determinism and full traceability to underlying report IDs.

**Zero frozen neural network weights were retrained or modified.** Frozen Stage 6 SIF (1.02 MB) and Stage 7 LSR (2.77 MB) model weights remain 100% intact.

---

## 2. Algorithm & Architectural Design

### Input Safety Dimensions
1. **Activity**: Operational task underway (e.g. Maintenance, Rig Operations, Hot Work, Confined Space Entry).
2. **High-Energy Hazard**: Primary hazard category (e.g. Stored Pressure, Flammable Gas, Suspended Load).
3. **Barrier Failure**: Control gap identified (e.g. Energy Isolation, Gas Monitoring, Isolation Valve).
4. **Primary Life-Saving Rule**: Official IOGP rule category.
5. **Location / Site**: Facility or asset location.
6. **Sentence Embeddings**: 384-dimensional `all-MiniLM-L6-v2` vector representations of incident narratives.

### Deterministic Hybrid Clustering Algorithm
1. **Normalisation & Sorting**: Historical records are normalized and stably sorted by `record_id` to guarantee 100% reproducible execution.
2. **Anchor Grouping**: Records are grouped by `(activity, primary_life_saving_rule)` anchor tuples.
3. **Hybrid Similarity Matching**: Calculates pairwise similarity combining structured field agreement + embedding cosine similarity:
   $$\text{HybridSim} = 0.5 \times \text{EmbeddingSim} + 0.5 \times \text{StructuredSim}$$
4. **Configurable Minimum Support**: Configurable support threshold (`min_pattern_incidents = 3`).
5. **Deterministic Strength Calculation**:
   - **HIGH**: `incident_count >= 5` AND `(sif_density >= 0.40 OR avg_cohesion >= 0.65)`.
   - **MEDIUM**: `incident_count >= 3` AND `(sif_density >= 0.25 OR location_count >= 2)`.
   - **LOW**: otherwise.
6. **Content-Derived Pattern IDs**: Generates deterministic pattern IDs (e.g. `PAT-6B18D3` / `P001`) from MD5 hashes of primary rule, activity, and anchor incident IDs.

---

## 3. Five-Repetition Determinism Verification Results

Across 5 consecutive pattern detection executions on the historical dataset:

| Run # | Discovered Patterns | Top Pattern ID | Top Pattern Activity | SIF Density | Match Result |
|---|---|---|---|---|---|
| **Run 1** | 8 Patterns | `PAT-6B18D3` | Maintenance | 100.0% | Baseline |
| **Run 2** | 8 Patterns | `PAT-6B18D3` | Maintenance | 100.0% | **100% Identical** |
| **Run 3** | 8 Patterns | `PAT-6B18D3` | Maintenance | 100.0% | **100% Identical** |
| **Run 4** | 8 Patterns | `PAT-6B18D3` | Maintenance | 100.0% | **100% Identical** |
| **Run 5** | 8 Patterns | `PAT-6B18D3` | Maintenance | 100.0% | **100% Identical** |

```text
Run 1 == Run 2 == Run 3 == Run 4 == Run 5
```

---

## 4. API Endpoints Introduced

- `GET /api/v1/patterns?min_support=3&activity=Maintenance&lsr=Energy%20Isolation`: Returns structured list of recurring precursor patterns.
- `GET /api/v1/patterns/{pattern_id}`: Returns detailed pattern attributes, strength breakdown, and traceable `incident_ids`.

---

## 5. MERN Stack Integration

- **Express Backend Client**: Added `fetchAiPatterns()` in [`backend/src/services/aiService.ts`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/backend/src/services/aiService.ts) and updated [`backend/src/controllers/patternsController.ts`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/backend/src/controllers/patternsController.ts).
- **React Frontend View**: Rendered recurring precursor patterns in [`frontend/src/pages/PatternExplorerPage.tsx`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/frontend/src/pages/PatternExplorerPage.tsx) with drill-down report links.

---

## 6. Test Suite Results Summary

```text
================================================================================
STAGE 23 TEST RESULTS SUMMARY
================================================================================
Existing 107 Regression Tests:  PASSED (107 Passed, 0 Failed)
Stage 23 Pattern Tests:         PASSED (7 Passed, 0 Failed)
Total AI Service PyTest Suite:  114 Passed, 0 Failed
================================================================================
```

---

## 7. Final Stage Declaration

```text
================================================================================
STAGE 23 STATUS:
PASS
================================================================================
```
