import React from 'react';
import type { Stage43IntelligenceResponse } from '../../types/intelligence';
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle,
  FileText,
  Activity,
  MapPin,
  Clock,
  Layers,
  HelpCircle,
  Info,
  ChevronRight,
  TrendingUp,
  FileCheck,
  Zap
} from 'lucide-react';

interface IntelligenceResultViewProps {
  data: Stage43IntelligenceResponse;
}

export const IntelligenceResultView: React.FC<IntelligenceResultViewProps> = ({ data }) => {
  const {
    request_id,
    input,
    sif_assessment,
    lsr_assessment,
    precursors,
    similar_incidents,
    barrier_analysis,
    risk_intelligence,
    bowtie,
    recommendations,
    evidence,
    explainability,
    triage,
    metadata
  } = data;

  const isCritical = sif_assessment.potential || triage.action === 'IMMEDIATE_ESCALATION';
  const isNeedsReview = triage.action === 'NEEDS_REVIEW' || lsr_assessment.human_review_required;

  return (
    <div className="space-y-6">
      {/* ==================================================================== */}
      {/* SECTION L: CALIBRATED TRIAGE BANNER */}
      {/* ==================================================================== */}
      <div className={`p-5 rounded-lg border-l-4 shadow-sm transition-all ${
        triage.action === 'IMMEDIATE_ESCALATION'
          ? 'border-l-red-600 bg-slate-900 text-white'
          : triage.action === 'NEEDS_REVIEW'
          ? 'border-l-amber-500 bg-slate-900 text-white'
          : 'border-l-emerald-500 bg-slate-900 text-white'
      }`}>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-lg ${
              triage.action === 'IMMEDIATE_ESCALATION'
                ? 'bg-red-600/30 text-red-400'
                : triage.action === 'NEEDS_REVIEW'
                ? 'bg-amber-500/30 text-amber-400'
                : 'bg-emerald-500/30 text-emerald-400'
            }`}>
              <ShieldAlert className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Stage 43 Triage Action</span>
                <span className="text-xs text-slate-500">| Pipeline v{metadata?.pipeline_version || '43.0.0'}</span>
              </div>
              <h2 className="text-xl font-bold tracking-tight text-white">{triage.action.replace(/_/g, ' ')}</h2>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {lsr_assessment.human_review_required && (
              <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse">
                <AlertTriangle className="h-3.5 w-3.5" />
                <span>Human Review Required</span>
              </span>
            )}
            <span className={`inline-flex items-center gap-1 rounded-md px-3 py-1 text-xs font-bold uppercase tracking-wider ${
              triage.action === 'IMMEDIATE_ESCALATION'
                ? 'bg-red-600 text-white'
                : triage.action === 'NEEDS_REVIEW'
                ? 'bg-amber-500 text-slate-950'
                : 'bg-emerald-600 text-white'
            }`}>
              {triage.confidence_category}
            </span>
          </div>
        </div>

        <p className="mt-3 text-sm text-slate-300 leading-relaxed font-sans">{triage.explanation}</p>
      </div>

      {/* Grid Layout for Core Assessments */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* ==================================================================== */}
        {/* SECTION A: INCIDENT OVERVIEW */}
        {/* ==================================================================== */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 text-white">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
            <FileText className="h-4 w-4 text-blue-400" />
            <span>A. Incident Overview</span>
          </h3>
          <div className="space-y-3 text-sm">
            <div className="bg-slate-950/60 p-3 rounded border border-slate-800">
              <span className="text-xs text-slate-400 block mb-1">Normalized Narrative Text:</span>
              <p className="text-slate-200 font-mono text-xs leading-relaxed">{input.normalized_text}</p>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-slate-500">Analysis Request ID:</span>
                <p className="font-mono text-slate-300 font-semibold">{request_id}</p>
              </div>
              <div>
                <span className="text-slate-500">Language Detected:</span>
                <p className="text-slate-300 uppercase font-semibold">{input.language}</p>
              </div>
            </div>
          </div>
        </div>

        {/* ==================================================================== */}
        {/* SECTION B: SIF ASSESSMENT */}
        {/* ==================================================================== */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 text-white">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-amber-400" />
              <span>B. SIF Precursor Assessment</span>
            </span>
            <span className="text-xs font-mono text-slate-500">{sif_assessment.model_version}</span>
          </h3>

          <div className="space-y-3">
            <div className="flex items-center justify-between bg-slate-950/60 p-3 rounded border border-slate-800">
              <div>
                <span className="text-xs text-slate-400">SIF Precursor Potential:</span>
                <p className={`text-base font-bold ${sif_assessment.potential ? 'text-red-400' : 'text-emerald-400'}`}>
                  {sif_assessment.potential ? 'CRITICAL SIF POTENTIAL' : 'NON-SIF INCIDENT'}
                </p>
              </div>
              <div className="text-right">
                <span className="text-xs text-slate-400">Risk Score:</span>
                <p className="text-xl font-extrabold font-mono text-amber-400">{sif_assessment.risk_score.toFixed(1)}/100</p>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-400 mb-1">
                <span>Calibrated SIF Probability:</span>
                <span className="font-mono font-bold text-white">{(sif_assessment.probability * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${sif_assessment.potential ? 'bg-red-500' : 'bg-emerald-500'}`}
                  style={{ width: `${Math.min(100, Math.max(5, sif_assessment.probability * 100))}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* ==================================================================== */}
      {/* SECTION C: LSR ASSESSMENT */}
      {/* ==================================================================== */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 text-white">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center justify-between">
          <span className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-emerald-400" />
            <span>C. IOGP Life-Saving Rules (LSR) Assessment</span>
          </span>
          <span className="text-xs text-slate-400">Agreement: <strong className="text-white">{lsr_assessment.agreement_state}</strong></span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
          <div className="bg-slate-950/60 p-3 rounded border border-slate-800">
            <span className="text-xs text-slate-400 block mb-1">Primary LSR Rule:</span>
            <p className="text-sm font-bold text-emerald-400">{lsr_assessment.primary}</p>
          </div>

          <div className="bg-slate-950/60 p-3 rounded border border-slate-800">
            <span className="text-xs text-slate-400 block mb-1">Provenance:</span>
            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold ${
              lsr_assessment.provenance === 'SOURCE_GROUNDED'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                : lsr_assessment.provenance === 'MODEL_PREDICTED'
                ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
            }`}>
              {lsr_assessment.provenance}
            </span>
          </div>

          <div className="bg-slate-950/60 p-3 rounded border border-slate-800">
            <span className="text-xs text-slate-400 block mb-1">Human Review State:</span>
            <span className={`text-xs font-bold ${lsr_assessment.human_review_required ? 'text-amber-400' : 'text-emerald-400'}`}>
              {lsr_assessment.human_review_required ? '⚠️ Pending Analyst Verification' : '✓ Confirmed / Standard'}
            </span>
          </div>
        </div>

        {/* Confidence Scores List */}
        {Object.keys(lsr_assessment.confidence || {}).length > 0 && (
          <div className="mt-3 bg-slate-950/40 p-3 rounded border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 block mb-2">Rule Confidence Distribution:</span>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {Object.entries(lsr_assessment.confidence).map(([rule, score]) => (
                <div key={rule} className="flex justify-between items-center bg-slate-900 px-2.5 py-1.5 rounded text-xs">
                  <span className="text-slate-300 truncate max-w-[120px]">{rule}</span>
                  <span className="font-mono text-emerald-400 font-bold">{(score * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Grid: Precursor Analysis & Barrier Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* ==================================================================== */}
        {/* SECTION D: PRECURSOR ANALYSIS */}
        {/* ==================================================================== */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 text-white">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
            <Activity className="h-4 w-4 text-purple-400" />
            <span>D. Precursor & Salient Token Analysis</span>
          </h3>

          {precursors.length > 0 ? (
            <div className="space-y-2">
              {precursors.map((p, idx) => (
                <div key={idx} className="flex justify-between items-center bg-slate-950/60 px-3 py-2 rounded border border-slate-800 text-xs">
                  <span className="font-mono text-amber-300 font-bold">"{p.token}"</span>
                  <span className="text-slate-400 font-mono">Weight: {(p.salience_weight * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">No salient precursor tokens extracted.</p>
          )}
        </div>

        {/* ==================================================================== */}
        {/* SECTION F: BARRIER ANALYSIS */}
        {/* ==================================================================== */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 text-white">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
            <Layers className="h-4 w-4 text-red-400" />
            <span>F. Safety Barrier Analysis</span>
          </h3>

          <div className="space-y-2 text-xs">
            <div className="bg-slate-950/60 p-2.5 rounded border border-slate-800">
              <span className="text-slate-400 font-semibold block mb-1">Failed / Disrupted Barriers:</span>
              <div className="flex flex-wrap gap-1.5">
                {barrier_analysis.failed_barriers.map((b, i) => (
                  <span key={i} className="bg-red-500/20 text-red-300 px-2 py-0.5 rounded border border-red-500/40 font-semibold">{b}</span>
                ))}
              </div>
            </div>

            <div className="bg-slate-950/60 p-2.5 rounded border border-slate-800">
              <span className="text-slate-400 font-semibold block mb-1">Missing Safety Barriers:</span>
              <div className="flex flex-wrap gap-1.5">
                {barrier_analysis.missing_barriers.map((b, i) => (
                  <span key={i} className="bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/40 font-semibold">{b}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* ==================================================================== */}
      {/* SECTION E: SIMILAR HISTORICAL INCIDENTS */}
      {/* ==================================================================== */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 text-white">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
          <FileCheck className="h-4 w-4 text-cyan-400" />
          <span>E. Similar Historical Incident Evidence (oilps_final_master_v2.csv)</span>
        </h3>

        {similar_incidents.length > 0 ? (
          <div className="space-y-3">
            {similar_incidents.map((sim, i) => (
              <div key={i} className="bg-slate-950/70 p-3.5 rounded border border-slate-800 text-xs space-y-1.5">
                <div className="flex justify-between items-center">
                  <span className="font-mono font-bold text-cyan-300">Record #{sim.record_id}</span>
                  <span className="bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded font-mono font-bold border border-cyan-500/40">
                    {(sim.similarity * 100).toFixed(1)}% Cosine Similarity
                  </span>
                </div>
                <p className="text-slate-300 leading-relaxed font-sans">{sim.narrative}</p>
                <div className="flex flex-wrap gap-4 text-[11px] text-slate-400 pt-1 border-t border-slate-900">
                  <span>Location: <strong className="text-white">{sim.site}</strong></span>
                  <span>Activity: <strong className="text-white">{sim.activity}</strong></span>
                  <span>LSR: <strong className="text-emerald-400">{sim.lsr_labels}</strong></span>
                  <span>Provenance: <strong className="text-slate-300">{sim.provenance}</strong></span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500 italic">No similar historical incident matches found.</p>
        )}
      </div>

      {/* ==================================================================== */}
      {/* SECTION G: RISK INTELLIGENCE */}
      {/* ==================================================================== */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 text-white">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-emerald-400" />
          <span>G. Historical Risk Intelligence (Stage 26–31 Metrics)</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          {/* Site Risk */}
          <div className="bg-slate-950/60 p-3 rounded border border-slate-800">
            <span className="text-slate-400 font-semibold block mb-1">Site Risk</span>
            {risk_intelligence.site.status === 'SUCCESS' ? (
              <div>
                <p className="text-white font-bold">{risk_intelligence.site.details.site_name}</p>
                <p className="text-amber-400 font-semibold">{risk_intelligence.site.details.risk_tier}</p>
                <span className="text-[11px] text-slate-500">{(risk_intelligence.site.details.sif_density * 100).toFixed(0)}% SIF Density</span>
              </div>
            ) : (
              <span className="text-amber-400 font-bold">INSUFFICIENT DATA</span>
            )}
          </div>

          {/* Activity Risk */}
          <div className="bg-slate-950/60 p-3 rounded border border-slate-800">
            <span className="text-slate-400 font-semibold block mb-1">Activity Risk</span>
            {risk_intelligence.activity.status === 'SUCCESS' ? (
              <div>
                <p className="text-white font-bold">{risk_intelligence.activity.details.activity_name}</p>
                <p className="text-amber-400 font-semibold">{risk_intelligence.activity.details.risk_tier}</p>
                <span className="text-[11px] text-slate-500">{(risk_intelligence.activity.details.sif_density * 100).toFixed(0)}% SIF Density</span>
              </div>
            ) : (
              <span className="text-amber-400 font-bold">INSUFFICIENT DATA</span>
            )}
          </div>

          {/* Early Warning */}
          <div className="bg-slate-950/60 p-3 rounded border border-slate-800">
            <span className="text-slate-400 font-semibold block mb-1">Early Warning Signal</span>
            <p className={`font-bold ${risk_intelligence.early_warning.details?.alert_level === 'WARNING' ? 'text-red-400' : 'text-emerald-400'}`}>
              {risk_intelligence.early_warning.details?.alert_level || 'NORMAL'}
            </p>
          </div>

          {/* Priority Score */}
          <div className="bg-slate-950/60 p-3 rounded border border-slate-800">
            <span className="text-slate-400 font-semibold block mb-1">Priority Classification</span>
            <p className="text-white font-bold">{risk_intelligence.priority.details?.priority_rank || 'MEDIUM_PRIORITY'}</p>
            <span className="text-[11px] text-slate-500">Score: {risk_intelligence.priority.details?.priority_score || 0}/100</span>
          </div>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* SECTION H: BOW-TIE DIAGRAM MAPPING */}
      {/* ==================================================================== */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 text-white">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
          <ChevronRight className="h-4 w-4 text-blue-400" />
          <span>H. Bow-Tie Risk Barrier Chain</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-center text-xs">
          <div className="bg-slate-950/80 p-3 rounded border border-blue-500/30">
            <span className="text-[10px] text-blue-400 uppercase font-bold block mb-1">Threat</span>
            <p className="text-white font-semibold">{bowtie.threat}</p>
          </div>

          <div className="bg-slate-950/80 p-3 rounded border border-red-500/30">
            <span className="text-[10px] text-red-400 uppercase font-bold block mb-1">Barrier Failure</span>
            <p className="text-white font-semibold">{bowtie.barrier_failures[0] || 'Uncontrolled Energy'}</p>
          </div>

          <div className="bg-slate-950/80 p-3 rounded border border-amber-500/30">
            <span className="text-[10px] text-amber-400 uppercase font-bold block mb-1">Top Event</span>
            <p className="text-white font-semibold">{bowtie.top_event}</p>
          </div>

          <div className="bg-slate-950/80 p-3 rounded border border-purple-500/30">
            <span className="text-[10px] text-purple-400 uppercase font-bold block mb-1">Consequences</span>
            <p className="text-white font-semibold">{bowtie.potential_consequences.join(', ')}</p>
          </div>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* SECTION I & J: RAG RECOMMENDATIONS & TRACEABILITY */}
      {/* ==================================================================== */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 text-white">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
          <Info className="h-4 w-4 text-emerald-400" />
          <span>I & J. Grounded Safety Recommendations & Source Traceability</span>
        </h3>

        {recommendations.length > 0 ? (
          <div className="space-y-3">
            {recommendations.map((rec, i) => (
              <div key={i} className="bg-slate-950/70 p-3.5 rounded border border-slate-800 text-xs space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-emerald-400 font-mono">Rule: {rec.rule}</span>
                  <span className="bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded font-bold border border-emerald-500/40">
                    {rec.status}
                  </span>
                </div>
                <p className="text-slate-200 leading-relaxed font-sans">{rec.recommendation_text}</p>
                <div className="text-[11px] text-slate-400 pt-1 border-t border-slate-900">
                  <span>Source Guidance: <strong className="text-slate-300 font-mono">{rec.grounded_sources.join(', ')}</strong></span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500 italic">No grounded recommendations available.</p>
        )}
      </div>

      {/* ==================================================================== */}
      {/* SECTION K: EXPLAINABILITY */}
      {/* ==================================================================== */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-5 text-white">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
          <HelpCircle className="h-4 w-4 text-blue-400" />
          <span>K. Explainability & Interpretation</span>
        </h3>
        <div className="bg-slate-950/60 p-3.5 rounded border border-slate-800 space-y-2 text-xs text-slate-300">
          <p><strong>SIF Reasoning:</strong> {explainability.sif_explanation}</p>
          <p><strong>LSR Reasoning:</strong> {explainability.lsr_explanation}</p>
          <p><strong>Risk Reasoning:</strong> {explainability.risk_explanation}</p>
          <p><strong>Triage Reasoning:</strong> {explainability.triage_explanation}</p>
        </div>
      </div>

    </div>
  );
};
