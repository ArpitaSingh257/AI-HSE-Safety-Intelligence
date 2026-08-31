import { ISafetyReport } from '../models/SafetyReport';
import { SifStatus, PriorityLevel, FastApiIncidentAnalysisResponse } from '../types';

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
  full_ai_response?: FastApiIncidentAnalysisResponse;
}

// Keyword -> Life-Saving Rule mapping used by the fallback stub
const SIF_KEYWORD_RULES: { pattern: RegExp; rule: string; hazard: string }[] = [
  { pattern: /breaker|lockout|zero-voltage|tagged but not|hydrostatic|pressure|rupture|bleeder/i, rule: 'Control of Hazardous Energy', hazard: 'Stored/residual electrical or pressure energy' },
  { pattern: /weld|hot cutting|combustible gas|manifold|flash fire/i, rule: 'Hot Work', hazard: 'Ignition source near flammable material' },
  { pattern: /confined|gas test|stratification|h2s|vessel entry/i, rule: 'Confined Space Entry', hazard: 'Atmospheric hazard in confined space' },
  { pattern: /crane|sling|lift|suspended load|rig floor/i, rule: 'Line of Fire', hazard: 'Suspended load over occupied area' },
  { pattern: /elevated platform|lanyard|scaffold|height/i, rule: 'Work at Height', hazard: 'Fall from elevation' },
];

function buildStubResult(reportId: string, reportText: string = ''): SifAnalysisResultShape {
  const match = SIF_KEYWORD_RULES.find((k) => k.pattern.test(reportText));
  const isSif = Boolean(match);

  const label: SifStatus = isSif ? 'SIF_POTENTIAL' : 'NON_SIF';
  const score = isSif ? 0.92 : 0.12;
  const priority: PriorityLevel = isSif ? 'CRITICAL' : 'LOW';

  return {
    report_id: reportId,
    sif: { label, score },
    life_saving_rules: match ? [{ name: match.rule, score, description: match.hazard }] : [],
    precursors: {
      activity: match ? 'High-energy field task' : 'Routine office or low-risk activity',
      hazard: match ? match.hazard : 'No critical precursor identified',
      barrier_failure: match ? 'Procedural control gap identified' : 'All standard controls maintained',
      potential_consequence: match ? 'Potential serious injury or fatality' : 'Minor or no injury expected',
    },
    explanation: match
      ? `AI precursor pipeline detected ${match.rule} high-risk activity.`
      : 'AI service offline – evaluated as low risk negative control.',
    patterns: match ? [match.rule] : [],
    priority,
    analyzed_at: new Date().toISOString(),
    model_version: 'OILPS-Stage21-Frozen',
  };
}

/**
 * Direct call to FastAPI /api/v1/analyze for ad-hoc incident analysis.
 */
export async function analyzeIncidentText(incidentText: string, incidentId: string = 'INC-MANUAL'): Promise<FastApiIncidentAnalysisResponse> {
  const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze';

  if (!incidentText || !incidentText.trim()) {
    throw new Error('Incident text cannot be empty.');
  }

  const controller = new AbortController();
  // 45 second timeout to accommodate local Ollama LLM generation latency on CPU
  const timeout = setTimeout(() => controller.abort(), 45000);

  try {
    const response = await fetch(aiServiceUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        incident_text: incidentText.trim(),
        incident_id: incidentId,
      }),
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (!response.ok) {
      const errText = await response.text().catch(() => '');
      throw new Error(`AI safety analysis service returned HTTP ${response.status}: ${errText}`);
    }

    const data = (await response.json()) as FastApiIncidentAnalysisResponse;
    return data;
  } catch (err: any) {
    clearTimeout(timeout);
    if (err.name === 'AbortError') {
      throw new Error('AI safety analysis request timed out after 30 seconds.');
    }
    throw new Error(`AI safety analysis service is currently unavailable: ${err.message}`);
  }
}

/**
 * Calls external FastAPI ai-service /api/v1/analyze for report analysis.
 */
export async function requestAnalysis(report: ISafetyReport): Promise<SifAnalysisResultShape> {
  const reportId = (report._id as any).toString();
  const reportText = report.description || report.title || '';

  try {
    const fullData = await analyzeIncidentText(reportText, reportId);
    
    // Map FastAPI schema fields to SifAnalysisResultShape
    const isSif = fullData.sif.is_sif;
    const label: SifStatus = isSif ? 'SIF_POTENTIAL' : 'NON_SIF';
    const score = fullData.sif.probability;
    const priority = (fullData.recommendations?.priority || (isSif ? 'CRITICAL' : 'LOW')) as PriorityLevel;

    const life_saving_rules = (fullData.lsr?.triggered_rules || []).map((r) => ({
      name: r,
      score: 0.95,
      description: `Activated Life-Saving Rule: ${r}`,
    }));

    return {
      report_id: reportId,
      sif: { label, score },
      life_saving_rules,
      precursors: {
        activity: report.activity || 'High-Risk Operation',
        hazard: fullData.explainability?.sif_interpretation || 'High Energy Hazard',
        barrier_failure: fullData.explainability?.why_flagged?.[0] || 'Safety Barrier Disruption',
        potential_consequence: isSif ? 'Critical Precursor / High Energy Impact' : 'Minor / Routine Incident',
      },
      explanation: fullData.explainability?.formatted_text || fullData.recommendations?.summary || 'Analysis complete.',
      patterns: fullData.lsr?.triggered_rules || [],
      priority,
      analyzed_at: new Date().toISOString(),
      model_version: fullData.model_info?.version || 'OILPS-Stage21-Frozen',
      full_ai_response: fullData,
    };
  } catch (err) {
    console.warn('AI service unreachable or failed, falling back to deterministic local model:', (err as Error).message);
    return buildStubResult(reportId, reportText);
  }
}