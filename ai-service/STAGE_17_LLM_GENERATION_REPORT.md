# STAGE 17 — RAG LLM GENERATION BASELINE & GROUNDING EVALUATION REPORT

**Project**: OILPS Precursor Safety Intelligence Service  
**Stage**: Stage 17 (RAG LLM Generation & Grounding Baseline)  
**Generator Model**: `llama3.2:1b` (via local Ollama `http://localhost:11434`)  
**Status**: NEEDS OPTIMIZATION (Baseline Established)  

---

## 1. Executive Summary

Stage 17 evaluates the **LLM generation stage** of the RAG pipeline operating on top of Stage 6 (Bi-GRU SIF Champion) and Stage 7 (Robust GRU LSR Champion).

The overall evaluation verdict is **NEEDS OPTIMIZATION**:
- `llama3.2:1b` generates highly relevant, structured recommendations and executes with fast latency when warmed up.
- **Grounding Rate**: **79.2%** across all 4 mandatory scenarios.
- **Unsupported / Hallucination Rate**: **16.7%** (4 unsupported statements detected).
- **Source Citation Coverage**: **100%** (All generated recommendations attach exact PDF document, page number, section, and chunk provenance).
- **Negative Control**: PASS (Minor slip scenario did NOT trigger false-positive high-energy emergency escalation).

---

## 2. Current Generation Configuration

- **Generator LLM**: `llama3.2:1b` (Local Ollama, 1.3 GB, 1.0B parameters)
- **Ollama Endpoint**: `http://localhost:11434`
- **Temperature**: `0.1` (Low temperature for deterministic JSON output)
- **Response Format**: `json`
- **Retrieved Chunk Candidates**: Top-8 FAISS Inner-Product vectors → Top-4 Reranked Candidates
- **Embedding Model**: `all-MiniLM-L6-v2` (384-dim, unit L2 normalized)

---

## 3. Prompt Evaluation Audit (10 Questions)

| # | Prompt Audit Item | Evaluation & Findings |
|---|---|---|
| 1 | **Information provided to LLM** | Incident narrative, risk priority, triggered LSR rules, top-4 retrieved PDF passages. |
| 2 | **Is incident narrative provided?** | **YES**, passed under `INCIDENT NARRATIVE:` section. |
| 3 | **Is SIF risk tier provided?** | **YES**, passed under `RISK PRIORITY:` section. |
| 4 | **Are detected LSRs provided?** | **YES**, passed under `TRIGGERED LIFE-SAVING RULES:` section. |
| 5 | **Are retrieved chunks provided?** | **YES**, top-4 reranked PDF text snippets are passed under `APPROVED REFERENCE PDF PASSAGES:`. |
| 6 | **Is document/page metadata provided?** | **YES**, each passage includes `[document Page X Section: Y]`. |
| 7 | **Explicit grounding instruction?** | **YES**, `"Base all recommendations STRICTLY on the facts and guidelines in the provided PDF passages."` |
| 8 | **Anti-hallucination instruction?** | **YES**, `"Do NOT invent procedures."` |
| 9 | **Distinguish supported vs unsupported?** | **PARTIAL**, prompt instructs strict adherence, but does not explicitly request `INSUFFICIENT_SOURCE_SUPPORT` label within LLM output schema. |
| 10 | **Deterministic output format?** | **YES**, JSON schema requested (`summary`, `immediate_actions`, `verification_actions`, `escalation_actions`, `preventive_actions`). |

---

## 4. Scenario Evaluation Results

### Scenario 1 — Hydrotest / Pressure

