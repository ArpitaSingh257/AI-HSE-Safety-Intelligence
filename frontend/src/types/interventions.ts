import type { PriorityLevel } from './reports';

export type InterventionStatus = 'OPEN' | 'IN_PROGRESS' | 'UNDER_VERIFICATION' | 'CLOSED';

export interface HSEIntervention {
  id: string; // e.g. "INT-2026-04"
  title: string;
  category: 'Engineering Control' | 'Administrative Control' | 'Training & Competency' | 'Process Safety Barrier' | 'PPE & Equipment';
  description: string;
  triggerSource: 'Pattern Detection' | 'High SIF Frequency' | 'Audit Finding' | 'Life-Saving Rule Non-Compliance';
  targetSite: string;
  targetActivity: string;
  associatedRule: string;
  priority: PriorityLevel;
  status: InterventionStatus;
  assignedOfficer: string;
  assignedOfficerRole: string;
  dueDate: string;
  createdDate: string;
  completionDate?: string;
  relatedReportIds: string[];
  patternId?: string;
  actionsTaken?: string[];
  verificationNotes?: string;
  effectivenessRating?: 'HIGHLY_EFFECTIVE' | 'EFFECTIVE' | 'NEEDS_REVISION';
}
