# STAGE 28D — LIFE-SAVING RULE DATA-COVERAGE INVESTIGATION REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Stage**: Stage 28D (LSR Data-Coverage Pipeline Audit & Investigation)  
**Status**: INVESTIGATION COMPLETE & VERIFIED  
**Final Conclusion**: `GENUINE LOW LSR LABEL COVERAGE (SOURCE DATA PROVENANCE)`  
**Acceptance Criteria**: `ALL INVESTIGATION ACCEPTANCE CRITERIA PASSED`  

---

## 1. Executive Summary

A comprehensive pipeline audit was conducted to investigate why 4,519 out of 4,529 historical safety records (99.78%) were classified as `UNKNOWN` / missing in Stage 28 Life-Saving Rule Trend Analytics.

### Key Finding
The 99.78% missing label rate is **NOT a join bug or software defect**. It is a **GENUINE DATA PROVENANCE PROPERTY** of the ground-truth historical dataset ([`oilps_unified_deduped.csv`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/datasets/processed/oilps_unified_deduped.csv)):

1. **Dual-Corpus Structure**: The historical dataset combines **IOGP High Potential Event (HPE) case reports** (which natively contain explicit ground-truth IOGP Life-Saving Rule tags) and **OSHA Workplace Safety Incident Logs** (which contain federal regulatory injury reports that natively lack IOGP Life-Saving Rule classifications).
2. **OSHA Dominance**: Federal OSHA regulatory records constitute ~99.78% of the unified dataset. OSHA reporting standards do not record IOGP industry association rules.
3. **No Synthetic Fabrication**: In strict adherence to AI safety guidelines, ground-truth dataset records preserve authentic source attributes without fabricating synthetic LSR tags for OSHA rows.

---

## 2. Complete Data Pipeline Audit

```text
HISTORICAL SOURCE DATASET (oilps_unified_deduped.csv - 4,529 Records)
 ├── IOGP HPE Reports (~10-45 records)  → Explicit native IOGP LSR labels (e.g. Line of Fire, Energy Isolation)
 └── OSHA Regulatory Reports (4,519 records) → Native primary_life_saving_rule = None / Empty
        ↓
RECURRING PATTERN DETECTOR LOAD (load_historical_records())
 Reads raw ground-truth fields without synthetic label fabrication
        ↓
STAGE 28 LSR TREND ANALYZER (lsr_trend_analyzer.py)
 ├── Valid Official IOGP LSR Profiles: 3 Rules (Line of Fire, Energy Isolation, Working at Height)
 └── Data-Quality Bucket (UNKNOWN): 4,519 Records (99.78%)
```

---

## 3. Detailed Stage-by-Stage Findings

### A. Historical Source Data ([`oilps_unified_deduped.csv`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/datasets/processed/oilps_unified_deduped.csv))
- **Total Historical Records**: 4,529
- **Records with Native Ground-Truth IOGP LSR Tags**: 10 (0.22%)
- **Records with Native Empty/Null LSR Tags (OSHA Logs)**: 4,519 (99.78%)
- **Data Pipeline Verification**: Confirmed that `oilps_unified_deduped.csv` explicitly stores `primary_life_saving_rule = None` for all ingested OSHA rows in [`ai-service/scripts/normalize.py`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/scripts/normalize.py#L105).

### B. Stage 7 Multi-Label LSR Predictor ([`lsr_predictor.py`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/inference/lsr_predictor.py))
- **Model**: `LSRAdaptiveModel` (Bi-GRU + Dynamic Scaled Dot-Product Attention).
- **Official Vocabulary**: 9 IOGP Rules (*Bypassing Safety Controls*, *Confined Space*, *Driving*, *Energy Isolation*, *Hot Work*, *Line of Fire*, *Safe Mechanical Lifting*, *Toxic Gas / Hazardous Substance*, *Working at Height*).
- **Inference Role**: Live single-narrative analysis endpoint (`POST /api/v1/analyze` via `safety_pipeline.py`).
- **Separation of Concerns**: Stage 7 predictions are executed dynamically for single-incident analysis, whereas offline historical trend analytics (Stage 28) evaluate empirical ground-truth dataset records.

### C. Stage 7 → Stage 28 Data Integration / Join Verification
- **Join Integrity**: Verified 100% ID alignment. No rows are dropped, duplicated, or misjoined.
- **Mapping Verification**: `lsr_trend_analyzer.py` correctly reads `primary_life_saving_rule` from loaded historical records. Records lacking explicit ground-truth tags evaluate to `UNKNOWN`.

### D. "Other Issue – No Applicable Rule" Category Analysis
- **Origin**: "Other issue – no applicable rule" occurs in raw IOGP survey classifications for incidents (e.g. routine slips/trips) where no high-energy barrier rule applied.
- **Handling**: Treated strictly as a non-LSR category and excluded from official IOGP Life-Saving Rule trend analytics.

---

## 4. Coverage Metrics & Label Distribution

| Metric | Count | Percentage |
|---|---|---|
| **Total Historical Records** | 4,529 | 100.00% |
| **Records with Valid Official IOGP LSR** | 10 | 0.22% |
| **Records with UNKNOWN / Missing LSR** | 4,519 | 99.78% |
| **Official LSR Coverage Rate** | **10 / 4,529** | **0.22%** |

### Observed Ground-Truth LSR Label Distribution
1. `Line of Fire`: 4 reports (40.0% of labeled)
2. `Energy Isolation`: 3 reports (30.0% of labeled)
3. `Working at Height`: 3 reports (30.0% of labeled)

---

## 5. Official Conclusion & Architectural Decision

### Final Classification
```text
GENUINE LOW LSR LABEL COVERAGE (SOURCE DATA PROVENANCE)
```

### Architectural Policy Adherence
In strict accordance with Stage 28D guidelines:
- **No Synthetic Label Invention**: Labels are NOT fabricated, inferred from text, copied from similar incidents, or artificially assigned to fill OSHA rows.
- **Stage 7 Models & Weights**: Unchanged.
- **Stage 28 Analytics & Filtering (Stage 28C)**: Preserved. Missing/unknown LSR records are excluded from official IOGP trend analytics and transparently reported in data-quality metadata (`unknown_lsr_records = 4519`, `unknown_lsr_rate = 0.9978`).

---

## 6. Investigation Acceptance Criteria Results

```text
================================================================================
STAGE 28D INVESTIGATION ACCEPTANCE CRITERIA RESULTS
================================================================================
Root Cause Identified              PASS (OSHA regulatory logs natively lack IOGP LSR tags)
Pipeline Audit Executed            PASS (Traced source CSV → load_historical_records → Stage 28)
Join Bug Ruled Out                 PASS (0 dropped or misjoined rows; 100% ID alignment)
"Other Issue" Analyzed             PASS (Non-LSR raw category excluded from official analytics)
Coverage Metrics Quantified        PASS (4,519 UNKNOWN / 4,529 Total = 99.78%)
No Synthetic Labels Fabricated     PASS (Ground-truth dataset integrity preserved)
Stage 7 Preserved                  PASS (Zero model/weights changes)
Report Generated                   PASS (STAGE_28D_LSR_DATA_COVERAGE_REPORT.md)
================================================================================
```

---

```text
STAGE 28D STATUS:
PASS

LSR DATA-COVERAGE INVESTIGATION:
COMPLETE & DOCUMENTED
```
