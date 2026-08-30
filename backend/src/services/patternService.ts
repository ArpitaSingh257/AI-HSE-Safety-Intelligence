import { SafetyReport } from '../models/SafetyReport';
import { SifAnalysisResult } from '../models/SifAnalysisResult';
import { Pattern } from '../models/Pattern';
import { PriorityLevel, TrendStatus } from '../types';

function priorityFromRate(rate: number): PriorityLevel {
  if (rate >= 0.75) return 'CRITICAL';
  if (rate >= 0.5) return 'HIGH';
  if (rate >= 0.25) return 'MEDIUM';
  return 'LOW';
}

function trendFromCounts(recentCount: number, olderCount: number): TrendStatus {
  if (olderCount === 0 && recentCount === 0) return 'STABLE';
  if (olderCount === 0) return 'SURGING';
  const ratio = recentCount / olderCount;
  if (ratio >= 1.5) return 'SURGING';
  if (ratio <= 0.5) return 'DECLINING';
  if (recentCount === olderCount) return 'STABLE';
  return 'RECURRING';
}

/**
 * Regenerates PrecursorPattern documents from current SafetyReport +
 * SifAnalysisResult data. Groups SIF-potential reports by
 * (activity, primary life-saving rule) and upserts one Pattern doc per
 * group. Called (a) after every successful /reports/:id/analyze, and
 * (b) on a scheduled cron job - see src/server.ts.
 */
export async function regeneratePatterns(): Promise<number> {
  const sifReports = await SafetyReport.find({ sif_status: 'SIF_POTENTIAL' }).lean();
  if (sifReports.length === 0) return 0;

  const reportIds = sifReports.map((r) => r._id);
  const analysisResults = await SifAnalysisResult.find({ reportId: { $in: reportIds } }).lean();
  const analysisByReportId = new Map(analysisResults.map((a) => [a.reportId.toString(), a]));

  // Group by (activity, primaryRule)
  type GroupKey = string;
  interface Group {
    activity: string;
    rule: string;
    reports: typeof sifReports;
  }
  const groups = new Map<GroupKey, Group>();

  for (const report of sifReports) {
    const analysis = analysisByReportId.get((report._id as any).toString());
    const rule = analysis?.life_saving_rules?.[0]?.name || report.life_saving_rule || 'Unclassified';
    const key = `${report.activity}::${rule}`;
    if (!groups.has(key)) {
      groups.set(key, { activity: report.activity, rule, reports: [] });
    }
    groups.get(key)!.reports.push(report);
  }

  // Need total (not just SIF) report counts per activity to compute a rate.
  const totalsByActivity = await SafetyReport.aggregate([
    { $group: { _id: '$activity', total: { $sum: 1 } } },
  ]);
  const totalByActivity = new Map(totalsByActivity.map((t: any) => [t._id, t.total]));

  const now = Date.now();
  const THIRTY_DAYS = 30 * 24 * 60 * 60 * 1000;

  let upserted = 0;

  for (const group of groups.values()) {
    if (group.reports.length < 2) continue; // require at least 2 matching reports to call it a "pattern"

    const activityTotal = totalByActivity.get(group.activity) || group.reports.length;
    const sifPotentialRate = Math.min(1, group.reports.length / activityTotal);

    const sites = group.reports.map((r) => r.site);
    const siteCounts = sites.reduce<Record<string, number>>((acc, s) => {
      acc[s] = (acc[s] || 0) + 1;
      return acc;
    }, {});
    const mostAffectedSite = Object.entries(siteCounts).sort((a, b) => b[1] - a[1])[0][0];

    const dates = group.reports.map((r) => new Date(r.date).getTime());
    const firstDetected = new Date(Math.min(...dates));
    const lastOccurrence = new Date(Math.max(...dates));

    const recentCount = dates.filter((d) => now - d <= THIRTY_DAYS).length;
    const olderCount = dates.length - recentCount;

    const hazards = new Set<string>();
    const barrierFailures = new Set<string>();
    for (const report of group.reports) {
      const analysis = analysisByReportId.get((report._id as any).toString());
      if (analysis?.precursors?.hazard) hazards.add(analysis.precursors.hazard);
      if (analysis?.precursors?.barrier_failure) barrierFailures.add(analysis.precursors.barrier_failure);
    }

    const priority = priorityFromRate(sifPotentialRate);
    const trendStatus = trendFromCounts(recentCount, olderCount);

    const name = `${group.rule} Failure — ${group.activity}`;
    const description = `Recurring ${group.rule} precursor pattern detected during ${group.activity} activities, most concentrated at ${mostAffectedSite}.`;
    const recommendedIntervention = `Reinforce ${group.rule} controls for ${group.activity} crews at ${mostAffectedSite}; review barrier verification steps before work authorization.`;

    await Pattern.findOneAndUpdate(
      { name },
      {
        name,
        description,
        reportCount: group.reports.length,
        mainActivity: group.activity,
        mostAffectedSite,
        sifPotentialRate,
        priority,
        primaryLifeSavingRule: group.rule,
        keyHazards: Array.from(hazards),
        commonBarrierFailures: Array.from(barrierFailures),
        firstDetected,
        lastOccurrence,
        trendStatus,
        recommendedIntervention,
        matchedReportIds: group.reports.map((r) => (r._id as any).toString()),
      },
      { upsert: true, new: true }
    );
    upserted += 1;
  }

  return upserted;
}