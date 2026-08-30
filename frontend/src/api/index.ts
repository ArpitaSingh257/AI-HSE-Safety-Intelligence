import { apiClient } from './client';
import {
  mockAuthService,
  mockReportsService,
  mockDashboardService,
  mockPatternsService,
  mockInterventionsService,
  mockAuditService,
} from './mockService';
import type { SafetyReport, SifAnalysisResult, CreateReportPayload, ReportFilterOptions } from '../types/reports';
import type { LoginCredentials, AuthResponse, User } from '../types/auth';
import type { PrecursorPattern } from '../types/patterns';
import type { HSEIntervention } from '../types/interventions';
import type { AuditLogEntry } from '../types/audit';
import type { DashboardOverviewResponse } from '../types/dashboard';

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';

/**
 * AUTH SERVICE (POST /api/auth/login, POST /api/auth/register, GET /api/auth/me)
 */
export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    if (USE_MOCK) {
      return mockAuthService.login(credentials);
    }
    try {
      const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
      return response.data;
    } catch {
      return mockAuthService.login(credentials);
    }
  },

  async register(data: Record<string, unknown>): Promise<AuthResponse> {
    if (USE_MOCK) {
      return mockAuthService.login({ email: (data.email as string) || 'user@oilindia.in' });
    }
    const response = await apiClient.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  async getMe(): Promise<User> {
    if (USE_MOCK) {
      return mockAuthService.getCurrentUser();
    }
    try {
      const response = await apiClient.get<User>('/auth/me');
      return response.data;
    } catch {
      return mockAuthService.getCurrentUser();
    }
  },
};

/**
 * REPORTS SERVICE (GET /api/reports, POST /api/reports, GET /api/reports/:id, PUT /api/reports/:id, DELETE /api/reports/:id, POST /api/reports/:id/analyze)
 */
export const reportsService = {
  async getReports(filters?: ReportFilterOptions): Promise<{ data: SafetyReport[]; total: number }> {
    if (USE_MOCK) {
      return mockReportsService.getReports(filters);
    }
    try {
      const response = await apiClient.get<{ data: SafetyReport[]; total: number }>('/reports', {
        params: filters,
      });
      return response.data;
    } catch {
      return mockReportsService.getReports(filters);
    }
  },

  async getReportById(id: string): Promise<SafetyReport> {
    if (USE_MOCK) {
      return mockReportsService.getReportById(id);
    }
    try {
      const response = await apiClient.get<SafetyReport>(`/reports/${id}`);
      return response.data;
    } catch {
      return mockReportsService.getReportById(id);
    }
  },

  async createReport(payload: CreateReportPayload): Promise<SafetyReport> {
    if (USE_MOCK) {
      return mockReportsService.createReport(payload);
    }
    try {
      const response = await apiClient.post<SafetyReport>('/reports', payload);
      return response.data;
    } catch {
      return mockReportsService.createReport(payload);
    }
  },

  async updateReport(id: string, updates: Partial<SafetyReport>): Promise<SafetyReport> {
    if (USE_MOCK) {
      return mockReportsService.updateReport(id, updates);
    }
    try {
      const response = await apiClient.put<SafetyReport>(`/reports/${id}`, updates);
      return response.data;
    } catch {
      return mockReportsService.updateReport(id, updates);
    }
  },

  async deleteReport(id: string): Promise<{ success: boolean }> {
    if (USE_MOCK) {
      return mockReportsService.deleteReport(id);
    }
    try {
      const response = await apiClient.delete<{ success: boolean }>(`/reports/${id}`);
      return response.data;
    } catch {
      return mockReportsService.deleteReport(id);
    }
  },

  async analyzeReport(id: string): Promise<SifAnalysisResult> {
    if (USE_MOCK) {
      return mockReportsService.analyzeReport(id);
    }
    try {
      const response = await apiClient.post<SifAnalysisResult>(`/reports/${id}/analyze`);
      return response.data;
    } catch {
      return mockReportsService.analyzeReport(id);
    }
  },

  async getAiResults(reportId: string): Promise<SifAnalysisResult> {
    if (USE_MOCK) {
      return mockReportsService.getAiResults(reportId);
    }
    try {
      const response = await apiClient.get<SifAnalysisResult>(`/ai-results/${reportId}`);
      return response.data;
    } catch {
      return mockReportsService.getAiResults(reportId);
    }
  },
};

