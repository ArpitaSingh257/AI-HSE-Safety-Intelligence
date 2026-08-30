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

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  userId: string;
  userName: string;
  userRole: string;
  action: AuditActionType;
  entityType: 'REPORT' | 'AI_MODEL' | 'PATTERN' | 'INTERVENTION' | 'AUTH' | 'SYSTEM';
  entityId?: string;
  ipAddress: string;
  status: 'SUCCESS' | 'WARNING' | 'FAILURE';
  details: string;
  changesSummary?: {
    before?: string;
    after?: string;
  };
}
