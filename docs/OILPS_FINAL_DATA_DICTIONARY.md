# OILPS FINAL MASTER DATASET DATA DICTIONARY (`oilps_final_master_v1.csv`)

**Project**: OILPS Precursor Safety Intelligence Service  
**Version**: Version 1.0 Final  
**Total Canonical Records**: 4,529 Records  

---

## 1. Overview & Provenance Guarantee

Every record in `oilps_final_master_v1.csv` is accounted for with an explicit provenance classification. 

> [!IMPORTANT]
> **Source-Grounded vs Model-Predicted Distinction**:  
> `SOURCE_GROUNDED` $\neq$ `MODEL_PREDICTED` and `MODEL_PREDICTED` $\neq$ Ground-Truth.  
> Model-assisted predictions represent operational outputs of the frozen classifier and must NEVER be represented as source evidence.

| Provenance State | Description | Total Count | Percentage |
| :--- | :--- | :--- | :--- |
| `SOURCE_GROUNDED` | Label directly supported by native source evidence | $10$ | $0.22\%$ |
| `SOURCE_GROUNDED_RECONSTRUCTED` | Label reconstructed from validated IOGP source extractions | $11$ | $0.24\%$ |
| `MODEL_PREDICTED` | High-confidence prediction by frozen LSR classifier | $1,842$ | $40.67\%$ |
| `HUMAN_REVIEW` | Medium-confidence prediction pending manual review | $1,106$ | $24.42\%$ |
| `UNKNOWN` | Unresolved / low-confidence abstained record | $1,560$ | $34.45\%$ |

---

## 2. Field Specifications & Dictionary Table

