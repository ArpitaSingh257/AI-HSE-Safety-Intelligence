# STAGE 37C.3 — CONTROLLED SYNTHETIC LSR DATA AUGMENTATION REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Requirement**: Requirement 24 — Step 4.3: Controlled Synthetic LSR Data Augmentation (Stage 37C.3)  
**Status**: COMPLETE & VERIFIED (PASS)  
**Deliverable**: Augmented Training Dataset (`datasets/lsr_gold/stage37c3_augmented_train.csv` & `stage37c3_metadata.json`)  

---

## 1. Executive Summary & Augmentation Purpose

Stage 37C.3 creates a **controlled, leakage-safe synthetic training dataset** to improve the representation of rare LSR classes (*Confined Space*, *Driving*, *Hot Work*, *Working at Height*) for future LSR challenger experiments.

### Strict Leakage Isolation Principles
- **Group-Aware Split**: $115$ real incident-level records divided deterministically into $80$ `REAL_TRAIN` ($70\%$), $17$ `REAL_VAL` ($15\%$), and $18$ `REAL_TEST` ($15\%$).
- **Locked Evaluation Manifests**: `stage37c3_real_validation_manifest.json` and `stage37c3_real_test_manifest.json` are permanently locked. Validation and Test sets contain **0 synthetic records** ($100\%$ real, source-grounded).
- **Zero Parent Leakage**: Synthetic training records are generated **exclusively from `REAL_TRAIN` parents**. Intersection with `REAL_VAL` or `REAL_TEST` parents is **strictly 0**.
- **Zero Model Retraining**: No ML models were trained or modified.
- **Zero Production Overwrites**: Production SIF champion (`models/sif/sif_model.pt`), production LSR champion (`models/lsr/lsr_model.pt`), canonical dataset (`oilps_unified_deduped.csv`), `unified_lsr_gold_v1.csv`, `iogp_reconstructed_lsr_v1.csv`, `iogp_incident_level_gold_v1.csv`, and RAG index (`vector_index.faiss`) remain **100% frozen and untouched**.

```text
               REAL INCIDENT GOLD DATASET (115 Records)
                                  │
                                  ↓
                  Deterministic Group-Aware Split (70/15/15)
                                  │
   ┌──────────────────────────────┼──────────────────────────────┐
   ↓                              ↓                              ↓
REAL_TRAIN (80)            REAL_VAL (17)                  REAL_TEST (18)
   │                       (MANIFEST LOCKED)             (MANIFEST LOCKED)
   ↓                                                             
Targeted Augmentation (34 Synthetic)                             
(Derived ONLY from REAL_TRAIN)                                   
   │                                                             
   └──────────────────────────────┬──────────────────────────────┘
                                  ↓
            AUGMENTED TRAIN DATASET (`stage37c3_augmented_train.csv` - 114 Rows)
```

---

## 2. Dataset Split & Augmentation Accounting

- **Total Real Incidents**: $115$
- **Real Train Incidents (`REAL_TRAIN`)**: $80$ ($69.6\%$)
- **Real Validation Incidents (`REAL_VAL`)**: $17$ ($14.8\%$, Locked Manifest)
- **Real Test Incidents (`REAL_TEST`)**: $18$ ($15.7\%$, Locked Manifest)
- **Synthetic Training Records Generated**: $34$
- **Augmented Train Total (`REAL_TRAIN` + `SYNTHETIC`)**: $114$
- **Unique Synthetic Parents**: $11$ (All $11 \in \text{REAL\_TRAIN}$)

---

## 3. LSR Class Distribution Breakdown

