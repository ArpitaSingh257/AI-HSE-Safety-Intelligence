import type { PriorityLevel } from './reports';

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
}