/**
 * DASHBOARD SERVICE (GET /api/dashboard/*)
 */
export const dashboardService = {
  async getOverview(): Promise<DashboardOverviewResponse> {
    if (USE_MOCK) {
      return mockDashboardService.getOverview();
    }
    try {
      const response = await apiClient.get<DashboardOverviewResponse>('/dashboard/overview');
      return response.data;
    } catch {
      return mockDashboardService.getOverview();
    }
  },

  async getSites() {
    if (USE_MOCK) return mockDashboardService.getSites();
    const response = await apiClient.get('/dashboard/sites');
    return response.data;
  },

  async getActivities() {
    if (USE_MOCK) return mockDashboardService.getActivities();
    const response = await apiClient.get('/dashboard/activities');
    return response.data;
  },

  async getLifeSavingRules() {
    if (USE_MOCK) return mockDashboardService.getLifeSavingRules();
    const response = await apiClient.get('/dashboard/life-saving-rules');
    return response.data;
  },

  async getPrecursors() {
    if (USE_MOCK) return mockDashboardService.getPrecursors();
    const response = await apiClient.get('/dashboard/precursors');
    return response.data;
  },

  async getTrends() {
    if (USE_MOCK) return mockDashboardService.getTrends();
    const response = await apiClient.get('/dashboard/trends');
    return response.data;
  },
};

/**
 * PATTERNS SERVICE (GET /api/patterns, GET /api/patterns/:id)
 */
export const patternsService = {
  async getPatterns(): Promise<PrecursorPattern[]> {
    if (USE_MOCK) {
      return mockPatternsService.getPatterns();
    }
    try {
      const response = await apiClient.get<PrecursorPattern[]>('/patterns');
      return response.data;
    } catch {
      return mockPatternsService.getPatterns();
    }
  },

  async getPatternById(id: string): Promise<PrecursorPattern> {
    if (USE_MOCK) {
      return mockPatternsService.getPatternById(id);
    }
    try {
      const response = await apiClient.get<PrecursorPattern>(`/patterns/${id}`);
      return response.data;
    } catch {
      return mockPatternsService.getPatternById(id);
    }
  },
};

/**
 * INTERVENTIONS SERVICE (GET /api/interventions)
 */
export const interventionsService = {
  async getInterventions(): Promise<HSEIntervention[]> {
    if (USE_MOCK) {
      return mockInterventionsService.getInterventions();
    }
    try {
      const response = await apiClient.get<HSEIntervention[]>('/interventions');
      return response.data;
    } catch {
      return mockInterventionsService.getInterventions();
    }
  },

  async updateIntervention(id: string, updates: Partial<HSEIntervention>): Promise<HSEIntervention> {
    if (USE_MOCK) {
      return mockInterventionsService.updateIntervention(id, updates);
    }
    try {
      const response = await apiClient.put<HSEIntervention>(`/interventions/${id}`, updates);
      return response.data;
    } catch {
      return mockInterventionsService.updateIntervention(id, updates);
    }
  },

  async createIntervention(newIntervention: Omit<HSEIntervention, 'id' | 'createdDate'>): Promise<HSEIntervention> {
    if (USE_MOCK) {
      return mockInterventionsService.createIntervention(newIntervention);
    }
    try {
      const response = await apiClient.post<HSEIntervention>('/interventions', newIntervention);
      return response.data;
    } catch {
      return mockInterventionsService.createIntervention(newIntervention);
    }
  },
};

/**
 * AUDIT LOGS SERVICE (GET /api/audit-logs)
 */
export const auditService = {
  async getAuditLogs(): Promise<AuditLogEntry[]> {
    if (USE_MOCK) {
      return mockAuditService.getAuditLogs();
    }
    try {
      const response = await apiClient.get<AuditLogEntry[]>('/audit-logs');
      return response.data;
    } catch {
      return mockAuditService.getAuditLogs();
    }
  },
};
