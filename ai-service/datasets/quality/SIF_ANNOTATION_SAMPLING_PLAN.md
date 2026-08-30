# SIF Negative & Positive Annotation Sampling Plan
**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Objective:** Establish a statistically sound, stratified sampling methodology to obtain verified SIF-positive (`SIF = 1`) and SIF-negative (`SIF = 0`) annotations from the 4,229 OSHA Oil & Gas records.

---

## 1. The Negative Class Challenge in Precursor NLP

### Current Corpus State:
- **Verified SIF Positives (`SIF = 1`):** **300 records** (100% from IOGP HPE, Fatal, and Tier 1 PSE).
- **Verified SIF Negatives (`SIF = 0`):** **0 records** (All 4,229 OSHA records currently marked `REVIEW_REQUIRED`).
- **The Problem:** Training a supervised binary classifier on positive-only data is scientifically impossible without introducing negative examples. However, **blindly assuming all OSHA records are non-SIF (`SIF = 0`) is completely false**, because many OSHA records involve high-pressure line blowouts, drilling rig floor crushing, and well fires.

---

## 2. Stratified Sampling Methodology

To build a balanced, representative training and validation subset, we recommend a **Stratified Sampling Target of 600 OSHA Records** (giving a total annotated dataset of ~900 records when combined with the 300 IOGP records).

### Stratification Matrix Across Operational Functions & Injury Classes:

| Stratification Stratum | OSHA Sub-Corpus Size | Recommended Sample Size | Expected Class Yield |
| :--- | :--- | :--- | :--- |
| **Stratum A: High-Energy Mechanical / Drilling** (NAICS 213111, Rig floor, Cathead, Drawworks, Derrick) | ~1,200 | **180 records** | ~60% SIF-1 / ~40% SIF-0 |
| **Stratum B: Pressurized / Chemical / Fire** (NAICS 211 / 324, Flash fire, H2S, Acid, High-pressure gas) | ~1,100 | **180 records** | ~70% SIF-1 / ~30% SIF-0 |
| **Stratum C: Work at Height / Scaffolding / Crane** (Falls >1.8m, Suspended loads, Mobile crane) | ~900 | **120 records** | ~50% SIF-1 / ~50% SIF-0 |
| **Stratum D: Low-Energy Occupational / Ergonomic** (Slips on ice, lifting boxes, insect stings, office tasks) | ~1,029 | **120 records** | **~5% SIF-1 / ~95% SIF-0 (Rich negative source)** |
| **TOTAL** | **4,229** | **600 records** | **Target ~300 SIF-1 / ~300 SIF-0** |

---

## 3. Inclusion & Exclusion Criteria for SIF-0 (Negative Class)

### Inclusion for SIF = 0 (Confirmed Non-SIF Precursor):
1. **Low Kinetic / Gravitational Energy:** Slips and trips on same level ground without falling into pits, machinery, or moving equipment.
2. **Ergonomic Overexertion:** Muscle strain while manually lifting non-hazardous items (<25 kg).
3. **Minor Hand Tool Incidents:** Minor hand cut from a utility knife opening packing tape, where no high pressure or flammables were present.
4. **Environmental Exposure without Escalation:** Mild dehydration or heat rash resolving with oral rehydration without vital organ failure.

### Exclusion for SIF = 0 (Must be Marked SIF = 1):
1. Any incident involving pressurized systems >100 psi, even if no fluid hit the worker.
2. Any fall from height >1.8 meters, regardless of harness arrest outcome.
3. Any suspended load failure or dropped object >5 kg from elevated structure.
4. Any flammable gas release, flash fire, or toxic gas (H2S, CO) release in an operational unit.

---

## 4. Handling Ambiguous & Edge Cases

- If an OSHA narrative lacks key physical parameters (e.g. *"Worker felt dizzy while working near battery"*, without mentioning whether H2S or heat caused it):
  - Mark `verified_sif_label = UNKNOWN`
  - Set `sif_annotation_status = NEEDS_REVIEW`
  - Provide explanation in `annotator_notes`
  - **Do NOT force binary label into training splits.**