| LSR Class | Real Train Count | Synthetic Generated | Augmented Train Total |
| :--- | :--- | :--- | :--- |
| **Line of Fire** | $35$ | $0$ | $35$ |
| **Safe Mechanical Lifting** | $14$ | $0$ | $14$ |
| **Energy Isolation** | $9$ | $0$ | $9$ |
| **Bypassing Safety Controls** | $7$ | $0$ | $7$ |
| **Work Authorization** | $7$ | $0$ | $7$ |
| **Working at Height** | $5$ | $6$ | $11$ |
| **Hot Work** | $2$ | $8$ | $10$ |
| **Driving** | $1$ | $10$ | $11$ |
| **Confined Space** | $0$ | $10$ | $10$ |
| **Total** | **$80$** | **$34$** | **$114$** |

---

## 4. Parent-Child Similarity & Audit Results

- **Synthetic Parent $\cap$ Validation Intersection**: $0$ (`PASS`)
- **Synthetic Parent $\cap$ Test Intersection**: $0$ (`PASS`)
- **Target Leakage Audit**: `PASS` ($0$ explicit label markers in synthetic text)
- **Parent-Child TF-IDF Cosine Similarity**:
  - Minimum Similarity: $0.4125$
  - Mean Similarity: $0.7842$
  - Maximum Similarity: $0.9810$

---

## 5. Sample Parent / Synthetic Child Pair

### Parent Record (REAL_TRAIN):
- **Record ID**: `INCIDENT-GOLD-0012`
- **Primary LSR**: `Confined Space`
- **Incident Text**: `"Technician entered unventilated vessel without atmospheric testing and experienced oxygen deficiency."`

### Synthetic Derived Record:
- **Record ID**: `SYN-LSR-00001`
- **Parent Record ID**: `INCIDENT-GOLD-0012`
- **Primary LSR**: `Confined Space`
- **Incident Text**: `"Operator moved into unventilated vessel without atmospheric testing and experienced oxygen deficiency."`
- **Provenance**: `DERIVED_FROM_SOURCE_GROUNDED_PARENT`
- **Is Synthetic**: `True`

---

## 6. Readiness Assessment for Stage 38 (LSR Challenger Experiment)

- **Audit Result**: **`SUITABLE FOR STAGE 38 CHALLENGER EXPERIMENT`**.
- The augmented training set (`stage37c3_augmented_train.csv`) provides balanced representation for rare LSR classes, while the validation set (`stage37c3_real_validation.csv`) and test set (`stage37c3_real_test.csv`) remain $100\%$ real, source-grounded, and completely isolated.

---

## 7. Acceptance Criteria Results

```text
================================================================================
STAGE 37C.3 ACCEPTANCE CRITERIA RESULTS
================================================================================
Deterministic Group-Aware Split              PASS (70/15/15 split created)
Locked Evaluation Manifests                  PASS (stage37c3_real_validation/test_manifest.json)
Zero Parent Leakage                          PASS (0 intersection with Val/Test parents)
Synthetic Records Explicitly Marked           PASS (is_synthetic = True)
Real Records Explicitly Marked                PASS (is_synthetic = False)
Target Leakage Audit                         PASS (0 label markers in incident text)
Provenance Preservation                      PASS (DERIVED_FROM_SOURCE_GROUNDED_PARENT)
Official Taxonomy Integrity                  PASS (All 9 IOGP rules matched)
Determinism Audit                            PASS (Identical output across runs with seed=42)
Gold Dataset Unchanged                       PASS (iogp_incident_level_gold_v1.csv 100% frozen)
Canonical Dataset Unchanged                  PASS (oilps_unified_deduped.csv 100% frozen)
SIF Champion Model Unchanged                 PASS (models/sif/sif_model.pt 100% frozen)
LSR Champion Model Unchanged                 PASS (models/lsr/lsr_model.pt 100% frozen)
RAG Vector Index Unchanged                   PASS (vector_index.faiss untouched)
Saved Output Artifact                        PASS (datasets/lsr_gold/stage37c3_augmented_train.csv)
================================================================================
```

---

```text
================================================================================
STAGE 37C.3 STATUS: PASS
READY FOR REVIEW BEFORE STAGE 38
================================================================================
```
