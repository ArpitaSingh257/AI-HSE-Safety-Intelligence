# Precursor Entity Annotation Audit & Consistency Analysis
**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Audit Focus:** Precursor Information Extraction schema, entity definitions, and logical consistency between `barrier` and `barrier_failure`.

---

## 1. Investigation: Why Was `verified_barrier = 0` While `verified_barrier_failure > 0`?

### Root Cause Analysis:
1. **Source Document Structure:** In the original IOGP Process Safety PDF (`IAOGP - Safety performance indicators.pdf`), the document contains an explicit heading labeled:
   ```text
   BARRIERS:
   Hardware Barrier Failures: Process Containment
   Human Barrier Failures: Operating in accordance with procedures - PTW, Isolation of equipment
   ```
2. **Parser Mapping:** Because the IOGP source text explicitly reported *Barrier Failures*, the initial extraction script mapped this text directly into `barrier_failure` (e.g. *"Hardware Barrier Failures: Process Containment"*) and left `barrier` unpopulated.
3. **Logical Inconsistency Identified:** A barrier failure cannot exist in isolation without an underlying barrier. 

---

## 2. Definitional Clarification: `barrier` vs `barrier_failure`

To ensure scientific and logical consistency in the OILPS pipeline, we enforce the following clear boundary:

| Precursor Field | Definition | Example (Energy Isolation) | Example (Working at Height) | Example (Mechanical Lifting) |
| :--- | :--- | :--- | :--- | :--- |
| **`hazard`** | The hazardous physical/chemical energy source. | High-pressure natural gas (85 barg) | 26m elevation (Gravitational potential) | Suspended 1.8-ton drill pipe stand |
| **`barrier`** | The intended protective control or safeguard. | **Double block and bleed (DBB) isolation** | **Full body harness with 100% tie-off** | **Elevator secondary safety latch** |
| **`barrier_failure`** | The specific failure mode or human/mechanical breakdown. | **Bleed valve left unverified prior to unbolting** | **Lanyard unclipped during transition** | **Latch failed to engage under hoisting tension** |
| **`activity`** | Operational task being performed. | Gas compressor valve maintenance | Derrick casing latching | Tripping pipe on rig floor |
| **`potential_consequence`**| Worst-case credible outcome. | Flash fire / vapor cloud explosion | Fatal trauma from high fall | Fatal crush / struck-by impact |

---

## 3. Precursor Extraction Status Across Corpus

| Precursor Field | Source-Grounded (IOGP) | Candidate / Unannotated (OSHA) | Extraction Readiness for Supervised ML |
| :--- | :--- | :--- | :--- |
| `activity` | 300 | 4,229 | High (Explicit in IOGP; high-density verb phrases in OSHA) |
| `hazard` | 300 | 4,229 | High (Mapped from energy source / OSHA SourceTitle) |
| `barrier` | Grounded via taxonomy | Awaiting Entity Span Annotation | Medium (Requires span annotation on review subset) |
| `barrier_failure` | 300 | Awaiting Entity Span Annotation | Medium (Requires span annotation on review subset) |
| `potential_consequence` | 300 | 4,229 | High (Explicit in IOGP; mapped from OSHA NatureTitle) |

---

## 4. Remediation & Consistency Standard

- The updated annotation schema in [`oilps_annotation.csv`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/datasets/annotation/oilps_annotation.csv) now contains explicit, separate fields for both `verified_barrier` and `verified_barrier_failure`.
- When annotators review a record, they identify both the **intended control** (`barrier`) and its **breakdown mode** (`barrier_failure`).
