export interface AIBarrierPattern {
  barrier_pattern_id: string;
  barrier_code_prefix?: string;
  barrier_code: string;
  barrier_name: string;
  incident_count: number;
  sif_incident_count: number;
  sif_density: number;
  pattern_strength: 'HIGH' | 'MEDIUM' | 'LOW';
  dominant_activity: string;
  dominant_lsr: string;
  dominant_hazard: string;
  locations: string[];
  potential_consequences: string[];
  stage23_pattern_ids: string[];
  incident_ids: string[];
  first_observed: string;
  last_observed: string;
  supporting_evidence: string[];
}

export interface BarrierPatternListResponse {
  total_barrier_patterns: number;
  min_support_threshold: number;
  barrier_patterns: AIBarrierPattern[];
}
