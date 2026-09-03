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
import type { Stage43IntelligenceResponse } from '../types/intelligence';

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

  async analyzeIncidentDirect(payload: { incidentText: string; title?: string; site?: string; activity?: string }): Promise<FastApiIncidentAnalysisResponse> {
    const response = await apiClient.post<FastApiIncidentAnalysisResponse>('/incidents/analyze', payload);
    return response.data;
  },

  async getSimilarReports(id: string): Promise<any> {
    try {
      const response = await apiClient.get(`/reports/${id}/similar`);
      return response.data;
    } catch (error) {
      console.warn(`Similar reports API call for report ${id} failed:`, error);
      return { query_report_id: id, total_matches: 0, similar_reports: [] };
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
  async getPatterns(): Promise<{ ai_patterns: AIRecurringPattern[]; db_patterns: PrecursorPattern[] }> {
    if (USE_MOCK) {
      const mockPats = await mockPatternsService.getPatterns();
      return { ai_patterns: [], db_patterns: mockPats };
    }
    try {
      const response = await apiClient.get<{ ai_patterns: AIRecurringPattern[]; db_patterns: PrecursorPattern[] }>('/patterns');
      if (Array.isArray(response.data)) {
        return { ai_patterns: [], db_patterns: response.data };
      }
      return {
        ai_patterns: response.data?.ai_patterns || [],
        db_patterns: response.data?.db_patterns || []
      };
    } catch (error) {
      if (shouldFallbackToMock(error)) {
        const mockPats = await mockPatternsService.getPatterns();
        return { ai_patterns: [], db_patterns: mockPats };
      }
      throw error;
    }
  },

  async getPatternById(id: string): Promise<any> {
    if (USE_MOCK) {
      return mockPatternsService.getPatternById(id);
    }
    try {
      const response = await apiClient.get<any>(`/patterns/${id}`);
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
 * BARRIER PATTERNS SERVICE (GET /api/barrier-patterns, GET /api/barrier-patterns/:id)
 */
export const barrierPatternsService = {
  async getBarrierPatterns(): Promise<any> {
    try {
      const response = await apiClient.get('/barrier-patterns');
      return response.data;
    } catch (error) {
      console.warn('Barrier patterns API call failed:', error);
      return { total_barrier_patterns: 0, barrier_patterns: [] };
    }
  },

  async getBarrierPatternById(id: string): Promise<any> {
    try {
      const response = await apiClient.get(`/barrier-patterns/${id}`);
      return response.data;
    } catch (error) {
      console.warn(`Barrier pattern detail call for ${id} failed:`, error);
      return null;
    }
  },
};

/**
 * SITE RISK SERVICE (GET /api/site-risk, GET /api/site-risk/:id)
 */
export const siteRiskService = {
  async getSiteRiskProfiles(): Promise<any> {
    try {
      const response = await apiClient.get('/site-risk');
      return response.data;
    } catch (error) {
      console.warn('Site risk profiles API call failed:', error);
      return { total_sites: 0, site_profiles: [] };
    }
  },

  async getSiteRiskProfileById(id: string): Promise<any> {
    try {
      const response = await apiClient.get(`/site-risk/${id}`);
      return response.data;
    } catch (error) {
      console.warn(`Site risk profile call for ${id} failed:`, error);
      return null;
    }
  },
};

/**
 * ACTIVITY RISK SERVICE (GET /api/activity-risk, GET /api/activity-risk/:id)
 */
export const activityRiskService = {
  async getActivityRiskProfiles(): Promise<any> {
    try {
      const response = await apiClient.get('/activity-risk');
      return response.data;
    } catch (error) {
      console.warn('Activity risk profiles API call failed:', error);
      return { total_activities: 0, activity_profiles: [] };
    }
  },

  async getActivityRiskProfileById(id: string): Promise<any> {
    try {
      const response = await apiClient.get(`/activity-risk/${id}`);
      return response.data;
    } catch (error) {
      console.warn(`Activity risk profile call for ${id} failed:`, error);
      return null;
    }
  },
};

/**
 * LSR TRENDS SERVICE (GET /api/lsr-trends, GET /api/lsr-trends/:rule)
 */
export const lsrTrendsService = {
  async getLsrTrendProfiles(): Promise<any> {
    try {
      const response = await apiClient.get('/lsr-trends');
      return response.data;
    } catch (error) {
      console.warn('LSR trend profiles API call failed:', error);
      return { total_lsr_rules: 0, lsr_profiles: [] };
    }
  },

  async getLsrTrendProfileByRule(rule: string): Promise<any> {
    try {
      const response = await apiClient.get(`/lsr-trends/${encodeURIComponent(rule)}`);
      return response.data;
    } catch (error) {
      console.warn(`LSR trend profile call for ${rule} failed:`, error);
      return null;
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

/**
 * STAGE 29 EARLY WARNINGS SERVICE (GET /api/early-warnings)
 */
export const earlyWarningsService = {
  async getEarlyWarnings(): Promise<any> {
    try {
      const response = await apiClient.get('/early-warnings');
      return response.data;
    } catch (error) {
      console.warn('Backend early warnings unreachable, attempting direct FastAPI call:', (error as Error).message);
      try {
        const directRes = await fetch('http://127.0.0.1:8000/api/v1/early-warnings');
        if (directRes.ok) return await directRes.json();
      } catch (e) {
        console.warn('Direct FastAPI call failed:', (e as Error).message);
      }
      return { total_warnings: 0, high_priority_count: 0, early_warning_count: 0, watch_count: 0, warnings: [] };
    }
  },

  async getEarlyWarningById(warningId: string): Promise<any> {
    try {
      const response = await apiClient.get(`/early-warnings/${warningId}`);
      return response.data;
    } catch (error) {
      console.warn(`Backend early warning for ${warningId} unreachable, attempting direct FastAPI call:`, (error as Error).message);
      try {
        const directRes = await fetch(`http://127.0.0.1:8000/api/v1/early-warnings/${encodeURIComponent(warningId)}`);
        if (directRes.ok) return await directRes.json();
      } catch (e) {
        console.warn('Direct FastAPI call failed:', (e as Error).message);
      }
      return null;
    }
  }
};

/**
 * STAGE 30 PRIORITIES SERVICE (GET /api/priorities)
 */
export const prioritiesService = {
  async getPriorities(): Promise<any> {
    try {
      const response = await apiClient.get('/priorities');
      return response.data;
    } catch (error) {
      console.warn('Backend priorities unreachable, attempting direct FastAPI call:', (error as Error).message);
      try {
        const directRes = await fetch('http://127.0.0.1:8000/api/v1/priorities');
        if (directRes.ok) return await directRes.json();
      } catch (e) {
        console.warn('Direct FastAPI call failed:', (e as Error).message);
      }
      return { total_priorities: 0, critical_count: 0, high_count: 0, medium_count: 0, priorities: [] };
    }
  },

  async getPriorityById(priorityId: string): Promise<any> {
    try {
      const response = await apiClient.get(`/priorities/${priorityId}`);
      return response.data;
    } catch (error) {
      console.warn(`Backend priority for ${priorityId} unreachable, attempting direct FastAPI call:`, (error as Error).message);
      try {
        const directRes = await fetch(`http://127.0.0.1:8000/api/v1/priorities/${encodeURIComponent(priorityId)}`);
        if (directRes.ok) return await directRes.json();
      } catch (e) {
        console.warn('Direct FastAPI call failed:', (e as Error).message);
      }
      return null;
    }
  }
};

/**
 * STAGE 31 RISK MATRIX SERVICE (GET /api/risk-matrix)
 */
export const riskMatrixService = {
  async getRiskMatrix(): Promise<any> {
    try {
      const response = await apiClient.get('/risk-matrix');
      return response.data;
    } catch (error) {
      console.warn('Backend risk matrix unreachable, attempting direct FastAPI call:', (error as Error).message);
      try {
        const directRes = await fetch('http://127.0.0.1:8000/api/v1/risk-matrix');
        if (directRes.ok) return await directRes.json();
      } catch (e) {
        console.warn('Direct FastAPI call failed:', (e as Error).message);
      }
      return { total_items: 0, critical_priority_count: 0, high_potential_rare_count: 0, frequent_lower_potential_count: 0, low_priority_monitor_count: 0, matrix_items: [] };
    }
  },

  async getRiskMatrixItemById(matrixItemId: string): Promise<any> {
    try {
      const response = await apiClient.get(`/risk-matrix/${matrixItemId}`);
      return response.data;
    } catch (error) {
      console.warn(`Backend risk matrix item for ${matrixItemId} unreachable, attempting direct FastAPI call:`, (error as Error).message);
      try {
        const directRes = await fetch(`http://127.0.0.1:8000/api/v1/risk-matrix/${encodeURIComponent(matrixItemId)}`);
        if (directRes.ok) return await directRes.json();
      } catch (e) {
        console.warn('Direct FastAPI call failed:', (e as Error).message);
      }
      return null;
    }
  }
};

/**
 * STAGE 32 BOW-TIE MAPPING SERVICE (GET /api/bow-ties/:report_id)
 */
export const bowTieService = {
  async getBowTieByReportId(reportId: string): Promise<any> {
    try {
      const response = await apiClient.get(`/bow-ties/${reportId}`);
      return response.data;
    } catch (error) {
      console.warn(`Backend Bow-Tie for ${reportId} unreachable, attempting direct FastAPI call:`, (error as Error).message);
      try {
        const directRes = await fetch(`http://127.0.0.1:8000/api/v1/bow-ties/${encodeURIComponent(reportId)}`);
        if (directRes.ok) return await directRes.json();
      } catch (e) {
        console.warn('Direct FastAPI call failed:', (e as Error).message);
      }
      return null;
    }
  }
};

/**
 * STAGE 33 HUMAN ANALYST FEEDBACK SERVICE
 */
export const feedbackService = {
  async submitFeedback(payload: any): Promise<any> {
    try {
      const response = await apiClient.post('/feedback', payload);
      return response.data;
    } catch (error) {
      console.warn('Backend feedback endpoint unreachable, attempting direct FastAPI call:', (error as Error).message);
      try {
        const directRes = await fetch('http://127.0.0.1:8000/api/v1/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (directRes.ok) return await directRes.json();
      } catch (e) {
        console.warn('Direct FastAPI feedback call failed:', (e as Error).message);
      }
      return null;
    }
  },

  async getFeedbackByReportId(reportId: string): Promise<any[]> {
    try {
      const response = await apiClient.get(`/feedback/reports/${reportId}`);
      return response.data || [];
    } catch (error) {
      console.warn(`Backend feedback history for ${reportId} unreachable:`, (error as Error).message);
      return [];
    }
  },

  async getFeedbackStats(): Promise<any> {
    try {
      const response = await apiClient.get('/feedback/stats');
      return response.data;
    } catch (error) {
      console.warn('Backend feedback stats unreachable:', (error as Error).message);
      return { total_feedback: 0, accepted_count: 0, corrected_count: 0, rejected_count: 0, accept_rate: 1.0, correction_rate: 0.0, reject_rate: 0.0 };
    }
  },

  async updateFeedbackStatus(feedbackId: string, status: string): Promise<any> {
    try {
      const response = await apiClient.patch(`/feedback/${feedbackId}/status`, { status });
      return response.data;
    } catch (error) {
      console.warn(`Failed to update feedback status for ${feedbackId}:`, (error as Error).message);
      return null;
    }
  }
};

/**
 * STAGE 34 CONFIDENCE-CALIBRATED TRIAGE SERVICE
 */
export const triageService = {
  async evaluateTriage(payload: any): Promise<any> {
    try {
      const response = await apiClient.post('/triage', payload);
      return response.data;
    } catch (error) {
      console.warn('Backend triage endpoint unreachable, attempting direct FastAPI call:', (error as Error).message);
      try {
        const directRes = await fetch('http://127.0.0.1:8000/api/v1/triage', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (directRes.ok) return await directRes.json();
      } catch (e) {
        console.warn('Direct FastAPI triage call failed:', (e as Error).message);
      }
      return null;
    }
  }
};

/**
 * STAGE 35 MULTILINGUAL TEXT NORMALIZATION SERVICE
 */
export const multilingualService = {
  async normalizeText(text: string): Promise<any> {
    try {
      const response = await apiClient.post('/text/normalize', { text });
      return response.data;
    } catch (error) {
      console.warn('Backend text normalize unreachable, attempting direct FastAPI call:', (error as Error).message);
      try {
        const directRes = await fetch('http://127.0.0.1:8000/api/v1/text/normalize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });
        if (directRes.ok) return await directRes.json();
      } catch (e) {
        console.warn('Direct FastAPI text normalize call failed:', (e as Error).message);
      }
      return null;
    }
  }
};

/**
 * STAGE 43 END-TO-END INTELLIGENCE SERVICE
 */
export const intelligenceService = {
  async analyzeIntelligence(data: {
    incident_text: string;
    site?: string;
    activity?: string;
    incident_id?: string;
  }): Promise<Stage43IntelligenceResponse> {
    try {
      const response = await apiClient.post('/intelligence/analyze', data);
      return response.data;
    } catch (error) {
      console.warn('Backend intelligence service unreachable, attempting direct FastAPI call:', (error as Error).message);
      try {
        const directRes = await fetch('http://127.0.0.1:8000/api/v1/intelligence/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        if (directRes.ok) return await directRes.json();
      } catch (e) {
        console.warn('Direct FastAPI intelligence call failed:', (e as Error).message);
      }
      throw error;
    }
  }
};