| Field Name | Data Type | Description | Source / Derivation | Allowed Values / Examples |
| :--- | :--- | :--- | :--- | :--- |
| `record_id` | String | Unique primary canonical record identifier | Upstream Canonical | `OILPS_IOGP_HPE_0001`, `OILPS_OSHA_0042` |
| `source` | String | Incident data source origin | Upstream Canonical | `IOGP_HPE`, `IOGP_SPI`, `OSHA`, `IOGP_SAFETY_DATA` |
| `source_document` | String | Source document filename | Source / Stage 39B | `IAOGP - High Potential Event Reports.pdf` |
| `source_record_id` | String | Upstream source record identifier | Upstream Canonical | `HPE_P006`, `2015010023` |
| `report_date` | String | Date of incident occurrence or report | Upstream Canonical | `13 Mar 2025`, `24 Oct 2024` |
| `country` | String | Country of incident | Upstream Canonical | `Gabon`, `Azerbaijan`, `United States` |
| `location` | String | Specific site or offshore/onshore location | Upstream Canonical | `Offshore Rig 4`, `Refinery Unit 2` |
| `function` | String | Operational function | Upstream Canonical | `Drilling`, `Production`, `Maintenance` |
| `industry` | String | Industry sector | Upstream Canonical | `Oil and Gas Exploration and Production` |
| `activity` | String | Specific work activity at time of incident | Upstream Canonical | `Transport – Land`, `Lifting operations` |
| `event_type` | String | High-level event category | Upstream Canonical | `High Potential Event`, `Process Safety Event` |
| `cause` | String | Primary cause description | Upstream Canonical | `Caught in, under or between` |
| `narrative` | String | Main descriptive incident narrative text | Upstream Canonical | Full text description of event |
| `what_went_wrong` | String | Explanation of barrier failure / root cause | Upstream Canonical | Specific text detailing failure |
| `corrective_actions` | String | Immediate or long-term corrective actions | Upstream Canonical | Remediation steps taken |
| `causal_factors` | String | Categorized causal factors | Upstream Canonical | Technical or organizational factors |
| `severity` | String | Incident severity classification | Upstream Canonical | `Fatality`, `High Potential Event`, `Recordable` |
| `sif_potential` | String | SIF precursor classification | Production SIF Model | `SIF_PRECURSOR`, `NON_SIF` |
| `hazard` | String | Primary safety hazard category | Upstream Canonical | `Mechanical`, `Pressure`, `Chemical` |
| `barrier` | String | Intended safety barrier | Upstream Canonical | `Permit to Work`, `PPE`, `Guardrail` |
| `barrier_failure` | String | Mechanism of barrier failure | Upstream Canonical | `Bypassed`, `Inadequate Design` |
| `potential_consequence` | String | Worst-case potential outcome | Upstream Canonical | `Multiple Fatalities`, `Major Damage` |
| `lsr_labels` | String | Assigned Life-Saving Rule(s) | Reconstructed / Model | Pipe-separated string (e.g. `Line of Fire \| Driving`) |
| `lsr_primary` | String | Primary Life-Saving Rule | Reconstructed / Model | Single rule string or `UNKNOWN` |
| `lsr_secondary` | String | Secondary Life-Saving Rule(s) | Reconstructed / Model | JSON list string or `UNKNOWN` |
| `lsr_provenance` | String | Explicit provenance classification | Stage 39A / 39B / 40 / 41 | `SOURCE_GROUNDED`, `SOURCE_GROUNDED_RECONSTRUCTED`, `MODEL_PREDICTED`, `HUMAN_REVIEW`, `UNKNOWN` |
| `lsr_confidence` | Float | Confidence score / probability | Reconstructed / Model | `0.0` to `1.0` |
| `lsr_assignment_method` | String | Method of assignment | Pipeline System | `NATIVE_CANONICAL_LABEL`, `IOGP_RECONSTRUCTION_MATCH`, `MODEL_ASSISTED_INFERENCE`, `NOT_ASSIGNED` |
| `lsr_prob_bypassing_safety_controls` | Float | Model probability for Bypassing Safety Controls | Frozen LSR Classifier | `0.0000` to `1.0000` |
| `lsr_prob_confined_space` | Float | Model probability for Confined Space | Frozen LSR Classifier | `0.0000` to `1.0000` |
| `lsr_prob_driving` | Float | Model probability for Driving | Frozen LSR Classifier | `0.0000` to `1.0000` |
| `lsr_prob_energy_isolation` | Float | Model probability for Energy Isolation | Frozen LSR Classifier | `0.0000` to `1.0000` |
| `lsr_prob_hot_work` | Float | Model probability for Hot Work | Frozen LSR Classifier | `0.0000` to `1.0000` |
| `lsr_prob_line_of_fire` | Float | Model probability for Line of Fire | Frozen LSR Classifier | `0.0000` to `1.0000` |
| `lsr_prob_safe_mechanical_lifting` | Float | Model probability for Safe Mechanical Lifting | Frozen LSR Classifier | `0.0000` to `1.0000` |
| `lsr_prob_work_authorization` | Float | Model probability for Work Authorization | Frozen LSR Classifier | `0.0000` to `1.0000` |
| `lsr_prob_working_at_height` | Float | Model probability for Working at Height | Frozen LSR Classifier | `0.0000` to `1.0000` |
| `final_lsr_provenance` | String | Master standardized provenance state | Stage 41 QC | `SOURCE_GROUNDED`, `SOURCE_GROUNDED_RECONSTRUCTED`, `MODEL_PREDICTED`, `HUMAN_REVIEW`, `UNKNOWN` |
| `final_lsr_status` | String | Master operational status | Stage 41 QC | `SOURCE_GROUNDED`, `HIGH_CONFIDENCE_MODEL_PREDICTED`, `MEDIUM_CONFIDENCE_HUMAN_REVIEW`, `UNKNOWN` |
| `final_lsr_quality_flag` | String | Automated quality audit flag | Stage 41 QC | `NORMAL`, `VERY_SHORT_NARRATIVE`, `LOW_MARGIN_BORDERLINE`, `NO_FLAG` |

---

## 3. Official 9-Rule IOGP Taxonomy Reference

1. **Bypassing Safety Controls**: Obtain authorization before bypassing or disabling safety controls.
2. **Confined Space**: Obtain authorization before entering a confined space.
3. **Driving**: Always wear seatbelts, obey speed limits, and refrain from using mobile phones while driving.
4. **Energy Isolation**: Verify isolation and zero energy state before work begins.
5. **Hot Work**: Control flammables and ignition sources during hot work.
6. **Line of Fire**: Keep yourself and others out of the line of fire (moving equipment, dropped objects, pressure).
7. **Safe Mechanical Lifting**: Plan lifting operations and control the area.
8. **Work Authorization**: Work with a valid permit to work when required.
9. **Working at Height**: Protect yourself against falling when working at height.
