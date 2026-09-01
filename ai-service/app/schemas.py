"""
schemas.py - Production Pydantic Schemas for OILPS AI Inference API Contract.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class IncidentAnalysisRequest(BaseModel):
    incident_text: str = Field(
        ...,
        description="The raw narrative text describing the workplace safety incident or precursor event.",
        json_schema_extra={"example": "During hydrostatic testing of the 6-inch discharge line at 4,500 psi, an operator attempted to tighten a leaking fitting. The bleeder plug ruptured and struck the worker."}
    )
    incident_id: Optional[str] = Field(
        default=None,
        description="Optional client-side incident tracking identifier.",
        json_schema_extra={"example": "INC-2026-0891"}
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

class SourceCitationSchema(BaseModel):
    document: str = Field(..., description="Source reference document filename")
    page: int = Field(..., description="Page number of retrieved reference")
    section: str = Field(default="General", description="Section header")
    chunk_id: str = Field(..., description="Unique ID of source passage")
    similarity: float = Field(default=0.0, description="Cosine similarity score")
    snippet: str = Field(default="", description="Relevant supporting text passage snippet")

class SafetyRecommendationsResponse(BaseModel):
    status: str = Field(default="GROUNDED", description="RAG recommendation status: GROUNDED, INSUFFICIENT_SOURCE_SUPPORT, or FALLBACK")
    grounded: bool = Field(default=True, description="Flag indicating if recommendation is grounded in retrieved PDF sources")
    priority: str = Field(..., description="Action priority level: CRITICAL, HIGH, MODERATE, or LOW.")
    summary: str = Field(..., description="High-level narrative overview of the required safety response.")
    immediate_actions: List[str] = Field(default_factory=list, description="Immediate stop-work, isolation, or evacuation actions.")
    verification_actions: List[str] = Field(default_factory=list, description="Specific safety barrier and permit checks to verify before proceeding.")
    control_verification: List[str] = Field(default_factory=list, description="Alias for verification_actions for backward compatibility.")
    escalation_actions: List[str] = Field(default_factory=list, description="Escalation protocol for HSE officers and site leadership.")
    escalation: List[str] = Field(default_factory=list, description="Alias for escalation_actions for backward compatibility.")
    preventive_actions: List[str] = Field(default_factory=list, description="Longer-term preventive actions and engineering controls.")
    sources: List[SourceCitationSchema] = Field(default_factory=list, description="Source provenance citations from approved safety PDFs.")
    rule_specific_guidance: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Detailed per-rule guidance for all triggered Life-Saving Rules.")
    disclaimer: str = Field(
        default="Recommendations are generated as decision-support guidance from retrieved approved safety documents. They do not replace site-specific operating procedures or competent HSE professional review.",
        description="Standard safety decision-support disclaimer."
    )

class ModelInfo(BaseModel):
    sif_model: str = Field(default="Stage 6 Optimized Bidirectional GRU + Attention", description="Frozen SIF champion architecture name.")
    lsr_model: str = Field(default="Stage 7 Robust Bidirectional GRU + Attention", description="Frozen LSR champion architecture name.")
    version: str = Field(default="2.0.0", description="Production AI model engine version.")
    status: str = Field(default="FROZEN_FOR_PRODUCTION", description="Model freeze confirmation.")

class LSRExplanationSchema(BaseModel):
    rule: str = Field(..., description="Official IOGP Life-Saving Rule canonical name.")
    model_probability: str = Field(..., description="Model probability percentage, e.g. '82.4%'")
    why_triggered: str = Field(..., description="Non-technical explanation of rule activation.")

class ExplainableSafetyOutputSchema(BaseModel):
    risk_level_display: str = Field(..., description="Categorical risk indicator badge: 🔴 CRITICAL, 🟠 HIGH, 🟡 MODERATE, or 🟢 LOW.")
    sif_interpretation: str = Field(..., description="Clear explanation of SIF precursor potential.")
    why_flagged: List[str] = Field(default_factory=list, description="Bullet points explaining why the incident was flagged.")
    lsr_explanations: List[LSRExplanationSchema] = Field(default_factory=list, description="User-friendly explanation of each triggered Life-Saving Rule.")
    grounding_banner: str = Field(..., description="Status badge indicating if recommendations are grounded in reference PDFs.")
    formatted_text: str = Field(..., description="Clean ASCII/terminal formatted user-facing text layout.")

class IncidentAnalysisResponse(BaseModel):
    incident_id: Optional[str] = Field(default=None, description="Client-provided incident tracking identifier.")
    incident_text: str = Field(..., description="Original incident narrative evaluated.")
    sif: SIFAnalysisResponse = Field(..., description="SIF precursor classification, probability, and risk tier.")
    lsr: LSRAnalysisResponse = Field(..., description="IOGP Life-Saving Rules multi-label activations and breakdown.")
    recommendations: Optional[SafetyRecommendationsResponse] = Field(default=None, description="Actionable safety recommendations and control verifications.")
    explainability: Optional[ExplainableSafetyOutputSchema] = Field(default=None, description="Stage 19 non-technical explainable safety intelligence response.")
    recurring_patterns: Optional[List["RecurringPatternSchema"]] = Field(default=None, description="Matching recurring precursor patterns if detected.")
    model_info: ModelInfo = Field(default_factory=ModelInfo, description="Metadata describing frozen champion architectures.")


class RecurringPatternSchema(BaseModel):
    pattern_id: str = Field(..., description="Deterministic pattern ID.")
    pattern_code: Optional[str] = Field(default=None, description="Short pattern code (e.g. P001).")
    pattern_name: str = Field(..., description="Human-readable pattern title.")
    summary: str = Field(..., description="Deterministic text summary of pattern.")
    pattern_strength: str = Field(..., description="Pattern strength: HIGH, MEDIUM, or LOW.")
    incident_count: int = Field(..., description="Total historical incident support count.")
    sif_incident_count: int = Field(..., description="Number of SIF-potential incidents in pattern.")
    sif_density: float = Field(..., description="Ratio of SIF incidents (0.0 to 1.0).")
    dominant_activity: str = Field(..., description="Primary activity associated with pattern.")
    dominant_lsr: str = Field(..., description="Primary Life-Saving Rule associated with pattern.")
    dominant_hazard: str = Field(..., description="Primary high-energy hazard associated with pattern.")
    dominant_barrier_failure: str = Field(..., description="Primary barrier failure associated with pattern.")
    locations: List[str] = Field(..., description="Locations where pattern has been observed.")
    first_observed: str = Field(..., description="Date of earliest observed incident in pattern.")
    last_observed: str = Field(..., description="Date of most recent observed incident in pattern.")
    incident_ids: List[str] = Field(..., description="List of contributing incident IDs.")
    evidence_quotes: List[str] = Field(..., description="Representative quotes from historical reports.")


class PatternListResponse(BaseModel):
    total_patterns: int = Field(..., description="Total recurring precursor patterns discovered.")
    min_support_threshold: int = Field(..., description="Configured minimum support threshold.")
    patterns: List[RecurringPatternSchema] = Field(..., description="List of detected recurring patterns.")


class BarrierPatternSchema(BaseModel):
    barrier_pattern_id: str = Field(..., description="Deterministic barrier pattern ID.")
    barrier_code_prefix: Optional[str] = Field(default=None, description="Short code (e.g. B001).")
    barrier_code: str = Field(..., description="Canonical barrier failure code.")
    barrier_name: str = Field(..., description="Human-readable barrier failure name.")
    incident_count: int = Field(..., description="Total unique incident occurrences.")
    sif_incident_count: int = Field(..., description="Number of SIF-potential incidents.")
    sif_density: float = Field(..., description="Ratio of SIF incidents (0.0 to 1.0).")
    pattern_strength: str = Field(..., description="Strength indicator: HIGH, MEDIUM, or LOW.")
    dominant_activity: str = Field(..., description="Primary activity associated with barrier failure.")
    dominant_lsr: str = Field(..., description="Primary Life-Saving Rule associated with barrier failure.")
    dominant_hazard: str = Field(..., description="Primary hazard associated with barrier failure.")
    locations: List[str] = Field(..., description="Locations where barrier failure was observed.")
    potential_consequences: List[str] = Field(..., description="Key worst-case consequences.")
    stage23_pattern_ids: List[str] = Field(..., description="Linked Stage 23 recurring pattern IDs.")
    incident_ids: List[str] = Field(..., description="List of contributing incident IDs.")
    first_observed: str = Field(..., description="Date of earliest observed failure.")
    last_observed: str = Field(..., description="Date of most recent observed failure.")
    supporting_evidence: List[str] = Field(..., description="Representative narrative quotes.")


class BarrierPatternListResponse(BaseModel):
    total_barrier_patterns: int = Field(..., description="Total recurring barrier failure patterns discovered.")
    min_support_threshold: int = Field(..., description="Configured minimum support threshold.")
    barrier_patterns: List[BarrierPatternSchema] = Field(..., description="List of detected barrier patterns.")


class SimilarReportItemSchema(BaseModel):
    report_id: str = Field(..., description="Historical report ID.")
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0).")
    similarity_percentage: int = Field(..., description="Similarity percentage integer.")
    report_date: str = Field(..., description="Reported date.")
    location: str = Field(..., description="Site or location.")
    activity: str = Field(..., description="Activity during incident.")
    hazard: str = Field(..., description="Primary hazard involved.")
    barrier_failure: str = Field(..., description="Barrier failure identified.")
    primary_life_saving_rule: str = Field(..., description="Associated IOGP Life-Saving Rule.")
    is_sif: bool = Field(..., description="SIF precursor indicator.")
    narrative_excerpt: str = Field(..., description="Concise text excerpt.")
    explanation: str = Field(..., description="Deterministic similarity explanation.")
    stage23_pattern_id: Optional[str] = Field(default=None, description="Linked Stage 23 pattern ID if applicable.")
    stage24_barrier_id: Optional[str] = Field(default=None, description="Linked Stage 24 barrier pattern ID if applicable.")


class SimilarReportsResponse(BaseModel):
    query_report_id: Optional[str] = Field(default=None, description="Query report ID if provided.")
    total_matches: int = Field(..., description="Total similar historical reports returned.")
    top_k: int = Field(..., description="Configured Top-K parameter.")
    min_similarity_threshold: float = Field(..., description="Minimum similarity threshold used.")
    similar_reports: List[SimilarReportItemSchema] = Field(..., description="Ranked similar historical reports.")


class SimilarReportSearchRequest(BaseModel):
    query_text: Optional[str] = Field(default=None, description="Free text narrative to search.")
    top_k: int = Field(default=5, ge=1, le=20, description="Top-K count.")
    min_similarity: float = Field(default=0.40, ge=0.0, le=1.0, description="Minimum similarity threshold.")


class SiteActivitySummarySchema(BaseModel):
    name: str = Field(..., description="Activity name.")
    report_count: int = Field(..., description="Report count.")
    sif_count: int = Field(..., description="SIF count.")
    sif_density: float = Field(..., description="SIF rate.")


class SiteHazardSummarySchema(BaseModel):
    name: str = Field(..., description="Hazard name.")
    count: int = Field(..., description="Occurrence count.")


class SiteBarrierSummarySchema(BaseModel):
    name: str = Field(..., description="Barrier failure name.")
    count: int = Field(..., description="Occurrence count.")
    sif_count: int = Field(..., description="SIF count.")
    sif_density: float = Field(..., description="SIF rate.")


class SiteLsrSummarySchema(BaseModel):
    name: str = Field(..., description="LSR rule name.")
    count: int = Field(..., description="Occurrence count.")


class SiteRiskProfileSchema(BaseModel):
    site_id: str = Field(..., description="Canonical site ID.")
    site_name: str = Field(..., description="Canonical site name.")
    total_reports: int = Field(..., description="Total unique report count.")
    sif_reports: int = Field(..., description="SIF report count.")
    non_sif_reports: int = Field(..., description="Non-SIF report count.")
    sif_density: float = Field(..., description="SIF density ratio (0.0 to 1.0).")
    recurring_pattern_count: int = Field(..., description="Stage 23 pattern count.")
    barrier_failure_pattern_count: int = Field(..., description="Stage 24 barrier pattern count.")
    risk_index: float = Field(..., description="Deterministic Site Risk Index R_s (0.0 to 1.0).")
    risk_level: str = Field(..., description="Risk level: CRITICAL, HIGH, MEDIUM, LOW, or INSUFFICIENT_DATA.")
    sif_component: float = Field(..., description="SIF component score.")
    pattern_component: float = Field(..., description="Pattern component score.")
    barrier_component: float = Field(..., description="Barrier component score.")
    top_activities: List[SiteActivitySummarySchema] = Field(..., description="Top activities.")
    top_hazards: List[SiteHazardSummarySchema] = Field(..., description="Top hazards.")
    top_barrier_failures: List[SiteBarrierSummarySchema] = Field(..., description="Top barrier failures.")
    top_life_saving_rules: List[SiteLsrSummarySchema] = Field(..., description="Top Life-Saving Rules.")
    first_observed: str = Field(..., description="Earliest report date.")
    last_observed: str = Field(..., description="Most recent report date.")
    report_ids: List[str] = Field(..., description="Contributing report IDs.")
    pattern_ids: List[str] = Field(..., description="Linked Stage 23 pattern IDs.")
    barrier_pattern_ids: List[str] = Field(..., description="Linked Stage 24 barrier pattern IDs.")


class SiteRiskListResponse(BaseModel):
    total_sites: int = Field(..., description="Total sites analyzed.")
    min_site_reports_threshold: int = Field(..., description="Minimum reports required for classification.")
    site_profiles: List[SiteRiskProfileSchema] = Field(..., description="Ranked site risk profiles.")


class ActivitySiteSummarySchema(BaseModel):
    site_name: str = Field(..., description="Site or location name.")
    count: int = Field(..., description="Occurrence count.")


class ActivityRiskProfileSchema(BaseModel):
    activity_id: str = Field(..., description="Canonical activity ID.")
    activity_name: str = Field(..., description="Canonical activity name.")
    total_reports: int = Field(..., description="Total unique report count.")
    sif_reports: int = Field(..., description="SIF report count.")
    non_sif_reports: int = Field(..., description="Non-SIF report count.")
    sif_density: float = Field(..., description="SIF density ratio (0.0 to 1.0).")
    recurring_pattern_count: int = Field(..., description="Stage 23 pattern count.")
    barrier_failure_pattern_count: int = Field(..., description="Stage 24 barrier pattern count.")
    risk_index: float = Field(..., description="Deterministic Activity Risk Index R_a (0.0 to 1.0).")
    risk_level: str = Field(..., description="Risk level: CRITICAL, HIGH, MEDIUM, LOW, or INSUFFICIENT_DATA.")
    sif_component: float = Field(..., description="SIF component score.")
    pattern_component: float = Field(..., description="Pattern component score.")
    barrier_component: float = Field(..., description="Barrier component score.")
    top_hazards: List[SiteHazardSummarySchema] = Field(..., description="Top hazards.")
    top_barrier_failures: List[SiteBarrierSummarySchema] = Field(..., description="Top barrier failures.")
    top_life_saving_rules: List[SiteLsrSummarySchema] = Field(..., description="Top Life-Saving Rules.")
    associated_sites: List[ActivitySiteSummarySchema] = Field(..., description="Associated operational sites.")
    first_observed: str = Field(..., description="Earliest report date.")
    last_observed: str = Field(..., description="Most recent report date.")
    report_ids: List[str] = Field(..., description="Contributing report IDs.")
    pattern_ids: List[str] = Field(..., description="Linked Stage 23 pattern IDs.")
    barrier_pattern_ids: List[str] = Field(..., description="Linked Stage 24 barrier pattern IDs.")


class ActivityRiskListResponse(BaseModel):
    total_activities: int = Field(..., description="Total activities analyzed.")
    min_activity_reports_threshold: int = Field(..., description="Minimum reports required for classification.")
    activity_profiles: List[ActivityRiskProfileSchema] = Field(..., description="Ranked activity risk profiles.")


class LsrTimeSeriesItemSchema(BaseModel):
    period: str = Field(..., description="Time period bucket (YYYY-MM).")
    report_count: int = Field(..., description="Report count in period.")
    sif_count: int = Field(..., description="SIF count in period.")
    sif_density: float = Field(..., description="SIF density ratio in period.")


class LsrActivitySummarySchema(BaseModel):
    activity_name: str = Field(..., description="Activity name.")
    count: int = Field(..., description="Occurrence count.")


class LsrBarrierSummarySchema(BaseModel):
    name: str = Field(..., description="Barrier failure name.")
    count: int = Field(..., description="Occurrence count.")


class LsrTrendProfileSchema(BaseModel):
    lsr_rule: str = Field(..., description="Canonical Life-Saving Rule name.")
    total_reports: int = Field(..., description="Total unique report count.")
    sif_reports: int = Field(..., description="SIF report count.")
    sif_density: float = Field(..., description="Overall SIF density ratio (0.0 to 1.0).")
    trend: str = Field(..., description="Trend state: INCREASING, STABLE, DECREASING, or INSUFFICIENT_DATA.")
    trend_delta: float = Field(..., description="Recent vs earlier SIF density delta.")
    time_series: List[LsrTimeSeriesItemSchema] = Field(..., description="Monthly time series breakdown.")
    top_sites: List[ActivitySiteSummarySchema] = Field(..., description="Top associated sites.")
    top_activities: List[LsrActivitySummarySchema] = Field(..., description="Top associated activities.")
    top_barrier_failures: List[LsrBarrierSummarySchema] = Field(..., description="Top associated barrier failures.")
    recurring_pattern_ids: List[str] = Field(..., description="Linked Stage 23 pattern IDs.")
    barrier_pattern_ids: List[str] = Field(..., description="Linked Stage 24 barrier pattern IDs.")
    first_observed: str = Field(..., description="Earliest report date.")
    last_observed: str = Field(..., description="Most recent report date.")
    report_ids: List[str] = Field(..., description="Contributing report IDs.")


class LsrTrendListResponse(BaseModel):
    total_lsr_rules: int = Field(..., description="Total official Life-Saving Rules analyzed.")
    min_lsr_reports_threshold: int = Field(..., description="Minimum reports required for trend calculation.")
    unknown_lsr_records: int = Field(default=0, description="Count of historical records with missing or unclassified LSR labels.")
    unknown_lsr_rate: float = Field(default=0.0, description="Ratio of records with missing LSR labels.")
    lsr_profiles: List[LsrTrendProfileSchema] = Field(..., description="List of official LSR trend profiles.")


class EarlyWarningProfileSchema(BaseModel):
    warning_id: str = Field(..., description="Unique early warning ID.")
    signal_type: str = Field(..., description="Signal type: BARRIER_FAILURE, RECURRING_PATTERN, SIF_DENSITY, SITE_RISK, ACTIVITY_RISK, LSR_TREND.")
    signal_name: str = Field(..., description="Signal or pattern name.")
    warning_level: str = Field(..., description="Warning level: HIGH_PRIORITY, EARLY_WARNING, WATCH, NORMAL, INSUFFICIENT_DATA.")
    period: str = Field(..., description="Most recent time period (YYYY-MM).")
    baseline_value: float = Field(..., description="Baseline period average metric.")
    recent_value: float = Field(..., description="Recent period average metric.")
    delta: float = Field(..., description="Recent vs baseline metric delta.")
    consecutive_increasing_periods: int = Field(..., description="Count of consecutive increasing periods.")
    affected_sites: List[ActivitySiteSummarySchema] = Field(..., description="Top affected sites.")
    affected_activities: List[LsrActivitySummarySchema] = Field(..., description="Top affected activities.")
    pattern_ids: List[str] = Field(..., description="Linked Stage 23 pattern IDs.")
    barrier_pattern_ids: List[str] = Field(..., description="Linked Stage 24 barrier pattern IDs.")
    supporting_incident_ids: List[str] = Field(..., description="Supporting historical report IDs.")
    reason: str = Field(..., description="Deterministic explanation string.")
    first_observed: str = Field(..., description="Earliest report date.")
    last_observed: str = Field(..., description="Most recent report date.")
    time_series: List[LsrTimeSeriesItemSchema] = Field(..., description="Time series breakdown.")


class EarlyWarningListResponse(BaseModel):
    total_warnings: int = Field(..., description="Total early warning signals evaluated.")
    high_priority_count: int = Field(..., description="Count of HIGH_PRIORITY warnings.")
    early_warning_count: int = Field(..., description="Count of EARLY_WARNING signals.")
    watch_count: int = Field(..., description="Count of WATCH signals.")
    warnings: List[EarlyWarningProfileSchema] = Field(..., description="List of early warning profiles.")


class PriorityComponentScoresSchema(BaseModel):
    sif_impact: float = Field(..., description="Normalized SIF precursor impact score (0.0 - 1.0).")
    recurrence: float = Field(..., description="Normalized recurrence frequency score (0.0 - 1.0).")
    barrier_impact: float = Field(..., description="Normalized barrier failure severity score (0.0 - 1.0).")
    site_activity: float = Field(..., description="Normalized site/activity concentration index (0.0 - 1.0).")
    early_warning: float = Field(..., description="Normalized early warning signal contribution (0.0 - 1.0).")


class PriorityProfileSchema(BaseModel):
    priority_id: str = Field(..., description="Unique priority ID.")
    entity_type: str = Field(..., description="Entity type: BARRIER_FAILURE, RECURRING_PATTERN, SITE, ACTIVITY.")
    entity_id: str = Field(..., description="Entity identifier.")
    entity_name: str = Field(..., description="Entity display name.")
    priority_score: float = Field(..., description="Unified priority score (0.00 - 1.00).")
    priority_level: str = Field(..., description="Priority classification level: CRITICAL, HIGH, MEDIUM, LOW, INSUFFICIENT_DATA.")
    components: PriorityComponentScoresSchema = Field(..., description="Normalized component scores breakdown.")
    supporting_report_ids: List[str] = Field(..., description="Supporting historical report IDs.")
    pattern_ids: List[str] = Field(..., description="Linked Stage 23 pattern IDs.")
    barrier_pattern_ids: List[str] = Field(..., description="Linked Stage 24 barrier pattern IDs.")
    site_ids: List[str] = Field(..., description="Linked site IDs.")
    activity_ids: List[str] = Field(..., description="Linked activity IDs.")
    warning_ids: List[str] = Field(..., description="Linked Stage 29 early warning IDs.")
    first_observed: str = Field(..., description="Earliest report date.")
    last_observed: str = Field(..., description="Most recent report date.")
    reason: str = Field(..., description="Deterministic explanation string.")


class PriorityListResponse(BaseModel):
    total_priorities: int = Field(..., description="Total HSE priorities evaluated.")
    critical_count: int = Field(..., description="Count of CRITICAL priorities.")
    high_count: int = Field(..., description="Count of HIGH priorities.")
    medium_count: int = Field(..., description="Count of MEDIUM priorities.")
    priorities: List[PriorityProfileSchema] = Field(..., description="Ranked list of priority profiles.")


class RiskMatrixItemSchema(BaseModel):
    matrix_item_id: str = Field(..., description="Unique matrix item ID.")
    entity_type: str = Field(..., description="Entity type: BARRIER_FAILURE, RECURRING_PATTERN, SITE, ACTIVITY.")
    entity_id: str = Field(..., description="Entity identifier.")
    entity_name: str = Field(..., description="Entity display name.")
    severity_score: float = Field(..., description="Normalized severity / SIF potential score (0.00 - 1.00).")
    recurrence_score: float = Field(..., description="Normalized recurrence frequency score (0.00 - 1.00).")
    severity_level: str = Field(..., description="Severity level: HIGH, LOW, INSUFFICIENT_DATA.")
    recurrence_level: str = Field(..., description="Recurrence level: HIGH, LOW, INSUFFICIENT_DATA.")
    quadrant: str = Field(..., description="Matrix quadrant: HIGH_SEVERITY_HIGH_RECURRENCE, HIGH_SEVERITY_LOW_RECURRENCE, LOW_SEVERITY_HIGH_RECURRENCE, LOW_SEVERITY_LOW_RECURRENCE, INSUFFICIENT_DATA.")
    classification: str = Field(..., description="Interpretation classification: CRITICAL_PRIORITY, HIGH_POTENTIAL_RARE, FREQUENT_LOWER_POTENTIAL, LOW_PRIORITY_MONITOR, INSUFFICIENT_DATA.")
    supporting_report_ids: List[str] = Field(..., description="Supporting historical report IDs.")
    pattern_ids: List[str] = Field(..., description="Linked Stage 23 pattern IDs.")
    barrier_pattern_ids: List[str] = Field(..., description="Linked Stage 24 barrier pattern IDs.")
    site_ids: List[str] = Field(..., description="Linked site IDs.")
    activity_ids: List[str] = Field(..., description="Linked activity IDs.")
    first_observed: str = Field(..., description="Earliest report date.")
    last_observed: str = Field(..., description="Most recent report date.")
    reason: str = Field(..., description="Deterministic explanation string.")


class RiskMatrixListResponse(BaseModel):
    total_items: int = Field(..., description="Total 2D risk matrix items evaluated.")
    critical_priority_count: int = Field(..., description="Count of CRITICAL_PRIORITY (High/High) items.")
    high_potential_rare_count: int = Field(..., description="Count of HIGH_POTENTIAL_RARE (High/Low) items.")
    frequent_lower_potential_count: int = Field(..., description="Count of FREQUENT_LOWER_POTENTIAL (Low/High) items.")
    low_priority_monitor_count: int = Field(..., description="Count of LOW_PRIORITY_MONITOR (Low/Low) items.")
    matrix_items: List[RiskMatrixItemSchema] = Field(..., description="List of 2D matrix items.")


class BowTieNodeSchema(BaseModel):
    id: str = Field(..., description="Node identifier.")
    type: str = Field(..., description="Node type: HAZARD, THREAT, FAILED_BARRIER, PREVENTIVE_BARRIER, MITIGATING_BARRIER, TOP_EVENT, CONSEQUENCE.")
    label: str = Field(..., description="Node label text.")
    provenance: str = Field(..., description="Provenance: OBSERVED, INFERRED, UNKNOWN.")
    canonical_barrier: Optional[str] = Field(default=None, description="Optional canonical barrier code.")
    barrier_role: Optional[str] = Field(default=None, description="Optional barrier role: PREVENTIVE, MITIGATING.")
    raw_evidence: Optional[str] = Field(default=None, description="Optional raw evidence text excerpt.")


class BowTieEdgeSchema(BaseModel):
    source: str = Field(..., description="Source node ID.")
    target: str = Field(..., description="Target node ID.")
    provenance: str = Field(..., description="Relationship provenance: OBSERVED, INFERRED, UNKNOWN.")


class BowTieProfileSchema(BaseModel):
    bow_tie_id: str = Field(..., description="Unique Bow-Tie ID.")
    report_id: str = Field(..., description="Associated report ID.")
    hazards: List[str] = Field(..., description="Identified hazards.")
    threats: List[str] = Field(..., description="Identified threats.")
    failed_barriers: List[str] = Field(..., description="Identified failed barriers.")
    preventive_barriers: List[str] = Field(..., description="Preventive barriers.")
    mitigating_barriers: List[str] = Field(..., description="Mitigating barriers.")
    top_events: List[str] = Field(..., description="Top event / loss of control labels.")
    consequences: List[str] = Field(..., description="Potential consequences.")
    nodes: List[BowTieNodeSchema] = Field(..., description="Bow-Tie graph nodes.")
    edges: List[BowTieEdgeSchema] = Field(..., description="Bow-Tie graph edges.")
    sif_information: Dict[str, Any] = Field(..., description="Stage 6 SIF context.")
    lsr_information: Dict[str, Any] = Field(..., description="Stage 7 LSR context.")
    pattern_ids: List[str] = Field(..., description="Linked Stage 23 precursor pattern IDs.")
    barrier_pattern_ids: List[str] = Field(..., description="Linked Stage 24 barrier pattern IDs.")
    evidence: Dict[str, Any] = Field(..., description="Supporting evidence excerpts.")
    provenance: str = Field(..., description="Overall provenance classification.")
    mapping_confidence: str = Field(..., description="Deterministic mapping confidence: HIGH, MEDIUM, LOW.")


class FeedbackSubmissionSchema(BaseModel):
    report_id: str = Field(..., description="Target report ID.")
    field_name: str = Field(..., description="AI prediction field being reviewed.")
    ai_value: Any = Field(..., description="Original AI prediction value.")
    human_value: Any = Field(..., description="Human correction or accepted value.")
    action: str = Field(..., description="Review action: ACCEPT, CORRECT, REJECT, NEEDS_REVIEW.")
    comment: Optional[str] = Field(default="", description="Optional analyst commentary.")
    reviewer_id: Optional[str] = Field(default="HSE_ANALYST_01", description="Reviewer identifier.")


class FeedbackRecordSchema(BaseModel):
    feedback_id: str = Field(..., description="Unique feedback record ID.")
    report_id: str = Field(..., description="Target report ID.")
    field_name: str = Field(..., description="AI prediction field.")
    ai_value: Any = Field(..., description="Original AI prediction value.")
    human_value: Any = Field(..., description="Human correction value.")
    action: str = Field(..., description="Review action: ACCEPT, CORRECT, REJECT, NEEDS_REVIEW.")
    comment: str = Field(..., description="Analyst commentary.")
    reviewer_id: str = Field(..., description="Reviewer identifier.")
    review_timestamp: str = Field(..., description="Review timestamp ISO 8601.")
    model_version: str = Field(..., description="Target model version.")
    pipeline_version: str = Field(..., description="System pipeline version.")
    schema_version: str = Field(..., description="Schema version.")
    status: str = Field(..., description="Lifecycle status: SUBMITTED, REVIEWED, ACCEPTED_FOR_EVALUATION.")
    revision: int = Field(..., description="Revision version number.")
    created_at: str = Field(..., description="Created timestamp.")
    updated_at: str = Field(..., description="Updated timestamp.")


class FeedbackStatsSchema(BaseModel):
    total_feedback: int = Field(..., description="Total feedback records evaluated.")
    accepted_count: int = Field(..., description="Count of ACCEPT actions.")
    corrected_count: int = Field(..., description="Count of CORRECT actions.")
    rejected_count: int = Field(..., description="Count of REJECT actions.")
    accept_rate: float = Field(..., description="Acceptance rate (0.00 - 1.00).")
    correction_rate: float = Field(..., description="Correction rate (0.00 - 1.00).")
    reject_rate: float = Field(..., description="Rejection rate (0.00 - 1.00).")
    field_breakdown: Dict[str, Any] = Field(..., description="Per-field accuracy breakdown.")


class HealthCheckResponse(BaseModel):
    status: str = Field(default="healthy", description="API health status.")
    ai_engine: str = Field(default="OILPS AI-HSE-Safety-Intelligence", description="Engine name.")
    sif_champion_loaded: bool = Field(..., description="Confirmation that Stage 6 SIF weights are active.")
    lsr_champion_loaded: bool = Field(..., description="Confirmation that Stage 7 LSR weights are active.")
    version: str = Field(default="2.0.0", description="Production API version.")
