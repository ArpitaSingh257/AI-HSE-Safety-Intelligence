import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { patternsService } from '../api';
import type { PrecursorPattern } from '../types/patterns';
import { PageHeader } from '../components/common/PageHeader';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Modal } from '../components/common/Modal';
import { formatPercentage } from '../utils/formatters';
import {
  ArrowRight,
  Lightbulb,
} from 'lucide-react';

export const PatternExplorerPage: React.FC = () => {
  const navigate = useNavigate();
  const [patterns, setPatterns] = useState<PrecursorPattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPattern, setSelectedPattern] = useState<PrecursorPattern | null>(null);

  useEffect(() => {
    const fetchPatterns = async () => {
      try {
        const data = await patternsService.getPatterns();
        setPatterns(data);
      } finally {
        setLoading(false);
      }
    };
    fetchPatterns();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Clustering Precursor Patterns across OIL Assets..." />;
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Precursor Pattern Explorer"
        subtitle="Unsupervised NLP clustering identifying recurring barrier breakdowns and systemic failure signatures."
        showDemoBadge={true}
      />

      {/* Pattern Grid */}
      <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
        {patterns.map((pat) => (
          <div
            key={pat.id}
            className="hse-card flex flex-col justify-between p-5 hover:border-slate-400 transition-colors cursor-pointer"
            onClick={() => setSelectedPattern(pat)}
          >
            <div>
              {/* Card Header */}
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className="font-mono text-xs font-bold text-slate-500">{pat.id}</span>
                <div className="flex items-center gap-1.5">
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
                      pat.trendStatus === 'SURGING'
                        ? 'bg-red-100 text-red-800'
                        : pat.trendStatus === 'RECURRING'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-slate-100 text-slate-700'
                    }`}
                  >
                    {pat.trendStatus}
                  </span>
                  <SeverityBadge priority={pat.priority} size="sm" />
                </div>
              </div>

              <h2 className="text-sm font-bold text-slate-900 leading-snug mb-2">
                {pat.name}
              </h2>

              <p className="text-xs text-slate-600 line-clamp-3 mb-4">
                {pat.description}
              </p>

              {/* Pattern Metrics */}
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
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Main Activity:</span>
                  <span className="font-medium text-slate-800">{pat.mainActivity}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-500">Most Affected Site:</span>
                  <span className="font-medium text-slate-800">{pat.mostAffectedSite}</span>
                </div>
              </div>
            </div>

            {/* Footer Action */}
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-700 font-semibold">
              <span>Inspect Cluster ({pat.matchedReportIds.length} Linked)</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </div>
          </div>
        ))}
      </div>

      {/* Pattern Detail Modal */}
      {selectedPattern && (
        <Modal
          isOpen={!!selectedPattern}
          onClose={() => setSelectedPattern(null)}
          title={`Pattern ${selectedPattern.id}: ${selectedPattern.name}`}
          subtitle={`Detected across ${selectedPattern.reportCount} incident narratives (SIF Potential: ${formatPercentage(selectedPattern.sifPotentialRate)})`}
          maxWidth="2xl"
          footer={
            <button
              onClick={() => setSelectedPattern(null)}
              className="rounded bg-slate-900 px-4 py-1.5 text-xs font-semibold text-white"
            >
              Close
            </button>
          }
        >
          <div className="space-y-4 text-xs text-slate-800">
            <div>
              <span className="font-semibold text-slate-700 block mb-1">Pattern Signature Summary</span>
              <p className="text-slate-600 bg-slate-50 p-3 rounded border border-slate-200">
                {selectedPattern.description}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="border border-slate-200 p-3 rounded bg-white">
                <span className="font-semibold text-slate-700 block mb-1.5">Common Barrier Failures</span>
                <ul className="list-disc list-inside space-y-1 text-slate-600 text-[11px]">
                  {selectedPattern.commonBarrierFailures.map((bf, idx) => (
                    <li key={idx}>{bf}</li>
                  ))}
                </ul>
              </div>

              <div className="border border-slate-200 p-3 rounded bg-white">
                <span className="font-semibold text-slate-700 block mb-1.5">Associated Hazards</span>
                <ul className="list-disc list-inside space-y-1 text-slate-600 text-[11px]">
                  {selectedPattern.keyHazards.map((hz, idx) => (
                    <li key={idx}>{hz}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="border-t border-slate-200 pt-3">
              <div className="flex items-center gap-1.5 font-semibold text-slate-900 mb-1">
                <Lightbulb className="h-4 w-4 text-amber-600" />
                <span>Recommended Systemic HSE Intervention:</span>
              </div>
              <p className="text-xs text-slate-700 bg-amber-50/60 border border-amber-200 p-3 rounded">
                {selectedPattern.recommendedIntervention}
              </p>
            </div>

            <div className="border-t border-slate-200 pt-3">
              <span className="font-semibold text-slate-700 block mb-2">Sample Linked Reports in this Cluster:</span>
              <div className="space-y-1.5">
                {selectedPattern.matchedReportIds.map((repId) => (
                  <button
                    key={repId}
                    onClick={() => {
                      setSelectedPattern(null);
                      navigate(`/reports/${repId}`);
                    }}
                    className="flex w-full items-center justify-between rounded bg-slate-100 p-2 text-xs font-mono text-slate-800 hover:bg-slate-200 transition-colors"
                  >
                    <span>{repId}</span>
                    <span className="text-[11px] font-sans text-slate-600 flex items-center gap-1">
                      View AI Narrative Breakdown <ArrowRight className="h-3 w-3" />
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
