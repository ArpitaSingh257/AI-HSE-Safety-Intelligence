export interface AIActivityRiskProfile {
  activity_id: string;
  activity_name: string;
  total_reports: number;
  sif_reports: number;
  non_sif_reports: number;
  sif_density: number;
  recurring_pattern_count: number;
  barrier_failure_pattern_count: number;
  risk_index: number;
  risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INSUFFICIENT_DATA';
  sif_component: number;
  pattern_component: number;
  barrier_component: number;
  top_hazards: { name: string; count: number }[];
  top_barrier_failures: { name: string; count: number; sif_count: number; sif_density: number }[];
  top_life_saving_rules: { name: string; count: number }[];
  associated_sites: { site_name: string; count: number }[];
  first_observed: string;
  last_observed: string;
  report_ids: string[];
  pattern_ids: string[];
  barrier_pattern_ids: string[];
}

export interface ActivityRiskListResponse {
  total_activities: number;
  min_activity_reports_threshold: number;
  activity_profiles: AIActivityRiskProfile[];
}
