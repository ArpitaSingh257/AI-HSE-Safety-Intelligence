import { SafetyReport } from '../models/SafetyReport';
import { Intervention } from '../models/Intervention';
import { SifAnalysisResult } from '../models/SifAnalysisResult';

// Rough, static lat/lng lookup for known site display names, purely so the
// map view has something to plot. Falls back to undefined (no marker) for
// any site name the platform hasn't seen before - it's not required data.
const SITE_COORDINATES: Record<string, [number, number]> = {
  Duliajan: [27.3596, 95.3197],
  Moran: [27.1852, 94.9312],
  Naharkatiya: [27.2833, 95.3333],
  Digboi: [27.3888, 95.6267],
};

function riskLevelFromRate(rate: number): 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' {
  if (rate >= 30) return 'CRITICAL';
  if (rate >= 20) return 'HIGH';
  if (rate >= 10) return 'MEDIUM';
  return 'LOW';
}

function coordinatesFor(site: string): [number, number] | undefined {
  const key = Object.keys(SITE_COORDINATES).find((k) => site.toLowerCase().includes(k.toLowerCase()));
  return key ? SITE_COORDINATES[key] : undefined;
}

async function countInRange(from: Date, to: Date, extraMatch: Record<string, unknown> = {}) {
  return SafetyReport.countDocuments({ date: { $gte: from, $lt: to }, ...extraMatch });
}

function percentChange(current: number, previous: number): number {
  if (previous === 0) return current === 0 ? 0 : 100;
  return Math.round(((current - previous) / previous) * 1000) / 10;
}

export async function getKpis() {
  const now = new Date();
  const THIRTY_DAYS = 30 * 24 * 60 * 60 * 1000;
  const last30Start = new Date(now.getTime() - THIRTY_DAYS);
  const prev30Start = new Date(now.getTime() - 2 * THIRTY_DAYS);

  const [totalReports, sifPotentialCount, criticalPrecursorsCount, activeInterventionsCount] = await Promise.all([
    SafetyReport.countDocuments({}),
    SafetyReport.countDocuments({ sif_status: 'SIF_POTENTIAL' }),
    SafetyReport.countDocuments({ sif_status: 'SIF_POTENTIAL', priority: 'CRITICAL' }),
    Intervention.countDocuments({ status: { $ne: 'CLOSED' } }),
  ]);

  const [reportsLast30, reportsPrev30, sifLast30, sifPrev30] = await Promise.all([
    countInRange(last30Start, now),
    countInRange(prev30Start, last30Start),
    countInRange(last30Start, now, { sif_status: 'SIF_POTENTIAL' }),
    countInRange(prev30Start, last30Start, { sif_status: 'SIF_POTENTIAL' }),
  ]);

  const sifPotentialPercentage = totalReports > 0 ? Math.round((sifPotentialCount / totalReports) * 1000) / 1000 : 0;

  const closedInterventions = await Intervention.find({
    status: 'CLOSED',
    completionDate: { $ne: null },
  }).lean();
  const resolutionDays = closedInterventions
    .map((i) => (i.completionDate ? (new Date(i.completionDate).getTime() - new Date(i.createdDate).getTime()) / 86400000 : null))
    .filter((d): d is number => d !== null && d >= 0);
  const averageResolutionDays =
    resolutionDays.length > 0
      ? Math.round((resolutionDays.reduce((a, b) => a + b, 0) / resolutionDays.length) * 10) / 10
      : 0;

  return {
    totalReports,
    totalReportsTrend: percentChange(reportsLast30, reportsPrev30),
    sifPotentialCount,
    sifPotentialPercentage,
    sifTrend: percentChange(sifLast30, sifPrev30),
    criticalPrecursorsCount,
    activeInterventionsCount,
    averageResolutionDays,
  };
}

