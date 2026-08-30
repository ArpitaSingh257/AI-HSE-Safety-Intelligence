# OILPS Safety Intelligence Annotation Guidelines
**Governing Authority:** IOGP Safety Standards (Report 459 / 423 / 590) & OSHA Operational Safety Definitions
**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence
**Document Purpose:** Standard operating procedure for annotating SIF Potential, Multi-Label Life-Saving Rules (LSR), and Precursor Entities.

---

## 1. Core Annotation Principles

1. **Energy & Barrier Basis for SIF:** SIF Potential is determined by **Hazardous Energy Exposure + Critical Barrier Failure**, NOT by the actual injury outcome.
   - $\text{Fatality} \neq \text{Automatically SIF}$ (e.g. natural death on site is not an operational SIF precursor).
   - $\text{No Injury} \neq \text{Non-SIF}$ (e.g. dropped 1.8-ton drill pipe on empty rig floor is 100% SIF Potential).
   - $\text{Hospitalization} \neq \text{Automatically SIF}$ (e.g. heat exhaustion without vital organ damage is Low SIF).
2. **Multi-Label Life-Saving Rules:** One incident can involve multiple rules (e.g., *Working at Height* + *Line of Fire* for dropped scaffolding material).
3. **No Hallucination in Extraction:** If an entity (barrier, consequence, or hazard) is not present or directly implied by factual evidence in the text, assign `NULL` / empty string.
4. **Provenance Integrity:** Never overwrite `source` or original source labels.

---

## 2. SIF Potential Annotation Rubric

### Decision Tree for SIF Potential (`verified_sif_label`):

```text
                                [Incident Narrative]
                                         │
                   Does the event involve High Hazardous Energy?
                   (Pressure > 100 psi, Height > 1.8m, Heavy Lift > 500kg,
                    Flammables/H2S, High Voltage > 440V, Mobile Heavy Plant)
                                  /            \
                                YES             NO ────> Label = 0 (Non-SIF)
                                /
           Did a Critical Safety Barrier Fail, Degrade, or Was Absent?
           (LOTO, Gas Test, PTW, Tie-off, BOP, Exclusion Zone, Guarding)
                                /            \
                              YES             NO ────> Label = 0 (Non-SIF)
                              /
         Under realistic alternate circumstances (timing, position),
         could the event have resulted in death or permanent impairment?
                              /            \
                            YES             NO ────> Label = 0 (Non-SIF)
                            /
                 Label = 1 (SIF Potential)
```

### Reference Annotation Examples:

| Narrative Excerpt | Energy Source | Barrier State | SIF Label | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| *"90-foot stand of drill pipe (1,800 kg) slipped out of the elevators and fell towards rig floor; crew evacuated in time."* | Gravitational / Kinetic (>1.8 tons) | Elevator safety latch failed | **`1` (SIF)** | High kinetic energy + mechanical barrier failure. Catastrophic crushing potential. |
| *"Technician disconnected 2" pressurized natural gas line (85 barg) before verifying zero energy; gas hissing rapidly."* | Chemical / Pressure (85 barg) | Double block & bleed bypassed | **`1` (SIF)** | High-pressure flammable release. Vapor cloud explosion / flash fire potential. |
| *"Employee slipped on office staircase while carrying paper documents, spraining left wrist; required overnight stay."* | Low kinetic energy | Standard handrail available | **`0` (Non-SIF)** | No high energy; no escalation pathway to fatality or permanent impairment. |
| *"Worker stung by bee while inspecting perimeter fence; hospitalized for observation due to mild allergy."* | Biological / Low energy | N/A | **`0` (Non-SIF)** | Isolated medical event without structural barrier breakdown. |

---

## 3. Multi-Label IOGP Life-Saving Rules (LSR) Rubric

Assign all Life-Saving Rules that directly apply to the precursor failure.

### 1. Bypassing Safety Controls (`LSR_BYPASS`)
- **Core Rule:** Obtain authorization before overriding or disabling safety controls.
- **When to Apply:**
  - Jumpering an electrical interlock, disabling fire/gas detectors, bypassing an ESD valve.
  - Removing machine guards or safety gates without approved bypass permit.
  - Operating equipment with known safety device defeats.
- **IOGP Source Example:** *"The monkey board self-closing safety gate had been tied open with rope to accelerate casing latching."*

### 2. Confined Space (`LSR_CONFINED`)
- **Core Rule:** Obtain authorization before entering a confined space; verify atmosphere is safe.
- **When to Apply:**
  - Entry into tanks, separators, vessels, mud pits, cellars, trenches (>1.2m), vaults.
  - Lack of continuous atmospheric testing or missing standby attendant.
- **IOGP Source Example:** *"Two inspectors entered crude oil desalter vessel for internal weld inspection without positive blinding on sour drain line."*

### 3. Driving (`LSR_DRIVING`)
- **Core Rule:** Follow safe driving rules; wear seatbelts, obey speed limits, avoid distractions.
- **When to Apply:**
  - Heavy truck rollover, crew bus transit collisions on oilfield roads.
  - Speeding on lease access roads, uninspected trailer brake failure, unbuckled driver.
- **IOGP Source Example:** *"Crew change bus swerved on unpaved laterite road during rainstorm, ending on roadside pipeline with 28 passengers."*

