import React from 'react';
import type { Stage43IntelligenceResponse } from '../../types/intelligence';
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle,
  FileText,
  Activity,
  ChevronRight,
  TrendingUp,
  FileCheck,
  Zap,
  Layers,
  Info,
  HelpCircle
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
    explainability,
    triage,
    metadata
  } = data;

  return (
    <div className="space-y-5 text-slate-900 font-sans">
      {/* ==================================================================== */}
      {/* SECTION L: CALIBRATED TRIAGE BANNER (LIGHT THEME) */}
      {/* ==================================================================== */}
      <div className={`p-4 rounded-lg border-l-4 border shadow-sm transition-all ${
        triage.action === 'IMMEDIATE_ESCALATION'
          ? 'border-l-red-600 border-red-200 bg-red-50/80 text-red-950'
          : triage.action === 'NEEDS_REVIEW'
          ? 'border-l-amber-500 border-amber-200 bg-amber-50/80 text-amber-950'
          : 'border-l-emerald-600 border-emerald-200 bg-emerald-50/80 text-emerald-950'
      }`}>
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-200/80">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${
              triage.action === 'IMMEDIATE_ESCALATION'
                ? 'bg-red-200/60 text-red-700'
                : triage.action === 'NEEDS_REVIEW'
                ? 'bg-amber-200/60 text-amber-800'
                : 'bg-emerald-200/60 text-emerald-800'
            }`}>
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600">Stage 43 Triage Action</span>
                <span className="text-[11px] text-slate-500">| Pipeline v{metadata?.pipeline_version || '43.0.0'}</span>
              </div>
              <h2 className="text-lg font-bold tracking-tight text-slate-900">{triage.action.replace(/_/g, ' ')}</h2>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {lsr_assessment.human_review_required && (
              <span className="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-700" />
                <span>Human Review Required</span>
              </span>
            )}
            <span className={`inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-bold uppercase tracking-wider ${
              triage.action === 'IMMEDIATE_ESCALATION'
                ? 'bg-red-600 text-white'
                : triage.action === 'NEEDS_REVIEW'
                ? 'bg-amber-600 text-white'
                : 'bg-emerald-700 text-white'
            }`}>
              {triage.confidence_category}
            </span>
          </div>
        </div>

        <p className="mt-2.5 text-xs text-slate-800 leading-relaxed font-sans">{triage.explanation}</p>
      </div>

      {/* Grid Layout for Core Assessments */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* ==================================================================== */}
        {/* SECTION A: INCIDENT OVERVIEW */}
        {/* ==================================================================== */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center gap-2">
            <FileText className="h-4 w-4 text-blue-600" />
            <span>A. Incident Overview</span>
          </h3>
          <div className="space-y-2.5 text-xs">
            <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
              <span className="text-[11px] text-slate-500 font-semibold block mb-1">Normalized Narrative Text:</span>
              <p className="text-slate-800 font-mono text-xs leading-relaxed">{input.normalized_text}</p>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs pt-1">
              <div>
                <span className="text-slate-500">Analysis Request ID:</span>
                <p className="font-mono text-slate-900 font-semibold">{request_id}</p>
              </div>
              <div>
                <span className="text-slate-500">Language Detected:</span>
                <p className="text-slate-900 uppercase font-semibold">{input.language}</p>
              </div>
            </div>
          </div>
        </div>

        {/* ==================================================================== */}
        {/* SECTION B: SIF ASSESSMENT */}
        {/* ==================================================================== */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-amber-600" />
              <span>B. SIF Precursor Assessment</span>
            </span>
            <span className="text-xs font-mono text-slate-400">{sif_assessment.model_version}</span>
          </h3>

          <div className="space-y-2.5">
            <div className="flex items-center justify-between bg-slate-50 p-2.5 rounded border border-slate-200">
              <div>
                <span className="text-[11px] text-slate-500 font-semibold">SIF Precursor Potential:</span>
                <p className={`text-sm font-bold ${sif_assessment.potential ? 'text-red-700' : 'text-emerald-700'}`}>
                  {sif_assessment.potential ? 'CRITICAL SIF POTENTIAL' : 'NON-SIF INCIDENT'}
                </p>
              </div>
              <div className="text-right">
                <span className="text-[11px] text-slate-500 font-semibold">Risk Score:</span>
                <p className="text-lg font-extrabold font-mono text-amber-700">{sif_assessment.risk_score.toFixed(1)}/100</p>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs text-slate-600 mb-1 font-semibold">
                <span>Calibrated SIF Probability:</span>
                <span className="font-mono font-bold text-slate-900">{(sif_assessment.probability * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${sif_assessment.potential ? 'bg-red-600' : 'bg-emerald-600'}`}
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
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center justify-between">
          <span className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-emerald-600" />
            <span>C. IOGP Life-Saving Rules (LSR) Assessment</span>
          </span>
          <span className="text-xs text-slate-500">Agreement: <strong className="text-slate-900">{lsr_assessment.agreement_state}</strong></span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-3">
          <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
            <span className="text-[11px] text-slate-500 block mb-0.5">Primary LSR Rule:</span>
            <p className="text-xs font-bold text-emerald-800">{lsr_assessment.primary}</p>
          </div>

          <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
            <span className="text-[11px] text-slate-500 block mb-0.5">Provenance:</span>
            <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold ${
              lsr_assessment.provenance === 'SOURCE_GROUNDED'
                ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                : lsr_assessment.provenance === 'MODEL_PREDICTED'
                ? 'bg-blue-100 text-blue-800 border border-blue-300'
                : 'bg-amber-100 text-amber-900 border border-amber-300'
            }`}>
              {lsr_assessment.provenance}
            </span>
          </div>

          <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
            <span className="text-[11px] text-slate-500 block mb-0.5">Human Review State:</span>
            <span className={`text-xs font-bold ${lsr_assessment.human_review_required ? 'text-amber-700' : 'text-emerald-700'}`}>
              {lsr_assessment.human_review_required ? '⚠️ Pending Verification' : '✓ Confirmed'}
            </span>
          </div>
        </div>

        {/* Confidence Scores List */}
        {Object.keys(lsr_assessment.confidence || {}).length > 0 && (
          <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
            <span className="text-[11px] font-semibold text-slate-600 block mb-1.5">Rule Confidence Distribution:</span>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {Object.entries(lsr_assessment.confidence).map(([rule, score]) => (
                <div key={rule} className="flex justify-between items-center bg-white px-2 py-1 rounded border border-slate-200 text-xs">
                  <span className="text-slate-700 truncate max-w-[120px] font-medium">{rule}</span>
                  <span className="font-mono text-emerald-700 font-bold">{(score * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Grid: Precursor Analysis & Barrier Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* ==================================================================== */}
        {/* SECTION D: PRECURSOR ANALYSIS */}
        {/* ==================================================================== */}
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center gap-2">
            <Activity className="h-4 w-4 text-purple-600" />
            <span>D. Precursor & Salient Token Analysis</span>
          </h3>

          {precursors.length > 0 ? (
            <div className="space-y-1.5">
              {precursors.map((p, idx) => (
                <div key={idx} className="flex justify-between items-center bg-slate-50 px-2.5 py-1.5 rounded border border-slate-200 text-xs">
                  <span className="font-mono text-slate-900 font-bold">"{p.token}"</span>
                  <span className="text-slate-600 font-mono">Weight: {(p.salience_weight * 100).toFixed(1)}%</span>
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
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center gap-2">
            <Layers className="h-4 w-4 text-red-600" />
            <span>F. Safety Barrier Analysis</span>
          </h3>

          <div className="space-y-2 text-xs">
            <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
              <span className="text-slate-600 font-semibold block mb-1 text-[11px]">Failed / Disrupted Barriers:</span>
              <div className="flex flex-wrap gap-1.5">
                {barrier_analysis.failed_barriers.map((b, i) => (
                  <span key={i} className="bg-red-50 text-red-800 px-2 py-0.5 rounded border border-red-200 font-semibold">{b}</span>
                ))}
              </div>
            </div>

            <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
              <span className="text-slate-600 font-semibold block mb-1 text-[11px]">Missing Safety Barriers:</span>
              <div className="flex flex-wrap gap-1.5">
                {barrier_analysis.missing_barriers.map((b, i) => (
                  <span key={i} className="bg-amber-50 text-amber-900 px-2 py-0.5 rounded border border-amber-200 font-semibold">{b}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* SECTION E: SIMILAR HISTORICAL INCIDENTS */}
      {/* ==================================================================== */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center gap-2">
          <FileCheck className="h-4 w-4 text-teal-600" />
          <span>E. Similar Historical Incident Evidence (oilps_final_master_v2.csv)</span>
        </h3>

        {similar_incidents.length > 0 ? (
          <div className="space-y-2.5">
            {similar_incidents.map((sim, i) => (
              <div key={i} className="bg-slate-50 p-3 rounded border border-slate-200 text-xs space-y-1.5">
                <div className="flex justify-between items-center">
                  <span className="font-mono font-bold text-teal-700">Record #{sim.record_id}</span>
                  <span className="bg-teal-50 text-teal-800 px-2 py-0.5 rounded font-mono font-bold border border-teal-200">
                    {(sim.similarity * 100).toFixed(1)}% Cosine Similarity
                  </span>
                </div>
                <p className="text-slate-800 leading-relaxed font-sans">{sim.narrative}</p>
                <div className="flex flex-wrap gap-3 text-[11px] text-slate-500 pt-1 border-t border-slate-200">
                  <span>Location: <strong className="text-slate-800">{sim.site}</strong></span>
                  <span>Activity: <strong className="text-slate-800">{sim.activity}</strong></span>
                  <span>LSR: <strong className="text-emerald-700">{sim.lsr_labels}</strong></span>
                  <span>Provenance: <strong className="text-slate-600">{sim.provenance}</strong></span>
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
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-emerald-600" />
          <span>G. Historical Risk Intelligence Metrics</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          {/* Site Risk */}
          <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
            <span className="text-slate-500 font-semibold block mb-1 text-[11px]">Site Risk</span>
            {risk_intelligence.site.status === 'SUCCESS' ? (
              <div>
                <p className="text-slate-900 font-bold">{risk_intelligence.site.details.site_name}</p>
                <p className="text-amber-700 font-semibold">{risk_intelligence.site.details.risk_tier}</p>
                <span className="text-[11px] text-slate-500">{(risk_intelligence.site.details.sif_density * 100).toFixed(0)}% SIF Density</span>
              </div>
            ) : (
              <span className="text-amber-700 font-bold">INSUFFICIENT DATA</span>
            )}
          </div>

          {/* Activity Risk */}
          <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
            <span className="text-slate-500 font-semibold block mb-1 text-[11px]">Activity Risk</span>
            {risk_intelligence.activity.status === 'SUCCESS' ? (
              <div>
                <p className="text-slate-900 font-bold">{risk_intelligence.activity.details.activity_name}</p>
                <p className="text-amber-700 font-semibold">{risk_intelligence.activity.details.risk_tier}</p>
                <span className="text-[11px] text-slate-500">{(risk_intelligence.activity.details.sif_density * 100).toFixed(0)}% SIF Density</span>
              </div>
            ) : (
              <span className="text-amber-700 font-bold">INSUFFICIENT DATA</span>
            )}
          </div>

          {/* Early Warning */}
          <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
            <span className="text-slate-500 font-semibold block mb-1 text-[11px]">Early Warning Signal</span>
            <p className={`font-bold ${risk_intelligence.early_warning.details?.alert_level === 'WARNING' ? 'text-red-700' : 'text-emerald-700'}`}>
              {risk_intelligence.early_warning.details?.alert_level || 'NORMAL'}
            </p>
          </div>

          {/* Priority Score */}
          <div className="bg-slate-50 p-2.5 rounded border border-slate-200">
            <span className="text-slate-500 font-semibold block mb-1 text-[11px]">Priority Classification</span>
            <p className="text-slate-900 font-bold">{risk_intelligence.priority.details?.priority_rank || 'MEDIUM_PRIORITY'}</p>
            <span className="text-[11px] text-slate-500">Score: {risk_intelligence.priority.details?.priority_score || 0}/100</span>
          </div>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* SECTION H: BOW-TIE DIAGRAM MAPPING */}
      {/* ==================================================================== */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center gap-2">
          <ChevronRight className="h-4 w-4 text-blue-600" />
          <span>H. Bow-Tie Risk Barrier Chain</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-center text-xs">
          <div className="bg-blue-50/80 p-2.5 rounded border border-blue-200">
            <span className="text-[10px] text-blue-700 uppercase font-bold block mb-1">Threat</span>
            <p className="text-slate-900 font-semibold">{bowtie.threat}</p>
          </div>

          <div className="bg-red-50/80 p-2.5 rounded border border-red-200">
            <span className="text-[10px] text-red-700 uppercase font-bold block mb-1">Barrier Failure</span>
            <p className="text-slate-900 font-semibold">{bowtie.barrier_failures[0] || 'Uncontrolled Energy'}</p>
          </div>

          <div className="bg-amber-50/80 p-2.5 rounded border border-amber-200">
            <span className="text-[10px] text-amber-800 uppercase font-bold block mb-1">Top Event</span>
            <p className="text-slate-900 font-semibold">{bowtie.top_event}</p>
          </div>

          <div className="bg-purple-50/80 p-2.5 rounded border border-purple-200">
            <span className="text-[10px] text-purple-700 uppercase font-bold block mb-1">Consequences</span>
            <p className="text-slate-900 font-semibold">{bowtie.potential_consequences.join(', ')}</p>
          </div>
        </div>
      </div>

      {/* ==================================================================== */}
      {/* SECTION I & J: RAG RECOMMENDATIONS & TRACEABILITY */}
      {/* ==================================================================== */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center gap-2">
          <Info className="h-4 w-4 text-emerald-600" />
          <span>I & J. Grounded Safety Recommendations & Source Traceability</span>
        </h3>

        {recommendations.length > 0 ? (
          <div className="space-y-2.5">
            {recommendations.map((rec, i) => (
              <div key={i} className="bg-slate-50 p-3 rounded border border-slate-200 text-xs space-y-1.5">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-emerald-800 font-mono">Rule: {rec.rule}</span>
                  <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-bold border border-emerald-300">
                    {rec.status}
                  </span>
                </div>
                <p className="text-slate-800 leading-relaxed font-sans">{rec.recommendation_text}</p>
                <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-200">
                  <span>Source Guidance: <strong className="text-slate-700 font-mono">{rec.grounded_sources.join(', ')}</strong></span>
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
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-3 flex items-center gap-2">
          <HelpCircle className="h-4 w-4 text-blue-600" />
          <span>K. Explainability & Interpretation</span>
        </h3>
        <div className="bg-slate-50 p-3 rounded border border-slate-200 space-y-1.5 text-xs text-slate-700 leading-relaxed">
          <p><strong className="text-slate-900">SIF Reasoning:</strong> {explainability.sif_explanation}</p>
          <p><strong className="text-slate-900">LSR Reasoning:</strong> {explainability.lsr_explanation}</p>
          <p><strong className="text-slate-900">Risk Reasoning:</strong> {explainability.risk_explanation}</p>
          <p><strong className="text-slate-900">Triage Reasoning:</strong> {explainability.triage_explanation}</p>
        </div>
      </div>
    </div>
  );
};
