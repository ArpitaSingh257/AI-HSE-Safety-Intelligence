# IOGP Safety Data Reporting & Domain Reference Guide
**Document Purpose:** Domain knowledge & canonical reference for the OILPS (Oil India Limited Precursor Safety) AI/NLP Pipeline.
**Governing Standard:** IOGP Safety Data Reporting User Guide / IOGP Life-Saving Rules Framework (Report 459 / 423 / 590).

---

## 1. Executive Summary & Domain Scope

In upstream and midstream Oil & Gas exploration and production (E&P), preventing major accidents, fatal incidents, and serious injuries requires identifying **precursor conditions** before catastrophic energy releases occur. 

The IOGP (International Association of Oil & Gas Producers) reporting system establishes standardized terminology, causal taxonomies, barrier definitions, and Life-Saving Rules utilized globally across operators including Oil India Limited (OIL).

---

## 2. Core Safety & SIF Terminology

### 2.1 Serious Injury & Fatality (SIF) Potential
- **Definition:** An event, unsafe act, unsafe condition, or near-miss where high-energy hazards or critical safety barriers failed, such that under slightly different circumstances (e.g., timing, distance, barrier configuration), a serious life-altering injury or fatality would have been the credible outcome.
- **Critical Distinction:** **SIF Potential $\neq$ Actual Injury Outcome**. An incident with zero injuries (e.g., dropped tubular from a derrick, uncontrolled hydrocarbon release, bypassed high-pressure ESD valve) can have **100% SIF Potential**, whereas a fractured finger from a dropped hand tool in an office workshop may have **Low SIF Potential**.

### 2.2 High Potential Event (HiPo / HPE)
- **IOGP Definition:** Any incident or near-miss that could have reasonably resulted in one or more fatalities or permanent disabling injuries under realistic alternate circumstances.
- **Characteristics in Data:**
  - High energy involved (mechanical, kinetic, electrical, pressure, gravitational, chemical/toxic).
  - Failure or absence of a critical barrier (LOTO, permit-to-work, gas testing, safety harness, blowout preventer).
  - Breach of an IOGP Life-Saving Rule.

### 2.3 Process Safety vs. Personal Safety Events
- **Process Safety Event (PSE):** Unplanned or uncontrolled release of any material including toxic substances, flammable hydrocarbons, or hazardous chemicals from primary containment (Tier 1 & Tier 2 per API RP 754 / IOGP Report 456).
- **Personal / Occupational Safety Event:** Incidents directly involving workforce physical interactions (falls from height, line of fire, struck-by suspended load, confined space asphyxiation, electrocution).

---

## 3. Safety Barrier Taxonomy & Failure Modes

A **Barrier** is any operational, engineered, or administrative control intended to prevent an initiator from escalating into a hazardous event, or mitigating the consequences thereof.

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Hazardous     │ ──X── │    Critical     │ ──X── │ Serious Injury  │
│ Energy Source   │       │ Safety Barrier  │       │   or Fatality   │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                   ▲
                             Failure Modes:
                       - Omission / Bypassed
                       - Degradation / Defective
                       - Inadequate Specification
                       - Human Error / Violation