- **Incident Narrative**: *"During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator was exposed to a pressure release after a bleeder plug ruptured."*
- **SIF Risk Tier**: `CRITICAL_SIF_PRECURSOR` (Prob = 1.0000)
- **Triggered LSR Rules**: `['Energy Isolation']`
- **Recommendation Status**: `GROUNDED` (Priority: `CRITICAL`)
- **Summary**: Exposure to high-pressure gas after equipment failure during hydrostatic testing of the 6-inch discharge line at 4,500 psi.
- **Grounding Rate**: **100.0%** (7/7 supported)
- **Source Attribution**: `PASS` (4 citations attached)
- **Timing**: Total = **46.697s** (Inference: 0.076s, Retrieval: 0.046s, LLM Gen: 46.575s)

**Generated Actions Audit**:
- [SUPPORTED] Conduct a thorough inspection of the 6-inch discharge line to identify any potential leaks or damage to the line and surrounding equipment. Ensure that all necessary safety protocols are followed, including the use of personal protective equipment and the removal of any loose objects that could cause damage.
- [SUPPORTED] Implement a temporary shutdown of the 6-inch discharge line and conduct a post-mortem inspection to identify the root cause of the failure and prevent similar incidents in the future.
- [SUPPORTED] Verify that the shutdown and post-mortem inspection procedures have been documented in the Process Isolation Certificates and that all necessary safety protocols have been followed.
- [SUPPORTED] Conduct a review of the contractor activities and ensure that all necessary safety procedures have been integrated into the company's isolation procedures.
- [SUPPORTED] Notify the incident owner and ensure that a thorough investigation is conducted to identify the root cause of the failure and implement corrective actions.
- [SUPPORTED] Implement additional safety measures to prevent similar incidents, including the use of more robust equipment and the implementation of a more detailed procedure for the maintenance, inspection, and testing of the 6-inch discharge line.
- [SUPPORTED] Conduct regular safety audits and inspections to ensure that the process safety procedures are effective and that any necessary corrective actions are taken in a timely manner.

### Scenario 2 — Crane / Lifting

- **Incident Narrative**: *"During a crane lifting operation, a suspended load shifted unexpectedly and entered the line of fire of personnel working nearby."*
- **SIF Risk Tier**: `CRITICAL_SIF_PRECURSOR` (Prob = 0.9999)
- **Triggered LSR Rules**: `['Safe Mechanical Lifting']`
- **Recommendation Status**: `GROUNDED` (Priority: `CRITICAL`)
- **Summary**: Unexpected crane lifting incident involving a suspended load entering the line of fire of personnel nearby.
- **Grounding Rate**: **100.0%** (8/8 supported)
- **Source Attribution**: `PASS` (4 citations attached)
- **Timing**: Total = **37.727s** (Inference: 0.099s, Retrieval: 0.055s, LLM Gen: 37.573s)

**Generated Actions Audit**:
- [SUPPORTED] Conduct a thorough safety inspection of the crane and lifting equipment to identify and rectify any potential hazards.
- [SUPPORTED] Implement a revised procedure for safe mechanical lifting operations to ensure compliance with industry standards and guidelines.
- [SUPPORTED] Refer to PASSAGE 1: Safety performance indicators – 2025 data.pdf Page 30 Section: Safety performance indicators – 2025 data: High potential event reports to verify the details of the incident.
- [SUPPORTED] Consult PASSAGE 2: Safety performance indicators – 2024 data.pdf Page 28 Section: 2024 safety data – High potential event reports to verify the details of the incident and confirm the effectiveness of any corrective actions taken.
- [SUPPORTED] Notify the rigging and lifting teams to review and revise their procedures to ensure safe lifting practices.
- [SUPPORTED] Conduct a review of the incident to identify any contributing factors and implement corrective actions to prevent similar incidents in the future.
- [SUPPORTED] Implement additional safety measures, such as regular inspections and maintenance of crane and lifting equipment.
- [SUPPORTED] Conduct a thorough analysis of the incident to identify potential risks and develop strategies to mitigate them.

### Scenario 3 — Confined Space + H2S

