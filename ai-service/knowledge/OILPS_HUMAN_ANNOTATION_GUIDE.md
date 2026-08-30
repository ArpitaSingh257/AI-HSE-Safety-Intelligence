# OILPS Human Domain Annotation Standard Operating Procedure
**Document Code:** OILPS-SOP-ANN-001 (Rev 2)  
**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence  
**Target Dataset:** `ai-service/datasets/annotation/osha_annotation_sample_600.csv`  
**Standard Governing Authority:** IOGP Safety Report 459/423/590 & Campbell Institute SIF Prevention Framework  

---

## 1. Scope & General Instructions

This document is the standard operating procedure for human and domain expert reviewers annotating the **600-record OSHA Oil & Gas stratified review sample** (`osha_annotation_sample_600.csv`).

### Core Annotation Ground Rules:
1. **Human Evaluation Only:** Reviewers must read every incident narrative carefully and enter judgments independently. Automated scripts must NOT populate `human_*` fields.
2. **Contextual Energy-Barrier Principle:** Serious Injury & Fatality (SIF) potential is determined strictly by holistic evaluation of **Hazardous Energy Exposure + Critical Safety Barrier Breakdown + Credible Catastrophic Escalation**, NOT by rigid numerical thresholds or historical injury outcomes alone.
3. **Multi-Label Life-Saving Rules:** Assign all applicable rules from the official 9 IOGP Life-Saving Rules.
4. **Decoupled Precursor Entities:** Strictly distinguish intended defenses (`human_barrier`) from failure modes (`human_barrier_failure`), and actual historical injuries from credible worst-case potential consequences (`human_potential_consequence`).

---

## 2. Field-by-Field Annotation Protocol

### A. SIF Potential Decision Framework (`human_sif_label`)

The fundamental equation governing SIF classification is:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            THE SIF POTENTIAL EQUATION                       │
│                                                                             │
│               Hazardous Energy Source (Chemical, Kinetic, Thermal, etc.)    │
│                                      +                                      │
│               Worker Exposure / Credible Exposure Pathway                   │
│                                      +                                      │
│               Critical Barrier Failure, Degradation, or Absence             │
│                                      +                                      │
│               Credible Fatal or Whole-Person Life-Altering Escalation       │
│                                      ═                                      │
│                                 SIF POTENTIAL                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Label Value | Meaning | Holistic Definitional Criteria |
| :--- | :--- | :--- |
| **`1`** | **SIF Potential** | The complete incident context demonstrates that a **hazardous energy source** interacted through a **worker exposure pathway**, where **critical protective barriers failed or were absent**, creating a **credible escalation path to fatality or life-altering disability** under realistic alternate circumstances. |
| **`0`** | **Non-SIF Potential** | The incident involved low energy, robust protective barriers remained intact, or the physical scenario possessed **zero credible escalation pathway** to death or permanent life-altering impairment. |
| **`UNKNOWN`** | **Insufficient Evidence** | The narrative lacks sufficient operational or physical detail to determine energy magnitude, exposure pathway, or barrier integrity. |

> [!WARNING]
> **CRITICAL METHODOLOGICAL RULE: NUMERICAL VALUES ARE CONTEXTUAL EXAMPLES, NOT HARD BOUNDARIES!**
> 1. **No Automatic SIF = 1 from Numbers:** A numerical parameter alone (e.g. *300 psi*, *3 meters elevation*, *1 ton weight*, *480V*) NEVER automatically triggers `SIF = 1` if the energy was fully contained, worker exposure was impossible, or effective secondary barriers prevented catastrophic escalation.
> 2. **No Automatic SIF = 0 from Absence of Numbers:** The absence of numerical metrics (e.g. *"gas line ruptured"*, *"worker fell from rig floor"*, *"struck by falling pipe"*) must NEVER automatically result in `SIF = 0`. Reviewers must evaluate the operational context, equipment type, and physical energy potential qualitatively.
> 3. **Contextual Indicators (Examples Only):**
>    - *Pressure / Pneumatic / Hydraulic:* e.g., Pressurized gas or fluid systems where sudden release or projectile trajectory can deliver fatal impact.
>    - *Gravitational / Fall from Height:* e.g., Elevated derrick, scaffolding, mast, or deck work where fall distance or landing hazard creates lethal kinetic impact.
>    - *Suspended / Heavy Mechanical Loads:* e.g., Hoisted tubulars, crane operations, or cathead winches capable of fatal crush or line-of-fire strike.
>    - *Electrical:* e.g., Energized circuits, arc-flash boundaries, or live conductors presenting lethal ventricular fibrillation or severe thermal arc blast.
>    - *Flammable / Toxic Atmospheres:* e.g., Hydrocarbon vapors, flash fires, nitrogen purges, or H2S concentrations with potential for asphyxiation or mass casualty.