```

### 3.1 Primary Barrier Categories
1. **Engineered / Physical Barriers:** Pressure relief valves (PRV), Emergency Shutdown (ESD) systems, machine guarding, blowout preventers (BOP), fire & gas detection systems, interlocks, scaffolding handrails.
2. **Administrative / Procedural Barriers:** Permit to Work (PTW), Lockout/Tagout (LOTO), Job Safety Analysis (JSA), energy isolation verification, pre-job safety meetings, gas testing protocols.
3. **Personal Protective Equipment (PPE) Barriers:** 5-point full body safety harness with 100% tie-off, self-contained breathing apparatus (SCBA), arc-flash suits, chemical resistant suits.

### 3.2 Barrier Failure Modes
- **Bypassed / Defeated:** Intentionally overriding an interlock, disabling a gas detector, or proceeding without applying padlocks.
- **Defective / Degraded:** Corroded pipe, frayed lifting sling, expired harness, leaking flange gasket, failed pressure relief valve.
- **Inadequate / Missing:** Working on energized circuits without PPE, entering tank without atmospheric testing, lifting load without lift plan or exclusion zone.
- **Procedural Breach:** Failure to follow standard operating procedure (SOP), communication breakdown between drill crew and mud engineer.

---

## 4. The 9 IOGP Life-Saving Rules (LSR) Reference

The IOGP Life-Saving Rules (IOGP Report 459) provide standard, actionable interventions targeting the most frequent fatal precursor scenarios in oil and gas operations.

| Life-Saving Rule | Code | Standard Definition | Key Precursor Indicators / Triggers |
| :--- | :--- | :--- | :--- |
| **Bypassing Safety Controls** | `LSR_BYPASS` | Obtain authorization before overriding or disabling safety controls. | Overriding ESD, jumpering safety interlock, disabling gas/fire detector, operating without guard, unauthorized hot-wire. |
| **Confined Space** | `LSR_CONFINED` | Obtain authorization before entering a confined space; verify atmosphere is safe. | Entry into vessel, tank, separator, sewer, pit, mud tank, or void space; oxygen deficiency; toxic gas accumulation; no attendant. |
| **Driving** | `LSR_DRIVING` | Follow safe driving rules; wear seatbelt, obey speed limits, avoid mobile phone use. | Crew bus transit, oilfield tanker rollover, speeding on rig access road, fatigue, unsecured load in pickup bed, seatbelt unbuckled. |
| **Energy Isolation** | `LSR_ISOLATION`| Verify isolation and zero energy state before work begins. | Electrical breaker lock, double block and bleed (DBB), LOTO padlock, residual pressure bleed-off, live line breaking. |
| **Hot Work** | `LSR_HOTWORK` | Control flammables and ignition sources in hazardous areas. | Welding, grinding, cutting, open flame in hazardous Zone 0/1/2, lack of spark containment, missing continuous gas monitoring. |
| **Line of Fire** | `LSR_LINEOFFIRE`| Keep yourself and others out of the line of fire. | Suspended loads, high-pressure test zones, energized hydraulic hoses, rotating drill pipe/cathead, pipe whip, pinch points. |
| **Safe Mechanical Lifting**| `LSR_LIFTING` | Plan lifting operations and control the area; do not walk under suspended loads. | Mobile crane, offshore pedestal crane, winch, forklift, slings, rigging hardware, overloaded boom, tagline missing, exclusion zone breached. |
| **Toxic Gas / Substances** | `LSR_TOXICGAS` | Protect yourself against exposure to toxic gas (e.g. H2S, benzene, CO). | Hydrogen sulfide (H2S) in drilling mud/wellhead, benzene exposure during sampling, sour gas leak, personal gas detector alarm. |
| **Working at Height** | `LSR_HEIGHT` | Protect yourself against a fall when working at height (>1.8m or over water/equipment). | Derrick monkey board, mast climbing, scaffolding without toe-board, cherry picker/MEWP without harness lanyard attached, open grating. |

---

## 5. Causal Factors & Precursor Taxonomies

To build an explainable intelligence pipeline, safety narratives are deconstructed into structured precursor components:

```
[Safety Report Narrative]
          │
          ├──> Activity               (e.g., Wellhead Xmas Tree Maintenance)
          ├──> Hazard                 (e.g., Pressurized Sour Hydrocarbons / H2S)
          ├──> Barrier                (e.g., Double Block and Bleed Isolation)
          ├──> Barrier Failure        (e.g., Upstream Isolation Valve Leaking)
          ├──> Potential Consequence  (e.g., High-Pressure Toxic Gas Release & Explosion)
          └──> Applicable LSR         (e.g., Energy Isolation, Toxic Gas)
```

### 5.1 Standard Upstream/Midstream Oil & Gas Activities
- **Drilling & Well Operations:** Tripping pipe, casing running, cementing, BOP testing, drilling fluid circulation, wireline logging, perforating.
- **Workover & Well Intervention:** Coiled tubing, snubbing, hydraulic fracturing, wellhead nipple-up, artificial lift installation.
- **Production & Plant Operations:** Pig launching/receiving, crude oil storage tank dipping, gas compressor maintenance, separator desanding.
- **Logistics & Marine:** Pipe yard loading, heavy haul transport, crew boat transfer, seismic survey mobilization.
- **Construction & Rig Move:** Derrick dismantling, mast scoping, pipeline trenching, hydrotesting, structural welding.

### 5.2 Standard Oil & Gas Hazards
1. **Flammable & Explosive Hydrocarbons:** Condensate, natural gas, crude oil mist, LPG.
2. **Toxic & Asphyxiating Gases:** H2S, Carbon Monoxide, Nitrogen purge, Sulphur Dioxide.
3. **High Pressure:** Wellhead pressure (5000+ psi), pneumatic/hydraulic lines, hydrotest manifolds.
4. **Gravitational / Elevated:** Fall from derrick, dropped objects from crown block (DROPS).
5. **High-Voltage Electrical:** Motor Control Centers (MCC), transformers, generator switchboards (440V - 11kV).
6. **Mechanical & Kinetic Energy:** Rotating kelly bushing, cathead, drawworks drum, winch lines under tension.

---

## 6. Annotation & Mapping Rules for OILPS

1. **SIF Determination Rule:**
   - Label = `1` (SIF Potential) IF the event involved high energy or critical toxic/flammable hazards AND at least one critical barrier failed or was absent, such that serious injury or fatality was plausible.
   - Label = `0` (Non-SIF) IF the event was low energy, administrative non-conformance without escalation path, or minor ergonomic/housekeeping hazard.
   - Label = `UNKNOWN / NEEDS_REVIEW` IF the narrative lacks critical context (e.g. pressure, height, or exact energy level).

2. **LSR Multi-Label Rule:**
   - Multiple rules may apply to a single incident (e.g., *Working at Height* + *Line of Fire* for a dropped tool from a scaffold; *Energy Isolation* + *Toxic Gas* for breaking a sour gas flange without LOTO).
   - Only assign rules when explicit or direct implicit evidence exists in the text.

3. **No Hallucination Rule:**
   - If an entity (e.g., exact barrier failure or location) is not mentioned in the source report, the extracted field must remain `NULL` / `None`.