### 4. Energy Isolation (`LSR_ISOLATION`)
- **Core Rule:** Verify isolation and zero energy state before work begins.
- **When to Apply:**
  - Lockout/Tagout (LOTO) failures; working on live 440V/11kV electrical circuits.
  - Breaking containment on lines under residual pressure (>0 psi).
  - Valve misalignment allowing pressurized fluid to energize disconnected hoses.
- **IOGP Source Example:** *"Bleed valve left unverified prior to flange loosening on 85-barg gas compressor manifold."*

### 5. Hot Work (`LSR_HOTWORK`)
- **Core Rule:** Control flammables and ignition sources in hazardous areas.
- **When to Apply:**
  - Welding, grinding, cutting torch use in Zone 0/1/2 hazardous process areas.
  - Failure to conduct continuous LEL gas monitoring during open-flame work.
- **IOGP Source Example:** *"Welder struck an arc to weld replacement flange onto crude oil manifold; trapped hydrocarbon vapors ignited."*

### 6. Line of Fire (`LSR_LINEOFFIRE`)
- **Core Rule:** Keep yourself and others out of the line of fire.
- **When to Apply:**
  - Standing under suspended loads, between moving equipment and fixed obstacles.
  - Exposed to whipping pressurized hoses, rotating catheads, tongs, or snapping winch lines.
- **IOGP Source Example:** *"Worker was positioned in narrow space between riser guide posts when 2.67-ton bottom hole assembly swung unexpectedly."*

### 7. Safe Mechanical Lifting (`LSR_LIFTING`)
- **Core Rule:** Plan lifting operations and control the area; do not walk under suspended loads.
- **When to Apply:**
  - Crane, forklift, telehandler, winch, or hoist operations.
  - Rigging failures, frayed slings, unrated shackles, missing taglines, overloaded booms.
- **IOGP Source Example:** *"Forklift lifted 714kg pipe spool using unapproved rigging; locking rim broke under pressure."*

### 8. Toxic Gas / Hazardous Substance (`LSR_TOXICGAS`)
- **Core Rule:** Protect yourself against exposure to toxic gas (H2S, SO2, CO, Benzene).
- **When to Apply:**
  - Hydrogen Sulfide (H2S) release during drilling, sampling, or vessel maintenance.
  - Breaking lines containing corrosive caustic/acid without chemical PPE and respirators.
- **IOGP Source Example:** *"Uncontrolled release of oil containing H2S occurred during flow meter calibration; personal H2S detectors alarmed."*

### 9. Working at Height (`LSR_HEIGHT`)
- **Core Rule:** Protect yourself against a fall when working at height (>1.8m).
- **When to Apply:**
  - Work on derrick platforms, scaffolding, cherry pickers, ladders, or open grating.
  - Failure to maintain 100% continuous lanyard tie-off; missing handrails/toe-boards.
- **IOGP Source Example:** *"Derrickman unclipped lanyard from inertia reel while transitioning across monkeyboard, falling 26m."*

### Auxiliary Category: Work Authorization (`LSR_WORK_AUTH`)
- **When to Apply:** Work performed without required Permit to Work (PTW), expired JSA, or unauthorized scope change.

---

## 4. Precursor Information Extraction Guidelines

For each report narrative, extract structured entities adhering strictly to the text evidence:

```text
{
  "activity": "<Standard operational verb phrase: e.g. Tripping drill pipe, Flange bolt replacement, Tank level gauging>",
  "hazard": "<Physical energy source: e.g. High-pressure natural gas (85 barg), Suspended 1.8-ton tubular load, 440V Electrical circuit>",
  "barrier": "<Intended control: e.g. Lockout/Tagout (LOTO) padlock, 5-point safety harness, Continuous LEL gas detector>",
  "barrier_failure": "<Specific failure mechanism: e.g. Bleed valve unverified before unbolting, Lanyard unclipped during transition>",
  "potential_consequence": "<Worst-case credible outcome: e.g. Fatal crush trauma, Catastrophic vapor cloud explosion, Electrocution>"
}
```

### Extraction Rules:
- **Null Safety:** If the narrative does NOT specify a barrier or exact hazard, record `""` or `None`. Do NOT speculate.
- **Conciseness:** Keep extracted entities focused (2 to 8 words per entity).

---

## 5. Annotation Workflow in `oilps_annotation.csv`

1. Open [`datasets/annotation/oilps_annotation.csv`](file:///c:/Users/Omkar%20Raut/OneDrive/Desktop/SIH-OIL/ai-service/datasets/annotation/oilps_annotation.csv).
2. For each row with `sif_annotation_status = 'REVIEW_REQUIRED'`:
   - Read `narrative`, `industry`, `severity`, and `cause`.
   - Apply the Energy + Barrier SIF decision rubric.
   - Enter `1` or `0` into `verified_sif_label`.
   - Review `candidate_primary_lsr` and `candidate_secondary_lsr`; enter approved rules into `verified_primary_lsr` and `verified_secondary_lsr`.
   - Fill `verified_activity`, `verified_hazard`, `verified_barrier_failure`, and `verified_potential_consequence`.
   - Change `sif_annotation_status` to `ANNOTATED`.