---

### B. SIF Decision Confidence (`human_sif_confidence`)

| Confidence Level | When to Assign |
| :--- | :--- |
| **`HIGH`** | Clear, unambiguous incident context with explicit energy sources, clear worker exposure pathway, and documented barrier status. |
| **`MEDIUM`** | High energy and barrier failure are clearly indicated by operational equipment and sequence, though specific physical parameters must be reasonably inferred. |
| **`LOW`** | Terse or fragmented narrative requiring substantial contextual inference to evaluate energy exposure or barrier failure. |

---

### C. Structured SIF Rationale (`human_sif_rationale`)

Annotators must provide a concise, structured 1- to 2-sentence rationale formatted as:
`"Energy: [Hazardous Energy Source] | Exposure: [Workforce Position/Action] | Barrier Failure: [Failed Control] | Escalation: [Credible Worst-Case Outcome]"`

*Example:*  
`"Energy: Pressurized natural gas | Exposure: Worker positioned near unbolted flange | Barrier Failure: Line not depressurized or verified prior to bolt removal | Escalation: Fatal blast trauma / flash fire ignition"`

---

### D. Life-Saving Rules (LSR) Multi-Label Annotation

Reviewers must assign rules using **ONLY the official 9 IOGP Life-Saving Rules** (or `'None'` if no rule applies):

```
1. Bypassing Safety Controls        6. Line of Fire
2. Confined Space                   7. Safe Mechanical Lifting
3. Driving                          8. Toxic Gas / Hazardous Substance
4. Energy Isolation                 9. Working at Height
5. Hot Work                        10. None (No rule applicable)
```

| Field Name | Description | Example Value |
| :--- | :--- | :--- |
| **`human_primary_lsr`** | The single most applicable IOGP rule addressing the primary failure initiator. | `Energy Isolation` |
| **`human_secondary_lsr`**| Secondary rule if the event involved a compounded secondary failure (leave blank if single-label). | `Line of Fire` |
| **`human_all_lsrs`** | Semicolon-separated list of all applicable rules. | `Energy Isolation; Line of Fire` |

*Candidate Heuristic Guidance:* The column `candidate_all_lsrs` contains automated keyword suggestions. Reviewers should **evaluate, accept, modify, or reject** these suggestions based strictly on the text evidence.

---

### E. Precursor Information Extraction Entities

Reviewers must extract 5 distinct precursor entities directly from or strongly grounded in the incident text:

