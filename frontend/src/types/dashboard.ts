export interface DashboardKpis {
  totalReports: number;
  totalReportsTrend: number; // e.g. +12%
  sifPotentialCount: number;
  sifPotentialPercentage: number;
  sifTrend: number; // e.g. -4%
  criticalPrecursorsCount: number;
  activeInterventionsCount: number;
  averageResolutionDays: number;
}

export interface HighRiskSiteSummary {
  site: string;
  code: string;
  totalReports: number;
  sifCount: number;
  sifRate: number; // percentage
  topRule: string;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  coordinates?: [number, number]; // [lat, lng]
}

export interface HighRiskActivitySummary {
  activity: string;
  totalReports: number;
  sifCount: number;
  sifRate: number;
  primaryHazard: string;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export interface LifeSavingRuleDistribution {
  rule: string;
  count: number;
  sifCount: number;
  percentage: number;
  trend: 'increasing' | 'stable' | 'decreasing';
  iconKey?: string;
}

export interface PrecursorFailureMatrixItem {
  activity: string;
  barrierFailure: string;
  hazard: string;
  incidentCount: number;
  sifRate: number;
  riskScore: number;
  rule: string;
}

export interface TrendDataPoint {
  date: string; // e.g. "Jan", "Feb", "2026-W08"
  totalReports: number;
  sifPotential: number;
  nonSif: number;
  nearMisses: number;
}

export interface DashboardOverviewResponse {
  kpis: DashboardKpis;
  highRiskSites: HighRiskSiteSummary[];
  highRiskActivities: HighRiskActivitySummary[];
  topLifeSavingRules: LifeSavingRuleDistribution[];
  precursorFailures: PrecursorFailureMatrixItem[];
  trends: TrendDataPoint[];
  lastUpdated: string;
}