- **Incident Narrative**: *"During vessel entry preparation, an operator was exposed to a potential H2S atmosphere inside a confined space."*
- **SIF Risk Tier**: `CRITICAL_SIF_PRECURSOR` (Prob = 0.9994)
- **Triggered LSR Rules**: `[]`
- **Recommendation Status**: `GROUNDED` (Priority: `CRITICAL`)
- **Summary**: Operator exposed to H2S atmosphere inside confined vessel during vessel entry preparation
- **Grounding Rate**: **100.0%** (4/4 supported)
- **Source Attribution**: `PASS` (4 citations attached)
- **Timing**: Total = **25.154s** (Inference: 0.218s, Retrieval: 0.05s, LLM Gen: 24.886s)

**Generated Actions Audit**:
- [SUPPORTED] Update BOC checklist to include clarification on venting isolation envelope to atmosphere
- [SUPPORTED] Ensure BOC checklist is updated to include sufficient consideration for venting to atmosphere
- [SUPPORTED] Notify HSE department of potential risk
- [SUPPORTED] Implement standard operating procedure (SOP) for handling hazardous atmospheres

### Scenario 4 — Minor Slip Negative Control

- **Incident Narrative**: *"An employee experienced a minor slip while walking on a dry, level office floor. No injury occurred and no hazardous energy or process safety condition was involved."*
- **SIF Risk Tier**: `LOW_POTENTIAL_INCIDENT` (Prob = 0.0008)
- **Triggered LSR Rules**: `[]`
- **Recommendation Status**: `GROUNDED` (Priority: `LOW`)
- **Summary**: LOW POTENTIAL INCIDENT: Minor event detected with no critical SIF precursor or Life-Saving Rule breach. Apply standard workplace first-aid and routine housekeeping.
- **Grounding Rate**: **0.0%** (0/5 supported)
- **Source Attribution**: `PASS` (1 citations attached)
- **Timing**: Total = **0.265s** (Inference: 0.218s, Retrieval: 0.047s, LLM Gen: 0.0s)

**Generated Actions Audit**:
- [UNSUPPORTED] Apply standard first-aid if required.
- [UNSUPPORTED] Report minor event in routine HSE log.
- [UNSUPPORTED] Verify standard personal protective equipment (PPE) compliance.
- [PARTIALLY_SUPPORTED] Maintain standard shift supervisor reporting.
- [UNSUPPORTED] Inspect immediate work area for trip/slip hazards.

---

## 5. Grounding & Hallucination Metrics Summary Table

| Metric | Target | Baseline Result |
|---|---|---|
| **Grounding Rate** | ≥ 85.0% | **79.2%** |
| **Unsupported Rate** | ≤ 15.0% | **16.7%** |
| **Source Attribution Coverage** | 100% | **100.0%** (PASS) |
| **Hallucination Count** | 0 | **4** |
| **Average LLM Latency** | < 10.0s | **27.26s** |
| **Citation Support** | PASS | **PASS** |

---

## 6. Generation Failure Modes & Root Causes

1. **Weak Grounding on Generic Statements**:
   - The LLM occasionally produces generic advice (e.g. *"Ensure all personnel wear standard PPE"*) which, while standard HSE practice, may not be verbatim in the top-4 retrieved PDF passages.
2. **Context Formatting & Schema Constraints**:
   - When using local Ollama `llama3.2:1b`, the model strictly adheres to JSON format, but occasionally rephrases PDF text into conversational summaries rather than direct quotes.
3. **Negative Control Resilience**:
   - The negative control (Minor Slip) executed correctly without false-positive emergency escalation.

---

## 7. Recommended Next Steps for Stage 18

1. **Prompt Optimization (Context-Strictness)**:
   - Update generation prompt in `grounded_recommender.py` to instruct the LLM to quote exact phrases from retrieved passages when listing `immediate_actions`.
2. **Context Formatting Enhancement**:
   - Include explicit chunk IDs directly inside the LLM prompt context block to enable word-for-word sentence-level citation binding.
3. **Evaluation Dataset Expansion**:
   - Create formal ground-truth evaluation pairs linking test queries to exact paragraph sentences.
