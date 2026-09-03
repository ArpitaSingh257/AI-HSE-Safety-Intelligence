export interface LsrTimeSeriesItem {
  period: string;
  report_count: number;
  sif_count: number;
  sif_density: number;
}

export interface AILsrTrendProfile {
  lsr_rule: string;
  rule_name?: string;
  lsr_code?: string;
  total_reports: number;
  sif_reports: number;
  sif_density: number;
  risk_index?: number;
  risk_level?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  trend?: 'INCREASING' | 'STABLE' | 'DECREASING' | 'WORSENING' | 'IMPROVING' | 'INSUFFICIENT_DATA';
  trend_status?: 'WORSENING' | 'STABLE' | 'IMPROVING';
  trend_delta?: number;
  time_series?: LsrTimeSeriesItem[];
  monthly_trend?: LsrTimeSeriesItem[];
  top_sites?: { site_name: string; count: number; report_count?: number }[];
  associated_sites?: { site_name: string; count: number; report_count?: number }[];
  top_activities?: { activity_name: string; name?: string; count: number; report_count?: number }[];
  top_barrier_failures?: { name: string; count: number; occurrence_count?: number }[];
  recurring_pattern_ids?: string[];
  barrier_pattern_ids?: string[];
  first_observed?: string;
  last_observed?: string;
  report_ids?: string[];
  reports_list?: any[];
}

export interface LsrTrendListResponse {
  total_lsr_rules: number;
  min_lsr_reports_threshold: number;
  unknown_lsr_records: number;
  unknown_lsr_rate: number;
  lsr_profiles: AILsrTrendProfile[];
}
