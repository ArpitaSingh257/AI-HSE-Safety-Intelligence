import type { PriorityLevel } from './reports';

export interface AIRecurringPattern {
  pattern_id: string;
  pattern_code?: string;
  pattern_name: string;
  summary: string;
  pattern_strength: 'HIGH' | 'MEDIUM' | 'LOW';
  incident_count: number;
  sif_incident_count: number;
  sif_density: number;
  dominant_activity: string;
  dominant_lsr: string;
  dominant_hazard: string;
  dominant_barrier_failure: string;
  locations: string[];
  first_observed: string;
  last_observed: string;
  incident_ids: string[];
  evidence_quotes: string[];
}

export interface PrecursorPattern {
  id: string; // e.g. "PAT-001"
  name: string; // e.g. "Energy Isolation Failure"
  description: string;
  reportCount: number;
  mainActivity: string; // e.g. "Maintenance"
  mostAffectedSite: string; // e.g. "Duliajan Production Site"
  sifPotentialRate: number; // e.g. 0.81 (81%)
  priority: PriorityLevel;
  primaryLifeSavingRule: string; // e.g. "Energy Isolation"
  keyHazards: string[];
  commonBarrierFailures: string[];
  firstDetected: string;
  lastOccurrence: string;
  trendStatus: 'SURGING' | 'RECURRING' | 'DECLINING' | 'STABLE';
  recommendedIntervention: string;
  matchedReportIds: string[];
  ai_pattern?: AIRecurringPattern;
}
