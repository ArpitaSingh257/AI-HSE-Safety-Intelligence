import { ISafetyReport } from '../models/SafetyReport';
import { SifStatus, PriorityLevel } from '../types';

export interface SifAnalysisResultShape {
  report_id: string;
  sif: { label: SifStatus; score: number };
  life_saving_rules: { name: string; score: number; description?: string }[];
  precursors: {
    activity: string;
    hazard: string;
    barrier_failure: string;
    potential_consequence: string;
  };
  explanation: string;
  patterns: string[];
  priority: PriorityLevel;
  analyzed_at: string | null;
  model_version: string | null;
}

// Keyword -> Life-Saving Rule mapping used by the stub so seeded reports
// come out with a realistic mix of SIF/NON-SIF classifications instead of
// all-identical stub results. Matches the SAMPLE_DESCRIPTIONS in seed.ts.
const SIF_KEYWORD_RULES: { pattern: RegExp; rule: string; hazard: string }[] = [
  { pattern: /breaker|lockout|zero-voltage|tagged but not/i, rule: 'Control of Hazardous Energy', hazard: 'Stored/residual electrical energy' },
  { pattern: /weld|hot cutting|combustible gas/i, rule: 'Hot Work', hazard: 'Ignition source near flammable material' },
  { pattern: /confined|gas test|stratification/i, rule: 'Confined Space Entry', hazard: 'Atmospheric hazard in confined space' },
  { pattern: /crane|sling|lift|suspended load|rig floor/i, rule: 'Line of Fire', hazard: 'Suspended load over occupied area' },
  { pattern: /elevated platform|lanyard|scaffold|height/i, rule: 'Work at Height', hazard: 'Fall from elevation' },
];

function buildStubResult(reportId: string, reportText: string = ''): SifAnalysisResultShape {
  const match = SIF_KEYWORD_RULES.find((k) => k.pattern.test(reportText));
  const isSif = Boolean(match);

  const label: SifStatus = isSif ? 'SIF_POTENTIAL' : 'NON_SIF';
  const score = isSif
    ? Number((0.6 + Math.random() * 0.4).toFixed(2))
    : Number((Math.random() * 0.35).toFixed(2));

  const priority: PriorityLevel = isSif
    ? (score > 0.85 ? 'CRITICAL' : 'HIGH')
    : (score > 0.2 ? 'MEDIUM' : 'LOW');

  return {
    report_id: reportId,
    sif: { label, score },
    life_saving_rules: match ? [{ name: match.rule, score, description: match.hazard }] : [],
    precursors: {
      activity: match ? 'Field task with elevated risk exposure' : 'Routine activity, no high-risk pattern matched',
      hazard: match ? match.hazard : 'Not yet analyzed',
      barrier_failure: match ? 'Procedural or physical control gap identified' : 'Not yet analyzed',
      potential_consequence: match ? 'Potential serious injury or fatality' : 'Minor or no injury expected',
    },
    explanation: match
      ? `Stub classification: description matched "${match.rule}" keyword pattern.`
      : 'AI service unavailable – stub result (no high-risk keywords matched).',
    patterns: match ? [match.rule] : [],
    priority,
    analyzed_at: null,
    model_version: 'stub-v1',
  };
}

/**
 * Calls the external ai-service /api/v1/analyze endpoint. Falls back to a
 * clearly-labeled stub result (never throws) if AI_SERVICE_URL is unset,
 * unreachable, or returns a non-2xx response - so the frontend can always
 * demo end-to-end even before ai-service/ is built.
 */
export async function requestAnalysis(report: ISafetyReport): Promise<SifAnalysisResultShape> {
  const aiServiceUrl = process.env.AI_SERVICE_URL;
  const reportId = (report._id as any).toString();

  if (!aiServiceUrl) {
    return buildStubResult(reportId, report.description);
  }

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);

    const response = await fetch(aiServiceUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        report_id: reportId,
        report_text: report.description,
        report_type: report.type,
        location: report.site,
        activity: report.activity,
      }),
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (!response.ok) {
      console.warn(`AI service returned ${response.status}, falling back to stub`);
      return buildStubResult(reportId, report.description);
    }

    const data = (await response.json()) as any;
    return {
      report_id: data.report_id ?? reportId,
      sif: data.sif ?? buildStubResult(reportId, report.description).sif,
      life_saving_rules: data.life_saving_rules ?? [],
      precursors: data.precursors ?? buildStubResult(reportId, report.description).precursors,
      explanation: data.explanation ?? 'No explanation provided.',
      patterns: data.patterns ?? [],
      priority: data.priority ?? 'LOW',
      analyzed_at: new Date().toISOString(),
      model_version: data.model_version ?? null,
    };
  } catch (err) {
    console.warn('AI service unreachable, falling back to stub:', (err as Error).message);
    return buildStubResult(reportId, report.description);
  }
}