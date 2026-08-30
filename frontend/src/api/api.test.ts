import { describe, it, expect } from 'vitest';
import { dashboardService, reportsService, auditService } from './index';

describe('API Contract & Mock Service Integration Tests', () => {
  it('GET /api/dashboard/overview returns valid DashboardOverviewResponse schema', async () => {
    const overview = await dashboardService.getOverview();

    // Verify KPI metrics
    expect(overview).toHaveProperty('kpis');
    expect(overview.kpis).toHaveProperty('totalReports');
    expect(overview.kpis).toHaveProperty('sifPotentialCount');
    expect(overview.kpis).toHaveProperty('sifPotentialPercentage');
    expect(typeof overview.kpis.totalReports).toBe('number');
    expect(overview.kpis.totalReports).toBeGreaterThan(0);

    // Verify high-risk sites array
    expect(Array.isArray(overview.highRiskSites)).toBe(true);
    expect(overview.highRiskSites.length).toBeGreaterThan(0);
    const site = overview.highRiskSites[0];
    expect(site).toHaveProperty('site');
    expect(site).toHaveProperty('sifRate');
    expect(site).toHaveProperty('riskLevel');

    // Verify high-risk activities array
    expect(Array.isArray(overview.highRiskActivities)).toBe(true);
    expect(overview.highRiskActivities.length).toBeGreaterThan(0);

    // Verify top Life-Saving Rules
    expect(Array.isArray(overview.topLifeSavingRules)).toBe(true);
    expect(overview.topLifeSavingRules.length).toBeGreaterThan(0);

    // Verify Trends
    expect(Array.isArray(overview.trends)).toBe(true);
    expect(overview.trends.length).toBeGreaterThan(0);
  });

  it('GET /api/reports returns valid paginated reports response matching schema', async () => {
    const res = await reportsService.getReports();

    expect(res).toHaveProperty('data');
    expect(res).toHaveProperty('total');
    expect(Array.isArray(res.data)).toBe(true);
    expect(res.data.length).toBeGreaterThan(0);

    const report = res.data[0];
    expect(report).toHaveProperty('id');
    expect(report).toHaveProperty('title');
    expect(report).toHaveProperty('type');
    expect(report).toHaveProperty('date');
    expect(report).toHaveProperty('site');
    expect(report).toHaveProperty('activity');
    expect(report).toHaveProperty('sif_status');
    expect(report).toHaveProperty('sif_score');
    expect(report).toHaveProperty('life_saving_rule');
    expect(report).toHaveProperty('priority');
    expect(report).toHaveProperty('analysis_status');
  });

  it('GET /api/reports/:id returns single report with full AI analysis metadata', async () => {
    const report = await reportsService.getReportById('OIL-2026-R001');

    expect(report.id).toBe('OIL-2026-R001');
    expect(report.ai_result).toBeDefined();
    if (report.ai_result) {
      expect(report.ai_result).toHaveProperty('sif');
      expect(report.ai_result).toHaveProperty('life_saving_rules');
      expect(Array.isArray(report.ai_result.life_saving_rules)).toBe(true);
      expect(report.ai_result).toHaveProperty('precursors');
      expect(report.ai_result.precursors).toHaveProperty('activity');
      expect(report.ai_result.precursors).toHaveProperty('hazard');
      expect(report.ai_result.precursors).toHaveProperty('barrier_failure');
      expect(report.ai_result.precursors).toHaveProperty('potential_consequence');
      expect(report.ai_result).toHaveProperty('explanation');
      expect(report.ai_result).toHaveProperty('priority');
    }
  });

  it('POST /api/reports creates a new report and appends to live audit log', async () => {
    const initialLogs = await auditService.getAuditLogs();
    const initialCount = initialLogs.length;

    const newReport = await reportsService.createReport({
      title: 'Automated Integration Test Report',
      type: 'Near-Miss',
      date: '2026-03-01',
      site: 'Duliajan Central Complex',
      department: 'Drilling',
      activity: 'Rig Floor Operations',
      reporter_name: 'Test Rig Inspector',
      description: 'Crane sling slack observed near rotary table',
    });

    expect(newReport.id).toMatch(/^OIL-2026-R\d+$/);

    // Verify live audit log appended
    const updatedLogs = await auditService.getAuditLogs();
    expect(updatedLogs.length).toBe(initialCount + 1);
    expect(updatedLogs[0].action).toBe('REPORT_CREATED');
    expect(updatedLogs[0].entityId).toBe(newReport.id);
  });
});
