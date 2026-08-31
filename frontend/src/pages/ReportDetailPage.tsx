import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { reportsService } from '../api';
import type { SafetyReport } from '../types/reports';
import { useAuth } from '../context/AuthContext';
import { PageHeader } from '../components/common/PageHeader';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { formatDate, formatScore } from '../utils/formatters';
import { IOGP_LIFE_SAVING_RULES } from '../utils/iogpRules';
import { ArrowLeft, Sparkles, AlertTriangle, FileText, MapPin, Building, User, ChevronRight, RefreshCw, ExternalLink } from 'lucide-react';

import { SafetyIntelligenceView } from '../components/SafetyIntelligenceView';

export const ReportDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { hasPermission } = useAuth();

  const [report, setReport] = useState<SafetyReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  const fetchReport = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await reportsService.getReportById(id);
      setReport(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [id]);

  const handleTriggerAnalysis = async () => {
    if (!id) return;
    setAnalyzing(true);
    try {
      await reportsService.analyzeReport(id);
      await fetchReport();
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading || !report) {
    return <LoadingSpinner label="Loading Safety Report & NLP Precursor Pipeline..." />;
  }

  const ai = report.ai_result;
  // Multiple Life-Saving Rules matched for this report
  const matchedRules = ai?.life_saving_rules || [];

  return (
    <div className="space-y-6">
      {/* Top Header & Breadcrumbs */}
      <div>
        <button
          onClick={() => navigate('/reports')}
          className="inline-flex items-center gap-1 text-xs font-semibold text-slate-600 hover:text-slate-950 mb-3"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Back to Reports List</span>
        </button>

        <PageHeader
          title={`Report ${report.id}: ${report.title}`}
          subtitle={`Submitted on ${formatDate(report.date)} for ${report.site} (${report.department})`}
          badge={<SeverityBadge sifStatus={report.sif_status} />}
          showDemoBadge={true}
          actions={
            hasPermission('canTriggerAIAnalysis') && (
              <button
                onClick={handleTriggerAnalysis}
                disabled={analyzing}
                className="flex items-center gap-1.5 rounded bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800 disabled:opacity-50 transition-colors shadow-xs"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${analyzing ? 'animate-spin' : ''}`} />
                <span>{analyzing ? 'Executing NLP Classifier...' : 'Trigger AI Re-Analysis'}</span>
              </button>
            )
          }
        />
      </div>

      {/* Visual End-to-End SIF Reasoning Chain */}
      <div className="hse-card p-4 bg-slate-900 text-white">
        <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-800">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
            End-to-End Decision Support Reasoning Chain
          </span>
          <span className="text-[10px] text-slate-400">SIH26165 Pipeline</span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-6 gap-2 text-center text-xs">
          <div className="rounded bg-slate-800 p-2 border border-slate-700">
            <span className="block text-[10px] text-slate-400 uppercase">1. Ingested Report</span>
            <span className="font-semibold text-white truncate block mt-0.5">{report.id}</span>
          </div>

          <div className="rounded bg-slate-800 p-2 border border-slate-700">
            <span className="block text-[10px] text-slate-400 uppercase">2. SIF Potential</span>
            <span className={`font-bold mt-0.5 block ${report.sif_status === 'SIF_POTENTIAL' ? 'text-red-400' : 'text-emerald-400'}`}>
              {report.sif_status === 'SIF_POTENTIAL' ? 'SIF DETECTED' : 'NON-SIF'}
            </span>
          </div>

          <div className="rounded bg-slate-800 p-2 border border-slate-700">
            <span className="block text-[10px] text-slate-400 uppercase">3. Activity / Hazard</span>
            <span className="font-medium text-slate-200 truncate block mt-0.5">
              {ai?.precursors?.activity || report.activity}
            </span>
          </div>

          <div className="rounded bg-slate-800 p-2 border border-slate-700">
            <span className="block text-[10px] text-slate-400 uppercase">4. Barrier Failure</span>
            <span className="font-medium text-amber-300 truncate block mt-0.5">
              {ai?.precursors?.barrier_failure || 'Under Inspection'}
            </span>
          </div>

          {/* Implicated Life-Saving Rules (Supporting Multiple Rules) */}
          <div className="rounded bg-slate-800 p-2 border border-slate-700">
            <span className="block text-[10px] text-slate-400 uppercase">5. Life-Saving Rule(s)</span>
            <span className="font-semibold text-white truncate block mt-0.5" title={matchedRules.map(r => r.name).join(', ') || report.life_saving_rule}>
              {matchedRules.length > 0
                ? matchedRules.map(r => r.name).join(' + ')
                : report.life_saving_rule}
            </span>
          </div>

          <div className="rounded bg-slate-800 p-2 border border-slate-700">
            <span className="block text-[10px] text-slate-400 uppercase">6. Priority Action</span>
            <span className="font-bold text-white truncate block mt-0.5">
              {report.priority} PRIORITY
            </span>
          </div>
        </div>
      </div>

      {/* Main 2-Column Layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left Column (7 Cols) */}
        <div className="space-y-6 lg:col-span-7">
          <div className="hse-card p-5">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 pb-2 border-b border-slate-100">
              Operational Metadata & Location
            </h2>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-slate-500 block">Asset Site:</span>
                <div className="flex items-center gap-1.5 mt-0.5 font-semibold text-slate-900">
                  <MapPin className="h-3.5 w-3.5 text-slate-500" />
                  <span>{report.site}</span>
                </div>
              </div>
              <div>
                <span className="text-slate-500 block">Department / Unit:</span>
                <div className="flex items-center gap-1.5 mt-0.5 font-semibold text-slate-900">
                  <Building className="h-3.5 w-3.5 text-slate-500" />
                  <span>{report.department}</span>
                </div>
              </div>
              <div>
                <span className="text-slate-500 block">Reporting Officer:</span>
                <div className="flex items-center gap-1.5 mt-0.5 font-semibold text-slate-900">
                  <User className="h-3.5 w-3.5 text-slate-500" />
                  <span>{report.reporter_name} ({report.reporter_role || 'Field Staff'})</span>
                </div>
              </div>
              <div>
                <span className="text-slate-500 block">Investigation Status:</span>
                <div className="mt-0.5 font-semibold text-slate-900">
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-800 border border-slate-200">
                    {report.investigation_status || 'Open'}
                  </span>
                </div>
              </div>
            </div>

            {report.location_detail && (
              <div className="mt-3 pt-3 border-t border-slate-100 text-xs">
                <span className="text-slate-500">Specific Location / Equipment Tag:</span>
                <p className="mt-0.5 font-mono font-medium text-slate-800">{report.location_detail}</p>
              </div>
            )}
          </div>

          <div className="hse-card p-5">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-slate-700" />
                <h2 className="text-sm font-bold text-slate-900">Original Free-Text Report Narrative</h2>
              </div>
              <span className="text-[10px] text-slate-400">Raw Input Text</span>
            </div>

            <div className="rounded border border-slate-200 bg-slate-50/70 p-4 font-mono text-xs text-slate-800 leading-relaxed whitespace-pre-wrap">
              {report.description}
            </div>

            {report.immediate_actions_taken && (
              <div className="mt-4 pt-4 border-t border-slate-100">
                <span className="text-xs font-semibold text-slate-700 block mb-1">
                  Immediate Containment Actions Taken on Site:
                </span>
                <p className="text-xs text-slate-600 bg-emerald-50/60 border border-emerald-200 p-2.5 rounded">
                  {report.immediate_actions_taken}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column (5 Cols) */}
        <div className="space-y-6 lg:col-span-5">
          {ai?.full_ai_response ? (
            <SafetyIntelligenceView data={ai.full_ai_response} />
          ) : ai ? (
            <div className="hse-card p-5 border-slate-300">
              <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-200">
                <div className="flex items-center gap-2">
                  <div className="rounded bg-slate-900 p-1.5 text-white">
                    <Sparkles className="h-4 w-4 text-slate-200" />
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-slate-900">AI Precursor Analysis</h2>
                    <span className="text-[10px] text-slate-500">Model: {ai.model_version || 'SIF-NLP-v2.4'}</span>
                  </div>
                </div>
                <SeverityBadge sifStatus={ai.sif.label} />
              </div>

              <div className="grid grid-cols-2 gap-3 mb-4 p-3 rounded bg-slate-50 border border-slate-200">
                <div>
                  <span className="text-[10px] font-semibold uppercase text-slate-500">SIF Confidence</span>
                  <div className="mt-0.5 text-xl font-bold text-slate-900">
                    {formatScore(ai.sif.score)}
                  </div>
                  <div className="text-[10px] text-slate-500">NLP Probability</div>
                </div>
                <div>
                  <span className="text-[10px] font-semibold uppercase text-slate-500">Assigned Priority</span>
                  <div className="mt-1">
                    <SeverityBadge priority={ai.priority} size="sm" />
                  </div>
                </div>
              </div>

              <div className="space-y-3 mb-5">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Extracted Precursor Dimensions
                </h3>

                <div className="rounded border border-slate-200 p-2.5 text-xs space-y-2 bg-white">
                  <div>
                    <span className="text-slate-500 text-[11px] block">Activity Underway:</span>
                    <span className="font-semibold text-slate-900">{ai.precursors.activity}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[11px] block">High-Energy Hazard:</span>
                    <span className="font-semibold text-slate-900">{ai.precursors.hazard}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[11px] block">Barrier Failure Identified:</span>
                    <span className="font-semibold text-amber-700">{ai.precursors.barrier_failure}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[11px] block">Potential Worst-Case Consequence:</span>
                    <span className="font-semibold text-red-700">{ai.precursors.potential_consequence}</span>
                  </div>
                </div>
              </div>

              {/* Multiple IOGP Life-Saving Rules Mapping */}
              <div className="space-y-2 mb-5">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    IOGP Life-Saving Rules Mapped ({matchedRules.length})
                  </h3>
                  <button
                    onClick={() => navigate('/life-saving-rules')}
                    className="text-[11px] text-slate-600 hover:text-slate-900 flex items-center gap-0.5"
                  >
                    <span>All Rules</span>
                    <ChevronRight className="h-3 w-3" />
                  </button>
                </div>

                <div className="space-y-2.5">
                  {matchedRules.map((rule, idx) => {
                    const ruleMeta = IOGP_LIFE_SAVING_RULES[rule.name];
                    return (
                      <div key={idx} className="rounded border border-slate-200 p-3 bg-slate-50 space-y-2">
                        <div className="flex items-center justify-between text-xs font-semibold text-slate-900">
                          <div className="flex items-center gap-1.5">
                            <span className="font-bold text-slate-900">{rule.name}</span>
                            {ruleMeta && (
                              <span className="rounded bg-slate-200 px-1.5 py-0.2 text-[10px] text-slate-700 font-mono">
                                {ruleMeta.id}
                              </span>
                            )}
                          </div>
                          <span className="text-slate-700 font-bold">{formatScore(rule.score)} confidence</span>
                        </div>

                        {/* Progress Bar */}
                        <div className="h-1.5 w-full rounded-full bg-slate-200 overflow-hidden">
                          <div
                            className={`h-full ${rule.score >= 0.8 ? 'bg-red-600' : 'bg-slate-700'}`}
                            style={{ width: `${rule.score * 100}%` }}
                          />
                        </div>

                        {ruleMeta && (
                          <div className="text-[11px] text-slate-600 pt-1 border-t border-slate-200/60">
                            <p className="italic mb-1">&quot;{ruleMeta.description}&quot;</p>
                            <span className="text-[10px] text-slate-500 font-semibold">Key Barrier:</span>
                            <span className="text-[10px] text-slate-600 block">{ruleMeta.mandatoryRequirements[0]}</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* NLP Explanation Text */}
              <div className="space-y-2 mb-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  AI Decision Support Explanation
                </h3>
                <div className="rounded border border-slate-200 bg-slate-50 p-3 text-xs text-slate-700 leading-relaxed">
                  {ai.explanation}
                </div>
              </div>

              {/* Associated Pattern Links */}
              {ai.patterns && ai.patterns.length > 0 && (
                <div className="pt-3 border-t border-slate-200">
                  <span className="text-[11px] font-semibold text-slate-500 block mb-1.5">
                    Associated Precursor Pattern:
                  </span>
                  {ai.patterns.map((pat, idx) => (
                    <button
                      key={idx}
                      onClick={() => navigate('/patterns')}
                      className="flex w-full items-center justify-between rounded bg-slate-100 hover:bg-slate-200 p-2 text-xs text-slate-800 transition-colors font-medium text-left"
                    >
                      <span className="truncate">{pat}</span>
                      <ExternalLink className="h-3.5 w-3.5 flex-shrink-0 ml-1 text-slate-500" />
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="hse-card p-6 text-center">
              <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2" />
              <h3 className="text-sm font-bold text-slate-900">AI Analysis Pending</h3>
              <p className="mt-1 text-xs text-slate-500">
                This report has not yet been processed by the NLP Precursor classifier.
              </p>
              {hasPermission('canTriggerAIAnalysis') && (
                <button
                  onClick={handleTriggerAnalysis}
                  disabled={analyzing}
                  className="mt-4 rounded bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white"
                >
                  Run Analysis Pipeline
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
