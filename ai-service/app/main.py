"""
main.py - Production FastAPI Entrypoint for OILPS AI-HSE-Safety-Intelligence Service.
"""

import sys
from pathlib import Path
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.schemas import HealthCheckResponse
from app.api.v1.endpoints.analyze import router as analyze_router, get_pipeline
from app.api.v1.endpoints.patterns import router as patterns_router
from app.api.v1.endpoints.barrier_patterns import router as barrier_patterns_router
from app.api.v1.endpoints.similar_reports import router as similar_reports_router
from app.api.v1.endpoints.site_risk import router as site_risk_router
from app.api.v1.endpoints.activity_risk import router as activity_risk_router
from app.api.v1.endpoints.lsr_trends import router as lsr_trends_router
from app.api.v1.endpoints.early_warnings import router as early_warnings_router
from app.api.v1.endpoints.priorities import router as priorities_router
from app.api.v1.endpoints.risk_matrix import router as risk_matrix_router
from app.api.v1.endpoints.bow_ties import router as bow_ties_router
from app.api.v1.endpoints.feedback import router as feedback_router
from app.api.v1.endpoints.triage import router as triage_router
from app.api.v1.endpoints.text_normalize import router as text_normalize_router
from app.api.v1.endpoints.intelligence import router as intelligence_router
from app.api.v1.endpoints.graph import router as graph_router
from app.api.v1.endpoints.agentic_investigation import router as agentic_router

app = FastAPI(
    title="OILPS AI Precursor Safety Intelligence Service",
    version="2.0.0",
    description="High-performance AI/NLP microservice providing real-time SIF precursor risk classification, IOGP Life-Saving Rules mapping, and attention interpretability diagnostics.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for MERN frontend & backend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 routes
app.include_router(analyze_router, prefix="/api/v1", tags=["Inference"])
app.include_router(intelligence_router, prefix="/api/v1/intelligence", tags=["End-to-End Intelligence API"])
app.include_router(graph_router, prefix="/api/v1/graph", tags=["Graph RAG Lineage Topology"])
app.include_router(agentic_router, prefix="/api/v1/agentic", tags=["Agentic Safety Intelligence Layer"])
app.include_router(patterns_router, prefix="/api/v1/patterns", tags=["Patterns"])
app.include_router(barrier_patterns_router, prefix="/api/v1/barrier-patterns", tags=["Barrier Patterns"])
app.include_router(similar_reports_router, prefix="/api/v1/similar-reports", tags=["Similar Reports"])
app.include_router(site_risk_router, prefix="/api/v1/site-risk", tags=["Site Risk"])
app.include_router(activity_risk_router, prefix="/api/v1/activity-risk", tags=["Activity Risk"])
app.include_router(lsr_trends_router, prefix="/api/v1/lsr-trends", tags=["LSR Trends"])
app.include_router(early_warnings_router, prefix="/api/v1/early-warnings", tags=["Early Warnings"])
app.include_router(priorities_router, prefix="/api/v1/priorities", tags=["Priorities"])
app.include_router(risk_matrix_router, prefix="/api/v1/risk-matrix", tags=["Risk Matrix"])
app.include_router(bow_ties_router, prefix="/api/v1/bow-ties", tags=["Bow-Tie Mapping"])
app.include_router(feedback_router, prefix="/api/v1/feedback", tags=["Human Analyst Feedback"])
app.include_router(triage_router, prefix="/api/v1/triage", tags=["Confidence-Calibrated Triage"])
app.include_router(text_normalize_router, prefix="/api/v1/text", tags=["Multilingual Text Normalization"])

@app.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health & Model Readiness Check",
    tags=["System"]
)
async def health_check():
    pipeline = get_pipeline()
    sif_ok = pipeline.sif_predictor.has_trained_weights
    lsr_ok = pipeline.lsr_predictor.has_trained_weights
    
    return HealthCheckResponse(
        status="healthy",
        ai_engine="OILPS AI-HSE-Safety-Intelligence",
        sif_champion_loaded=sif_ok,
        lsr_champion_loaded=lsr_ok,
        version="2.0.0"
    )

@app.get("/", tags=["System"])
async def root():
    return {
        "service": "OILPS AI Precursor Safety Intelligence Engine",
        "status": "online",
        "docs": "/docs",
        "inference_endpoint": "POST /api/v1/analyze",
        "models": {
            "sif": "Stage 6 Optimized Bidirectional GRU + Attention (Threshold = 0.30)",
            "lsr": "Stage 7 Robust Bidirectional GRU + Attention (9 IOGP Rules)"
        }
    }
