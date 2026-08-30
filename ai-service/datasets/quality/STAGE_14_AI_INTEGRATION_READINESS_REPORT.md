# STAGE 14: AI INTEGRATION READINESS & INFERENCE API CONTRACT REPORT

**Problem Statement:** SIH26165 — Oil India Limited Precursor Safety Intelligence  
**Component:** Production AI Service REST API & Integration Contract  
**Date:** 2026-08-30  
**Status:** **API INTEGRATION READY**  

> [!IMPORTANT]
> **Boundary Notice:** Stage 14 prepares the AI service for integration through a clean REST API contract; MERN/frontend integration is **NOT** performed in this stage.

---

## 1. AI Service Architecture & Frozen Production Champions

The AI inference microservice is encapsulated within `ai-service/app/` using FastAPI and Pydantic v2:

1. **SIF Binary Classifier Champion:**
   - **Architecture:** `Stage 6 Bidirectional GRU + Softmax Sequence Attention`
   - **Decision Threshold:** `0.30` (Validation-optimized for safety-critical precursor sensitivity)
   - **Test Recall (SIF=1):** `96.97%` | **Test F1:** `0.9231` | **PR-AUC:** `0.9715`
   - **Artifact Path:** `ai-service/models/sif/sif_model.pt`

2. **LSR Multi-Label Classifier Champion:**
   - **Architecture:** `Stage 7 Robust Bidirectional GRU + Scaled-Dot-Product Attention with LayerNorm`
   - **Thresholds:** Stage 7 Validation-Derived Independent Rule Thresholds:
     - *Bypassing Controls:* `0.50`, *Confined Space:* `0.50`, *Driving:* `0.25`, *Energy Isolation:* `0.30`, *Hot Work:* `0.45`, *Line of Fire:* `0.20`, *Safe Mechanical Lifting:* `0.20`, *Toxic Gas:* `0.50`, *Working at Height:* `0.25`.
   - **Test Micro-F1:** `0.7020` | **Exact Match Ratio:** `71.74%` | **Hamming Loss:** `0.0362`
   - **Artifact Path:** `ai-service/models/lsr/lsr_model.pt`

---

## 2. Production API Endpoints & Contract

### Endpoint 1: Precursor Safety Analysis
- **Route:** `POST /api/v1/analyze`
- **Request Content-Type:** `application/json`
- **Request Body Schema:**
```json
{
  "incident_text": "During hydrostatic testing of the 6-inch high pressure discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting. The bleeder plug ruptured and struck the worker in the chest.",
  "incident_id": "INC-2026-0042"
}
```

- **Response Body Schema (HTTP 200 OK):**
```json
{
  "incident_id": "INC-2026-0042",
  "incident_text": "During hydrostatic testing of the 6-inch high pressure discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting. The bleeder plug ruptured and struck the worker in the chest.",
  "sif": {
    "probability": 0.9842,
    "threshold": 0.30,
    "is_sif": true,
    "risk_tier": "CRITICAL_SIF_PRECURSOR",
    "salient_tokens": [
      {"token": "pressure", "weight": 0.2410},
      {"token": "ruptured", "weight": 0.1980},
      {"token": "bleeder", "weight": 0.1420}
    ]
  },
  "lsr": {
    "triggered_rules": [
      "Energy Isolation",
      "Line of Fire"
    ],
    "rule_predictions": [
      {"rule": "Energy Isolation", "probability": 0.8920, "threshold": 0.30, "triggered": true},
      {"rule": "Line of Fire", "probability": 0.7410, "threshold": 0.20, "triggered": true},
      {"rule": "Hot Work", "probability": 0.0410, "threshold": 0.45, "triggered": false},
      {"rule": "Safe Mechanical Lifting", "probability": 0.0820, "threshold": 0.20, "triggered": false},
      {"rule": "Working at Height", "probability": 0.0120, "threshold": 0.25, "triggered": false},
      {"rule": "Driving", "probability": 0.0030, "threshold": 0.25, "triggered": false},
      {"rule": "Toxic Gas / Hazardous Substance", "probability": 0.0620, "threshold": 0.50, "triggered": false},
      {"rule": "Confined Space", "probability": 0.0050, "threshold": 0.50, "triggered": false},
      {"rule": "Bypassing Safety Controls", "probability": 0.1240, "threshold": 0.50, "triggered": false}
    ],
    "salient_tokens": [
      {"token": "pressurized", "weight": 0.2310},
      {"token": "fitting", "weight": 0.1850}
    ]
  },
  "model_info": {
    "sif_model": "Stage 6 Optimized Bidirectional GRU + Attention",
    "lsr_model": "Stage 7 Robust Bidirectional GRU + Attention",
    "version": "2.0.0",
    "status": "FROZEN_FOR_PRODUCTION"
  }
}
```

---

### Endpoint 2: System Health Check
- **Route:** `GET /health`
- **Response (HTTP 200 OK):**
```json
{
  "status": "healthy",
  "ai_engine": "OILPS AI-HSE-Safety-Intelligence",
  "sif_champion_loaded": true,
  "lsr_champion_loaded": true,
  "version": "2.0.0"
}
```

---

## 3. How the Future MERN Backend Should Call the AI Service

In the subsequent system integration phase:
1. **Service URL:** `http://localhost:8000/api/v1/analyze` (or internal Docker container network hostname `http://ai-service:8000/api/v1/analyze`).
2. **Node.js Axios Integration Pattern:**
```javascript
const axios = require('axios');

async function analyzeIncidentWithAI(incidentText, incidentId) {
  try {
    const response = await axios.post('http://localhost:8000/api/v1/analyze', {
      incident_text: incidentText,
      incident_id: incidentId
    });
    return response.data;
  } catch (error) {
    console.error('AI Service Error:', error.message);
    throw error;
  }
}
```

---

## 4. Error Handling & Robustness Guarantees

- **Empty / Whitespace Input:** Safely returns HTTP 200 with probability `0.0`, `is_sif = false`, and empty triggered rules without raising unhandled runtime exceptions.
- **Out-of-Vocabulary (OOV) Handling:** Automatically mapped to `<UNK>` token without tensor crash.
- **Evaluation Mode:** All models strictly run under `torch.no_grad()` with `model.eval()`, preventing training gradients or state mutation.
