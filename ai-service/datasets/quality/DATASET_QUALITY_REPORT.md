# OILPS Dataset Quality & Statistical Profile Report

## 1. Dataset Overview

- **Total Records in ML-Ready Corpus:** 4529
- **Unique Sources:** 4
- **Schema Conformance:** 100% Canonical Schema Compliance

## 2. Source Distribution

| Source Tag | Source Document | Record Count | Percentage |
| :--- | :--- | :--- | :--- |
| `OSHA` | OSHA | 4229 | 93.38% |
| `IOGP_SPI` | IOGP_SPI | 190 | 4.2% |
| `IOGP_HPE` | IOGP_HPE | 97 | 2.14% |
| `IOGP_FATAL` | IOGP_FATAL | 13 | 0.29% |

## 3. SIF-Potential & Severity Distribution

| SIF Potential Status | Count | Percentage | Description |
| :--- | :--- | :--- | :--- |
| `REVIEW_REQUIRED` | 4229 | 93.38% | Needs domain annotation / review |
| `1` | 300 | 6.62% | Ground-truth IOGP HiPo / Fatal event |

## 4. Missing Value Analysis (Canonical Fields)

| Field Name | Available Count | Missing Count | Missing Rate (%) |
| :--- | :--- | :--- | :--- |
| `record_id` | 4529 | 0 | 0.0% |
| `source` | 4529 | 0 | 0.0% |
| `source_document` | 4529 | 0 | 0.0% |
| `source_record_id` | 4529 | 0 | 0.0% |
| `report_date` | 4529 | 0 | 0.0% |
| `country` | 4529 | 0 | 0.0% |
| `location` | 4229 | 300 | 6.62% |
| `function` | 300 | 4229 | 93.38% |
| `industry` | 4529 | 0 | 0.0% |
| `activity` | 184 | 4345 | 95.94% |
| `event_type` | 4326 | 203 | 4.48% |
| `cause` | 4314 | 215 | 4.75% |
| `narrative` | 4529 | 0 | 0.0% |
| `what_went_wrong` | 300 | 4229 | 93.38% |
| `corrective_actions` | 300 | 4229 | 93.38% |
| `causal_factors` | 299 | 4230 | 93.4% |
| `primary_life_saving_rule` | 10 | 4519 | 99.78% |
| `secondary_life_saving_rule` | 100 | 4429 | 97.79% |
| `life_saving_rules` | 105 | 4424 | 97.68% |
| `severity` | 4529 | 0 | 0.0% |
| `hospitalization` | 4229 | 300 | 6.62% |
| `amputation` | 4229 | 300 | 6.62% |
| `loss_of_eye` | 4229 | 300 | 6.62% |
| `sif_potential` | 4529 | 0 | 0.0% |
| `hazard` | 4022 | 507 | 11.19% |
| `barrier` | 0 | 4529 | 100.0% |
| `barrier_failure` | 184 | 4345 | 95.94% |
| `potential_consequence` | 4229 | 300 | 6.62% |
| `data_source_type` | 4529 | 0 | 0.0% |

## 5. Domain Observations & Leakage Risks

1. **Narrative Text Quality:** 100% of retained records have non-empty incident narratives.
2. **SIF Label Discipline:** We do NOT equate OSHA hospitalization/amputation directly to SIF. OSHA records are preserved with severity indicators while preserving `sif_potential = REVIEW_REQUIRED` pending domain annotation.
3. **Cross-Source Imbalance:** IOGP documents contribute high-density HiPo oilfield narratives with explicit barrier context, while OSHA contributes large-scale empirical operational narratives from drilling, servicing, pipeline, and refinery sectors.
4. **Data Leakage Mitigation:** Stratified group splitting prevents similar phrasing or incident batches from crossing between training and evaluation splits.

## 6. Recommended Next Steps

1. Conduct structured human/domain expert annotation on `datasets/annotation/oilps_annotation.csv`.
2. Finalize stratified 70/15/15 train/val/test splits.
3. Build baseline TF-IDF and calibrated logistic regression models for SIF & LSR.
