import type { LsrTimeSeriesItem } from './lsrTrends';

export interface EarlyWarningProfile {
  warning_id: string;
  signal_type: 'BARRIER_FAILURE' | 'RECURRING_PATTERN' | 'SIF_DENSITY' | 'SITE_RISK' | 'ACTIVITY_RISK' | 'LSR_TREND' | string;
  signal_name?: string;
  category_name?: string;
  target_name?: string;
  barrier_name?: string;
  warning_level: 'HIGH_PRIORITY_ESCALATION' | 'EARLY_WARNING_ALERT' | 'WATCH_SIGNAL' | 'HIGH_PRIORITY' | 'EARLY_WARNING' | 'WATCH' | 'NORMAL' | 'INSUFFICIENT_DATA';
  period?: string;
  baseline_value?: number;
  recent_value?: number;
  baseline_rate?: number;
  recent_rate?: number;
  delta?: number;
  delta_rate?: number;
  consecutive_increasing_periods?: number;
  consecutive_increases?: number;
  consecutive_increase_periods?: number;
  affected_sites?: { site_name: string; count: number }[];
  affected_activities?: { activity_name: string; count: number }[];
  pattern_ids?: string[];
  barrier_pattern_ids?: string[];
  supporting_incident_ids?: string[];
  report_ids?: string[];
  reports_list?: any[];
  total_reports?: number;
  reason?: string;
  rationale?: string;
  first_observed?: string;
  last_observed?: string;
  time_series?: LsrTimeSeriesItem[];
  monthly_trend?: LsrTimeSeriesItem[];
  site_breakdown?: { name: string; count: number; sif_count?: number }[];
  activity_breakdown?: { name: string; count: number }[];
  top_barrier_failures?: string[];
  rag_recommendations?: {
    immediate_actions: string[];
    recommended_controls: string[];
    verification_actions: string[];
  };
}

export interface EarlyWarningListResponse {
  total_warnings?: number;
  total_warnings_evaluated?: number;
  high_priority_count?: number;
  high_priority_escalations_count?: number;
  early_warning_count?: number;
  early_warning_alerts_count?: number;
  watch_count?: number;
  watch_signals_count?: number;
  warnings?: EarlyWarningProfile[];
  warning_signals?: EarlyWarningProfile[];
}
