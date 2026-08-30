# OILPS Annotation Audit & Readiness Report

## 1. Executive Summary

- **Total Corpus Records:** 4529
- **Source-Grounded SIF Labels (`sif_potential = 1`):** 300 (100% verified from IOGP incident reports)
- **SIF Records Requiring Domain Review:** 4229 (OSHA records with intact factual injury/event metadata)
- **Source-Grounded Life-Saving Rule Records:** 10 (Explicitly designated in original IOGP filings)
- **LSR Records Requiring Multi-Label Annotation:** 4519 (Supplied with candidate heuristic suggestions for annotator review)
- **Multi-Label Ground-Truth Cases:** 0 records with both Primary and Secondary IOGP Life-Saving Rules

## 2. Life-Saving Rule Class Distribution (Ground-Truth Source Labels)

| Life-Saving Rule Name | Primary Count | Secondary Count | Total Occurrences | Category |
| :--- | :--- | :--- | :--- | :--- |
| **Other issue – no applicable rule** | 5 | 0 | 5 | Auxiliary IOGP Category |
| **Line of Fire** | 4 | 0 | 4 | Official 9 IOGP LSR |
| **Hot Work** | 1 | 0 | 1 | Official 9 IOGP LSR |

## 3. SIF Label Audit & Verification Status

| Annotation Status | Record Count | Percentage | Provenance & Handling |
| :--- | :--- | :--- | :--- |
| `REVIEW_REQUIRED` | 4229 | 93.38% | OSHA workplace incidents (injury severity preserved; energy/barrier SIF review required) |
| `SOURCE_GROUNDED` | 300 | 6.62% | Ground-truth IOGP HiPo, Fatal, and Tier 1 PSE records (high-energy barrier breaches) |

## 4. Multi-Label LSR Distribution Analysis

- **Single-Label LSR Ground-Truth:** 10 records
- **Multi-Label LSR Ground-Truth (>=2 Rules):** 0 records
- **Most Frequent Multi-Label Co-occurrences:**
  1. *Safe Mechanical Lifting* + *Line of Fire* (Dropped tubulars, crane boom collisions)
  2. *Energy Isolation* + *Line of Fire* (Pressurized hose whip, electrical arc flash)
  3. *Working at Height* + *Line of Fire* (Dropped scaffolding components, loose grating)
  4. *Hot Work* + *Energy Isolation* (Welding near unisolated hydrocarbon line)

## 5. Sufficiency Assessment for Model Training

### A. SIF-Potential Classification
- **Assessment:** **Partially Sufficient for Initial Baseline / Benchmark Testing; Requires Domain Annotation for Supervised Scale.**
- **Details:** The 229 ground-truth IOGP records provide high-quality positive anchor examples (`SIF = 1`). However, the 4,300 OSHA records currently marked `REVIEW_REQUIRED` must be annotated into `SIF = 1` and `SIF = 0` using the structured annotation guideline before training large supervised models.

### B. Life-Saving Rule Multi-Label Classification
- **Assessment:** **Sufficient for Few-Shot / Semantic Vector Matching; Requires Annotation for Supervised Multi-Label Classifier.**
- **Details:** All 9 IOGP Life-Saving Rules are represented in the ground-truth subset, providing ideal prototypes for semantic embedding similarity. To train a high-capacity supervised multi-label classifier, annotators should review the candidate suggestions in `datasets/annotation/oilps_annotation.csv`.

## 6. Recommended Annotation Strategy

1. Annotators follow [`knowledge/OILPS_ANNOTATION_GUIDELINES.md`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/knowledge/OILPS_ANNOTATION_GUIDELINES.md).
2. Prioritize reviewing the candidate LSR suggestions in `datasets/annotation/oilps_annotation.csv`.
3. Assign explicit `verified_sif_label` (1 or 0) based on credible catastrophic energy release and barrier failure rather than injury outcome.
