export interface AISiteRiskProfile {
  site_id: string;
  site_name: string;
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
  top_activities: { name: string; report_count: number; sif_count: number; sif_density: number }[];
  top_hazards: { name: string; count: number }[];
  top_barrier_failures: { name: string; count: number; sif_count: number; sif_density: number }[];
  top_life_saving_rules: { name: string; count: number }[];
  first_observed: string;
  last_observed: string;
  report_ids: string[];
  pattern_ids: string[];
  barrier_pattern_ids: string[];
}

export interface SiteRiskListResponse {
  total_sites: number;
  min_site_reports_threshold: number;
  site_profiles: AISiteRiskProfile[];
}
