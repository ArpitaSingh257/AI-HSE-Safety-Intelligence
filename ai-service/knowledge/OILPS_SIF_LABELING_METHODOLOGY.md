# OILPS SIF Potential Labeling Methodology & Provenance Framework
**Document Purpose:** Define the scientific, barrier-centric criteria for Serious Injury & Fatality (SIF) potential labeling in the OILPS AI/NLP pipeline.
**Governing Principle:** SIF Potential is an objective property of **Hazardous Energy Exposure + Critical Safety Barrier Breakdown**, strictly distinguished from actual injury outcome and distinct reporting classifications.

---

## 1. Distinction Between Event Classifications & SIF Potential

To maintain complete scientific defensibility, we explicitly decouple four distinct concepts in safety reporting:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Actual Fatal Outcome (IOGP_FATAL)                                       │
│    - Realized event resulting in one or more occupational deaths.           │
│    - Source-grounded SIF Positive (Realized Catastrophic).                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. High Potential Event (IOGP_HPE)                                          │
│    - An event/near-miss with realistic potential for fatality/disabling     │
│      injury under realistic alternate circumstances.                        │
│    - Source-grounded SIF Positive (Explicit IOGP Definition).               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. Tier 1 Process Safety Event (IOGP_SPI)                                   │
│    - Unplanned Loss of Primary Containment (LOPC) exceeding API RP 754      │
│      chemical/flammable release quantity thresholds.                        │
│    - NOT explicitly labeled as "SIF" by IOGP.                              │
│    - OILPS Label: DERIVED_SOURCE_RULE (Mapped via explicit Energy-Barrier). │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. Regulatory Severity Records (OSHA)                                       │
│    - Occupational events recording medical outcomes (hospitalization,       │
│      amputation) without inherent high-energy potential equivalence.        │
│    - OILPS Label: REVIEW_REQUIRED (Awaiting human/domain review).          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Source-by-Source SIF Provenance Analysis

### A. IOGP High Potential Event Reports (`IOGP_HPE` — 97 Records)
- **Source Label Nature:** Explicit High Potential Event.
- **SIF Label Assignment:** `verified_sif_label = 1`
- **SIF Label Type:** **`SOURCE_GROUNDED`**
- **Scientific Justification:** The official IOGP Standard (Report 459 / Report 423) defines a High Potential Event (HiPo) strictly as: *"Any incident or near-miss that could have reasonably resulted in one or more fatalities or permanent disabling injuries under realistic alternate circumstances."* The source itself establishes direct equivalence to SIF potential.

### B. IOGP Fatal Incident Reports (`IOGP_FATAL` — 13 Records)
- **Source Label Nature:** Investigated Fatal Occurrence.
- **SIF Label Assignment:** `verified_sif_label = 1`
- **SIF Label Type:** **`SOURCE_GROUNDED`**
- **Scientific Justification:** Fatal incidents represent the realized end of the SIF spectrum resulting from uncontrolled high energy release or barrier failure.

### C. IOGP Tier 1 Process Safety Events (`IOGP_SPI` — 190 Records)
- **Source Label Nature:** Tier 1 Loss of Primary Containment (LOPC) per API RP 754 / IOGP Report 456.
- **SIF Label Assignment:** `verified_sif_label = 1`
- **SIF Label Type:** **`DERIVED_SOURCE_RULE`** (NOT Source-Grounded)
- **Exact Derivation Rule (`RULE_SPI_TIER1_SIF`):**
  - *Premise:* IOGP reports these as Tier 1 Process Safety Events (uncontrolled toxic/flammable releases), not explicitly as SIF.
  - *OILPS Rule:* Because Tier 1 LOPC events in operational areas (such as high-pressure natural gas releases >1000 kg, sour H2S gas releases >5 ppm, wellhead leaks, and tank overfill fires) involve hazardous chemical/thermal energy exceeding critical containment barriers, they meet the OILPS precursor criteria for credible catastrophic escalation.
  - *Provenance Transparency:* Preserved as `DERIVED_SOURCE_RULE` to make clear that IOGP provided the Tier 1 PSE designation, while the SIF-potential equivalence is derived by our project methodology.

### D. OSHA Workplace Safety Dataset (`OSHA` — 4,229 Records)
- **Source Label Nature:** Federal Regulatory Non-Fatal & Fatal Inspection Records.
- **SIF Label Assignment:** `verified_sif_label = ""` (Unassigned)
- **SIF Label Type:** **`UNANNOTATED`** (`sif_annotation_status = 'REVIEW_REQUIRED'`)
- **Scientific Justification:** In the OSHA dataset, fields like `Hospitalized`, `Amputation`, and `Loss of Eye` record medical outcomes, not potential. A minor fingertip pinch or mild heat exhaustion is hospitalized but non-SIF; conversely, a high-pressure line blowout where workers stepped away has zero hospitalization but high SIF potential.
- **Rule:** No SIF label is assigned to OSHA records without human/domain verification against the Energy-Barrier decision tree.

---

## 3. Summary of Label Types

| Source Tag | Document | Record Count | Original Source Label | OILPS SIF Label | SIF Label Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `IOGP_HPE` | `High Potential Event Reports.pdf` | **97** | High Potential Event | `1` | **`SOURCE_GROUNDED`** |
| `IOGP_FATAL`| `Safety performance indicators.pdf` | **13** | Fatal Incident | `1` | **`SOURCE_GROUNDED`** |
| `IOGP_SPI` | `Safety performance indicators.pdf` | **190** | Tier 1 PSE (LOPC) | `1` | **`DERIVED_SOURCE_RULE`** |
| `OSHA` | `January2015toNovember2025.csv` | **4,229** | Regulatory Severity | *Unassigned* | **`UNANNOTATED`** (`REVIEW_REQUIRED`) |
| **TOTAL** | **All Sources** | **4,529** | — | — | — |