export async function getHighRiskSites() {
  const agg = await SafetyReport.aggregate([
    {
      $group: {
        _id: '$site',
        totalReports: { $sum: 1 },
        sifCount: { $sum: { $cond: [{ $eq: ['$sif_status', 'SIF_POTENTIAL'] }, 1, 0] } },
        rules: { $push: { $cond: [{ $eq: ['$sif_status', 'SIF_POTENTIAL'] }, '$life_saving_rule', '$$REMOVE'] } },
      },
    },
    { $sort: { totalReports: -1 } },
  ]);

  return agg.map((row: any, idx: number) => {
    const sifRate = row.totalReports > 0 ? Math.round((row.sifCount / row.totalReports) * 1000) / 10 : 0;
    const ruleCounts: Record<string, number> = {};
    for (const r of row.rules || []) ruleCounts[r] = (ruleCounts[r] || 0) + 1;
    const topRule = Object.entries(ruleCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A';

    return {
      site: row._id,
      code: `SITE-${String(idx + 1).padStart(2, '0')}`,
      totalReports: row.totalReports,
      sifCount: row.sifCount,
      sifRate,
      topRule,
      riskLevel: riskLevelFromRate(sifRate),
      coordinates: coordinatesFor(row._id || ''),
    };
  });
}

export async function getHighRiskActivities() {
  const agg = await SafetyReport.aggregate([
    {
      $group: {
        _id: '$activity',
        totalReports: { $sum: 1 },
        sifCount: { $sum: { $cond: [{ $eq: ['$sif_status', 'SIF_POTENTIAL'] }, 1, 0] } },
      },
    },
    { $sort: { totalReports: -1 } },
  ]);

  // Pull the most common hazard per activity from SifAnalysisResult so the
  // "primaryHazard" field isn't just a placeholder.
  const hazardAgg = await SifAnalysisResult.aggregate([
    { $lookup: { from: 'safetyreports', localField: 'reportId', foreignField: '_id', as: 'report' } },
    { $unwind: '$report' },
    { $group: { _id: { activity: '$report.activity', hazard: '$precursors.hazard' }, count: { $sum: 1 } } },
    { $sort: { count: -1 } },
  ]);
  const hazardByActivity = new Map<string, string>();
  for (const h of hazardAgg) {
    if (!hazardByActivity.has(h._id.activity)) hazardByActivity.set(h._id.activity, h._id.hazard);
  }

  return agg.map((row: any) => {
    const sifRate = row.totalReports > 0 ? Math.round((row.sifCount / row.totalReports) * 1000) / 10 : 0;
    return {
      activity: row._id,
      totalReports: row.totalReports,
      sifCount: row.sifCount,
      sifRate,
      primaryHazard: hazardByActivity.get(row._id) || 'Not yet analyzed',
      riskLevel: riskLevelFromRate(sifRate),
    };
  });
}

export async function getTopLifeSavingRules() {
  const now = Date.now();
  const THIRTY_DAYS = 30 * 24 * 60 * 60 * 1000;

  const agg = await SafetyReport.aggregate([
    { $match: { life_saving_rule: { $nin: ['Pending Evaluation', ''] } } },
    {
      $group: {
        _id: '$life_saving_rule',
        count: { $sum: 1 },
        sifCount: { $sum: { $cond: [{ $eq: ['$sif_status', 'SIF_POTENTIAL'] }, 1, 0] } },
        dates: { $push: '$date' },
      },
    },
    { $sort: { count: -1 } },
    { $limit: 10 },
  ]);

  return agg.map((row: any) => {
    const recentCount = row.dates.filter((d: Date) => now - new Date(d).getTime() <= THIRTY_DAYS).length;
    const olderCount = row.dates.length - recentCount;
    let trend: 'increasing' | 'stable' | 'decreasing' = 'stable';
    if (olderCount === 0 && recentCount > 0) trend = 'increasing';
    else if (olderCount > 0) {
      const ratio = recentCount / olderCount;
      if (ratio >= 1.3) trend = 'increasing';
      else if (ratio <= 0.7) trend = 'decreasing';
    }

    return {
      rule: row._id,
      count: row.count,
      sifCount: row.sifCount,
      percentage: row.count > 0 ? Math.round((row.sifCount / row.count) * 1000) / 10 : 0,
      trend,
    };
  });
}

export async function getPrecursorFailures() {
  const agg = await SifAnalysisResult.aggregate([
    { $lookup: { from: 'safetyreports', localField: 'reportId', foreignField: '_id', as: 'report' } },
    { $unwind: '$report' },
    {
      $group: {
        _id: {
          activity: '$report.activity',
          barrierFailure: '$precursors.barrier_failure',
          hazard: '$precursors.hazard',
          rule: { $arrayElemAt: ['$life_saving_rules.name', 0] },
        },
        incidentCount: { $sum: 1 },
        avgScore: { $avg: '$sif.score' },
      },
    },
    { $sort: { incidentCount: -1 } },
    { $limit: 10 },
  ]);

  return agg.map((row: any) => ({
    activity: row._id.activity,
    barrierFailure: row._id.barrierFailure,
    hazard: row._id.hazard,
    incidentCount: row.incidentCount,
    sifRate: Math.round(row.avgScore * 1000) / 10,
    riskScore: Math.round(row.avgScore * 100),
    rule: row._id.rule || 'Unclassified',
  }));
}

export async function getTrends() {
  const now = new Date();
  const months: { start: Date; end: Date; label: string }[] = [];
  for (let i = 5; i >= 0; i--) {
    const start = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const end = new Date(now.getFullYear(), now.getMonth() - i + 1, 1);
    months.push({ start, end, label: start.toLocaleString('en-US', { month: 'short', year: 'numeric' }) });
  }

  const results = await Promise.all(
    months.map(async (m) => {
      const [totalReports, sifPotential, nonSif, nearMisses] = await Promise.all([
        SafetyReport.countDocuments({ date: { $gte: m.start, $lt: m.end } }),
        SafetyReport.countDocuments({ date: { $gte: m.start, $lt: m.end }, sif_status: 'SIF_POTENTIAL' }),
        SafetyReport.countDocuments({ date: { $gte: m.start, $lt: m.end }, sif_status: 'NON_SIF' }),
        SafetyReport.countDocuments({ date: { $gte: m.start, $lt: m.end }, type: 'Near-Miss' }),
      ]);
      return { date: m.label, totalReports, sifPotential, nonSif, nearMisses };
    })
  );

  return results;
}

export async function getOverview() {
  const [kpis, highRiskSites, highRiskActivities, topLifeSavingRules, precursorFailures, trends] = await Promise.all([
    getKpis(),
    getHighRiskSites(),
    getHighRiskActivities(),
    getTopLifeSavingRules(),
    getPrecursorFailures(),
    getTrends(),
  ]);

  return {
    kpis,
    highRiskSites,
    highRiskActivities,
    topLifeSavingRules,
    precursorFailures,
    trends,
    lastUpdated: new Date().toISOString(),
  };
}
