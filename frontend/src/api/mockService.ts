import { 
  MOCK_REPORTS, 
  MOCK_PATTERNS, 
  MOCK_INTERVENTIONS, 
  MOCK_AUDIT_LOGS, 
  MOCK_DASHBOARD_DATA 
} from './mockData';
import type { SafetyReport, SifAnalysisResult, CreateReportPayload, ReportFilterOptions } from '../types/reports';
import type { User, LoginCredentials, AuthResponse, UserRole } from '../types/auth';
import type { PrecursorPattern } from '../types/patterns';
import type { HSEIntervention } from '../types/interventions';
import type { AuditLogEntry, AuditActionType } from '../types/audit';
import type { DashboardOverviewResponse } from '../types/dashboard';

// In-memory working copies for mock CRUD operations
let reports = [...MOCK_REPORTS];
const patterns = [...MOCK_PATTERNS];
let interventions = [...MOCK_INTERVENTIONS];
let auditLogs = [...MOCK_AUDIT_LOGS];

// Mock latency simulator (100ms - 300ms)
const delay = (ms: number = 180) => new Promise(resolve => setTimeout(resolve, ms));

// Helper function to append live audit log entries
function appendAuditLog(
  action: AuditActionType,
  entityType: AuditLogEntry['entityType'],
  entityId: string,
  details: string,
  user?: { id: string; name: string; role: string },
  changesSummary?: { before?: string; after?: string }
) {
  const newEntry: AuditLogEntry = {
    id: `AUD-${Date.now().toString().slice(-4)}`,
    timestamp: new Date().toISOString(),
    userId: user?.id || 'USR-001',
    userName: user?.name || 'Debojit Phukan',
    userRole: user?.role || 'HSE Analyst',
    action,
    entityType,
    entityId,
    ipAddress: '10.14.22.45',
    status: 'SUCCESS',
    details,
    changesSummary,
  };
  auditLogs = [newEntry, ...auditLogs];
}

export const mockAuthService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    await delay();
    const role: UserRole = credentials.role || 'HSE Analyst';
    const mockUser: User = {
      id: 'USR-001',
      name: role === 'Admin' ? 'Ananya Roy (Admin)' : role === 'HSE Manager' ? 'Rajesh Sharma (HSE Lead)' : role === 'HSE Analyst' ? 'Debojit Phukan (Analyst)' : 'Site Field Auditor (Viewer)',
      email: credentials.email || 'officer@oilindia.in',
      role,
      department: 'Corporate HSE & Process Safety Directorate',
      site: 'Duliajan Central Complex',
    };
    const token = 'mock-jwt-token-sih26165-' + Date.now();

    // LIVE AUDIT LOG: Record user login event
    appendAuditLog(
      'USER_LOGIN',
      'AUTH',
      mockUser.id,
      `User ${mockUser.name} authenticated with role ${mockUser.role} via Secure JWT`,
      { id: mockUser.id, name: mockUser.name, role: mockUser.role }
    );

    return { token, user: mockUser };
  },

  async getCurrentUser(): Promise<User> {
    await delay(100);
    const stored = localStorage.getItem('sih_oil_auth_user');
    if (stored) {
      return JSON.parse(stored);
    }
    return {
      id: 'USR-001',
      name: 'Debojit Phukan',
      email: 'debojit.p@oilindia.in',
      role: 'HSE Analyst',
      department: 'Process Safety Division',
      site: 'Duliajan Central Complex',
    };
  }
};

