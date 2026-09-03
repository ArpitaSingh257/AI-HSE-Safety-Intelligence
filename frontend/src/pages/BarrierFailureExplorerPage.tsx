import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { barrierPatternsService } from '../api';
import type { AIBarrierPattern } from '../types/barrierPatterns';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Modal } from '../components/common/Modal';
import { formatPercentage } from '../utils/formatters';
import { ArrowRight, ShieldAlert, AlertTriangle, Layers, Calendar, MapPin, Activity, Flame, ShieldX } from 'lucide-react';

export const BarrierFailureExplorerPage: React.FC = () => {
  const navigate = useNavigate();
  const [barrierPatterns, setBarrierPatterns] = useState<AIBarrierPattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBarrier, setSelectedBarrier] = useState<AIBarrierPattern | null>(null);

  useEffect(() => {
    const fetchPatterns = async () => {
      try {
        const res = await barrierPatternsService.getBarrierPatterns();
        const STRENGTH_WEIGHT: Record<string, number> = { HIGH: 3, MEDIUM: 2, LOW: 1 };
        const sorted = [...(res.barrier_patterns || [])].sort((a, b) => {
          const wA = STRENGTH_WEIGHT[a.pattern_strength] || 0;
          const wB = STRENGTH_WEIGHT[b.pattern_strength] || 0;
          if (wB !== wA) return wB - wA;
          return b.occurrences - a.occurrences;
        });
        setBarrierPatterns(sorted);
      } finally {
        setLoading(false);
      }
    };
    fetchPatterns();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Mining Repeated Safety Barrier Failure Patterns across Historical Corpus..." />;
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Repeated Barrier Failure Pattern Explorer"
        subtitle="Stage 24 NLP mining identifying systemic, repeated safety control weaknesses (General Incident Pattern → Specific Barrier Failure)."
        showDemoBadge={true}
      />

      {barrierPatterns.length === 0 ? (
        <div className="p-8 text-center bg-slate-50 border border-slate-200 rounded-lg text-slate-600">
          <ShieldAlert className="h-10 w-10 text-slate-400 mx-auto mb-3" />
          <h3 className="text-sm font-bold text-slate-800">No Recurring Barrier Failures Identified</h3>
          <p className="text-xs text-slate-500 mt-1">No safety barrier failed in 3 or more incidents across the available historical dataset.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {barrierPatterns.map((bar) => (
            <div
              key={bar.barrier_pattern_id}
              className="hse-card flex flex-col justify-between p-5 hover:border-slate-400 transition-colors cursor-pointer border-t-4 border-t-amber-600"
              onClick={() => setSelectedBarrier(bar)}
            >
              <div>
                {/* Header */}
                <div className="flex items-start justify-between gap-2 mb-3">
                  <span className="font-mono text-xs font-bold text-slate-500">{bar.barrier_code_prefix || bar.barrier_pattern_id}</span>
                  <span
                    className={`rounded px-2 py-0.5 text-[10px] font-extrabold ${
                      bar.pattern_strength === 'HIGH'
                        ? 'bg-red-600 text-white'
                        : bar.pattern_strength === 'MEDIUM'
                        ? 'bg-amber-500 text-slate-950'
                        : 'bg-slate-700 text-white'
                    }`}
                  >
                    {bar.pattern_strength} STRENGTH
                  </span>
                </div>

                <h3 className="text-sm font-bold text-slate-900 leading-snug mb-2 flex items-center gap-1.5">
                  <ShieldX className="h-4 w-4 text-red-600 shrink-0" />
                  <span>{bar.barrier_name}</span>
                </h3>

                <p className="text-xs font-mono text-amber-800 bg-amber-50 p-2 rounded border border-amber-200 mb-4 truncate">
                  Code: {bar.barrier_code}
                </p>

                {/* Metrics */}
                <div className="space-y-2 border-t border-slate-100 pt-3 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Occurrences:</span>
                    <span className="font-bold text-slate-900">{bar.incident_count} Unique Incidents</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">SIF Impact Rate:</span>
                    <span className="font-bold text-red-600">
                      {formatPercentage(bar.sif_density)} ({bar.sif_incident_count} SIF)
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Primary Activity:</span>
                    <span className="font-medium text-slate-800 truncate max-w-[150px]">{bar.dominant_activity}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Associated Hazard:</span>
                    <span className="font-medium text-slate-800 truncate max-w-[150px]">{bar.dominant_hazard}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-500">Life-Saving Rule:</span>
                    <span className="font-medium text-slate-800 truncate max-w-[150px]">{bar.dominant_lsr}</span>
                  </div>
                </div>
              </div>

              {/* Action */}
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-800 font-semibold">
                <span>Inspect Barrier Failure ({bar.incident_ids.length} Incidents)</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Barrier Pattern Detail Modal */}
      {selectedBarrier && (
        <Modal
          isOpen={!!selectedBarrier}
          onClose={() => setSelectedBarrier(null)}
          title={`Barrier Failure Pattern ${selectedBarrier.barrier_code_prefix || selectedBarrier.barrier_pattern_id}: ${selectedBarrier.barrier_name}`}
          subtitle={`Repeated across ${selectedBarrier.incident_count} historical safety incidents (SIF Impact: ${formatPercentage(selectedBarrier.sif_density)})`}
          maxWidth="2xl"
          footer={
            <button
              onClick={() => setSelectedBarrier(null)}
              className="rounded bg-slate-900 px-4 py-1.5 text-xs font-semibold text-white"
            >
              Close
            </button>
          }
        >
          <div className="space-y-4 text-xs text-slate-800">
            <div className="bg-amber-50/80 border border-amber-200 p-3 rounded text-slate-800">
              <span className="font-bold text-amber-900 block text-xs mb-1">Systemic Barrier Breakdown Summary</span>
              <p className="text-slate-700 leading-relaxed font-mono text-[11px]">
                Canonical Code: {selectedBarrier.barrier_code} | Strength: {selectedBarrier.pattern_strength} | SIF Density: {formatPercentage(selectedBarrier.sif_density)}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="border border-slate-200 p-3 rounded bg-white space-y-1.5">
                <span className="font-semibold text-slate-700 block text-[11px] uppercase border-b border-slate-100 pb-1">Associated Safety Dimensions</span>
                <div><span className="text-slate-500">Main Activity:</span> <span className="font-bold text-slate-900">{selectedBarrier.dominant_activity}</span></div>
                <div><span className="text-slate-500">Main Hazard:</span> <span className="font-bold text-slate-900">{selectedBarrier.dominant_hazard}</span></div>
                <div><span className="text-slate-500">Life-Saving Rule:</span> <span className="font-bold text-slate-900">{selectedBarrier.dominant_lsr}</span></div>
                <div><span className="text-slate-500">Potential Consequences:</span> <span className="font-semibold text-red-700">{selectedBarrier.potential_consequences.join(', ')}</span></div>
              </div>

              <div className="border border-slate-200 p-3 rounded bg-white space-y-1.5">
                <span className="font-semibold text-slate-700 block text-[11px] uppercase border-b border-slate-100 pb-1">Traceability & Scope</span>
                <div><span className="text-slate-500">First Observed:</span> <span className="font-mono text-slate-800">{selectedBarrier.first_observed}</span></div>
                <div><span className="text-slate-500">Last Observed:</span> <span className="font-mono text-slate-800">{selectedBarrier.last_observed}</span></div>
                <div><span className="text-slate-500">Affected Sites:</span> <span className="font-semibold text-slate-900">{selectedBarrier.locations.join(', ')}</span></div>
                <div><span className="text-slate-500">Linked Stage 23 Patterns:</span> <span className="font-mono text-slate-800">{selectedBarrier.stage23_pattern_ids.join(', ')}</span></div>
              </div>
            </div>

            {selectedBarrier.supporting_evidence && selectedBarrier.supporting_evidence.length > 0 && (
              <div className="border-t border-slate-200 pt-3">
                <span className="font-semibold text-slate-700 block mb-2">Representative Evidence Quotes:</span>
                <div className="space-y-2">
                  {selectedBarrier.supporting_evidence.map((quote, idx) => (
                    <div key={idx} className="p-2.5 rounded bg-slate-50 border border-slate-200 text-slate-600 italic text-[11px] leading-relaxed">
                      &quot;{quote}&quot;
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="border-t border-slate-200 pt-3">
              <span className="font-semibold text-slate-700 block mb-2">Supporting Historical Incident Report IDs ({selectedBarrier.incident_ids.length}):</span>
              <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto p-2 bg-slate-50 rounded border border-slate-200 font-mono text-xs">
                {selectedBarrier.incident_ids.map((id) => (
                  <button
                    key={id}
                    onClick={() => {
                      setSelectedBarrier(null);
                      navigate(`/reports/${id}`);
                    }}
                    className="px-2 py-0.5 bg-white border border-slate-200 rounded text-slate-800 font-bold hover:bg-slate-100 hover:border-slate-400 transition-colors"
                  >
                    {id}
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
