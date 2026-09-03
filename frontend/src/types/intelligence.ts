export interface Stage43InputSection {
  original_text: string;
  normalized_text: string;
  language: string;
  normalization_method: string;
}

export interface Stage43SIFAssessment {
  potential: boolean;
  probability: number;
  risk_score: number;
  triage: string;
  model_version: string;
}

export interface Stage43LSRAssessment {
  labels: string[];
  primary: string;
  secondary: string[];
  confidence: Record<string, number>;
  provenance: string;
  agreement_state: string;
  human_review_required: boolean;
}

export interface Stage43PrecursorItem {
  token: string;
  precursor_type: string;
  salience_weight: number;
}

export interface Stage43SimilarIncident {
  record_id: string;
  similarity: number;
  narrative: string;
  site: string;
  activity: string;
  lsr_labels: string;
  provenance: string;
}

export interface Stage43BarrierAnalysis {
  observed_barriers: string[];
  failed_barriers: string[];
  missing_barriers: string[];
}

export interface Stage43RiskSubSection {
  status: string;
  details: Record<string, any>;
}

export interface Stage43RiskIntelligence {
  site: Stage43RiskSubSection;
  activity: Stage43RiskSubSection;
  recurrence: Stage43RiskSubSection;
  lsr_trends: Stage43RiskSubSection;
  early_warning: Stage43RiskSubSection;
  priority: Stage43RiskSubSection;
  severity_recurrence: Stage43RiskSubSection;
}

export interface Stage43BowTie {
  threat: string;
  barrier_failures: string[];
  top_event: string;
  potential_consequences: string[];
}

export interface Stage43Recommendation {
  rule: string;
  recommendation_text: string;
  grounded_sources: string[];
  status: string;
}

export interface Stage43Explainability {
  sif_explanation: string;
  lsr_explanation: string;
  risk_explanation: string;
  triage_explanation: string;
}

export interface Stage43Triage {
  action: string;
  confidence_category: string;
  human_review_required: boolean;
  explanation: string;
}

export interface Stage43Metadata {
  pipeline_version: string;
  deterministic_core: boolean;
  historical_dataset: Record<string, any>;
}

export interface Stage43IntelligenceResponse {
  request_id: string;
  input: Stage43InputSection;
  sif_assessment: Stage43SIFAssessment;
  lsr_assessment: Stage43LSRAssessment;
  precursors: Stage43PrecursorItem[];
  similar_incidents: Stage43SimilarIncident[];
  barrier_analysis: Stage43BarrierAnalysis;
  risk_intelligence: Stage43RiskIntelligence;
  bowtie: Stage43BowTie;
  recommendations: Stage43Recommendation[];
  evidence: string[];
  explainability: Stage43Explainability;
  triage: Stage43Triage;
  metadata: Stage43Metadata;
}
