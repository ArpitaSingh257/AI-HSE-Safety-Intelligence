import React from 'react';
import type { FastApiIncidentAnalysisResponse } from '../types/reports';
import { AlertTriangle, CheckCircle, ShieldAlert, FileText, ExternalLink, Info, Lock } from 'lucide-react';

interface SafetyIntelligenceViewProps {
  data: FastApiIncidentAnalysisResponse;
}

export const SafetyIntelligenceView: React.FC<SafetyIntelligenceViewProps> = ({ data }) => {
  const exp = data.explainability;
  const recs = data.recommendations;
  const sif = data.sif;
  const lsr = data.lsr;

  const isCritical = recs.priority === 'CRITICAL' || sif.risk_tier === 'CRITICAL_SIF_PRECURSOR';
  const isHigh = recs.priority === 'HIGH' || sif.risk_tier === 'ELEVATED_SIF_POTENTIAL';

  // Grounding status styling
  const groundingStatus = recs.status || 'GROUNDED';
  const isGrounded = groundingStatus === 'GROUNDED';
  const isPartiallyGrounded = groundingStatus === 'PARTIALLY_GROUNDED';

  return (
    <div className="space-y-6">
      {/* Top Banner — Safety Intelligence Header */}
      <div className={`hse-card p-5 border-l-4 ${isCritical ? 'border-l-red-600 bg-slate-900 text-white' : isHigh ? 'border-l-amber-500 bg-slate-900 text-white' : 'border-l-emerald-500 bg-slate-900 text-white'}`}>
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className={`p-2 rounded ${isCritical ? 'bg-red-600/30 text-red-400' : 'bg-emerald-600/30 text-emerald-400'}`}>
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-base font-bold tracking-tight">EXPLAINABLE SAFETY INTELLIGENCE</h2>
              <span className="text-[11px] text-slate-400">OILPS AI Safety Engine (Stage 21 Frozen Core)</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Grounding Status Badge */}
            <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ${
              isGrounded
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                : isPartiallyGrounded
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                : 'bg-orange-500/20 text-orange-300 border border-orange-500/40'
            }`}>
              <CheckCircle className="h-3.5 w-3.5" />
              <span>{groundingStatus.replace(/_/g, ' ')}</span>
            </span>

            {/* Risk Level Badge */}
            <span className={`inline-flex items-center gap-1 rounded px-3 py-1 text-xs font-bold ${
              isCritical
                ? 'bg-red-600 text-white'
                : isHigh
                ? 'bg-amber-500 text-slate-950'
                : 'bg-emerald-600 text-white'
            }`}>
              {exp?.risk_level_display || (isCritical ? '🔴 CRITICAL' : '🟢 LOW')}
            </span>
          </div>
        </div>

        {/* SIF Potential & Non-Technical Summary */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded bg-slate-800/80 p-3 border border-slate-700/80">
            <span className="block text-[10px] uppercase font-semibold text-slate-400">SIF Precursor Probability</span>
            <div className="mt-1 flex items-baseline gap-2">
              <span className={`text-2xl font-extrabold ${sif.is_sif ? 'text-red-400' : 'text-emerald-400'}`}>
                {(sif.probability * 100).toFixed(1)}%
              </span>
              <span className="text-xs text-slate-400">({sif.is_sif ? 'SIF DETECTED' : 'LOW RISK'})</span>
            </div>
          </div>

          <div className="md:col-span-2 rounded bg-slate-800/80 p-3 border border-slate-700/80">
            <span className="block text-[10px] uppercase font-semibold text-slate-400">Safety Assessment</span>
            <p className="mt-1 text-xs text-slate-200 leading-relaxed font-medium">
              {exp?.sif_interpretation || recs.summary}
            </p>
          </div>
        </div>
      </div>

      {/* Why Was This Flagged? */}
      {exp?.why_flagged && exp.why_flagged.length > 0 && (
        <div className="hse-card p-5">
          <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
            <AlertTriangle className="h-4 w-4 text-amber-600" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Why Was This Flagged?
            </h3>
          </div>
          <ul className="space-y-2 text-xs">
            {exp.why_flagged.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-200/80">
                <span className="h-1.5 w-1.5 rounded-full bg-slate-600 mt-1.5 flex-shrink-0" />
                <span className="leading-relaxed">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Life-Saving Rules Activated */}
      {exp?.lsr_explanations && exp.lsr_explanations.length > 0 && (
        <div className="hse-card p-5">
          <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
            <Lock className="h-4 w-4 text-slate-700" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
              Life-Saving Rules Activated ({exp.lsr_explanations.length})
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {exp.lsr_explanations.map((rule, idx) => (
              <div key={idx} className="rounded border border-slate-200 bg-slate-50/80 p-3 text-xs space-y-1.5">
                <div className="flex items-center justify-between font-bold text-slate-900">
                  <span>{rule.rule}</span>
                  <span className="text-slate-600 font-mono text-[11px]">{rule.model_probability}</span>
                </div>
                <p className="text-slate-600 text-[11px] leading-relaxed">
                  {rule.why_triggered}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actionable Safety Guidance */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Immediate Actions */}
        <div className="hse-card p-5 border-t-2 border-t-red-600">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3 pb-2 border-b border-slate-100 flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-red-600" />
            Immediate Actions
          </h3>
          <ul className="space-y-2 text-xs">
            {(recs.immediate_actions || []).map((action, idx) => (
              <li key={idx} className="flex items-start gap-2 text-slate-800 bg-red-50/50 p-2.5 rounded border border-red-100">
                <span className="font-bold text-red-600 flex-shrink-0">{idx + 1}.</span>
                <span className="leading-relaxed font-medium">{action}</span>
              </li>
            ))}
            {(!recs.immediate_actions || recs.immediate_actions.length === 0) && (
              <p className="text-xs text-slate-500 italic">No immediate high-risk containment actions required.</p>
            )}
          </ul>
        </div>

        {/* Verify Before Resuming */}
        <div className="hse-card p-5 border-t-2 border-t-amber-500">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3 pb-2 border-b border-slate-100 flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-amber-500" />
            Verify Before Resuming
          </h3>
          <ul className="space-y-2 text-xs">
            {(recs.verification_actions || recs.control_verification || []).map((action, idx) => (
              <li key={idx} className="flex items-start gap-2 text-slate-800 bg-amber-50/50 p-2.5 rounded border border-amber-100">
                <span className="font-bold text-amber-600 flex-shrink-0">✓</span>
                <span className="leading-relaxed font-medium">{action}</span>
              </li>
            ))}
            {(!recs.verification_actions || recs.verification_actions.length === 0) && (
              <p className="text-xs text-slate-500 italic">Standard job safety verification applies.</p>
            )}
          </ul>
        </div>

        {/* Escalation Protocol */}
        <div className="hse-card p-5 border-t-2 border-t-slate-700">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 mb-3 pb-2 border-b border-slate-100 flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-slate-700" />
            Escalation Protocol
          </h3>
          <ul className="space-y-2 text-xs">
            {(recs.escalation_actions || recs.escalation || []).map((action, idx) => (
              <li key={idx} className="flex items-start gap-2 text-slate-800 bg-slate-50 p-2.5 rounded border border-slate-200">
                <span className="font-bold text-slate-700 flex-shrink-0">➔</span>
                <span className="leading-relaxed font-medium">{action}</span>
              </li>
            ))}
            {(!recs.escalation_actions || recs.escalation_actions.length === 0) && (
              <p className="text-xs text-slate-500 italic">Notify line supervisor per standard site procedures.</p>
            )}
          </ul>
        </div>
      </div>

      {/* Grounded Evidence Sources */}
      {recs.sources && recs.sources.length > 0 && (
        <div className="hse-card p-5">
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-slate-700" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                Authoritative Grounding Evidence Sources ({recs.sources.length})
              </h3>
            </div>
            <span className="text-[10px] text-slate-500">FAISS Cosine Similarity Search</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {recs.sources.map((src, idx) => (
              <div key={idx} className="rounded border border-slate-200 bg-slate-50/70 p-3 text-xs space-y-1.5">
                <div className="flex items-center justify-between font-semibold text-slate-900">
                  <span className="font-bold text-slate-800 truncate">{src.document}</span>
                  <span className="text-[10px] font-mono rounded bg-slate-200 px-1.5 py-0.5 text-slate-700">
                    Page {src.page}
                  </span>
                </div>
                <p className="text-slate-600 italic text-[11px] leading-relaxed line-clamp-3 bg-white p-2 rounded border border-slate-200/60">
                  &quot;{src.snippet}&quot;
                </p>
                <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1">
                  <span>Section: {src.section}</span>
                  <span className="font-bold text-slate-700">{(src.similarity * 100).toFixed(0)}% Match</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Disclaimer Footer */}
      {recs.disclaimer && (
        <div className="rounded bg-slate-100 p-3 border border-slate-200 text-[11px] text-slate-600 flex items-start gap-2">
          <Info className="h-4 w-4 text-slate-500 flex-shrink-0 mt-0.5" />
          <p className="leading-relaxed">{recs.disclaimer}</p>
        </div>
      )}
    </div>
  );
};
