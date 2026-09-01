import type { LsrTimeSeriesItem } from './lsrTrends';

export interface EarlyWarningProfile {
  warning_id: string;
  signal_type: 'BARRIER_FAILURE' | 'RECURRING_PATTERN' | 'SIF_DENSITY' | 'SITE_RISK' | 'ACTIVITY_RISK' | 'LSR_TREND';
  signal_name: string;
  warning_level: 'HIGH_PRIORITY' | 'EARLY_WARNING' | 'WATCH' | 'NORMAL' | 'INSUFFICIENT_DATA';
  period: string;
  baseline_value: number;
  recent_value: number;
  delta: number;
  consecutive_increasing_periods: number;
  affected_sites: { site_name: string; count: number }[];
  affected_activities: { activity_name: string; count: number }[];
  pattern_ids: string[];
  barrier_pattern_ids: string[];
  supporting_incident_ids: string[];
  reason: string;
  first_observed: string;
  last_observed: string;
  time_series: LsrTimeSeriesItem[];
}

export interface EarlyWarningListResponse {
  total_warnings: number;
  high_priority_count: number;
  early_warning_count: number;
  watch_count: number;
  warnings: EarlyWarningProfile[];
}
