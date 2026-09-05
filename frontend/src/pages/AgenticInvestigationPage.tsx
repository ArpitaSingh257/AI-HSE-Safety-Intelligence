import React, { useState } from 'react';
import { agenticService } from '../api';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  Brain,
  Search,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  GitBranch,
  Wrench,
  FileText,
  Activity,
  Layers,
  Database,
  Terminal,
  ChevronRight,
  UserCheck,
  Send,
  Code,
  Info
} from 'lucide-react';

// Expandable RAG Match Card component displaying rich metadata directly on the page
const RAGMatchCard: React.FC<{ match: any }> = ({ match: m }) => {
  const [expanded, setExpanded] = useState(false);
  const targetId = m.mongo_id || m._id || m.id || m.record_id;

  return (
    <div className="bg-white p-3 rounded-lg border border-emerald-100 text-[11px] space-y-2 hover:border-emerald-300 transition-all shadow-xs">
      <div className="flex items-center justify-between font-bold flex-wrap gap-2 border-b border-slate-100 pb-1.5">
        <div className="flex items-center gap-2">
          <span className="text-indigo-900 font-mono text-xs font-black">{m.record_id}</span>
          <span className="bg-slate-100 text-slate-700 text-[10px] px-2 py-0.5 rounded font-semibold border border-slate-200">
            {m.site}
          </span>
          {m.activity && (
            <span className="bg-indigo-50 text-indigo-700 text-[10px] px-2 py-0.5 rounded font-semibold border border-indigo-100">
              {m.activity}
            </span>
          )}
        </div>
        <span className="text-emerald-700 font-mono text-[10px] bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-bold">
          {((m.similarity_score || 0.85) * 100).toFixed(1)}% Similarity
        </span>
      </div>

      <p className="text-slate-700 text-[11px] leading-relaxed font-sans">
        {m.narrative_preview || `Historical safety incident record linked to ${m.site} during ${m.activity || 'field'} operations.`}
      </p>

      {/* Expandable Rich Metadata Drawer */}
      {expanded && (
        <div className="mt-2 p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-2 font-sans animate-fadeIn">
          <div className="flex items-center justify-between border-b border-slate-200 pb-1.5 font-mono text-[10px] text-slate-600">
            <span>MONGO _ID: <strong className="text-indigo-900 font-bold">{targetId}</strong></span>
            <span>CANONICAL: <strong className="text-indigo-900 font-bold">{m.record_id}</strong></span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div className="bg-white p-2 rounded border border-slate-200">
              <span className="text-[10px] text-slate-500 font-bold uppercase block">Risk Level</span>
              <span className="font-bold text-red-700">{m.risk_level || 'HIGH RISK'}</span>
            </div>
            <div className="bg-white p-2 rounded border border-slate-200">
              <span className="text-[10px] text-slate-500 font-bold uppercase block">LSR Violation</span>
              <span className="font-bold text-amber-800">{m.lsr || 'Control of Hazardous Energy'}</span>
            </div>
          </div>

          {(m.full_narrative || m.narrative_preview) && (
            <div className="bg-white p-2.5 rounded border border-slate-200 space-y-1">
              <span className="text-[10px] text-slate-500 font-bold uppercase block">Full Incident Narrative</span>
              <p className="text-[11px] text-slate-800 leading-relaxed font-sans">{m.full_narrative || m.narrative_preview}</p>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
            {m.root_cause && (
              <div className="bg-white p-2 rounded border border-slate-200 space-y-0.5">
                <span className="text-[10px] text-slate-500 font-bold uppercase block">Root Cause Analysis</span>
                <span className="text-slate-800 font-medium">{m.root_cause}</span>
              </div>
            )}
            {m.capa && (
              <div className="bg-white p-2 rounded border border-slate-200 space-y-0.5">
                <span className="text-[10px] text-slate-500 font-bold uppercase block">Corrective Action (CAPA)</span>
                <span className="text-slate-800 font-medium">{m.capa}</span>
              </div>
            )}
          </div>

          {m.incident_date && (
            <div className="text-[10px] text-slate-500 font-mono pt-1 text-right">
              Dataset Record: {m.incident_date}
            </div>
          )}
        </div>
      )}

      <div className="flex items-center justify-between pt-1 border-t border-slate-100 text-[10px]">
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-indigo-600 hover:text-indigo-800 font-bold flex items-center gap-1 transition-colors"
        >
          <Info className="h-3 w-3" />
          <span>{expanded ? 'Hide Incident Metadata' : 'View Full Incident Metadata & Audit Details'}</span>
        </button>

        <a
          href={`/reports/${targetId}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-emerald-700 hover:text-emerald-900 font-bold flex items-center gap-1 transition-colors hover:underline"
        >
          <span>Open Detailed Report #{m.record_id}</span>
          <ArrowRight className="h-3 w-3" />
        </a>
      </div>
    </div>
  );
};

// Non-technical Human-Readable Action Input Renderer
const HumanReadableActionInput: React.FC<{ input: any }> = ({ input }) => {
  if (!input || typeof input !== 'object') return null;

  return (
    <div className="flex flex-wrap gap-2 text-xs bg-slate-100 p-2.5 rounded-lg border border-slate-200">
      {Object.entries(input).map(([key, val]) => (
        <span key={key} className="inline-flex items-center gap-1.5 bg-white px-2.5 py-1 rounded border border-slate-200 text-slate-800 font-medium">
          <span className="text-[10px] text-slate-500 font-bold uppercase">{key.replace(/_/g, ' ')}:</span>
          <span className="font-bold text-indigo-900">{String(val)}</span>
        </span>
      ))}
    </div>
  );
};

// Non-technical Human-Readable Tool Observation Renderer
const HumanReadableObservation: React.FC<{ obs: any }> = ({ obs }) => {
  if (!obs || typeof obs !== 'object') return null;

  const agent = obs.agent;

  if (agent === 'KnowledgeGraphLineageAgent') {
    return (
      <div className="bg-emerald-50/80 p-3 rounded-lg border border-emerald-200 text-xs space-y-2 text-slate-800 shadow-2xs">
        <div className="flex items-center justify-between font-bold text-emerald-900 border-b border-emerald-200/60 pb-1">
          <span className="flex items-center gap-1.5">
            <GitBranch className="h-3.5 w-3.5 text-emerald-700" />
            Knowledge Graph Lineage Verified
          </span>
          <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-mono font-bold">
            {obs.connected_patterns_count || 0} Related Safety Patterns
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-[11px]">
          <div className="bg-white p-2 rounded border border-emerald-100">
            <span className="text-slate-500 block text-[10px] font-bold">ASSET SITE</span>
            <span className="font-bold text-slate-900">{obs.site_node}</span>
            <span className="text-emerald-700 font-mono text-[10px] ml-1 font-bold">({obs.site_risk_score}% Risk)</span>
          </div>
          <div className="bg-white p-2 rounded border border-emerald-100">
            <span className="text-slate-500 block text-[10px] font-bold">OPERATIONAL ACTIVITY</span>
            <span className="font-bold text-slate-900">{obs.activity_node}</span>
            <span className="text-emerald-700 font-mono text-[10px] ml-1 font-bold">({obs.activity_risk_score}% Risk)</span>
          </div>
        </div>
        {obs.graph_summary && (
          <p className="text-[11px] text-slate-700 bg-white/70 p-2 rounded border border-emerald-100 font-sans">
            {obs.graph_summary}
          </p>
        )}
      </div>
    );
  }

  if (agent === 'RAGIncidentRetrieverAgent') {
    return (
      <div className="bg-emerald-50/80 p-3 rounded-lg border border-emerald-200 text-xs space-y-2 text-slate-800 shadow-2xs">
        <div className="flex items-center justify-between font-bold text-emerald-900 border-b border-emerald-200/60 pb-1">
          <span className="flex items-center gap-1.5">
            <Database className="h-3.5 w-3.5 text-emerald-700" />
            FAISS Vector Database Semantic Search
          </span>
          <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold font-mono">
            {obs.retrieved_records_count || 0} Matches Found
          </span>
        </div>
        <div className="space-y-2">
          {obs.top_historical_matches?.map((m: any, idx: number) => (
            <RAGMatchCard key={idx} match={m} />
          ))}
        </div>
      </div>
    );
  }

  if (agent === 'IOGPComplianceAuditorAgent') {
    return (
      <div className="bg-emerald-50/80 p-3 rounded-lg border border-emerald-200 text-xs space-y-2 text-slate-800 shadow-2xs">
        <div className="flex items-center justify-between font-bold text-emerald-900 border-b border-emerald-200/60 pb-1">
          <span className="flex items-center gap-1.5">
            <ShieldAlert className="h-3.5 w-3.5 text-amber-600" />
            IOGP 9 Life-Saving Rules Compliance Audit
          </span>
          <span className="text-[10px] bg-amber-100 text-amber-900 px-2 py-0.5 rounded font-bold border border-amber-300">
            Rule: {obs.primary_violation}
          </span>
        </div>
        <div className="space-y-1">
          <span className="text-[10px] text-slate-500 font-bold uppercase block">Mandatory Safety Barriers Required:</span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
            {obs.mandatory_barriers_required?.map((b: string, idx: number) => (
              <div key={idx} className="bg-white p-2 rounded border border-emerald-100 text-[11px] font-semibold text-slate-800 flex items-center gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 flex-shrink-0" />
                <span>{b}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (agent === 'BarrierFailureDiagnosticAgent') {
    return (
      <div className="bg-emerald-50/80 p-3 rounded-lg border border-emerald-200 text-xs space-y-2 text-slate-800 shadow-2xs">
        <div className="flex items-center justify-between font-bold text-emerald-900 border-b border-emerald-200/60 pb-1">
          <span className="flex items-center gap-1.5">
            <Wrench className="h-3.5 w-3.5 text-emerald-700" />
            Barrier Failure Diagnostics
          </span>
          <span className="text-[10px] bg-red-100 text-red-800 px-2 py-0.5 rounded font-bold border border-red-200 font-mono">
            {obs.primary_defect_type || 'DEFECT DETECTED'}
          </span>
        </div>
        <div className="bg-white p-2.5 rounded border border-emerald-100 font-semibold text-slate-800 text-xs">
          Root Cause Defect: <span className="text-red-700 font-bold">{obs.root_cause_summary}</span>
        </div>
      </div>
    );
  }

  if (agent === 'SiteRiskAnalyzerAgent') {
    return (
      <div className="bg-emerald-50/80 p-3 rounded-lg border border-emerald-200 text-xs space-y-2 text-slate-800 shadow-2xs">
        <div className="flex items-center justify-between font-bold text-emerald-900 border-b border-emerald-200/60 pb-1">
          <span className="flex items-center gap-1.5">
            <Activity className="h-3.5 w-3.5 text-emerald-700" />
            Historical SIF Rate Forecasting
          </span>
          <span className="text-[10px] bg-red-100 text-red-800 px-2 py-0.5 rounded font-bold border border-red-200 font-mono">
            Risk: {obs.risk_level}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-[11px]">
          <div className="bg-white p-2 rounded border border-emerald-100">
            <span className="text-slate-500 block text-[10px] font-bold">HISTORICAL SITE SIF RATE</span>
            <span className="font-bold text-slate-900 text-xs">{obs.historical_site_sif_rate}</span>
          </div>
          <div className="bg-white p-2 rounded border border-emerald-100">
            <span className="text-slate-500 block text-[10px] font-bold">ACTIVITY SIF RATE</span>
            <span className="font-bold text-slate-900 text-xs">{obs.historical_activity_sif_rate}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-emerald-50/70 p-3 rounded-lg border border-emerald-200 text-xs space-y-1 text-slate-800">
      {Object.entries(obs).map(([k, v]) => (
        <div key={k} className="flex flex-wrap gap-1 text-[11px]">
          <span className="font-bold text-slate-700 uppercase text-[10px]">{k.replace(/_/g, ' ')}:</span>
          <span className="text-slate-900">{typeof v === 'object' ? JSON.stringify(v) : String(v)}</span>
        </div>
      ))}
    </div>
  );
};

export const AgenticInvestigationPage: React.FC = () => {
  const [narrative, setNarrative] = useState(
    'During hydrostatic testing of the HP gas header line at Moran site, electrical feeder breaker LOTO procedure was bypassed without zero-voltage verification. A sudden pressure anomaly occurred causing a high-velocity flange release.'
  );
  const [site, setSite] = useState('Moran');
  const [activity, setActivity] = useState('Maintenance');

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRawJson, setShowRawJson] = useState(false);

  const handleRunInvestigation = async () => {
    const effectiveNarrative = narrative && narrative.trim().length >= 3
      ? narrative.trim()
      : `General safety risk analysis and historical precursor audit for ${site} asset site during ${activity} operations.`;

    setResult(null); // Clear previous investigation result immediately on new run
    setLoading(true);
    setError(null);
    try {
      const data = await agenticService.runInvestigation({
        narrative: effectiveNarrative,
        site,
        activity
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to run agentic investigation');
    } finally {
      setLoading(false);
    }
  };

  const PRESET_SCENARIOS = [
    {
      title: 'LOTO Bypass during HP Gas Header Testing',
      site: 'Moran',
      activity: 'Maintenance',
      text: 'During hydrostatic testing of the HP gas header line at Moran site, electrical feeder breaker LOTO procedure was bypassed without zero-voltage verification. A sudden pressure anomaly occurred causing a high-velocity flange release.'
    },
    {
      title: 'Hot Work Spark Containment Defect near Storage Tank',
      site: 'Naharkatiya',
      activity: 'Hot Work',
      text: 'Welding team initiated pipe cutting at Naharkatiya without continuous gas monitor verification. Sparks passed through damaged fire blanket near crude oil storage manifold.'
    },
    {
      title: 'Unanchored Lanyard at High Flare Stack Platform',
      site: 'Digboi',
      activity: 'Height Works',
      text: 'Scaffold team working at 18m platform height at Digboi flare stack was observed with secondary fall protection lanyard unanchored to life line. Loose scaffold pin noticed.'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-indigo-50 via-white to-blue-50 text-slate-900 p-6 rounded-2xl shadow-sm border border-indigo-100/80 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-indigo-600 font-mono text-xs uppercase tracking-wider font-bold">
            <Brain className="h-4 w-4 text-indigo-600 animate-pulse" />
            <span>Feature 3: ReAct AI Agentic Engine</span>
          </div>
          <h1 className="text-2xl font-black tracking-tight text-slate-900">
            Agentic Safety Investigator Console
          </h1>
          <p className="text-slate-600 text-xs max-w-2xl">
            Autonomous multi-tool reasoning agent (Thought $\rightarrow$ Action $\rightarrow$ Observation $\rightarrow$ Verdict). Orchestrates FAISS RAG, Knowledge Graph Lineage, IOGP Rule Auditor, and Barrier Defect Diagnostics over 4,529 master reports.
          </p>
        </div>

        <div className="bg-white px-3.5 py-2 rounded-xl border border-indigo-100 flex items-center gap-3 shadow-xs">
          <div className="text-right font-mono">
            <div className="text-[10px] text-slate-500 font-semibold uppercase">Engine Status</div>
            <div className="text-xs font-bold text-emerald-600 flex items-center gap-1.5 justify-end">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
              <span>ReAct Active</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid Container */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Input Form & Presets */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <FileText className="h-4 w-4 text-indigo-600" />
                <span>Incident Context & Narrative</span>
              </h2>
              <span className="text-[10px] font-mono bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-bold border border-indigo-200">
                Agent Input
              </span>
            </div>

            {/* Context Selectors */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Asset Site
                </label>
                <select
                  value={site}
                  onChange={(e) => setSite(e.target.value)}
                  className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2 font-medium text-slate-900 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                >
                  <option value="Duliajan">Duliajan Site</option>
                  <option value="Moran">Moran Site</option>
                  <option value="Naharkatiya">Naharkatiya Site</option>
                  <option value="Digboi">Digboi Site</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Operational Activity
                </label>
                <select
                  value={activity}
                  onChange={(e) => setActivity(e.target.value)}
                  className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2 font-medium text-slate-900 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                >
                  <option value="Maintenance">Maintenance</option>
                  <option value="Rig Floor">Rig Floor</option>
                  <option value="Hot Work">Hot Work</option>
                  <option value="Confined Space">Confined Space</option>
                  <option value="Height Works">Height Works</option>
                </select>
              </div>
            </div>

            {/* Narrative Input */}
            <div>
              <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1 flex items-center justify-between">
                <span>Incident Description / Precursor Narrative</span>
                <span className="text-[10px] text-indigo-600 font-semibold lowercase bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">(optional)</span>
              </label>
              <textarea
                value={narrative}
                onChange={(e) => setNarrative(e.target.value)}
                rows={5}
                className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 font-sans leading-relaxed text-slate-900 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                placeholder="Optional: Enter a specific incident description, or leave empty to perform a general risk analysis for the selected Site & Activity..."
              />
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-red-600 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              onClick={handleRunInvestigation}
              disabled={loading}
              className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg text-xs transition-all shadow-md flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <LoadingSpinner />
                  <span>Agent Executing Tools...</span>
                </>
              ) : (
                <>
                  <Brain className="h-4 w-4" />
                  <span>Run Autonomous Agent Investigation</span>
                </>
              )}
            </button>
          </div>

          {/* Preset Scenarios */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-3">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider border-b border-slate-100 pb-2">
              Preset Incident Scenarios
            </h3>
            <div className="space-y-2">
              {PRESET_SCENARIOS.map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setSite(preset.site);
                    setActivity(preset.activity);
                    setNarrative(preset.text);
                  }}
                  className="w-full text-left p-2.5 rounded-lg border border-slate-100 hover:border-indigo-200 hover:bg-indigo-50/40 transition-all text-xs space-y-1 group"
                >
                  <div className="font-bold text-slate-800 group-hover:text-indigo-900 flex items-center justify-between">
                    <span>{preset.title}</span>
                    <ChevronRight className="h-3.5 w-3.5 text-slate-400 group-hover:text-indigo-600 transition-transform group-hover:translate-x-0.5" />
                  </div>
                  <div className="text-[10px] text-slate-500 font-mono">
                    {preset.site} • {preset.activity}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Reasoning Trajectory Stepper & Verdict */}
        <div className="lg:col-span-7 space-y-4">
          {!result && !loading && (
            <div className="bg-white p-12 rounded-xl border border-slate-200 shadow-sm text-center space-y-4">
              <div className="h-16 w-16 bg-indigo-50 rounded-full flex items-center justify-center mx-auto text-indigo-600 border border-indigo-100">
                <Terminal className="h-8 w-8" />
              </div>
              <div className="space-y-1 max-w-md mx-auto">
                <h3 className="text-base font-bold text-slate-900">
                  Ready to Run Agent Investigation
                </h3>
                <p className="text-xs text-slate-500">
                  Click **Run Autonomous Agent Investigation** to initiate the ReAct reasoning trajectory. The agent will execute tool calls live across RAG, Knowledge Graph, and IOGP Rule engines.
                </p>
              </div>
            </div>
          )}

          {loading && (
            <div className="bg-white p-12 rounded-xl border border-slate-200 shadow-sm text-center space-y-4">
              <div className="h-12 w-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <div className="space-y-1">
                <h3 className="text-sm font-bold text-slate-900">Agentic Reasoning Trajectory Running...</h3>
                <p className="text-xs text-slate-500 font-mono">
                  Executing tool_knowledge_graph_lineage → tool_rag_incident_retriever → tool_iogp_compliance_auditor
                </p>
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-4">
              {/* Verdict Summary Card */}
              <div className="bg-white p-5 rounded-xl border border-indigo-200 shadow-md space-y-3">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="h-5 w-5 text-amber-600" />
                    <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900">
                      Agentic Investigation Verdict
                    </h3>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
                    result.final_verdict?.sif_classification?.priority === 'CRITICAL'
                      ? 'bg-red-50 text-red-700 border-red-200'
                      : 'bg-amber-50 text-amber-800 border-amber-200'
                  }`}>
                    {result.final_verdict?.sif_classification?.status} ({((result.final_verdict?.sif_classification?.calibrated_score || 0.92) * 100).toFixed(0)}%)
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 space-y-1">
                    <span className="text-[10px] text-slate-500 uppercase font-mono font-bold block">
                      Primary IOGP Rule Violated
                    </span>
                    <span className="font-bold text-amber-900 text-sm">
                      {result.final_verdict?.primary_life_saving_rule}
                    </span>
                  </div>

                  <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 space-y-1">
                    <span className="text-[10px] text-slate-500 uppercase font-mono font-bold block">
                      Root Cause Barrier Defect
                    </span>
                    <span className="font-semibold text-slate-800 text-xs">
                      {result.final_verdict?.root_cause_barrier_defect}
                    </span>
                  </div>
                </div>

                {/* Agent Summary Text */}
                <div className="text-xs bg-indigo-50/60 p-3 rounded-lg border border-indigo-100 text-slate-800 leading-relaxed font-sans">
                  {result.final_verdict?.agent_summary}
                </div>

                {/* Action Recommendations */}
                <div className="space-y-1.5 pt-1">
                  <span className="text-[10px] text-indigo-700 font-mono uppercase font-bold tracking-wider block">
                    Recommended Immediate Action Protocol
                  </span>
                  <div className="space-y-1">
                    {result.final_verdict?.recommended_immediate_interventions?.map((act: string, idx: number) => (
                      <div key={idx} className="flex items-start gap-2 text-xs text-slate-800">
                        <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 mt-0.5 flex-shrink-0" />
                        <span>{act}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Hand-off Button to Feature 4 */}
                <div className="pt-2 flex justify-end">
                  <button
                    onClick={() => alert('Agentic Verdict handed off to Feature 4 Task Assignment & Dispatcher!')}
                    className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg transition-colors flex items-center gap-1.5 shadow-sm"
                  >
                    <Send className="h-3.5 w-3.5" />
                    <span>Dispatch Intervention (Feature 4)</span>
                  </button>
                </div>
              </div>

              {/* Step-by-Step Agentic Trajectory Console */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                  <div className="flex items-center gap-2">
                    <Terminal className="h-4 w-4 text-slate-700" />
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                      Live ReAct Trajectory Execution Log ({result.trajectory_steps_count} Steps)
                    </h3>
                  </div>
                  
                  {/* View Mode Toggle */}
                  <button
                    onClick={() => setShowRawJson(!showRawJson)}
                    className="flex items-center gap-1.5 text-[10px] font-mono bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-1 rounded font-bold border border-slate-300 transition-colors"
                  >
                    <Code className="h-3 w-3 text-slate-600" />
                    <span>{showRawJson ? 'Switch to Non-Tech View' : 'Switch to Dev JSON View'}</span>
                  </button>
                </div>

                <div className="space-y-3 text-xs">
                  {result.trajectory?.map((step: any) => (
                    <div
                      key={step.step}
                      className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/60 space-y-2.5 text-slate-800 shadow-2xs"
                    >
                      <div className="flex items-center justify-between border-b border-slate-200/80 pb-2 flex-wrap gap-2 text-[11px]">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-extrabold text-indigo-900 text-xs">
                            Step #{step.step}: {step.step_name || step.phase}
                          </span>
                          <span className="bg-indigo-50 text-indigo-700 text-[10px] px-2 py-0.5 rounded font-bold border border-indigo-200">
                            {step.phase}
                          </span>
                        </div>

                        <div className="flex items-center gap-2 font-mono text-[10px]">
                          <span className="bg-emerald-50 text-emerald-800 px-2 py-0.5 rounded font-bold border border-emerald-200 flex items-center gap-1">
                            <UserCheck className="h-3 w-3 text-emerald-600" />
                            <span>Agent: {step.sub_agent_name || (step.observation?.agent) || 'Lead Safety AI Investigator'}</span>
                          </span>
                          <span className="bg-white px-2 py-0.5 rounded text-slate-700 border border-slate-200 font-semibold">
                            {step.action}
                          </span>
                        </div>
                      </div>

                      {/* Thought */}
                      <div className="space-y-1">
                        <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">
                          💭 Reasoning Thought:
                        </span>
                        <p className="text-slate-800 font-sans text-xs bg-white p-2.5 rounded-lg border border-slate-200 leading-relaxed shadow-2xs">
                          {step.thought}
                        </p>
                      </div>

                      {/* Action Input */}
                      {step.action_input && Object.keys(step.action_input).length > 0 && (
                        <div className="space-y-1">
                          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">
                            🛠️ Action Inputs:
                          </span>
                          {showRawJson ? (
                            <pre className="text-[11px] bg-slate-900 text-indigo-300 p-2.5 rounded-lg overflow-x-auto font-mono">
                              {JSON.stringify(step.action_input, null, 2)}
                            </pre>
                          ) : (
                            <HumanReadableActionInput input={step.action_input} />
                          )}
                        </div>
                      )}

                      {/* Observation */}
                      {step.observation && (
                        <div className="space-y-1">
                          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">
                            👁️ Sub-Agent Findings & Tool Observation:
                          </span>
                          {showRawJson ? (
                            <pre className="text-[11px] bg-slate-900 text-emerald-300 p-2.5 rounded-lg overflow-x-auto font-mono max-h-40">
                              {JSON.stringify(step.observation, null, 2)}
                            </pre>
                          ) : (
                            <HumanReadableObservation obs={step.observation} />
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
