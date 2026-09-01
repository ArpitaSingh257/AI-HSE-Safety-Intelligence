import { Request, Response } from 'express';
import { FilterQuery } from 'mongoose';
import { SafetyReport, ISafetyReport } from '../models/SafetyReport';
import { SifAnalysisResult } from '../models/SifAnalysisResult';
import { Site } from '../models/Site';
import { Activity } from '../models/Activity';
import { SITE_NAMES, ACTIVITY_NAMES, SiteName, ActivityName } from '../types';
import { requestAnalysis, analyzeIncidentText, fetchAiSimilarReports } from '../services/aiService';
import { regeneratePatterns } from '../services/patternService';
import { logAudit } from '../services/auditService';
import { CreateReportInput, UpdateReportInput } from '../validators/reportValidator';

/** Maps a rich display string (e.g. "Duliajan Central Complex") down to the
 * canonical Site enum value ("Duliajan") by substring match. Returns null if
 * no known site name appears in the string. */
function normalizeSiteName(input: string): SiteName | null {
  return SITE_NAMES.find((n) => input.toLowerCase().includes(n.toLowerCase())) || null;
}

function normalizeActivityName(input: string): ActivityName | null {
  return ACTIVITY_NAMES.find((n) => input.toLowerCase().includes(n.toLowerCase())) || null;
}

export async function getReports(req: Request, res: Response) {
  const {
    search,
    type,
    site,
    activity,
    sif_status,
    priority,
    life_saving_rule,
    analysis_status,
    dateFrom,
    dateTo,
    sortBy = 'date',
    sortOrder = 'desc',
    page = '1',
    limit = '20',
  } = req.query as Record<string, string>;

  const query: FilterQuery<ISafetyReport> = {};

  if (search) {
    query.$or = [
      { title: { $regex: search, $options: 'i' } },
      { description: { $regex: search, $options: 'i' } },
      { site: { $regex: search, $options: 'i' } },
      { activity: { $regex: search, $options: 'i' } },
      { life_saving_rule: { $regex: search, $options: 'i' } },
    ];
  }

  if (type && type !== 'ALL') query.type = type as any;
  if (site && site !== 'ALL') query.site = site;
  if (activity && activity !== 'ALL') query.activity = activity;
  if (sif_status && sif_status !== 'ALL') query.sif_status = sif_status as any;
  if (priority && priority !== 'ALL') query.priority = priority as any;
  if (life_saving_rule && life_saving_rule !== 'ALL') query.life_saving_rule = life_saving_rule;
  if (analysis_status && analysis_status !== 'ALL') query.analysis_status = analysis_status as any;

  if (dateFrom || dateTo) {
    query.date = {};
    if (dateFrom) (query.date as any).$gte = new Date(dateFrom);
    if (dateTo) (query.date as any).$lte = new Date(dateTo);
  }

  const pageNum = Math.max(1, parseInt(page, 10) || 1);
  const limitNum = Math.max(1, Math.min(100, parseInt(limit, 10) || 20));
  const sortField = sortBy === 'created_at' ? 'createdAt' : sortBy === 'updated_at' ? 'updatedAt' : sortBy;
  const sortDir = sortOrder === 'asc' ? 1 : -1;

  const [reports, total] = await Promise.all([
    SafetyReport.find(query)
      .sort({ [sortField]: sortDir })
      .skip((pageNum - 1) * limitNum)
      .limit(limitNum),
    SafetyReport.countDocuments(query),
  ]);

  res.json({ data: reports.map((r) => r.toJSON()), total });
}

export async function getReportById(req: Request, res: Response) {
  const report = await SafetyReport.findById(req.params.id);
  if (!report) return res.status(404).json({ message: `Report ${req.params.id} not found` });

  const aiResult = await SifAnalysisResult.findOne({ reportId: report._id });
  const json: any = report.toJSON();
  if (aiResult) json.ai_result = aiResult.toJSON();

  res.json(json);
}

export async function getSimilarReportsForReport(req: Request, res: Response) {
  const data = await fetchAiSimilarReports(req.params.id);
  if (!data) {
    return res.json({
      query_report_id: req.params.id,
      total_matches: 0,
      top_k: 5,
      min_similarity_threshold: 0.40,
      similar_reports: []
    });
  }
  res.json(data);
}

