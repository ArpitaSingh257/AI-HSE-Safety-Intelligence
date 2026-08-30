# FINAL PRODUCTION VALIDATION & MODEL FREEZE REPORT

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Date:** 2026-08-30
**Model Freeze Status:** **`FROZEN_FOR_PRODUCTION`**
**Deterministic Seed:** `42`

---

## 1. Frozen Production Champions

1. **SIF Production Champion: `Stage 6 Bidirectional GRU + Attention`**
   - **Test Recall (SIF=1):** **`94.95%`**
   - **Test F1-Score:** **`0.9082`**
   - **Test PR-AUC:** **`0.9440`**
   - **Decision Threshold:** **`0.30`**

2. **LSR Production Champion: `Stage 7 Robust Bidirectional GRU + Attention`**
   - **Test Micro-F1:** **`0.6795`**
   - **Test Macro-F1:** **`0.5618`**
   - **Test Hamming Loss:** **`0.0403`**
   - **Test Exact Match Ratio:** **`68.84%`**
   - **Thresholds:** Stage 7 Validation-Learned Independent Rule Thresholds.

---

## 2. LSR Per-Rule Breakdown (9 IOGP Life-Saving Rules)

| Official IOGP Life-Saving Rule | Frozen Threshold | Test Support | Precision | Recall | F1-Score |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Bypassing Safety Controls** | 0.50 | 0 | 0.0000 | 0.0000 | **0.0000** |
| **Confined Space** | 0.50 | 2 | 0.5000 | 0.5000 | **0.5000** |
| **Driving** | 0.25 | 15 | 0.9286 | 0.8667 | **0.8966** |
| **Energy Isolation** | 0.30 | 16 | 0.6250 | 0.6250 | **0.6250** |
| **Hot Work** | 0.45 | 13 | 0.8462 | 0.8462 | **0.8462** |
| **Line of Fire** | 0.20 | 5 | 0.2500 | 0.2000 | **0.2222** |
| **Safe Mechanical Lifting** | 0.20 | 14 | 0.6000 | 0.6429 | **0.6207** |
| **Toxic Gas / Hazardous Substance** | 0.50 | 2 | 0.6667 | 1.0000 | **0.8000** |
| **Working at Height** | 0.25 | 9 | 0.4615 | 0.6667 | **0.5455** |
| **OVERALL (MICRO)** | — | **76** | **0.6625** | **0.6974** | **0.6795** |

---

## 3. Demo Scenario Verification Audit

### A. Hydrotest Pressurized Fitting Failure:
- **Narrative:** "During hydrostatic testing of the 6-inch high pressure discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting while the line remained pressurized. The bleeder plug ruptured and struck the worker in the chest."
- **SIF Probability:** `99.99%` (Alert: `SIF`)
- **Triggered Life-Saving Rules:** `['Energy Isolation']`
- **Salient Interpretability Tokens:** **pressure** (0.873), **fitting** (0.038), **pressurized** (0.027), **high** (0.023), **remained** (0.013)

### B. Crane Lifting / Sling Failure:
- **Narrative:** "A crawler crane was lifting a 2-ton casing bundle across the rig floor when the nylon sling parted due to sharp edge contact. The casing bundle swung downward, striking the floor near the rotary table."
- **SIF Probability:** `99.97%` (Alert: `SIF`)
- **Triggered Life-Saving Rules:** `None`
- **Salient Interpretability Tokens:** **2** (0.360), **crane** (0.191), **casing** (0.131), **ton** (0.086), **floor** (0.063)

### C. Confined-Space H2S Incident:
- **Narrative:** "An employee entered an enclosed crude oil storage separator without continuous gas monitoring or ventilation. Lethal levels of hydrogen sulfide (H2S) gas overcame the worker inside the vessel."
- **SIF Probability:** `88.75%` (Alert: `SIF`)
- **Triggered Life-Saving Rules:** `None`
- **Salient Interpretability Tokens:** **employee** (0.471), **vessel** (0.335), **oil** (0.064), **crude** (0.035), **an** (0.020)

### D. Minor Slip on Ice in Yard:
- **Narrative:** "While walking across the paved maintenance yard after a shift change, an operator slipped on a patch of ice and bruised their knee. First aid applied; worker returned to full duty immediately."
- **SIF Probability:** `27.79%` (Alert: `NON-SIF`)
- **Triggered Life-Saving Rules:** `None`
- **Salient Interpretability Tokens:** **while** (0.300), **shift** (0.242), **operator** (0.115), **an** (0.088), **walking** (0.067)

