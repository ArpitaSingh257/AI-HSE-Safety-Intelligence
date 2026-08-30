"""
lsr_recommendations_kb.py - Centralized IOGP Life-Saving Rules Safety Recommendation Knowledge Base.
Provides structured, actionable, and decision-support guidance for all 9 official IOGP Life-Saving Rules.
"""

LSR_KNOWLEDGE_BASE = {
    "Bypassing Safety Controls": {
        "rule_name": "Bypassing Safety Controls",
        "description": "Obtain authorization before overriding, disabling, or bypassing any safety controls or interlocks.",
        "immediate_actions": [
            "Halt the affected operation immediately until safety control status is verified.",
            "Verify whether safety device override/interlock bypass has formal management of change (MOC) approval."
        ],
        "recommended_controls": [
            "Enforce strict permit-to-work (PTW) bypass authorization procedures.",
            "Log and track all temporary safety overrides on a dedicated site bypass register with explicit time limits."
        ],
        "verification_actions": [
            "Inspect physical interlocks, emergency shutdown (ESD) valves, and safety switches prior to restart.",
            "Confirm that redundant monitoring or dedicated safety watch is stationed while bypass is active."
        ],
        "escalation_guidance": "Escalate unauthorized safety control bypasses immediately to the Site Superintendent and Lead HSE Officer."
    },
    "Confined Space": {
        "rule_name": "Confined Space",
        "description": "Obtain authorization before entering a confined space.",
        "immediate_actions": [
            "Prohibit all personnel entry into the enclosed vessel, separator, tank, or mud pit.",
            "Immediately verify atmospheric testing for oxygen levels, explosive vapors, and toxic gases (H2S, CO)."
        ],
        "recommended_controls": [
            "Mandate active mechanical forced-air ventilation throughout the duration of entry.",
            "Ensure continuous multi-gas monitoring at multiple depths within the confined space.",
            "Station a dedicated, trained Confined Space Attendant at the entrance with emergency retrieval gear."
        ],
        "verification_actions": [
            "Inspect signed Confined Space Entry Permit and gas test log sheet before authorizing entry.",
            "Verify all energy lines connected to the vessel are positively isolated with blind flanges (LOTO)."
        ],
        "escalation_guidance": "Any unmonitored or unauthorized entry must trigger immediate evacuation and HSE incident reporting."
    },
    "Driving": {
        "rule_name": "Driving",
        "description": "Follow safe driving rules: wear seatbelts, respect speed limits, and avoid mobile phone use while driving.",
        "immediate_actions": [
            "Review vehicle roadworthiness, tire integrity, and load securement before field transit.",
            "Ensure driver is fully rested, licensed, and briefed on weather/route hazards."
        ],
        "recommended_controls": [
            "Enforce in-vehicle monitoring systems (IVMS) with real-time speed and harsh braking alerts.",
            "Implement journey management plans (JMP) for long-distance or remote oilfield transits."
        ],
        "verification_actions": [
            "Verify 100% seatbelt compliance for all vehicle occupants prior to departure.",
            "Confirm zero mobile device interaction policy during vehicle operation."
        ],
        "escalation_guidance": "Report vehicle rollovers, near-misses, and road transport collisions to Fleet Management and HSE."
    },
    "Energy Isolation": {
        "rule_name": "Energy Isolation",
        "description": "Verify isolation and zero energy state before work begins.",
        "immediate_actions": [
            "Cease work on pressurized, electrical, or mechanical systems immediately.",
            "Verify positive isolation, depressurization, and de-energization (zero energy state)."
        ],
        "recommended_controls": [
            "Apply Lockout/Tagout (LOTO) padlocks and tags at all physical isolation points.",
            "Install tested blind flanges or double block and bleed (DBB) arrangements on pressurized manifolds."
        ],
        "verification_actions": [
            "Conduct physical bleeder valve checks and electrical voltage testing to prove zero residual energy.",
            "Verify Isolation Certificate against the Piping and Instrumentation Diagram (P&ID)."
        ],
        "escalation_guidance": "Escalate any pressurized leak, incomplete isolation, or failed bleed test directly to the Maintenance Lead."
    },
    "Hot Work": {
        "rule_name": "Hot Work",
        "description": "Control flammables and ignition sources.",
        "immediate_actions": [
            "Stop all open flame, welding, cutting, and grinding activities in hazardous zones.",
            "Conduct atmospheric combustible gas testing (LEL < 1%) across the 15-meter radius."
        ],
        "recommended_controls": [
            "Remove all combustible materials or shield with certified fire-retardant blankets.",
            "Deploy a dedicated Fire Watch with charged fire extinguishers for the duration of hot work plus 30 mins after."
        ],
        "verification_actions": [
            "Inspect valid Hot Work Permit and continuous LEL gas detector calibration.",
            "Verify pressurized process lines within the radius are purged, isolated, or shielded."
        ],
        "escalation_guidance": "Any gas detection alarm or fire flash must trigger immediate work stoppage and alarm activation."
    },
    "Line of Fire": {
        "rule_name": "Line of Fire",
        "description": "Keep yourself and others out of the line of fire.",
        "immediate_actions": [
            "Establish and barricade red hazard zones around moving equipment, suspended loads, and pressurized lines.",
            "Reposition all personnel to designated safe standing zones outside swing trajectories."
        ],
        "recommended_controls": [
            "Use hands-free taglines and push-poles for guiding loads rather than manual hand contact.",
            "Install whip-checks and safety restraints on all high-pressure hose connections."
        ],
        "verification_actions": [
            "Confirm physical barriers and warning signage are intact before initiating high-energy operations.",
            "Conduct pre-job Line-of-Fire hazard walk with the work crew during toolbox talks (TBT)."
        ],
        "escalation_guidance": "Report all dropped objects, snapped cables, and projectile events into the Precursor Safety System."
    },
    "Safe Mechanical Lifting": {
        "rule_name": "Safe Mechanical Lifting",
        "description": "Plan lifting operations and control the lift area.",
        "immediate_actions": [
            "Suspend lifting operations immediately if rigging integrity, crane stability, or load path is compromised.",
            "Verify that no personnel are standing beneath or adjacent to the suspended load."
        ],
        "recommended_controls": [
            "Execute lift strictly according to an approved Lift Plan (critical lift review for loads > 10 tons).",
            "Use certified, color-coded slings, shackles, and spreader bars with valid load inspection tags."
        ],
        "verification_actions": [
            "Inspect slings for cuts, abrasions, wire kinks, or sharp edge contact before every lift.",
            "Verify ground bearing capacity, outrigger extension pads, and crane load-chart limits."
        ],
        "escalation_guidance": "Parted slings, crane load-moment limiter trips, or uncontrolled load drops require immediate HSE investigation."
    },
    "Toxic Gas / Hazardous Substance": {
        "rule_name": "Toxic Gas / Hazardous Substance",
        "description": "Wear respiratory protection and monitor for toxic gas releases (e.g. H2S).",
        "immediate_actions": [
            "Evacuate upwind/crosswind immediately if toxic gas (H2S, sulfur dioxide) alarm triggers.",
            "Mandate positive-pressure Self-Contained Breathing Apparatus (SCBA) or airline respirators."
        ],
        "recommended_controls": [
            "Deploy fixed and personal multi-gas monitors set to conservative alarm thresholds (H2S > 5 ppm).",
            "Establish secondary emergency muster points and maintain visible wind socks across the facility."
        ],
        "verification_actions": [
            "Bump test and calibrate personal gas detectors prior to shift entry into designated gas zones.",
            "Confirm emergency escape breathing apparatus (EEBA) packs are present and fully pressurized."
        ],
        "escalation_guidance": "Any confirmed toxic gas release > 10 ppm requires immediate facility alarm and emergency team mobilization."
    },
    "Working at Height": {
        "rule_name": "Working at Height",
        "description": "Protect yourself against a fall when working at height (> 1.8 meters / 6 feet).",
        "immediate_actions": [
            "Halt elevated work if fall protection, guardrails, or anchor points are missing or unsecured.",
            "Ensure 100% tie-off using a certified full-body harness with double lanyards."
        ],
        "recommended_controls": [
            "Install engineered anchor points capable of supporting 5,000 lbs (22.2 kN) per worker.",
            "Erect fully planked scaffolding with double guardrails, toe boards, and green inspection tags."
        ],
        "verification_actions": [
            "Inspect harnesses, lanyards, and self-retracting lifelines (SRLs) for damage or deployment markers.",
            "Verify scaffold erection tag validity and secure tools with lanyards to prevent dropped objects."
        ],
        "escalation_guidance": "Falls from height, deployed fall arresters, or scaffold structural shifts require immediate medical and safety review."
    }
}