export async function createReport(req: Request<{}, {}, CreateReportInput>, res: Response) {
  const payload = req.body;

  const siteName = normalizeSiteName(payload.site);
  if (!siteName) {
    return res.status(400).json({
      message: `Unrecognized site "${payload.site}". Must reference one of: ${SITE_NAMES.join(', ')}`,
    });
  }
  const activityName = normalizeActivityName(payload.activity);
  if (!activityName) {
    return res.status(400).json({
      message: `Unrecognized activity "${payload.activity}". Must reference one of: ${ACTIVITY_NAMES.join(', ')}`,
    });
  }

  const siteDoc = await Site.findOneAndUpdate(
    { name: siteName },
    { name: siteName, department: payload.department },
    { upsert: true, new: true, setDefaultsOnInsert: true }
  );
  const activityDoc = await Activity.findOneAndUpdate(
    { name: activityName },
    { name: activityName },
    { upsert: true, new: true, setDefaultsOnInsert: true }
  );

  const report = await SafetyReport.create({
    title: payload.title,
    type: payload.type,
    date: payload.date ? new Date(payload.date) : new Date(),
    siteId: siteDoc._id,
    site: payload.site,
    activityId: activityDoc._id,
    activity: payload.activity,
    department: payload.department,
    location_detail: payload.location_detail,
    reporterId: req.user!.userId,
    reporter_name: payload.reporter_name,
    reporter_role: req.user!.role,
    description: payload.description,
    immediate_actions_taken: payload.immediate_actions_taken,
    sif_status: 'PENDING_ANALYSIS',
    sif_score: 0,
    life_saving_rule: 'Pending Evaluation',
    priority: payload.priority || 'MEDIUM',
    analysis_status: 'PENDING',
    investigation_status: 'Open',
  });

  await logAudit({
    req,
    action: 'REPORT_CREATED',
    entityType: 'REPORT',
    entityId: (report._id as any).toString(),
    details: `Submitted ${payload.type} "${payload.title}" for ${payload.site} (${payload.department})`,
  });

  res.status(201).json(report.toJSON());
}

export async function updateReport(req: Request<{ id: string }, {}, UpdateReportInput>, res: Response) {
  const report = await SafetyReport.findById(req.params.id);
  if (!report) return res.status(404).json({ message: `Report ${req.params.id} not found` });

  Object.assign(report, req.body);
  await report.save();

  await logAudit({
    req,
    action: 'REPORT_UPDATED',
    entityType: 'REPORT',
    entityId: req.params.id,
    details: `Updated report ${req.params.id} details and investigation status to "${report.investigation_status}"`,
  });

  res.json(report.toJSON());
}

export async function deleteReport(req: Request, res: Response) {
  const report = await SafetyReport.findById(req.params.id);
  if (!report) return res.status(404).json({ message: `Report ${req.params.id} not found` });

  await SifAnalysisResult.deleteOne({ reportId: report._id });
  await report.deleteOne();

  await logAudit({
    req,
    action: 'REPORT_DELETED',
    entityType: 'REPORT',
    entityId: req.params.id,
    details: `Deleted report ${req.params.id} from active register`,
  });

  res.json({ success: true });
}

export async function analyzeReport(req: Request, res: Response) {
  const report = await SafetyReport.findById(req.params.id);
  if (!report) return res.status(404).json({ message: `Report ${req.params.id} not found` });

  await logAudit({
    req,
    action: 'AI_ANALYSIS_TRIGGERED',
    entityType: 'AI_MODEL',
    entityId: req.params.id,
    details: `AI analysis manually triggered for report ${req.params.id}`,
  });

  const result = await requestAnalysis(report);

  const saved = await SifAnalysisResult.findOneAndUpdate(
    { reportId: report._id },
    {
      reportId: report._id,
      sif: result.sif,
      life_saving_rules: result.life_saving_rules,
      precursors: result.precursors,
      explanation: result.explanation,
      patterns: result.patterns,
      priority: result.priority,
      analyzed_at: result.analyzed_at ? new Date(result.analyzed_at) : new Date(),
      model_version: result.model_version,
    },
    { upsert: true, new: true }
  );

  report.sif_status = result.sif.label as any;
  report.sif_score = result.sif.score;
  report.life_saving_rule = result.life_saving_rules[0]?.name || report.life_saving_rule;
  report.priority = result.priority as any;
  report.analysis_status = 'COMPLETED';
  await report.save();

  const patternsUpdated = await regeneratePatterns();

  await logAudit({
    req,
    action: 'AI_ANALYSIS_COMPLETED',
    entityType: 'AI_MODEL',
    entityId: req.params.id,
    details: `AI pipeline classified report ${req.params.id} as ${result.sif.label} (${(result.sif.score * 100).toFixed(0)}% confidence). Patterns refreshed: ${patternsUpdated}.`,
  });

  res.json(saved!.toJSON());
}

export async function getAiResults(req: Request, res: Response) {
  const result = await SifAnalysisResult.findOne({ reportId: req.params.reportId });
  if (!result) {
    return res.status(404).json({ message: `AI results for report ${req.params.reportId} not found` });
  }
  res.json(result.toJSON());
}

export async function analyzeIncidentDirect(req: Request, res: Response) {
  const { incident_text, incident_id } = req.body;
  if (!incident_text || typeof incident_text !== 'string' || !incident_text.trim()) {
    return res.status(400).json({ message: 'Incident text is required and cannot be empty.' });
  }

  try {
    const result = await analyzeIncidentText(incident_text.trim(), incident_id || 'INC-MANUAL');
    return res.json(result);
  } catch (err: any) {
    const statusCode = err.message.includes('timed out') ? 504 : 503;
    return res.status(statusCode).json({ message: err.message });
  }
}
