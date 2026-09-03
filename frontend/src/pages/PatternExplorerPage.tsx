import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { patternsService } from '../api';
import type { PrecursorPattern, AIRecurringPattern } from '../types/patterns';
import { PageHeader } from '../components/common/PageHeader';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Modal } from '../components/common/Modal';
import { formatPercentage } from '../utils/formatters';
import { ArrowRight, Lightbulb, ShieldAlert, Sparkles, CheckCircle, FileText } from 'lucide-react';

export const PatternExplorerPage: React.FC = () => {
  const navigate = useNavigate();
  const [aiPatterns, setAiPatterns] = useState<AIRecurringPattern[]>([]);
  const [dbPatterns, setDbPatterns] = useState<PrecursorPattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAiPattern, setSelectedAiPattern] = useState<AIRecurringPattern | null>(null);
  const [selectedDbPattern, setSelectedDbPattern] = useState<PrecursorPattern | null>(null);

  useEffect(() => {
    const fetchPatterns = async () => {
      try {
        const res = await patternsService.getPatterns();
        
        const STRENGTH_WEIGHT: Record<string, number> = { HIGH: 3, MEDIUM: 2, LOW: 1 };
        const PRIORITY_WEIGHT: Record<string, number> = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };

        const sortedAi = [...(res.ai_patterns || [])].sort((a, b) => {
          const wA = STRENGTH_WEIGHT[a.pattern_strength] || 0;
          const wB = STRENGTH_WEIGHT[b.pattern_strength] || 0;
          if (wB !== wA) return wB - wA;
          return b.incident_count - a.incident_count;
        });

        const sortedDb = [...(res.db_patterns || [])].sort((a, b) => {
          const wA = PRIORITY_WEIGHT[a.priority] || 0;
          const wB = PRIORITY_WEIGHT[b.priority] || 0;
          if (wB !== wA) return wB - wA;
          return b.reportCount - a.reportCount;
        });

        setAiPatterns(sortedAi);
        setDbPatterns(sortedDb);
      } finally {
        setLoading(false);
      }
    };
    fetchPatterns();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Clustering Precursor Patterns across Historical Safety Reports..." />;
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Precursor Pattern Explorer"
        subtitle="Unsupervised NLP clustering & hybrid similarity engine identifying recurring safety failure signatures across historical reports."
        showDemoBadge={true}
      />

      {/* AI Microservice Patterns (Stage 23 Engine) */}
      {aiPatterns.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-200">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded bg-slate-900 text-white">
                <Sparkles className="h-4 w-4 text-slate-200" />
              </div>
              <h2 className="text-sm font-bold text-slate-900">
                Stage 23 AI Recurring Precursor Patterns ({aiPatterns.length})
              </h2>
            </div>
            <span className="text-xs font-mono text-slate-500">384-dim all-MiniLM-L6-v2 Embeddings</span>
          </div>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
            {aiPatterns.map((pat) => (
              <div
                key={pat.pattern_id}
                className="hse-card flex flex-col justify-between p-5 hover:border-slate-400 transition-colors cursor-pointer border-t-4 border-t-slate-800"
                onClick={() => setSelectedAiPattern(pat)}
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <span className="font-mono text-xs font-bold text-slate-500">{pat.pattern_code || pat.pattern_id}</span>
                    <span
                      className={`rounded px-2 py-0.5 text-[10px] font-extrabold ${
                        pat.pattern_strength === 'HIGH'
                          ? 'bg-red-600 text-white'
                          : pat.pattern_strength === 'MEDIUM'
                          ? 'bg-amber-500 text-slate-950'
                          : 'bg-slate-700 text-white'
                      }`}
                    >
                      {pat.pattern_strength} STRENGTH
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-slate-900 leading-snug mb-2">
                    {pat.pattern_name}
                  </h3>

                  <p className="text-xs text-slate-600 line-clamp-3 mb-4 leading-relaxed">
                    {pat.summary}
                  </p>

                  <div className="space-y-2 border-t border-slate-100 pt-3 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Historical Support:</span>
                      <span className="font-bold text-slate-900">{pat.incident_count} Incidents</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">SIF Precursor Density:</span>
                      <span className="font-bold text-red-600">
                        {pat.incident_count > 0 ? `${Math.round((pat.sif_incident_count / pat.incident_count) * 100)}%` : '0%'} ({pat.sif_incident_count} SIF)
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Primary Rule:</span>
                      <span className="font-medium text-slate-800">{pat.dominant_lsr}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Barrier Failure:</span>
                      <span className="font-medium text-slate-800 truncate max-w-[150px]">{pat.dominant_barrier_failure}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-800 font-semibold">
                  <span>Inspect Pattern ({pat.incident_ids.length} Incidents)</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* DB Patterns (If present) */}
      {dbPatterns.length > 0 && (
        <div className="space-y-4 pt-4 border-t border-slate-200">
          <div className="flex items-center justify-between pb-2">
            <h2 className="text-sm font-bold text-slate-900">
              Operational Precursor Patterns ({dbPatterns.length})
            </h2>
          </div>

          <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
            {dbPatterns.map((pat) => (
              <div
                key={pat.id}
                className="hse-card flex flex-col justify-between p-5 hover:border-slate-400 transition-colors cursor-pointer"
                onClick={() => setSelectedDbPattern(pat)}
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <span className="font-mono text-xs font-bold text-slate-500">{pat.id}</span>
                    <SeverityBadge priority={pat.priority} size="sm" />
                  </div>

                  <h3 className="text-sm font-bold text-slate-900 leading-snug mb-2">
                    {pat.name}
                  </h3>

                  <p className="text-xs text-slate-600 line-clamp-3 mb-4">
                    {pat.description}
                  </p>

                  <div className="space-y-2 border-t border-slate-100 pt-3 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Incident Frequency:</span>
                      <span className="font-bold text-slate-900">{pat.reportCount} Reports</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">SIF Probability:</span>
                      <span className="font-bold text-red-600">
                        {formatPercentage(pat.sifPotentialRate)}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-800 font-semibold">
                  <span>Inspect Pattern ({pat.matchedReportIds.length} Linked)</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Pattern Detail Modal */}
      {selectedAiPattern && (
        <Modal
          isOpen={!!selectedAiPattern}
          onClose={() => setSelectedAiPattern(null)}
          title={`Pattern ${selectedAiPattern.pattern_code || selectedAiPattern.pattern_id}: ${selectedAiPattern.pattern_name}`}
          subtitle={`Discovered across ${selectedAiPattern.incident_count} incidents (SIF Density: ${formatPercentage(selectedAiPattern.sif_density)})`}
          maxWidth="2xl"
          footer={
            <button
              onClick={() => setSelectedAiPattern(null)}
              className="rounded bg-slate-900 px-4 py-1.5 text-xs font-semibold text-white"
            >
              Close
            </button>
          }
        >
          <div className="space-y-4 text-xs text-slate-800">
            <div>
              <span className="font-semibold text-slate-700 block mb-1">Pattern Summary & Scope</span>
              <p className="text-slate-700 bg-slate-50 p-3 rounded border border-slate-200 leading-relaxed font-medium">
                {selectedAiPattern.summary}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="border border-slate-200 p-3 rounded bg-white space-y-1.5">
                <span className="font-semibold text-slate-700 block text-[11px] uppercase">Structured Safety Dimensions</span>
                <div><span className="text-slate-500">Activity:</span> <span className="font-bold text-slate-900">{selectedAiPattern.dominant_activity}</span></div>
                <div><span className="text-slate-500">Life-Saving Rule:</span> <span className="font-bold text-slate-900">{selectedAiPattern.dominant_lsr}</span></div>
                <div><span className="text-slate-500">Hazard:</span> <span className="font-bold text-slate-900">{selectedAiPattern.dominant_hazard}</span></div>
                <div><span className="text-slate-500">Barrier Failure:</span> <span className="font-bold text-amber-700">{selectedAiPattern.dominant_barrier_failure}</span></div>
              </div>

              <div className="border border-slate-200 p-3 rounded bg-white space-y-1.5">
                <span className="font-semibold text-slate-700 block text-[11px] uppercase">Traceability & Observed Window</span>
                <div><span className="text-slate-500">First Observed:</span> <span className="font-mono text-slate-800">{selectedAiPattern.first_observed}</span></div>
                <div><span className="text-slate-500">Last Observed:</span> <span className="font-mono text-slate-800">{selectedAiPattern.last_observed}</span></div>
                <div><span className="text-slate-500">Affected Sites:</span> <span className="font-semibold text-slate-900">{selectedAiPattern.locations.join(', ')}</span></div>
              </div>
            </div>

            {selectedAiPattern.evidence_quotes && selectedAiPattern.evidence_quotes.length > 0 && (
              <div className="border-t border-slate-200 pt-3">
                <span className="font-semibold text-slate-700 block mb-2">Representative Evidence Snippets:</span>
                <div className="space-y-2">
                  {selectedAiPattern.evidence_quotes.map((quote, idx) => (
                    <div key={idx} className="p-2.5 rounded bg-slate-50 border border-slate-200 text-slate-600 italic text-[11px] leading-relaxed">
                      &quot;{quote}&quot;
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="border-t border-slate-200 pt-3">
              <span className="font-semibold text-slate-700 block mb-2">Traceable Incident IDs ({selectedAiPattern.incident_ids.length}):</span>
              <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto p-2 bg-slate-50 rounded border border-slate-200 font-mono text-xs">
                {selectedAiPattern.incident_ids.map((id) => (
                  <span key={id} className="px-2 py-0.5 bg-white border border-slate-200 rounded text-slate-800 font-bold">
                    {id}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </Modal>
      )}

      {/* DB Pattern Detail Modal */}
      {selectedDbPattern && (
        <Modal
          isOpen={!!selectedDbPattern}
          onClose={() => setSelectedDbPattern(null)}
          title={`Pattern ${selectedDbPattern.id}: ${selectedDbPattern.name}`}
          subtitle={`Detected across ${selectedDbPattern.reportCount} incident narratives`}
          maxWidth="2xl"
          footer={
            <button
              onClick={() => setSelectedDbPattern(null)}
              className="rounded bg-slate-900 px-4 py-1.5 text-xs font-semibold text-white"
            >
              Close
            </button>
          }
        >
          <div className="space-y-4 text-xs text-slate-800">
            <p className="text-slate-600 bg-slate-50 p-3 rounded border border-slate-200">
              {selectedDbPattern.description}
            </p>
          </div>
        </Modal>
      )}
    </div>
  );
};
