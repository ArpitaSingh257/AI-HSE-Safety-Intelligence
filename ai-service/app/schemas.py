"""
schemas.py - Production Pydantic Schemas for OILPS AI Inference API Contract.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class IncidentAnalysisRequest(BaseModel):
    incident_text: str = Field(
        ...,
        description="The raw narrative text describing the workplace safety incident or precursor event.",
        example="During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting. The bleeder plug ruptured and struck the worker."
    )
    incident_id: Optional[str] = Field(
        default=None,
        description="Optional client-side incident tracking identifier.",
        example="INC-2026-0891"
    )

class SalientToken(BaseModel):
    token: str = Field(..., description="Vocabulary word token attended by the sequence attention layer.")
    weight: float = Field(..., description="Normalized attention salience weight (interpretability diagnostic).")

class SIFAnalysisResponse(BaseModel):
    probability: float = Field(..., description="Continuous calibrated probability score for Serious Injury & Fatality precursor potential.")
    threshold: float = Field(..., description="Validation-derived decision threshold (0.30) optimizing safety-critical precursor recall.")
    is_sif: bool = Field(..., description="Binary alert flag: True if probability >= threshold.")
    risk_tier: str = Field(..., description="Categorical risk tier: CRITICAL_SIF_PRECURSOR, ELEVATED_SIF_POTENTIAL, MODERATE_HAZARD, or LOW_POTENTIAL_INCIDENT.")
    salient_tokens: List[SalientToken] = Field(default_factory=list, description="Top tokens highlighting critical energy and failure mechanisms.")

class LSRRulePrediction(BaseModel):
    rule: str = Field(..., description="Official IOGP Life-Saving Rule canonical name.")
    probability: float = Field(..., description="Model probability score for this specific barrier rule.")
    threshold: float = Field(..., description="Stage 7 learned decision threshold for this specific rule.")
    triggered: bool = Field(..., description="True if rule probability >= rule threshold.")

class LSRAnalysisResponse(BaseModel):
    triggered_rules: List[str] = Field(default_factory=list, description="List of all official IOGP Life-Saving Rules activated for this incident.")
    rule_predictions: List[LSRRulePrediction] = Field(default_factory=list, description="Detailed per-rule probabilities, thresholds, and trigger statuses.")
    salient_tokens: List[SalientToken] = Field(default_factory=list, description="Top tokens salient to barrier failure and operational activity.")

class ModelInfo(BaseModel):
    sif_model: str = Field(default="Stage 6 Optimized Bidirectional GRU + Attention", description="Frozen SIF champion architecture name.")
    lsr_model: str = Field(default="Stage 7 Robust Bidirectional GRU + Attention", description="Frozen LSR champion architecture name.")
    version: str = Field(default="2.0.0", description="Production AI model engine version.")
    status: str = Field(default="FROZEN_FOR_PRODUCTION", description="Model freeze confirmation.")

class IncidentAnalysisResponse(BaseModel):
    incident_id: Optional[str] = Field(default=None, description="Client-provided incident tracking identifier.")
    incident_text: str = Field(..., description="Original incident narrative evaluated.")
    sif: SIFAnalysisResponse = Field(..., description="SIF precursor classification, probability, and risk tier.")
    lsr: LSRAnalysisResponse = Field(..., description="IOGP Life-Saving Rules multi-label activations and breakdown.")
    model_info: ModelInfo = Field(default_factory=ModelInfo, description="Metadata describing frozen champion architectures.")

class HealthCheckResponse(BaseModel):
    status: str = Field(default="healthy", description="API health status.")
    ai_engine: str = Field(default="OILPS AI-HSE-Safety-Intelligence", description="Engine name.")
    sif_champion_loaded: bool = Field(..., description="Confirmation that Stage 6 SIF weights are active.")
    lsr_champion_loaded: bool = Field(..., description="Confirmation that Stage 7 LSR weights are active.")
    version: str = Field(default="2.0.0", description="Production API version.")
