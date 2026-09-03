export interface TriageRequest {
  report_id: string;
  raw_sif_probability?: number;
  priority_level?: string;
  priority_score?: number;
  early_warning_level?: string;
  risk_matrix_category?: string;
}

export interface TriageResult {
  report_id: string;
  sif_raw_probability: number;
  sif_calibrated_probability: number;
  calibration_status: 'ACTIVE' | 'INSUFFICIENT_DATA' | 'UNAVAILABLE';
  calibration_method: string;
  calibration_version: string;
  triage_level: 'IMMEDIATE_ESCALATION' | 'NEEDS_REVIEW' | 'AUTO_CLEAR';
  reason_code: string;
  human_readable_reason: string;
  priority_level: string;
  priority_score: number;
  early_warning_level: string;
  risk_matrix_category: string;
  model_version: string;
  pipeline_version: string;
  policy_version: string;
}

export interface TriageBatchResponse {
  total_evaluated: number;
  immediate_escalation_count: number;
  needs_review_count: number;
  auto_clear_count: number;
  triage_results: TriageResult[];
}