```text
┌─────────────────────────┬──────────────────────────────────────────────────────────────────────────┐
│ Field Name              │ Definition & Annotation Standard                                         │
├─────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ human_activity          │ Specific operational task (e.g., 'Tripping drill pipe', 'LOTO pump rep')│
├─────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ human_hazard            │ Physical/chemical hazardous energy (e.g., 'Pressurized crude line')      │
├─────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ human_barrier           │ Intended protective defense (e.g., 'Double Block & Bleed', 'Harness')    │
├─────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ human_barrier_failure   │ Specific failure mechanism (e.g., 'Bleed valve unverified before cut')   │
├─────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ human_potential_conseq. │ Credible worst-case outcome (e.g., 'Fatal vapor cloud explosion')        │
└─────────────────────────┴──────────────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> **ACTUAL INJURY OUTCOME $\neq$ POTENTIAL CONSEQUENCE:**
> - Do NOT copy the OSHA `NatureTitle` (e.g. "Fractures" or "Amputations") into `human_potential_consequence`.
> - Ask: *"If this hazardous event had escalated under realistic alternate circumstances, what was the credible catastrophic consequence?"* (e.g., Fatal crush, Hypoxic asphyxiation, Severe whole-body burns).

---

## 3. Evidence & Inference Standards

1. **Explicit Evidence:** Physical facts, named equipment (*BOP*, *Drawworks*, *Derrick*, *Scaffolding*), stated chemicals (*H2S*, *Methanol*, *Amine*).
2. **Permissible Domain Inference:** Standard industry operating conditions (e.g., well killing or hydrotesting implies high fluid pressure; rig floor casing operations imply heavy suspended gravitational loads).
3. **Impermissible Hallucination:** Inventing unmentioned barriers or guessing exact pressures when no context is provided. If absent, record `None` or `Unknown`.

---

## 4. 10 Detailed Reference Annotation Examples

### Example 1: Drilling Rig Floor — Heavy Tubular Handling
- **Narrative:** *"A team of drill crew was picking up a joint of casing on the rig floor. The air winch tugger line was operated without a signalman. The pipe missed the mousehole, swung across the rig floor, and struck the floorhand in the shoulder."*
- **`human_sif_label`:** `1`
- **`human_sif_confidence`:** `HIGH`
- **`human_sif_rationale`:** `"Energy: Suspended heavy tubular load | Exposure: Floorhand in swing radius | Barrier Failure: Tugger operated without signalman and red zone exclusion breached | Escalation: Fatal crush/struck-by impact"`
- **`human_primary_lsr`:** `Safe Mechanical Lifting`
- **`human_secondary_lsr`:** `Line of Fire`
- **`human_all_lsrs`:** `Safe Mechanical Lifting; Line of Fire`
- **`human_activity`:** `Picking up casing on rig floor`
- **`human_hazard`:** `Suspended heavy tubular load (gravitational/kinetic energy)`
- **`human_barrier`:** `Dedicated signalman; Rig floor red zone exclusion barrier`
- **`human_barrier_failure`:** `Tugger operated without signal; personnel positioned in line of fire`
- **`human_potential_consequence`:** `Fatal crushing or head trauma`

---

### Example 2: Pressure Testing / Hydrotest Blowout
- **Narrative:** *"A crew was performing hydrostatic pressure testing on a newly installed gas line. An employee approached the manifold to tighten a fitting when the test plug blew out under pressure, narrowly missing his head and destroying the blast shield."*
- **`human_sif_label`:** `1`
- **`human_sif_confidence`:** `HIGH`
- **`human_sif_rationale`:** `"Energy: High hydrostatic pressure | Exposure: Worker approaching pressurized test manifold | Barrier Failure: Tightening fitting while line under pressure; exclusion zone breached | Escalation: Fatal projectile impact / blast trauma"`
- **`human_primary_lsr`:** `Energy Isolation`
- **`human_secondary_lsr`:** `Line of Fire`
- **`human_all_lsrs`:** `Energy Isolation; Line of Fire`
- **`human_activity`:** `Pipeline hydrostatic pressure testing`
- **`human_hazard`:** `High-pressure fluid / projectile energy`
- **`human_barrier`:** `Zero energy depressurization before intervention; Hard exclusion zone`
- **`human_barrier_failure`:** `Intervention attempted on pressurized system; exclusion zone violated`
- **`human_potential_consequence`:** `Fatal projectile trauma`

---

### Example 3: Work at Height — Scaffolding
- **Narrative:** *"A contractor scaffolder was dismantling scaffolding on an elevated crude column. While passing a scaffold tube to a colleague, he unclipped his safety harness lanyard to reach around a pipe rack and lost his footing, falling to the deck below."*
- **`human_sif_label`:** `1`
- **`human_sif_confidence`:** `HIGH`
- **`human_sif_rationale`:** `"Energy: Gravitational potential (elevated pipe rack) | Exposure: Scaffolder working over open deck | Barrier Failure: Disconnected 100% tie-off safety harness lanyard | Escalation: Fatal fall from height"`
- **`human_primary_lsr`:** `Working at Height`
- **`human_secondary_lsr`:** `Line of Fire`
- **`human_all_lsrs`:** `Working at Height; Line of Fire`
- **`human_activity`:** `Scaffolding dismantling at elevated pipe rack`
- **`human_hazard`:** `Elevated work surface (gravitational energy)`
- **`human_barrier`:** `Full body safety harness with 100% continuous tie-off`
- **`human_barrier_failure`:** `Lanyard unclipped during position transition`
- **`human_potential_consequence`:** `Fatal blunt force impact from height`

---

### Example 4: Hot Work / Tank Flash Fire
- **Narrative:** *"Employees were using a cutting torch to remove a bracket from an out-of-service crude oil storage tank. Hydrocarbon vapors inside the tank ignited from sparks entering a drain nozzle, causing a flash fire that singed the welder's fire-resistant coveralls."*
- **`human_sif_label`:** `1`
- **`human_sif_confidence`:** `HIGH`
- **`human_sif_rationale`:** `"Energy: Flammable hydrocarbon vapor and open flame torch ignition | Exposure: Welder in hazardous zone | Barrier Failure: Inadequate gas testing and unsealed tank nozzle | Escalation: Catastrophic tank explosion and multiple fatalities"`
- **`human_primary_lsr`:** `Hot Work`
- **`human_secondary_lsr`:** `Bypassing Safety Controls`
- **`human_all_lsrs`:** `Hot Work; Bypassing Safety Controls`
- **`human_activity`:** `Torch cutting on crude storage tank`
- **`human_hazard`:** `Flammable crude oil vapor atmosphere / Open flame ignition source`
- **`human_barrier`:** `Continuous LEL gas monitoring; Spark containment / nozzle sealing`
- **`human_barrier_failure`:** `Failure to verify 0% LEL and open nozzle left unsealed`
- **`human_potential_consequence`:** `Catastrophic vapor explosion and fatal thermal burns`

---

### Example 5: Toxic Gas / Confined Space
- **Narrative:** *"An operator entered a production separator vessel to remove accumulated sludge. The vessel atmosphere had not been tested following nitrogen purging. Within seconds, the operator collapsed due to oxygen deficiency. The standby attendant sounded the emergency alarm and initiated external rescue."*
- **`human_sif_label`:** `1`
- **`human_sif_confidence`:** `HIGH`
- **`human_sif_rationale`:** `"Energy: Oxygen-deficient / toxic atmosphere (N2 purge residue) | Exposure: Operator inside enclosed separator | Barrier Failure: Entry without pre-entry atmospheric gas test and entry permit verification | Escalation: Fatal asphyxiation"`
- **`human_primary_lsr`:** `Confined Space`
- **`human_secondary_lsr`:** `Toxic Gas / Hazardous Substance`
- **`human_all_lsrs`:** `Confined Space; Toxic Gas / Hazardous Substance`
- **`human_activity`:** `Internal vessel sludge removal`
- **`human_hazard`:** `Oxygen-deficient / nitrogen-purged atmosphere`
- **`human_barrier`:** `Multi-gas atmospheric testing; Confined space entry permit controls`
- **`human_barrier_failure`:** `Vessel entered without verifying safe oxygen levels (>19.5%)`
- **`human_potential_consequence`:** `Fatal toxic/hypoxic asphyxiation`

---

### Example 6: Land Transport / Heavy Tanker Rollover
- **Narrative:** *"A crude oil transport truck was traveling on an unpaved lease road in wet conditions. The right tires drifted into the soft shoulder, causing the trailer to overturn and spill crude. The driver was wearing a seatbelt and escaped with minor bruises."*
- **`human_sif_label`:** `1`
- **`human_sif_confidence`:** `HIGH`
- **`human_sif_rationale`:** `"Energy: Heavy commercial vehicle kinetic energy | Exposure: Driver in cab during rollover | Barrier Failure: Excessive speed on degraded road surface | Escalation: Fatal vehicle rollover / cabin crush"`
- **`human_primary_lsr`:** `Driving`
- **`human_secondary_lsr`:** `Line of Fire`
- **`human_all_lsrs`:** `Driving; Line of Fire`
- **`human_activity`:** `Crude oil tanker road transport`
- **`human_hazard`:** `Heavy vehicle kinetic energy on unstable road shoulder`
- **`human_barrier`:** `In-Vehicle Monitoring System (IVMS) speed limit compliance; Safe following distance`
- **`human_barrier_failure`:** `Vehicle speed excessive for road conditions leading to shoulder collapse`
- **`human_potential_consequence`:** `Fatal vehicular rollover / severe crush injury`

---

### Example 7: Live Electrical Arc Flash / Energy Isolation
- **Narrative:** *"An electrical technician was inspecting a Motor Control Center (MCC) breaker for a seawater injection pump. While using a metal tool, the tool bridged live busbars, causing an arc flash explosion that blew the panel door open and scorched the switchgear room wall."*
- **`human_sif_label`:** `1`
- **`human_sif_confidence`:** `HIGH`
- **`human_sif_rationale`:** `"Energy: High-voltage electrical power and arc flash thermal blast | Exposure: Technician working within arc flash boundary | Barrier Failure: LOTO not executed; uninsulated tool used on live circuit | Escalation: Fatal electrocution / catastrophic arc flash burn"`
- **`human_primary_lsr`:** `Energy Isolation`
- **`human_secondary_lsr`:** `Bypassing Safety Controls`
- **`human_all_lsrs`:** `Energy Isolation; Bypassing Safety Controls`
- **`human_activity`:** `MCC electrical breaker troubleshooting`
- **`human_hazard`:** `Live electrical circuit / Arc flash explosion`
- **`human_barrier`:** `Lockout/Tagout (LOTO) zero-voltage verification; Arc-flash PPE`
- **`human_barrier_failure`:** `Breaker panel opened and worked on while energized`
- **`human_potential_consequence`:** `Fatal electrocution and severe blast/thermal trauma`

---

### Example 8: Low-Energy Non-SIF Baseline — Slip on Ice
- **Narrative:** *"An employee was walking from the field office trailer to his pickup truck across the gravel parking lot in freezing weather. He slipped on a patch of ice, fell onto his left wrist, and sustained a wrist fracture. He was transported to the clinic, casted, and hospitalized overnight for pain management."*
- **`human_sif_label`:** `0`
- **`human_sif_confidence`:** `HIGH`
- **`human_sif_rationale`:** `"Energy: Low kinetic energy (fall on same level from walking height) | Exposure: Person walking on parking lot | Barrier Failure: Ice salt not applied | Escalation: Minor non-disabling fracture; zero credible escalation pathway to death or permanent whole-person impairment"`
- **`human_primary_lsr`:** `None`
- **`human_secondary_lsr`:** `None`
- **`human_all_lsrs`:** `None`
- **`human_activity`:** `Walking across field parking lot`
- **`human_hazard`:** `Slippery ground surface (ice)`
- **`human_barrier`:** `Gravel sanding / walkway gritting`
- **`human_barrier_failure`:** `Inadequate ice clearing on parking surface`
- **`human_potential_consequence`:** `Minor localized fracture / sprain (Non-SIF)`

---

### Example 9: Low-Energy Non-SIF Baseline — Minor Tool Drawer Pinch
- **Narrative:** *"A warehouse clerk was closing a steel parts cabinet drawer while sorting pipe fittings. The drawer slammed shut on his index fingertip, resulting in a minor skin laceration and small bone chip. The employee received stitches and returned to modified duty."*
- **`human_sif_label`:** `0`
- **`human_sif_confidence`:** `HIGH`
- **`human_sif_rationale`:** `"Energy: Low mechanical energy (manually closed drawer) | Exposure: Finger in drawer gap | Barrier Failure: Inattention during closing | Escalation: Minor localized cut; zero fatal or permanent whole-person disabling potential"`
- **`human_primary_lsr`:** `None`
- **`human_secondary_lsr`:** `None`
- **`human_all_lsrs`:** `None`
- **`human_activity`:** `Sorting inventory in parts warehouse`
- **`human_hazard`:** `Cabinet drawer pinch point`
- **`human_barrier`:** `Drawer soft-close mechanism / Hand placement awareness`
- **`human_barrier_failure`:** `Finger placed in closing path of manual drawer`
- **`human_potential_consequence`:** `Minor localized laceration (Non-SIF)`

---

### Example 10: Low-Energy Non-SIF Baseline — Insect Sting
- **Narrative:** *"A roustabout was clearing weeds around the well pad perimeter fence line when he was stung by a wasp on his forearm. The area swelled mildly, and as a precaution he was driven to the regional clinic for an antihistamine injection and observation before returning to work."*
- **`human_sif_label`:** `0`
- **`human_sif_confidence`:** `HIGH`
- **`human_sif_rationale`:** `"Energy: Low biological hazard (isolated wasp sting) | Exposure: Weed trimming | Barrier Failure: N/A | Escalation: Transient localized swelling without anaphylaxis or systemic collapse; zero operational SIF precursor potential"`
- **`human_primary_lsr`:** `None`
- **`human_secondary_lsr`:** `None`
- **`human_all_lsrs`:** `None`
- **`human_activity`:** `Perimeter vegetation clearance`
- **`human_hazard`:** `Biological (wasp)`
- **`human_barrier`:** `Insect repellent / pre-work visual inspection`
- **`human_barrier_failure`:** `Wasp nest undisturbed until close contact`
- **`human_potential_consequence`:** `Minor localized skin irritation (Non-SIF)`

---

## 5. Quality Assurance & Adjudication Protocol

To guarantee high inter-annotator reliability ($>0.85$ Cohen's Kappa), the following QA protocol is enforced:

```text
               [600-Record Review Corpus]
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
[Annotator 1 (100% = 600)]         [Annotator 2 (Double Review 20% = 120)]
         │                                   │
         └─────────────────┬─────────────────┘
                           │
                 [Compare SIF & LSRs]
                    /              \
            AGREEMENT              DISAGREEMENT
                │                       │
      [Confirmed Ground Truth]   [Lead HSE SME Adjudication]
                                        │
                                 [Document Resolution in
                                  adjudication_log.json]
```

### QA Verification Rules:
1. **Invalid Label Blocker:** Any record with `human_sif_label` outside `['1', '0', 'UNKNOWN']` is flagged automatically as invalid.
2. **LSR Taxonomy Validation:** Any rule in `human_all_lsrs` not matching the official 9 IOGP names is rejected.
3. **Disagreement Logging:** Disagreements between independent annotators are recorded with full rationale before the senior adjudicator makes the final binding decision.
