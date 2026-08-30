# STAGE 15: AI SAFETY RECOMMENDATION ENGINE REPORT

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence  
**Component:** Decision-Support Safety Recommendation Engine  
**Date:** 2026-08-30  
**Status:** **OPERATIONAL & PRODUCTION-READY**  

> [!IMPORTANT]
> **Safety Guardrail Disclaimer:** Stage 15 does **not** retrain or modify the SIF/LSR models. Recommendations are generated as a separate decision-support layer using model outputs and a structured safety knowledge mapping. They do not replace site operating procedures or qualified HSE professional judgment.

---

## 1. Safety Recommendation Engine Architecture

```text
Incident Narrative Text
          ↓
Stage 6 SIF Model  ──> SIF Probability, Classification & Risk Tier
          ↓
Stage 7 LSR Model  ──> Multi-Label Life-Saving Rule Probabilities & Triggers
          ↓
Safety Recommendation Engine (inference/recommendation_engine.py)
          ↓
IOGP Life-Saving Rules Knowledge Base (knowledge/lsr_recommendations_kb.py)
          ↓
Structured Actionable Output:
  • Priority Level (CRITICAL / HIGH / MODERATE / LOW)
  • Executive Risk Summary
  • Immediate Stop-Work / Emergency Actions
  • Barrier & Control Verification Checklist
  • Management Escalation Protocols
```

---

## 2. Priority Hierarchy & Risk-Tier Mapping

| SIF Precursor Status | Life-Saving Rules Triggered | Safety Action Priority | Required Response Scope |
| :--- | :--- | :--- | :--- |
| **`is_sif = True`** or **`CRITICAL_SIF_PRECURSOR`** | Any | **`CRITICAL`** | Immediate Stop Work Authority (SWA), physical energy isolation verification, mandatory Superintendent & HSE escalation. |
| **`ELEVATED_SIF_POTENTIAL`** | $\ge 2$ Rules | **`HIGH`** | Pre-job safety barrier walk, permit re-validation, supervisor review before proceeding. |
| **`MODERATE_HAZARD`** | $1$ Rule | **`MODERATE`** | JSA control confirmation and toolbox talk communication. |
| **`LOW_POTENTIAL_INCIDENT`** | None ($0$) | **`LOW`** | Standard first-aid and routine housekeeping; zero critical escalation. |

---

## 3. The 9 IOGP Life-Saving Rules Knowledge Base Mappings

1. **Bypassing Safety Controls:** MOC verification, physical ESD interlock inspections, dedicated safety watch during bypass.
2. **Confined Space:** Immediate entry prohibition, continuous multi-gas atmospheric testing, mechanical forced ventilation, trained entrance attendant.
3. **Driving:** IVMS speed and braking compliance, Journey Management Plan (JMP), 100% seatbelt adherence, zero mobile phone usage.
4. **Energy Isolation:** Lockout/Tagout (LOTO) padlocks, blind flanges / double block & bleed, physical bleeder valve depressurization check.
5. **Hot Work:** 15m radius LEL gas testing (<1%), combustible removal/shielding, dedicated Fire Watch with charged extinguishers (+30 min watch).
6. **Line of Fire:** Red hazard zone barricading, hands-free taglines for suspended loads, whip-checks on high-pressure hoses.
7. **Safe Mechanical Lifting:** Certified Lift Plan execution, pre-lift sling/shackle inspection, clear drop-zone enforcement, ground stability checks.
8. **Toxic Gas / Hazardous Substance:** Upwind evacuation on alarm, positive-pressure SCBA gear, personal multi-gas bump testing (H2S alarm >5 ppm).
9. **Working at Height:** 100% double-lanyard tie-off, full-body harness inspection, green-tagged scaffolding with guardrails and toe boards.

---

## 4. Example End-to-End API Recommendation Output

When calling `POST /api/v1/analyze` for a high-pressure hydrotest incident:

```json
{
  "incident_id": "INC-2026-0042",
  "incident_text": "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting. The bleeder plug ruptured and struck the worker in the chest.",
  "sif": {
    "probability": 0.9842,
    "threshold": 0.30,
    "is_sif": true,
    "risk_tier": "CRITICAL_SIF_PRECURSOR"
  },
  "lsr": {
    "triggered_rules": ["Energy Isolation", "Line of Fire"]
  },
  "recommendations": {
    "priority": "CRITICAL",
    "summary": "CRITICAL PRECURSOR EVENT: Immediate high-energy hazard detected. Work in affected area must be placed on hold until critical barriers and energy isolation are physically verified.",
    "immediate_actions": [
      "Initiate immediate 'Stop Work Authority' (SWA) if high-energy operations remain active.",
      "Cease work on pressurized, electrical, or mechanical systems immediately.",
      "Verify positive isolation, depressurization, and de-energization (zero energy state).",
      "Establish and barricade red hazard zones around moving equipment, suspended loads, and pressurized lines."
    ],
    "control_verification": [
      "Verify primary and secondary safety barriers for all active energy sources.",
      "Conduct physical bleeder valve checks and electrical voltage testing to prove zero residual energy.",
      "Verify Isolation Certificate against the Piping and Instrumentation Diagram (P&ID).",
      "Confirm physical barriers and warning signage are intact before initiating high-energy operations."
    ],
    "escalation": [
      "Notify Site Superintendent, Safety Officer, and Operations Manager for mandatory SIF review.",
      "Escalate any pressurized leak, incomplete isolation, or failed bleed test directly to the Maintenance Lead.",
      "Report all dropped objects, snapped cables, and projectile events into the Precursor Safety System."
    ]
  }
}
```
