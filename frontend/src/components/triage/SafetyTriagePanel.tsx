import React, { useState, useEffect } from 'react';
import { triageService } from '../../api';
import type { TriageResult } from '../../types/triage';
import { AlertOctagon, AlertTriangle, CheckCircle, Info, Shield, Scale, Activity } from 'lucide-react';

interface SafetyTriagePanelProps {
  reportId: string;
  rawSifProb?: number;
  priorityLevel?: string;
  priorityScore?: number;
  earlyWarningLevel?: string;
  riskMatrixCategory?: string;
}

export const SafetyTriagePanel: React.FC<SafetyTriagePanelProps> = ({
  reportId,
  rawSifProb = 0.50,
  priorityLevel = 'MEDIUM',
  priorityScore = 0.50,
  earlyWarningLevel = 'NORMAL',
  riskMatrixCategory = 'LOW_SEVERITY_LOW_RECURRENCE'
}) => {
  const [triage, setTriage] = useState<TriageResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTriage = async () => {
      setLoading(true);
      try {
        const res = await triageService.evaluateTriage({
          report_id: reportId,
          raw_sif_probability: rawSifProb,
          priority_level: priorityLevel,
          priority_score: priorityScore,
          early_warning_level: earlyWarningLevel,
          risk_matrix_category: riskMatrixCategory
        });
        if (res) {
          setTriage(res);
        }
      } catch (err) {
        console.warn('Failed to load triage decision:', err);
      } finally {
        setLoading(false);
      }
    };

    if (reportId) {
      loadTriage();
    }
  }, [reportId, rawSifProb, priorityLevel, priorityScore, earlyWarningLevel, riskMatrixCategory]);

  if (loading) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 animate-pulse text-xs text-slate-500">
        Evaluating confidence-calibrated operational safety triage...
      </div>
    );
  }

  if (!triage) return null;

  const isEscalation = triage.triage_level === 'IMMEDIATE_ESCALATION';
  const isNeedsReview = triage.triage_level === 'NEEDS_REVIEW';
  const isAutoClear = triage.triage_level === 'AUTO_CLEAR';

  return (
    <div
      className={`rounded-lg border p-4 transition-all ${
        isEscalation
          ? 'bg-red-50/80 border-red-300'
          : isNeedsReview
          ? 'bg-amber-50/80 border-amber-300'
          : 'bg-emerald-50/80 border-emerald-300'
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {isEscalation && <AlertOctagon className="h-5 w-5 text-red-600 animate-bounce" />}
          {isNeedsReview && <AlertTriangle className="h-5 w-5 text-amber-600" />}
          {isAutoClear && <CheckCircle className="h-5 w-5 text-emerald-600" />}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Stage 34 — Operational Safety Triage
            </h4>
            <span
              className={`text-sm font-extrabold flex items-center gap-1.5 ${
                isEscalation ? 'text-red-900' : isNeedsReview ? 'text-amber-900' : 'text-emerald-900'
              }`}
            >
              {isEscalation && '🔴 IMMEDIATE ESCALATION'}
              {isNeedsReview && '🟡 NEEDS REVIEW'}
              {isAutoClear && '🟢 AUTO-CLEAR'}
            </span>
          </div>
        </div>

        <div className="text-right">
          <span className="text-[10px] font-bold text-slate-500 block uppercase">Policy Version</span>
          <span className="text-xs font-mono font-bold text-slate-800">{triage.policy_version}</span>
        </div>
      </div>

      {/* Probabilities & Calibration Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3 bg-white/80 p-2.5 rounded border border-slate-200 text-xs">
        <div>
          <span className="text-[10px] text-slate-500 font-semibold block">Raw SIF Probability</span>
          <span className="font-mono font-bold text-slate-800">
            {(triage.sif_raw_probability * 100).toFixed(1)}%
          </span>
        </div>

        <div>
          <span className="text-[10px] text-slate-500 font-semibold block flex items-center gap-1">
            <Scale className="h-3 w-3 text-indigo-600" /> Calibrated SIF
          </span>
          <span className="font-mono font-bold text-indigo-900">
            {(triage.sif_calibrated_probability * 100).toFixed(1)}%
          </span>
        </div>

        <div>
          <span className="text-[10px] text-slate-500 font-semibold block">Calibration Status</span>
          <span
            className={`font-semibold text-[11px] ${
              triage.calibration_status === 'ACTIVE' ? 'text-emerald-700' : 'text-amber-700'
            }`}
          >
            {triage.calibration_status}
          </span>
        </div>

        <div>
          <span className="text-[10px] text-slate-500 font-semibold block">Method</span>
          <span className="font-mono text-slate-700 uppercase text-[11px]">
            {triage.calibration_method}
          </span>
        </div>
      </div>

      {/* Triage Decision Reason */}
      <div className="bg-white/90 p-2.5 rounded border border-slate-200 text-xs text-slate-800 space-y-1">
        <div className="flex items-center justify-between">
          <span className="font-bold text-slate-900 flex items-center gap-1">
            <Info className="h-3.5 w-3.5 text-blue-600" /> Triage Reason:
          </span>
          <code className="bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded text-[10px] font-mono font-bold">
            {triage.reason_code}
          </code>
        </div>
        <p className="text-slate-700 leading-relaxed text-[11px]">
          {triage.human_readable_reason}
        </p>
      </div>

      {/* Upstream Risk Context Badges */}
      <div className="mt-2.5 flex flex-wrap items-center justify-between gap-2 text-[10px]">
        <div className="flex flex-wrap items-center gap-2">
          <span className="bg-slate-200 text-slate-800 font-bold px-2 py-0.5 rounded">
            Priority: {triage.priority_level} ({triage.priority_score.toFixed(2)})
          </span>
          <span className="bg-slate-200 text-slate-800 font-bold px-2 py-0.5 rounded">
            Early Warning: {triage.early_warning_level}
          </span>
          <span className="bg-slate-200 text-slate-800 font-bold px-2 py-0.5 rounded">
            Matrix: {triage.risk_matrix_category}
          </span>
        </div>

        {(isNeedsReview || isEscalation) && (
          <button
            onClick={() => {
              const el = document.getElementById('analyst-feedback-section');
              if (el) el.scrollIntoView({ behavior: 'smooth' });
            }}
            className="px-2.5 py-1 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded text-[10px] transition-colors"
          >
            Open Analyst Review →
          </button>
        )}
      </div>
    </div>
  );
};
