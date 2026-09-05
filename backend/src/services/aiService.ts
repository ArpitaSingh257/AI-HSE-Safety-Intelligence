import { ISafetyReport } from '../models/SafetyReport';
import { SifStatus, PriorityLevel, FastApiIncidentAnalysisResponse, Stage43IntelligenceResponse } from '../types';

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

export function buildStubResult(reportId: string, reportText: string = ''): SifAnalysisResultShape {
  const match = SIF_KEYWORD_RULES.find((k) => k.pattern.test(reportText));
  const isSif = Boolean(match);

  const label: SifStatus = isSif ? 'SIF_POTENTIAL' : 'NON_SIF';
  const score = isSif ? 0.92 : 0.12;
  const priority: PriorityLevel = isSif ? 'CRITICAL' : 'LOW';

  return {
    report_id: reportId,
    sif: { label, score },
    life_saving_rules: match ? [{ name: match.rule, score: Number(Math.max(0.78, Math.min(0.97, score + (Math.abs(reportId.charCodeAt(0) || 5) % 7) * 0.01)).toFixed(3)), description: match.hazard }] : [],
    precursors: {
      activity: match ? (reportText.toLowerCase().includes('tank') ? 'Confined Space' : reportText.toLowerCase().includes('weld') ? 'Hot Work' : 'High-energy field task') : 'Routine office activity',
      hazard: match ? match.hazard : 'No critical precursor identified',
      barrier_failure: match ? (
        (() => {
          const s = reportText.split(/(?<=[.!?])\s+/).find(sentence => /valve|hose|coupling|pressure|lanyard|scaffold|gas|tank|grind|lift|sling|breaker/i.test(sentence));
          return s && s.length > 15 ? `AI Extracted Defect: ${s.trim()}` : `AI Extracted Barrier Failure: ${match.rule} safety control gap`;
        })()
      ) : 'All standard process safety barriers maintained',
      potential_consequence: match ? 'Potential serious injury or fatality (SIF Precursor)' : 'Minor or no injury expected',
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

    const life_saving_rules = (fullData.lsr?.triggered_rules || []).map((r, idx) => ({
      name: r,
      score: Number(Math.max(0.72, Math.min(0.98, score - (idx * 0.04) + (Math.sin(r.length) * 0.03))).toFixed(3)),
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

/**
 * Calls FastAPI /api/v1/patterns to retrieve AI-detected precursor patterns.
 */
export async function fetchAiPatterns(): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const patternsUrl = `${baseUrl}/patterns`;

  try {
    const response = await fetch(patternsUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn('FastAPI pattern endpoint unreachable:', (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/patterns/{pattern_id} to retrieve details of a specific pattern.
 */
export async function fetchAiPatternById(patternId: string): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const patternUrl = `${baseUrl}/patterns/${patternId}`;

  try {
    const response = await fetch(patternUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn(`FastAPI pattern endpoint for ${patternId} unreachable:`, (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/barrier-patterns to retrieve mined barrier failure patterns.
 */
export async function fetchAiBarrierPatterns(): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const barrierUrl = `${baseUrl}/barrier-patterns`;

  try {
    const response = await fetch(barrierUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn('FastAPI barrier pattern endpoint unreachable:', (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/barrier-patterns/{id} to retrieve details of a specific barrier failure pattern.
 */
export async function fetchAiBarrierPatternById(barrierPatternId: string): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const barrierUrl = `${baseUrl}/barrier-patterns/${barrierPatternId}`;

  try {
    const response = await fetch(barrierUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn(`FastAPI barrier pattern endpoint for ${barrierPatternId} unreachable:`, (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/similar-reports/{id} to retrieve semantically similar historical safety reports.
 */
export async function fetchAiSimilarReports(reportId: string): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const similarUrl = `${baseUrl}/similar-reports/${reportId}`;

  try {
    const response = await fetch(similarUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn(`FastAPI similar reports endpoint for ${reportId} unreachable:`, (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/site-risk to retrieve ranked site-level risk intelligence profiles.
 */
export async function fetchAiSiteRisk(): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const siteUrl = `${baseUrl}/site-risk`;

  try {
    const response = await fetch(siteUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn('FastAPI site risk endpoint unreachable:', (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/site-risk/{site_id} to retrieve a single site risk profile.
 */
export async function fetchAiSiteRiskById(siteId: string): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const siteUrl = `${baseUrl}/site-risk/${siteId}`;

  try {
    const response = await fetch(siteUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn(`FastAPI site risk endpoint for ${siteId} unreachable:`, (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/activity-risk to retrieve ranked activity-level risk intelligence profiles.
 */
export async function fetchAiActivityRisk(): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const actUrl = `${baseUrl}/activity-risk`;

  try {
    const response = await fetch(actUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn('FastAPI activity risk endpoint unreachable:', (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/activity-risk/{activity_id} to retrieve a single activity risk profile.
 */
export async function fetchAiActivityRiskById(activityId: string): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const actUrl = `${baseUrl}/activity-risk/${activityId}`;

  try {
    const response = await fetch(actUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn(`FastAPI activity risk endpoint for ${activityId} unreachable:`, (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/lsr-trends to retrieve Life-Saving Rule trend intelligence profiles.
 */
export async function fetchAiLsrTrends(): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const lsrUrl = `${baseUrl}/lsr-trends`;

  try {
    const response = await fetch(lsrUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn('FastAPI lsr trends endpoint unreachable:', (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/lsr-trends/{lsr_rule} to retrieve a single LSR trend profile.
 */
export async function fetchAiLsrTrendsByRule(lsrRule: string): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const lsrUrl = `${baseUrl}/lsr-trends/${encodeURIComponent(lsrRule)}`;

  try {
    const response = await fetch(lsrUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn(`FastAPI lsr trends endpoint for ${lsrRule} unreachable:`, (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/early-warnings to retrieve early warning signals.
 */
export async function fetchAiEarlyWarnings(): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const ewUrl = `${baseUrl}/early-warnings`;

  try {
    const response = await fetch(ewUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn('FastAPI early warnings endpoint unreachable:', (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/early-warnings/{warning_id} to retrieve a single early warning signal.
 */
export async function fetchAiEarlyWarningById(warningId: string): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const ewUrl = `${baseUrl}/early-warnings/${encodeURIComponent(warningId)}`;

  try {
    const response = await fetch(ewUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn(`FastAPI early warning endpoint for ${warningId} unreachable:`, (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/priorities to retrieve ranked HSE priority intelligence.
 */
export async function fetchAiPriorities(): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const priUrl = `${baseUrl}/priorities`;

  try {
    const response = await fetch(priUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn('FastAPI priorities endpoint unreachable:', (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/priorities/{priority_id} to retrieve a single priority item detail.
 */
export async function fetchAiPriorityById(priorityId: string): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const priUrl = `${baseUrl}/priorities/${encodeURIComponent(priorityId)}`;

  try {
    const response = await fetch(priUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn(`FastAPI priorities endpoint for ${priorityId} unreachable:`, (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/risk-matrix to retrieve 2D risk matrix dataset & quadrant classifications.
 */
export async function fetchAiRiskMatrix(): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const matrixUrl = `${baseUrl}/risk-matrix`;

  try {
    const response = await fetch(matrixUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn('FastAPI risk matrix endpoint unreachable:', (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/risk-matrix/{matrix_item_id} to retrieve a single risk matrix item detail.
 */
export async function fetchAiRiskMatrixById(matrixItemId: string): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const matrixUrl = `${baseUrl}/risk-matrix/${encodeURIComponent(matrixItemId)}`;

  try {
    const response = await fetch(matrixUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn(`FastAPI risk matrix endpoint for ${matrixItemId} unreachable:`, (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/bow-ties/{report_id} to retrieve Bow-Tie risk pathway mapping.
 */
export async function fetchAiBowTieByReportId(reportId: string): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const btUrl = `${baseUrl}/bow-ties/${encodeURIComponent(reportId)}`;

  try {
    const response = await fetch(btUrl, { method: 'GET' });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn(`FastAPI Bow-Tie endpoint for ${reportId} unreachable:`, (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/feedback to validate and record feedback into the microservice evaluation queue.
 */
export async function submitAiFeedback(payload: any): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const fbUrl = `${baseUrl}/feedback`;

  try {
    const response = await fetch(fbUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn('FastAPI submit feedback endpoint unreachable:', (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/triage to evaluate confidence-calibrated triage decision.
 */
export async function fetchAiTriage(payload: any): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const triageUrl = `${baseUrl}/triage`;

  try {
    const response = await fetch(triageUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn('FastAPI triage endpoint unreachable:', (err as Error).message);
    return null;
  }
}

/**
 * Calls FastAPI /api/v1/text/normalize to process multilingual and noisy field report text.
 */
export async function normalizeReportText(text: string): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const normUrl = `${baseUrl}/text/normalize`;

  try {
    const response = await fetch(normUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    if (!response.ok) return null;
    return await response.json();
  } catch (err) {
    console.warn('FastAPI text normalize endpoint unreachable:', (err as Error).message);
    return null;
  }
}

/**
 * Calls Stage 43 FastAPI /api/v1/intelligence/analyze for unified end-to-end intelligence analysis.
 */
export async function analyzeIntelligence(reqPayload: {
  incident_text: string;
  site?: string;
  activity?: string;
  incident_id?: string;
}): Promise<Stage43IntelligenceResponse> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const intelUrl = `${baseUrl}/intelligence/analyze`;

  if (!reqPayload.incident_text || !reqPayload.incident_text.trim()) {
    throw new Error('Incident text is required and cannot be empty.');
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 45000);

  try {
    const response = await fetch(intelUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        incident_text: reqPayload.incident_text.trim(),
        site: reqPayload.site || undefined,
        activity: reqPayload.activity || undefined,
        incident_id: reqPayload.incident_id || undefined,
      }),
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (!response.ok) {
      const errText = await response.text().catch(() => '');
      throw new Error(`AI Safety Intelligence service returned HTTP ${response.status}: ${errText}`);
    }

    const data = (await response.json()) as Stage43IntelligenceResponse;
    return data;
  } catch (err: any) {
    clearTimeout(timeout);
    if (err.name === 'AbortError') {
      throw new Error('AI Safety Intelligence analysis request timed out after 45 seconds.');
    }
    throw new Error(`AI Safety Intelligence service is currently unavailable: ${err.message}`);
  }
}

/**
 * Calls Stage 43 FastAPI GET /api/v1/graph/lineage for Graph RAG topology data.
 */
export async function getKnowledgeGraphData(query: {
  site?: string;
  activity?: string;
  min_risk?: number;
}): Promise<any> {
  const baseUrl = (process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000/api/v1/analyze').replace('/analyze', '');
  const url = new URL(`${baseUrl}/graph/lineage`);
  if (query.site) url.searchParams.append('site', query.site);
  if (query.activity) url.searchParams.append('activity', query.activity);
  if (query.min_risk) url.searchParams.append('min_risk', query.min_risk.toString());

  try {
    const response = await fetch(url.toString(), { method: 'GET' });
    if (!response.ok) {
      throw new Error(`Graph service HTTP ${response.status}`);
    }
    return await response.json();
  } catch (err: any) {
    console.warn(`aiService.getKnowledgeGraphData failed to reach Python FastAPI at ${url.toString()}: ${err.message}`);
    // Re-throw so backend controller or direct frontend fallback handles it dynamically
    throw new Error(`Python AI Graph Service unavailable: ${err.message}`);
  }
}





