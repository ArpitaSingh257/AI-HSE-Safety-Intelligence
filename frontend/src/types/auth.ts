export type UserRole = 'Admin' | 'HSE Manager' | 'HSE Analyst' | 'Viewer';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  department: string;
  site?: string;
  avatar?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginCredentials {
  email: string;
  password?: string;
  role?: UserRole;
}

export interface AuthResponse {
  token: string;
  user: User;
}

// Permissions by role
export interface RolePermissions {
  canViewReports: boolean;
  canCreateReport: boolean;
  canEditReport: boolean;
  canDeleteReport: boolean;
  canTriggerAIAnalysis: boolean;
  canManageInterventions: boolean;
  canViewAuditLogs: boolean;
  canManageUsers: boolean;
}

export const ROLE_PERMISSIONS: Record<UserRole, RolePermissions> = {
  'Admin': {
    canViewReports: true,
    canCreateReport: true,
    canEditReport: true,
    canDeleteReport: true,
    canTriggerAIAnalysis: true,
    canManageInterventions: true,
    canViewAuditLogs: true,
    canManageUsers: true,
  },
  'HSE Manager': {
    canViewReports: true,
    canCreateReport: true,
    canEditReport: true,
    canDeleteReport: false,
    canTriggerAIAnalysis: true,
    canManageInterventions: true,
    canViewAuditLogs: true,
    canManageUsers: false,
  },
  'HSE Analyst': {
    canViewReports: true,
    canCreateReport: true,
    canEditReport: true,
    canDeleteReport: false,
    canTriggerAIAnalysis: true,
    canManageInterventions: false,
    canViewAuditLogs: false,
    canManageUsers: false,
  },
  'Viewer': {
    canViewReports: true,
    canCreateReport: false,
    canEditReport: false,
    canDeleteReport: false,
    canTriggerAIAnalysis: false,
    canManageInterventions: false,
    canViewAuditLogs: false,
    canManageUsers: false,
  },
};
