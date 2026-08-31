export type ReportType = 'Unsafe Act' | 'Unsafe Condition' | 'Near-Miss' | 'Incident';
export type SifStatus = 'SIF_POTENTIAL' | 'NON_SIF' | 'PENDING_ANALYSIS';
export type PriorityLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type AnalysisStatus = 'COMPLETED' | 'IN_PROGRESS' | 'PENDING' | 'FAILED';

export interface PrecursorDetails {
  activity: string;
  hazard: string;
  barrier_failure: string;
  potential_consequence: string;
}

export interface LifeSavingRuleMatch {
  name: string;
  score: number; // 0.0 to 1.0
  description?: string;
}

export interface AISourceCitation {
  document: string;
  page: number;
  section: string;
  chunk_id: string;
  similarity: number;
  snippet: string;
}

export interface AISafetyRecommendations {
  status: string;
  grounded: boolean;
  priority: string;
  summary: string;
  immediate_actions: string[];
  verification_actions: string[];
  control_verification: string[];
  escalation_actions: string[];
  escalation: string[];
  preventive_actions: string[];
  sources: AISourceCitation[];
  disclaimer: string;
}

export interface LSRExplanation {
  rule: string;
  model_probability: string;
  why_triggered: string;
}

export interface AIExplainableOutput {
  risk_level_display: string;
  sif_interpretation: string;
  why_flagged: string[];
  lsr_explanations: LSRExplanation[];
  grounding_banner: string;
  formatted_text: string;
}

export interface AIModelInfo {
  sif_model: string;
  lsr_model: string;
  version: string;
  status: string;
}

export interface FastApiIncidentAnalysisResponse {
  incident_id?: string;
  incident_text: string;
  sif: {
    probability: number;
    threshold: number;
    is_sif: boolean;
    risk_tier: string;
    salient_tokens: { token: string; weight: number }[];
  };
  lsr: {
    triggered_rules: string[];
    rule_predictions: { rule: string; probability: number; threshold: number; triggered: boolean }[];
    salient_tokens: { token: string; weight: number }[];
  };
  recommendations: AISafetyRecommendations;
  explainability: AIExplainableOutput;
  model_info: AIModelInfo;
}

export interface SifAnalysisResult {
  report_id: string;
  sif: {
    label: SifStatus;
    score: number; // 0.0 to 1.0
  };
  life_saving_rules: LifeSavingRuleMatch[];
  precursors: PrecursorDetails;
  explanation: string;
  patterns: string[];
  priority: PriorityLevel;
  analyzed_at?: string;
  model_version?: string;
  full_ai_response?: FastApiIncidentAnalysisResponse;
}

export interface SafetyReport {
  id: string; // e.g. "R001"
  title: string;
  type: ReportType;
  date: string; // ISO date string
  site: string; // e.g. "Duliajan Production Site", "Moran Oilfield", "Digboi Refinery"
  department: string;
  location_detail?: string;
  activity: string; // e.g. "Maintenance", "Rig Operations", "Pipeline Inspection", "Hot Work"
  reporter_name: string;
  reporter_role?: string;
  description: string; // Original free-text report
  immediate_actions_taken?: string;
  
  // SIF & AI fields
  sif_status: SifStatus;
  sif_score: number; // 0 to 100 or 0.0 to 1.0
  life_saving_rule: string;
  priority: PriorityLevel;
  analysis_status: AnalysisStatus;
  ai_result?: SifAnalysisResult;
  
  // Metadata
  created_at: string;
  updated_at: string;
  investigation_status?: 'Open' | 'Under Review' | 'Intervention Scheduled' | 'Closed';
}

export interface ReportFilterOptions {
  search?: string;
  type?: ReportType | 'ALL';
  site?: string | 'ALL';
  activity?: string | 'ALL';
  sif_status?: SifStatus | 'ALL';
  priority?: PriorityLevel | 'ALL';
  life_saving_rule?: string | 'ALL';
  analysis_status?: AnalysisStatus | 'ALL';
  dateFrom?: string;
  dateTo?: string;
  sortBy?: keyof SafetyReport;
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

export interface CreateReportPayload {
  title: string;
  type: ReportType;
  date: string;
  site: string;
  department: string;
  location_detail?: string;
  activity: string;
  reporter_name: string;
  description: string;
  immediate_actions_taken?: string;
  priority?: PriorityLevel;
}
