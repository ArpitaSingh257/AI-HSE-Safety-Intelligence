export interface LsrTimeSeriesItem {
  period: string;
  report_count: number;
  sif_count: number;
  sif_density: number;
}

export interface AILsrTrendProfile {
  lsr_rule: string;
  total_reports: number;
  sif_reports: number;
  sif_density: number;
  trend: 'INCREASING' | 'STABLE' | 'DECREASING' | 'INSUFFICIENT_DATA';
  trend_delta: number;
  time_series: LsrTimeSeriesItem[];
  top_sites: { site_name: string; count: number }[];
  top_activities: { activity_name: string; count: number }[];
  top_barrier_failures: { name: string; count: number }[];
  recurring_pattern_ids: string[];
  barrier_pattern_ids: string[];
  first_observed: string;
  last_observed: string;
  report_ids: string[];
}

export interface LsrTrendListResponse {
  total_lsr_rules: number;
  min_lsr_reports_threshold: number;
  unknown_lsr_records: number;
  unknown_lsr_rate: number;
  lsr_profiles: AILsrTrendProfile[];
}
