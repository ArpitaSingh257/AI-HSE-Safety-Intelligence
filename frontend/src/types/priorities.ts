export interface PriorityComponentScores {
  sif_impact: number;
  recurrence: number;
  barrier_impact: number;
  site_activity: number;
  early_warning: number;
}

export interface HSEPriorityProfile {
  priority_id: string;
  entity_type: 'BARRIER_FAILURE' | 'RECURRING_PATTERN' | 'SITE' | 'ACTIVITY';
  entity_id: string;
  entity_name: string;
  priority_score: number;
  priority_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INSUFFICIENT_DATA';
  components: PriorityComponentScores;
  supporting_report_ids: string[];
  pattern_ids: string[];
  barrier_pattern_ids: string[];
  site_ids: string[];
  activity_ids: string[];
  warning_ids: string[];
  first_observed: string;
  last_observed: string;
  reason: string;
}

export interface PriorityListResponse {
  total_priorities: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  priorities: HSEPriorityProfile[];
}
