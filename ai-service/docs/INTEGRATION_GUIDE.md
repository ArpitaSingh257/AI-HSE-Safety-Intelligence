# MERN BACKEND INTEGRATION GUIDE FOR OILPS AI SERVICE

**Project**: OILPS Precursor Safety Intelligence Service  
**Version**: 2.0.0 (Stage 21 Production Freeze)  
**AI Service Base URL**: `http://127.0.0.1:8000`  
**Swagger Interactive Docs**: `http://127.0.0.1:8000/docs`  

---

## 1. System Architecture Overview

The OILPS AI Microservice is a standalone Python/FastAPI application. The MERN Backend communicates with the AI Microservice via standard HTTP REST API endpoints.

```text
React Frontend  ──(HTTP REST)──>  MERN Express Backend  ──(HTTP REST)──>  AI FastAPI Service (Port 8000)
                                                                                  │
                                                                   ┌──────────────┴──────────────┐
                                                                   │ Stage 6 Bi-GRU SIF Champion │
                                                                   │ Stage 7 Bi-GRU LSR Champion │
                                                                   │ FAISS Vector Store          │
                                                                   │ Grounded RAG Generator      │
                                                                   │ Stage 20 Grounding Guard    │
                                                                   └─────────────────────────────┘
```

> **IMPORTANT SAFETY BOUNDARY**: The AI Microservice is an **AI-Based Decision-Support System**. It provides data-driven risk insights and grounded recommendations to assist HSE officers and site supervisors. It does **NOT** act as an autonomous safety authority and does not replace site-specific operating procedures or competent-person reviews.

---

## 2. How to Start the AI Service

### Prerequisites
- Python 3.10+ environment (`oil-sif`)
- Local Ollama running `llama3.2:1b` (optional, extractive fallback active if Ollama offline)

### Command to Launch Server
```powershell
cd ai-service
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

---

## 3. Endpoints Reference

### 3.1. Health Check Endpoint
- **Method**: `GET`
- **URL**: `/health`
- **Description**: Verifies that the AI Microservice, Stage 6 SIF model, and Stage 7 LSR model are loaded and operational.

#### Response Example (`200 OK`):
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

### 3.2. Incident Safety Analysis Endpoint
- **Method**: `POST`
- **URL**: `/api/v1/analyze`
- **Headers**: `Content-Type: application/json`
- **Description**: Evaluates incident narratives, calculates SIF probability and risk tier, predicts multi-label IOGP Life-Saving Rules, executes RAG retrieval from approved PDFs, applies Stage 20 grounding validation, and returns explainable safety intelligence.

#### Request Example:
```json
{
  "incident_text": "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator was exposed to a pressure release after a bleeder plug ruptured.",
  "incident_id": "INC-2026-0891"
}
```

#### Response Example (`200 OK`):
```json
{
  "incident_id": "INC-2026-0891",
  "incident_text": "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator was exposed to a pressure release after a bleeder plug ruptured.",
  "sif": {
    "probability": 0.88,
    "threshold": 0.30,
    "is_sif": true,
    "risk_tier": "CRITICAL_SIF_PRECURSOR",
    "salient_tokens": [
      { "token": "pressurized", "weight": 0.185 },
      { "token": "ruptured", "weight": 0.162 }
    ]
  },
  "lsr": {
    "triggered_rules": ["Energy Isolation"],
    "rule_predictions": [
      {
        "rule": "Energy Isolation",
        "probability": 0.824,
        "threshold": 0.50,
        "triggered": true
      }
    ],
    "salient_tokens": [
      { "token": "bleeder", "weight": 0.194 }
    ]
  },
  "recommendations": {
    "status": "GROUNDED",
    "grounded": true,
    "priority": "CRITICAL",
    "summary": "Initiate immediate Stop Work Authority and depressurize pressure line...",
    "immediate_actions": [
      "Initiate immediate Stop Work Authority (SWA).",
      "Isolate and depressurize all connected high-pressure energy sources."
    ],
    "verification_actions": [
      "Verify isolation and zero energy state before work begins on pressure systems.",
      "Test for trapped pressure before loosening fittings or bleeder plugs."
    ],
    "control_verification": [
      "Verify isolation and zero energy state before work begins on pressure systems."
    ],
    "escalation_actions": [
      "Notify Site Superintendent, Safety Officer, and Operations Manager."
    ],
    "escalation": [
      "Notify Site Superintendent, Safety Officer, and Operations Manager."
    ],
    "preventive_actions": [
      "Inspect pressure fittings and conduct pre-hydrotest barrier audits."
    ],
    "sources": [
      {
        "document": "IOGP Life-Saving Rules.pdf",
        "page": 12,
        "section": "Energy Isolation",
        "chunk_id": "iogp_p12_c01",
        "similarity": 0.845,
        "snippet": "Verify isolation and zero energy state before work begins on pressure systems..."
      }
    ],
    "disclaimer": "Recommendations are generated as decision-support guidance from retrieved approved safety documents."
  },
  "explainability": {
    "risk_level_display": "🔴 CRITICAL",
    "sif_interpretation": "Model probability: 88.00%. The incident narrative contains operational characteristics associated with a potential Serious Injury or Fatality (SIF) precursor event.",
    "why_flagged": [
      "Key energy & hazard indicators detected: pressurized, ruptured, bleeder.",
      "Incident activity activated 1 IOGP Life-Saving Rule(s): Energy Isolation."
    ],
    "lsr_explanations": [
      {
        "rule": "Energy Isolation",
        "model_probability": "82.4%",
        "why_triggered": "The incident narrative describes operational conditions and barrier requirements associated with Energy Isolation."
      }
    ],
    "grounding_banner": "✓ GROUNDED — Recommendations are directly supported by retrieved safety-resource evidence.",
    "formatted_text": "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n..."
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

## 4. Error Response Formats & Status Codes

| Status Code | Condition | JSON Response Body |
|---|---|---|
| `422 Unprocessable Entity` | Empty/Null/Short text (< 10 chars) | `{"detail": "Incident narrative text is too short. Please provide a detailed description."}` |
| `422 Unprocessable Entity` | Malformed JSON request body | `{"detail": [{"loc": ["body"], "msg": "value is not a valid dict"}]}` |
| `500 Internal Server Error` | Unexpected processing failure | `{"detail": "Internal processing failure: <error message>"}` |

---

## 5. Performance & Timeout Guidance for MERN Developers

- **Average API Response Time**:
  - Warm LLM Cache (`llama3.2:1b` in RAM): **~2.8s – 4.5s**
  - First-time cold start (loading Ollama into RAM): **~15s – 25s**
  - Extractive Fallback (Ollama offline/timeout): **~0.04s**
- **Recommended MERN Axios Timeout**: Set `timeout: 30000` (30 seconds) on the Node.js Express backend HTTP client call to Python service.
