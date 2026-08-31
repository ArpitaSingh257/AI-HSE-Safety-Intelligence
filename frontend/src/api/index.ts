import { apiClient } from './client';
import {
  mockAuthService,
  mockReportsService,
  mockDashboardService,
  mockPatternsService,
  mockInterventionsService,
  mockAuditService,
} from './mockService';
import type { SafetyReport, SifAnalysisResult, CreateReportPayload, ReportFilterOptions, FastApiIncidentAnalysisResponse } from '../types/reports';
import type { LoginCredentials, AuthResponse, User } from '../types/auth';
import type { PrecursorPattern } from '../types/patterns';
import type { HSEIntervention } from '../types/interventions';
import type { AuditLogEntry } from '../types/audit';
import type { DashboardOverviewResponse } from '../types/dashboard';

const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';

/**
 * Decides whether a failed real-API call should silently fall back to mock
 * data, or whether the error should propagate to the UI.
 *
 * - No response at all (network down, backend not running) → fallback to
 *   mock so the demo still works offline.
 * - 4xx client errors (validation failures, 404s, auth errors) → these are
 *   REAL errors the user needs to see (e.g. "Description must be at least
 *   10 characters"). Never mask these with fake mock data - doing so causes
 *   silent data loss where the user thinks something saved when it didn't.
 * - 5xx server errors → backend is reachable but broken, fallback is a
 *   reasonable demo safety net.
 */
function shouldFallbackToMock(error: any): boolean {
  if (!error?.response) return true;
  const status = error.response.status;
  if (status >= 400 && status < 500) return false;
  return true;
}

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
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockAuthService.login(credentials);
      }
      throw error;
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
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockAuthService.getCurrentUser();
      }
      throw error;
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
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockReportsService.getReports(filters);
      }
      throw error;
    }
  },

  async getReportById(id: string): Promise<SafetyReport> {
    if (USE_MOCK) {
      return mockReportsService.getReportById(id);
    }
    try {
      const response = await apiClient.get<SafetyReport>(`/reports/${id}`);
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockReportsService.getReportById(id);
      }
      throw error;
    }
  },

  async createReport(payload: CreateReportPayload): Promise<SafetyReport> {
    if (USE_MOCK) {
      return mockReportsService.createReport(payload);
    }
    try {
      const response = await apiClient.post<SafetyReport>('/reports', payload);
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockReportsService.createReport(payload);
      }
      throw error;
    }
  },

  async updateReport(id: string, updates: Partial<SafetyReport>): Promise<SafetyReport> {
    if (USE_MOCK) {
      return mockReportsService.updateReport(id, updates);
    }
    try {
      const response = await apiClient.put<SafetyReport>(`/reports/${id}`, updates);
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockReportsService.updateReport(id, updates);
      }
      throw error;
    }
  },

  async deleteReport(id: string): Promise<{ success: boolean }> {
    if (USE_MOCK) {
      return mockReportsService.deleteReport(id);
    }
    try {
      const response = await apiClient.delete<{ success: boolean }>(`/reports/${id}`);
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockReportsService.deleteReport(id);
      }
      throw error;
    }
  },

  async analyzeReport(id: string): Promise<SifAnalysisResult> {
    if (USE_MOCK) {
      return mockReportsService.analyzeReport(id);
    }
    try {
      const response = await apiClient.post<SifAnalysisResult>(`/reports/${id}/analyze`);
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockReportsService.analyzeReport(id);
      }
      throw error;
    }
  },

  async getAiResults(reportId: string): Promise<SifAnalysisResult> {
    if (USE_MOCK) {
      return mockReportsService.getAiResults(reportId);
    }
    try {
      const response = await apiClient.get<SifAnalysisResult>(`/ai-results/${reportId}`);
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockReportsService.getAiResults(reportId);
      }
      throw error;
    }
  },

  async analyzeIncidentDirect(incidentText: string): Promise<FastApiIncidentAnalysisResponse> {
    const response = await apiClient.post<FastApiIncidentAnalysisResponse>('/incidents/analyze', {
      incident_text: incidentText,
    }, { timeout: 35000 });
    return response.data;
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
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockDashboardService.getOverview();
      }
      throw error;
    }
  },

  async getSites() {
    if (USE_MOCK) return mockDashboardService.getSites();
    try {
      const response = await apiClient.get('/dashboard/sites');
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockDashboardService.getSites();
      }
      throw error;
    }
  },

  async getActivities() {
    if (USE_MOCK) return mockDashboardService.getActivities();
    try {
      const response = await apiClient.get('/dashboard/activities');
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockDashboardService.getActivities();
      }
      throw error;
    }
  },

  async getLifeSavingRules() {
    if (USE_MOCK) return mockDashboardService.getLifeSavingRules();
    try {
      const response = await apiClient.get('/dashboard/life-saving-rules');
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockDashboardService.getLifeSavingRules();
      }
      throw error;
    }
  },

  async getPrecursors() {
    if (USE_MOCK) return mockDashboardService.getPrecursors();
    try {
      const response = await apiClient.get('/dashboard/precursors');
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockDashboardService.getPrecursors();
      }
      throw error;
    }
  },

  async getTrends() {
    if (USE_MOCK) return mockDashboardService.getTrends();
    try {
      const response = await apiClient.get('/dashboard/trends');
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockDashboardService.getTrends();
      }
      throw error;
    }
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
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockPatternsService.getPatterns();
      }
      throw error;
    }
  },

  async getPatternById(id: string): Promise<PrecursorPattern> {
    if (USE_MOCK) {
      return mockPatternsService.getPatternById(id);
    }
    try {
      const response = await apiClient.get<PrecursorPattern>(`/patterns/${id}`);
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockPatternsService.getPatternById(id);
      }
      throw error;
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
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockInterventionsService.getInterventions();
      }
      throw error;
    }
  },

  async updateIntervention(id: string, updates: Partial<HSEIntervention>): Promise<HSEIntervention> {
    if (USE_MOCK) {
      return mockInterventionsService.updateIntervention(id, updates);
    }
    try {
      const response = await apiClient.put<HSEIntervention>(`/interventions/${id}`, updates);
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockInterventionsService.updateIntervention(id, updates);
      }
      throw error;
    }
  },

  async createIntervention(newIntervention: Omit<HSEIntervention, 'id' | 'createdDate'>): Promise<HSEIntervention> {
    if (USE_MOCK) {
      return mockInterventionsService.createIntervention(newIntervention);
    }
    try {
      const response = await apiClient.post<HSEIntervention>('/interventions', newIntervention);
      return response.data;
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockInterventionsService.createIntervention(newIntervention);
      }
      throw error;
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
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        return mockAuditService.getAuditLogs();
      }
      throw error;
    }
  },
};