export const mockReportsService = {
  async getReports(filters?: ReportFilterOptions): Promise<{ data: SafetyReport[]; total: number }> {
    await delay();
    let result = [...reports];

    if (filters?.search) {
      const q = filters.search.toLowerCase();
      result = result.filter(r =>
        r.id.toLowerCase().includes(q) ||
        r.title.toLowerCase().includes(q) ||
        r.description.toLowerCase().includes(q) ||
        r.site.toLowerCase().includes(q) ||
        r.activity.toLowerCase().includes(q) ||
        r.life_saving_rule.toLowerCase().includes(q)
      );
    }

    if (filters?.type && filters.type !== 'ALL') {
      result = result.filter(r => r.type === filters.type);
    }

    if (filters?.site && filters.site !== 'ALL') {
      result = result.filter(r => r.site === filters.site);
    }

    if (filters?.activity && filters.activity !== 'ALL') {
      result = result.filter(r => r.activity === filters.activity);
    }

    if (filters?.sif_status && filters.sif_status !== 'ALL') {
      result = result.filter(r => r.sif_status === filters.sif_status);
    }

    if (filters?.priority && filters.priority !== 'ALL') {
      result = result.filter(r => r.priority === filters.priority);
    }

    if (filters?.life_saving_rule && filters.life_saving_rule !== 'ALL') {
      result = result.filter(r => r.life_saving_rule === filters.life_saving_rule);
    }

    if (filters?.analysis_status && filters.analysis_status !== 'ALL') {
      result = result.filter(r => r.analysis_status === filters.analysis_status);
    }

    // Sorting
    const sortBy = filters?.sortBy || 'date';
    const sortOrder = filters?.sortOrder || 'desc';
    result.sort((a, b) => {
      const valA = a[sortBy] ?? '';
      const valB = b[sortBy] ?? '';
      if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
      if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return {
      data: result,
      total: result.length,
    };
  },

  async getReportById(id: string): Promise<SafetyReport> {
    await delay();
    const report = reports.find(r => r.id === id);
    if (!report) {
      throw new Error(`Report ${id} not found`);
    }
    return report;
  },

  async createReport(payload: CreateReportPayload): Promise<SafetyReport> {
    await delay(300);
    const newId = `OIL-2026-R${String(reports.length + 1).padStart(3, '0')}`;
    const now = new Date().toISOString();

    const newReport: SafetyReport = {
      id: newId,
      title: payload.title,
      type: payload.type,
      date: payload.date || now,
      site: payload.site,
      department: payload.department,
      location_detail: payload.location_detail,
      activity: payload.activity,
      reporter_name: payload.reporter_name,
      description: payload.description,
      immediate_actions_taken: payload.immediate_actions_taken,
      sif_status: 'PENDING_ANALYSIS',
      sif_score: 0,
      life_saving_rule: 'Pending Evaluation',
      priority: payload.priority || 'MEDIUM',
      analysis_status: 'PENDING',
      created_at: now,
      updated_at: now,
      investigation_status: 'Open',
    };

    reports = [newReport, ...reports];

    // LIVE AUDIT LOG: Record report creation
    appendAuditLog(
      'REPORT_CREATED',
      'REPORT',
      newId,
      `Submitted ${payload.type} "${payload.title}" for ${payload.site} (${payload.department})`,
      { id: 'USR-001', name: payload.reporter_name, role: 'Field Reporter' }
    );

    return newReport;
  },

  async updateReport(id: string, updates: Partial<SafetyReport>): Promise<SafetyReport> {
    await delay();
    const index = reports.findIndex(r => r.id === id);
    if (index === -1) throw new Error(`Report ${id} not found`);

    const original = reports[index];
    const updated = {
      ...original,
      ...updates,
      updated_at: new Date().toISOString(),
    };
    reports[index] = updated;

    // LIVE AUDIT LOG: Record report update
    appendAuditLog(
      'REPORT_UPDATED',
      'REPORT',
      id,
      `Updated report ${id} details and investigation status to "${updated.investigation_status}"`
    );

    return updated;
  },

  async deleteReport(id: string): Promise<{ success: boolean }> {
    await delay();
    reports = reports.filter(r => r.id !== id);

    // LIVE AUDIT LOG: Record report deletion
    appendAuditLog(
      'REPORT_DELETED',
      'REPORT',
      id,
      `Deleted report ${id} from active register`
    );

    return { success: true };
  },

  async analyzeReport(id: string): Promise<SifAnalysisResult> {
    await delay(600);
    const report = reports.find(r => r.id === id);
    if (!report) throw new Error(`Report ${id} not found`);

    const text = report.description.toLowerCase();
    let isSif = false;
    const matchedRules: { name: string; score: number }[] = [];
    let hazard = 'General Industrial Operation';
    let barrier = 'Standard Procedural Control';
    let consequence = 'Minor Near-Miss';
    let priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' = 'LOW';
    let score = 0.25;

    // Support multiple rules (e.g. Energy Isolation + Hot Work + Confined Space)
    if (text.includes('breaker') || text.includes('electric') || text.includes('voltage') || text.includes('loto') || text.includes('isolation')) {
      isSif = true;
      matchedRules.push({ name: 'Energy Isolation', score: 0.96 });
      hazard = 'High-Voltage / Hazardous Energy';
      barrier = 'Zero-Energy Verification & Lockout';
      consequence = 'Electrocution & Arc Flash Fatality';
      priority = 'CRITICAL';
      score = 0.94;
    }
    if (text.includes('weld') || text.includes('spark') || text.includes('flame') || text.includes('cutting') || text.includes('fire')) {
      isSif = true;
      matchedRules.push({ name: 'Hot Work', score: 0.94 });
      hazard = 'Flammable Gas / Hydrocarbon Vapor';
      barrier = 'Spark Habitat & Continuous Gas Monitoring';
      consequence = 'Vapor Cloud Explosion';
      priority = 'CRITICAL';
      score = Math.max(score, 0.89);
    }
    if (text.includes('tank') || text.includes('confined') || text.includes('h2s') || text.includes('toxic') || text.includes('asphyxiat')) {
      isSif = true;
      matchedRules.push({ name: 'Confined Space', score: 0.98 });
      hazard = 'Stratified H2S & Low Oxygen';
      barrier = 'Multi-Level Atmospheric Testing';
      consequence = 'Fatal Gas Inhalation';
      priority = 'CRITICAL';
      score = Math.max(score, 0.95);
    }
    if (text.includes('crane') || text.includes('sling') || text.includes('lifting') || text.includes('tubular') || text.includes('hoist')) {
      isSif = true;
      matchedRules.push({ name: 'Safe Mechanical Lifting', score: 0.95 });
      hazard = 'Suspended Heavy Load (Kinetic/Gravitational)';
      barrier = 'Rigging Inspection & Exclusion Radius';
      consequence = 'Crush Impact / Struck-by Fatality';
      priority = 'CRITICAL';
      score = Math.max(score, 0.91);
    }
    if (text.includes('height') || text.includes('scaffold') || text.includes('fall') || text.includes('derrick') || text.includes('tie-off')) {
      isSif = true;
      matchedRules.push({ name: 'Working at Height', score: 0.93 });
      hazard = 'Elevated Fall Risk (> 1.8m)';
      barrier = '100% Dual-Lanyard Tie-Off Anchor';
      consequence = 'Fatal Fall from Elevation';
      priority = priority === 'CRITICAL' ? 'CRITICAL' : 'HIGH';
      score = Math.max(score, 0.87);
    }

    if (matchedRules.length === 0) {
      matchedRules.push({ name: 'Work Authorization', score: 0.40 });
    }

    const aiResult: SifAnalysisResult = {
      report_id: id,
      sif: {
        label: isSif ? 'SIF_POTENTIAL' : 'NON_SIF',
        score: isSif ? score : 0.15,
      },
      life_saving_rules: matchedRules,
      precursors: {
        activity: report.activity,
        hazard,
        barrier_failure: barrier,
        potential_consequence: consequence,
      },
      explanation: `AI NLP pipeline evaluated narrative for high-energy hazard indicators and barrier integrity. Identified ${matchedRules.map(r => r.name).join(' & ')} compliance vulnerabilities with hazard "${hazard}". Classified as ${isSif ? 'SIF_POTENTIAL' : 'NON_SIF'} decision support advisory.`,
      patterns: isSif ? [`PAT-00${Math.floor(Math.random() * 5) + 1}: Precursor Cluster`] : [],
      priority,
      analyzed_at: new Date().toISOString(),
      model_version: 'SIF-NLP-v2.4',
    };

    report.sif_status = aiResult.sif.label;
    report.sif_score = aiResult.sif.score;
    report.life_saving_rule = matchedRules[0].name;
    report.priority = priority;
    report.analysis_status = 'COMPLETED';
    report.ai_result = aiResult;
    report.updated_at = new Date().toISOString();

    // LIVE AUDIT LOG: Record AI analysis completion
    appendAuditLog(
      'AI_ANALYSIS_COMPLETED',
      'AI_MODEL',
      id,
      `NLP Pipeline classified report ${id} as ${aiResult.sif.label} (${(aiResult.sif.score * 100).toFixed(0)}% confidence, Rule: ${matchedRules.map(r => r.name).join(', ')})`
    );

    return aiResult;
  },

  async getAiResults(reportId: string): Promise<SifAnalysisResult> {
    await delay();
    const report = reports.find(r => r.id === reportId);
    if (!report || !report.ai_result) {
      throw new Error(`AI results for report ${reportId} not found`);
    }
    return report.ai_result;
  }
};

export const mockDashboardService = {
  async getOverview(): Promise<DashboardOverviewResponse> {
    await delay();
    return MOCK_DASHBOARD_DATA;
  },

  async getSites() {
    await delay();
    return MOCK_DASHBOARD_DATA.highRiskSites;
  },

  async getActivities() {
    await delay();
    return MOCK_DASHBOARD_DATA.highRiskActivities;
  },

  async getLifeSavingRules() {
    await delay();
    return MOCK_DASHBOARD_DATA.topLifeSavingRules;
  },

  async getPrecursors() {
    await delay();
    return MOCK_DASHBOARD_DATA.precursorFailures;
  },

  async getTrends() {
    await delay();
    return MOCK_DASHBOARD_DATA.trends;
  },
};

export const mockPatternsService = {
  async getPatterns(): Promise<PrecursorPattern[]> {
    await delay();
    return patterns;
  },

  async getPatternById(id: string): Promise<PrecursorPattern> {
    await delay();
    const pattern = patterns.find(p => p.id === id);
    if (!pattern) throw new Error(`Pattern ${id} not found`);
    return pattern;
  }
};

export const mockInterventionsService = {
  async getInterventions(): Promise<HSEIntervention[]> {
    await delay();
    return interventions;
  },

  async updateIntervention(id: string, updates: Partial<HSEIntervention>): Promise<HSEIntervention> {
    await delay();
    const index = interventions.findIndex(i => i.id === id);
    if (index === -1) throw new Error(`Intervention ${id} not found`);
    const original = interventions[index];
    const updated = { ...original, ...updates };
    interventions[index] = updated;

    // LIVE AUDIT LOG: Record intervention status change
    appendAuditLog(
      'INTERVENTION_STATUS_UPDATED',
      'INTERVENTION',
      id,
      `Updated intervention ${id} (${updated.title}) status from "${original.status}" to "${updated.status}"`,
      undefined,
      { before: `Status: ${original.status}`, after: `Status: ${updated.status}` }
    );

    return updated;
  },

  async createIntervention(newIntervention: Omit<HSEIntervention, 'id' | 'createdDate'>): Promise<HSEIntervention> {
    await delay();
    const id = `INT-2026-${String(interventions.length + 1).padStart(3, '0')}`;
    const created: HSEIntervention = {
      ...newIntervention,
      id,
      createdDate: new Date().toISOString().split('T')[0],
    };
    interventions = [created, ...interventions];

    // LIVE AUDIT LOG: Record intervention creation
    appendAuditLog(
      'INTERVENTION_CREATED',
      'INTERVENTION',
      id,
      `Authorized HSE intervention ${id} "${created.title}" targeted for ${created.targetSite}`
    );

    return created;
  }
};

export const mockAuditService = {
  async getAuditLogs(): Promise<AuditLogEntry[]> {
    await delay();
    return auditLogs;
  }
};
