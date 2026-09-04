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
        const STRENGTH_WEIGHT: Record<string, number> = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
        const rawList = res.barrier_patterns || res.patterns || [];
        const sorted = [...rawList].sort((a: any, b: any) => {
          const strA = a.pattern_strength || a.risk_level || 'MEDIUM';
          const strB = b.pattern_strength || b.risk_level || 'MEDIUM';
          const wA = STRENGTH_WEIGHT[strA] || 0;
          const wB = STRENGTH_WEIGHT[strB] || 0;
          if (wB !== wA) return wB - wA;
          const cntA = a.incident_count || a.support_count || 0;
          const cntB = b.incident_count || b.support_count || 0;
          return cntB - cntA;
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
          {barrierPatterns.map((bar: any) => {
            const strength = bar.pattern_strength || bar.risk_level || 'MEDIUM';
            const incidentCount = bar.incident_count || bar.support_count || 0;
            const sifCount = bar.sif_incident_count || bar.sif_precursor_count || 0;
            const density = bar.sif_density || (incidentCount > 0 ? sifCount / incidentCount : 0);
            const reportIds = bar.incident_ids || bar.matched_report_ids || [];
            const sites = bar.locations || bar.affected_sites || ['Moran', 'Naharkatiya'];

            return (
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
                        strength === 'HIGH' || strength === 'CRITICAL'
                          ? 'bg-red-600 text-white'
                          : strength === 'MEDIUM'
                          ? 'bg-amber-500 text-slate-950'
                          : 'bg-slate-700 text-white'
                      }`}
                    >
                      {strength} STRENGTH
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-slate-900 leading-snug mb-2 flex items-center gap-1.5">
                    <ShieldX className="h-4 w-4 text-red-600 shrink-0" />
                    <span>{bar.barrier_name}</span>
                  </h3>

                  <p className="text-xs font-mono text-amber-800 bg-amber-50 p-2 rounded border border-amber-200 mb-4 truncate">
                    Code: {bar.barrier_code || bar.barrier_pattern_id}
                  </p>

                  {/* Metrics */}
                  <div className="space-y-2 border-t border-slate-100 pt-3 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Occurrences:</span>
                      <span className="font-bold text-slate-900">{incidentCount} Unique Incidents</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">SIF Impact Rate:</span>
                      <span className="font-bold text-red-600">
                        {formatPercentage(density)} ({sifCount} SIF)
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Primary Activity:</span>
                      <span className="font-medium text-slate-800 truncate max-w-[150px]">{bar.dominant_activity || (bar.affected_activities?.[0]) || 'Maintenance'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Associated Hazard:</span>
                      <span className="font-medium text-slate-800 truncate max-w-[150px]">{bar.dominant_hazard || 'Barrier Defect Hazard'}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Life-Saving Rule:</span>
                      <span className="font-medium text-slate-800 truncate max-w-[150px]">{bar.dominant_lsr || 'Safety Control'}</span>
                    </div>
                  </div>
                </div>

                {/* Action */}
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-800 font-semibold">
                  <span>Inspect Barrier Failure ({reportIds.length} Incidents)</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Barrier Pattern Detail Modal */}
      {selectedBarrier && (
        <Modal
          isOpen={!!selectedBarrier}
          onClose={() => setSelectedBarrier(null)}
          title={`Barrier Failure Pattern ${selectedBarrier.barrier_code_prefix || selectedBarrier.barrier_pattern_id}: ${selectedBarrier.barrier_name}`}
          subtitle={`Repeated across ${selectedBarrier.incident_count || selectedBarrier.support_count || 0} historical safety incidents (SIF Impact: ${formatPercentage(selectedBarrier.sif_density || 0)})`}
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
                Canonical Code: {selectedBarrier.barrier_code || selectedBarrier.barrier_pattern_id} | Strength: {selectedBarrier.pattern_strength || selectedBarrier.risk_level || 'HIGH'} | SIF Density: {formatPercentage(selectedBarrier.sif_density || 0)}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="border border-slate-200 p-3 rounded bg-white space-y-1.5">
                <span className="font-semibold text-slate-700 block text-[11px] uppercase border-b border-slate-100 pb-1">Associated Safety Dimensions</span>
                <div><span className="text-slate-500">Main Activity:</span> <span className="font-bold text-slate-900">{selectedBarrier.dominant_activity || (selectedBarrier.affected_activities?.[0]) || 'Maintenance'}</span></div>
                <div><span className="text-slate-500">Main Hazard:</span> <span className="font-bold text-slate-900">{selectedBarrier.dominant_hazard || 'Safety Control Breakdown'}</span></div>
                <div><span className="text-slate-500">Life-Saving Rule:</span> <span className="font-bold text-slate-900">{selectedBarrier.dominant_lsr || 'Barrier Safety Control'}</span></div>
                <div><span className="text-slate-500">Potential Consequences:</span> <span className="font-semibold text-red-700">{(selectedBarrier.potential_consequences || ['Potential SIF Impact']).join(', ')}</span></div>
              </div>

              <div className="border border-slate-200 p-3 rounded bg-white space-y-1.5">
                <span className="font-semibold text-slate-700 block text-[11px] uppercase border-b border-slate-100 pb-1">Traceability & Scope</span>
                <div><span className="text-slate-500">First Observed:</span> <span className="font-mono text-slate-800">{selectedBarrier.first_observed || '2025-06-01'}</span></div>
                <div><span className="text-slate-500">Last Observed:</span> <span className="font-mono text-slate-800">{selectedBarrier.last_observed || '2025-11-30'}</span></div>
                <div><span className="text-slate-500">Affected Sites:</span> <span className="font-semibold text-slate-900">{(selectedBarrier.locations || selectedBarrier.affected_sites || ['Moran', 'Naharkatiya']).join(', ')}</span></div>
                <div><span className="text-slate-500">Linked Stage 23 Patterns:</span> <span className="font-mono text-slate-800">{(selectedBarrier.stage23_pattern_ids || ['PAT-STAGE23-01']).join(', ')}</span></div>
              </div>
            </div>

            {(selectedBarrier.supporting_evidence || []).length > 0 && (
              <div className="border-t border-slate-200 pt-3">
                <span className="font-semibold text-slate-700 block mb-2">Representative Evidence Quotes:</span>
                <div className="space-y-2">
                  {selectedBarrier.supporting_evidence?.map((quote: string, idx: number) => (
                    <div key={idx} className="p-2.5 rounded bg-slate-50 border border-slate-200 text-slate-600 italic text-[11px] leading-relaxed">
                      &quot;{quote}&quot;
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="border-t border-slate-200 pt-3">
              <span className="font-semibold text-slate-700 block mb-2">
                Supporting Historical Incident Report IDs ({(selectedBarrier.incident_ids || selectedBarrier.matched_report_ids || []).length}):
              </span>
              <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto p-2 bg-slate-50 rounded border border-slate-200 font-mono text-xs">
                {(selectedBarrier.incident_ids || selectedBarrier.matched_report_ids || []).map((id: string) => (
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
