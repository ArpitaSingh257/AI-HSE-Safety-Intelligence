// Central type definitions. Every model/route imports role, status, and
// priority types from HERE ONLY, so casing never drifts across files.

export type UserRole = 'Admin' | 'HSE Manager' | 'HSE Analyst' | 'Viewer';

export const USER_ROLES: UserRole[] = ['Admin', 'HSE Manager', 'HSE Analyst', 'Viewer'];

export type ReportType = 'Unsafe Act' | 'Unsafe Condition' | 'Near-Miss' | 'Incident';
export const REPORT_TYPES: ReportType[] = ['Unsafe Act', 'Unsafe Condition', 'Near-Miss', 'Incident'];

export type SifStatus = 'SIF_POTENTIAL' | 'NON_SIF' | 'PENDING_ANALYSIS';
export const SIF_STATUSES: SifStatus[] = ['SIF_POTENTIAL', 'NON_SIF', 'PENDING_ANALYSIS'];

export type PriorityLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export const PRIORITY_LEVELS: PriorityLevel[] = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

export type AnalysisStatus = 'COMPLETED' | 'IN_PROGRESS' | 'PENDING' | 'FAILED';
export const ANALYSIS_STATUSES: AnalysisStatus[] = ['COMPLETED', 'IN_PROGRESS', 'PENDING', 'FAILED'];

export type InvestigationStatus = 'Open' | 'Under Review' | 'Intervention Scheduled' | 'Closed';
export const INVESTIGATION_STATUSES: InvestigationStatus[] = ['Open', 'Under Review', 'Intervention Scheduled', 'Closed'];

export type SiteName = 'Duliajan' | 'Moran' | 'Naharkatiya' | 'Digboi';
export const SITE_NAMES: SiteName[] = ['Duliajan', 'Moran', 'Naharkatiya', 'Digboi'];

export type ActivityName = 'Maintenance' | 'Rig Floor' | 'Hot Work' | 'Confined Space' | 'Height Works';
export const ACTIVITY_NAMES: ActivityName[] = ['Maintenance', 'Rig Floor', 'Hot Work', 'Confined Space', 'Height Works'];

export type TrendStatus = 'SURGING' | 'RECURRING' | 'DECLINING' | 'STABLE';
export const TREND_STATUSES: TrendStatus[] = ['SURGING', 'RECURRING', 'DECLINING', 'STABLE'];

export type InterventionCategory =
  | 'Engineering Control'
  | 'Administrative Control'
  | 'Training & Competency'
  | 'Process Safety Barrier'
  | 'PPE & Equipment';
export const INTERVENTION_CATEGORIES: InterventionCategory[] = [
  'Engineering Control',
  'Administrative Control',
  'Training & Competency',
  'Process Safety Barrier',
  'PPE & Equipment',
];

export type InterventionTriggerSource =
  | 'Pattern Detection'
  | 'High SIF Frequency'
  | 'Audit Finding'
  | 'Life-Saving Rule Non-Compliance';
export const INTERVENTION_TRIGGER_SOURCES: InterventionTriggerSource[] = [
  'Pattern Detection',
  'High SIF Frequency',
  'Audit Finding',
  'Life-Saving Rule Non-Compliance',
];

export type InterventionStatus = 'OPEN' | 'IN_PROGRESS' | 'UNDER_VERIFICATION' | 'CLOSED';
export const INTERVENTION_STATUSES: InterventionStatus[] = ['OPEN', 'IN_PROGRESS', 'UNDER_VERIFICATION', 'CLOSED'];

export type EffectivenessRating = 'HIGHLY_EFFECTIVE' | 'EFFECTIVE' | 'NEEDS_REVISION';
export const EFFECTIVENESS_RATINGS: EffectivenessRating[] = ['HIGHLY_EFFECTIVE', 'EFFECTIVE', 'NEEDS_REVISION'];

export type AuditActionType =
  | 'USER_LOGIN'
  | 'USER_LOGOUT'
  | 'REPORT_CREATED'
  | 'REPORT_UPDATED'
  | 'REPORT_DELETED'
  | 'AI_ANALYSIS_TRIGGERED'
  | 'AI_ANALYSIS_COMPLETED'
  | 'PATTERN_IDENTIFIED'
  | 'INTERVENTION_CREATED'
  | 'INTERVENTION_STATUS_UPDATED'
  | 'SYSTEM_CONFIG_CHANGED';

export type AuditEntityType = 'REPORT' | 'AI_MODEL' | 'PATTERN' | 'INTERVENTION' | 'AUTH' | 'SYSTEM';
export type AuditStatus = 'SUCCESS' | 'WARNING' | 'FAILURE';

export interface JwtPayload {
  userId: string;
  name: string;
  email: string;
  role: UserRole;
}

// Full FastAPI AI Service Response Contracts (Stage 21 Frozen)
export interface AISourceCitation {
  document: string;
  page: number;
  section: string;
  chunk_id: string;
  similarity: number;
  snippet: string;
}

export interface AISafetyRecommendations {
  status: string;
  grounded: boolean;
  priority: string;
  summary: string;
  immediate_actions: string[];
  verification_actions: string[];
  control_verification: string[];
  escalation_actions: string[];
  escalation: string[];
  preventive_actions: string[];
  sources: AISourceCitation[];
  disclaimer: string;
}

export interface LSRExplanation {
  rule: string;
  model_probability: string;
  why_triggered: string;
}

export interface AIExplainableOutput {
  risk_level_display: string;
  sif_interpretation: string;
  why_flagged: string[];
  lsr_explanations: LSRExplanation[];
  grounding_banner: string;
  formatted_text: string;
}

export interface AIModelInfo {
  sif_model: string;
  lsr_model: string;
  version: string;
  status: string;
}

export interface FastApiIncidentAnalysisResponse {
  incident_id?: string;
  incident_text: string;
  sif: {
    probability: number;
    threshold: number;
    is_sif: boolean;
    risk_tier: string;
    salient_tokens: { token: string; weight: number }[];
  };
  lsr: {
    triggered_rules: string[];
    rule_predictions: { rule: string; probability: number; threshold: number; triggered: boolean }[];
    salient_tokens: { token: string; weight: number }[];
  };
  recommendations: AISafetyRecommendations;
  explainability: AIExplainableOutput;
  model_info: AIModelInfo;
}

// RBAC matrix - single source of truth, imported by every route file.
export const PERMISSIONS = {
  canCreateReport: ['Admin', 'HSE Manager', 'HSE Analyst'] as UserRole[],
  canEditReport: ['Admin', 'HSE Manager', 'HSE Analyst'] as UserRole[],
  canDeleteReport: ['Admin'] as UserRole[],
  canTriggerAIAnalysis: ['Admin', 'HSE Manager', 'HSE Analyst'] as UserRole[],
  canManagePatterns: ['Admin', 'HSE Manager'] as UserRole[],
  canManageInterventions: ['Admin', 'HSE Manager'] as UserRole[],
  canDeleteIntervention: ['Admin'] as UserRole[],
  canViewAuditLogs: ['Admin', 'HSE Manager'] as UserRole[],
};