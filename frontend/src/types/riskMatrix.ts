export interface SupportingReportDetail {
  id: string;
  sif_status?: 'SIF_POTENTIAL' | 'NON_SIF';
  priority?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  date?: string;
  site?: string;
  activity?: string;
}

export interface RAGSafetyRecommendations {
  engineering_control: string;
  procedural_protocol: string;
  governance_audit: string;
  rag_citations: string[];
}

export interface RiskMatrixItem {
  matrix_item_id: string;
  entity_type: 'BARRIER_FAILURE' | 'RECURRING_PATTERN' | 'SITE' | 'ACTIVITY';
  entity_id: string;
  entity_name: string;
  severity_score: number;
  recurrence_score: number;
  severity_level: 'HIGH' | 'LOW' | 'INSUFFICIENT_DATA';
  recurrence_level: 'HIGH' | 'LOW' | 'INSUFFICIENT_DATA';
  quadrant:
    | 'HIGH_SEVERITY_HIGH_RECURRENCE'
    | 'HIGH_SEVERITY_LOW_RECURRENCE'
    | 'LOW_SEVERITY_HIGH_RECURRENCE'
    | 'LOW_SEVERITY_LOW_RECURRENCE'
    | 'INSUFFICIENT_DATA';
  classification:
    | 'CRITICAL_PRIORITY'
    | 'HIGH_POTENTIAL_RARE'
    | 'FREQUENT_LOWER_POTENTIAL'
    | 'LOW_PRIORITY_MONITOR'
    | 'INSUFFICIENT_DATA';
  supporting_report_ids: string[];
  supporting_reports?: SupportingReportDetail[];
  pattern_ids: string[];
  barrier_pattern_ids: string[];
  site_ids: string[];
  activity_ids: string[];
  first_observed: string;
  last_observed: string;
  reason: string;
  recommendations?: RAGSafetyRecommendations;
}

export interface RiskMatrixListResponse {
  total_items: number;
  critical_priority_count: number;
  high_potential_rare_count: number;
  frequent_lower_potential_count: number;
  low_priority_monitor_count: number;
  matrix_items: RiskMatrixItem[];
}
