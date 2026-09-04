import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { bowTieService } from '../../api';
import type { BowTieProfile, BowTieNode } from '../../types/bowTie';
import { LoadingSpinner } from '../common/LoadingSpinner';
import {
  GitCommit,
  ShieldAlert,
  AlertTriangle,
  Flame,
  ArrowRight,
  Info,
  CheckCircle2,
  HelpCircle,
  FileText,
  Search
} from 'lucide-react';

interface BowTieViewProps {
  reportId: string;
}

export const BowTieView: React.FC<BowTieViewProps> = ({ reportId }) => {
  const navigate = useNavigate();
  const [bowTie, setBowTie] = useState<BowTieProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedNode, setSelectedNode] = useState<BowTieNode | null>(null);

  useEffect(() => {
    const fetchBowTie = async () => {
      setLoading(true);
      try {
        const data = await bowTieService.getBowTieByReportId(reportId);
        setBowTie(data);
        if (data && data.nodes && data.nodes.length > 0) {
          setSelectedNode(data.nodes[0]);
        }
      } catch (err) {
        console.warn(`Failed to load Bow-Tie pathway for report ${reportId}:`, err);
      } finally {
        setLoading(false);
      }
    };
    fetchBowTie();
  }, [reportId]);

  if (loading) {
    return <LoadingSpinner label="Constructing Bow-Tie Risk Pathway & Provenance Nodes..." />;
  }

  if (!bowTie || !bowTie.nodes || bowTie.nodes.length === 0) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-6 text-center text-xs text-slate-500">
        No Bow-Tie barrier pathway available for report <span className="font-mono text-slate-700">{reportId}</span>.
      </div>
    );
  }

  const getProvenanceBadge = (prov: string) => {
    switch (prov) {
      case 'OBSERVED':
        return (
          <span className="bg-emerald-100 text-emerald-800 border border-emerald-300 font-extrabold text-[9px] px-1.5 py-0.5 rounded">
            OBSERVED
          </span>
        );
      case 'INFERRED':
        return (
          <span className="bg-amber-100 text-amber-900 border border-amber-300 font-bold text-[9px] px-1.5 py-0.5 rounded">
            INFERRED
          </span>
        );
      default:
        return (
          <span className="bg-slate-100 text-slate-600 border border-slate-300 font-medium text-[9px] px-1.5 py-0.5 rounded">
            UNKNOWN
          </span>
        );
    }
  };

  const hazards = bowTie.nodes.filter((n) => n.type === 'HAZARD');
  const threats = bowTie.nodes.filter((n) => n.type === 'THREAT');
  const barriers = bowTie.nodes.filter((n) => n.type === 'FAILED_BARRIER' || n.type === 'PREVENTIVE_BARRIER');
  const topEvents = bowTie.nodes.filter((n) => n.type === 'TOP_EVENT');
  const consequences = bowTie.nodes.filter((n) => n.type === 'CONSEQUENCE');

  return (
    <div className="space-y-4">
      {/* Governance Banner */}
      <div className="bg-slate-900 text-white rounded-lg p-3.5 shadow-sm border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <GitCommit className="h-4 w-4 text-amber-400 shrink-0" />
          <div className="text-[11px] leading-snug">
            <p className="font-bold text-amber-300">Bow-Tie Barrier Pathway & Risk Provenance</p>
            <p className="text-slate-300">
              Qualitative safety barrier flow: <span className="text-amber-200">Threats</span> &rarr; <span className="text-amber-300">Failed Barriers</span> &rarr; <span className="text-red-300 font-bold">Top Event</span> &rarr; <span className="text-blue-300">Consequences</span>.
            </p>
          </div>
        </div>
      </div>

      {/* Bow-Tie Visual Flow Diagram (Sleek 2x2 or 4-Stage Layout) */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
            <GitCommit className="h-4 w-4 text-slate-700" /> Incident Bow-Tie Barrier Pathway
          </h3>
          <span className="text-[10px] font-mono text-slate-500">Mapping Confidence: <strong className="text-slate-800">{bowTie.mapping_confidence}</strong></span>
        </div>

        {/* Responsive 2x2 Flow Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {/* Stage 1: Threats & Hazards */}
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2">
            <div className="flex items-center justify-between border-b border-slate-200 pb-1.5">
              <span className="text-[10px] font-black text-slate-800 uppercase flex items-center gap-1">
                <Search className="h-3 w-3 text-slate-600" /> 1. Threats & Hazards
              </span>
              <span className="text-[10px] text-slate-500 font-mono">Stage 1</span>
            </div>
            <div className="space-y-2">
              {hazards.map((n) => (
                <div
                  key={n.id}
                  onClick={() => setSelectedNode(n)}
                  className={`p-2.5 rounded-lg border cursor-pointer text-xs space-y-1.5 transition-all ${
                    selectedNode?.id === n.id ? 'bg-slate-900 text-white border-slate-900 shadow-sm' : 'bg-white text-slate-800 border-slate-200 hover:border-slate-400'
                  }`}
                >
                  <div className="flex items-center justify-between gap-1 flex-wrap">
                    <span className="font-bold text-[9px] text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200 uppercase">HAZARD</span>
                    {getProvenanceBadge(n.provenance)}
                  </div>
                  <p className="font-bold text-xs leading-snug">{n.label}</p>
                </div>
              ))}
              {threats.map((n) => (
                <div
                  key={n.id}
                  onClick={() => setSelectedNode(n)}
                  className={`p-2.5 rounded-lg border cursor-pointer text-xs space-y-1.5 transition-all ${
                    selectedNode?.id === n.id ? 'bg-slate-900 text-white border-slate-900 shadow-sm' : 'bg-white text-slate-800 border-slate-200 hover:border-slate-400'
                  }`}
                >
                  <div className="flex items-center justify-between gap-1 flex-wrap">
                    <span className="font-bold text-[9px] text-purple-600 bg-purple-50 px-1.5 py-0.5 rounded border border-purple-200 uppercase">THREAT</span>
                    {getProvenanceBadge(n.provenance)}
                  </div>
                  <p className="font-bold text-xs leading-snug">{n.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Stage 2: Failed Barriers */}
          <div className="bg-amber-50/60 border border-amber-200/80 rounded-lg p-3 space-y-2">
            <div className="flex items-center justify-between border-b border-amber-200 pb-1.5">
              <span className="text-[10px] font-black text-amber-950 uppercase flex items-center gap-1">
                <ShieldAlert className="h-3 w-3 text-amber-600" /> 2. Failed Barriers
              </span>
              <span className="text-[10px] text-amber-800 font-mono">Stage 2</span>
            </div>
            <div className="space-y-2">
              {barriers.map((n) => (
                <div
                  key={n.id}
                  onClick={() => setSelectedNode(n)}
                  className={`p-2.5 rounded-lg border cursor-pointer text-xs space-y-1.5 transition-all ${
                    selectedNode?.id === n.id ? 'bg-amber-900 text-white border-amber-900 font-bold shadow-sm' : 'bg-white text-slate-800 border-amber-200 hover:border-amber-400'
                  }`}
                >
                  <div className="flex items-center justify-between gap-1 flex-wrap">
                    <span className="font-bold text-[9px] text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200 uppercase flex items-center gap-1">
                      <ShieldAlert className="h-2.5 w-2.5" /> FAILED BARRIER
                    </span>
                    {getProvenanceBadge(n.provenance)}
                  </div>
                  <p className="font-bold text-xs leading-snug text-amber-950">{n.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Stage 3: Top Event (Loss of Control) */}
          <div className="bg-red-50/60 border border-red-200/80 rounded-lg p-3 space-y-2">
            <div className="flex items-center justify-between border-b border-red-200 pb-1.5">
              <span className="text-[10px] font-black text-red-950 uppercase flex items-center gap-1">
                <AlertTriangle className="h-3 w-3 text-red-600" /> 3. Top Event (Loss of Control)
              </span>
              <span className="text-[10px] text-red-800 font-mono">Stage 3</span>
            </div>
            <div className="space-y-2">
              {topEvents.map((n) => (
                <div
                  key={n.id}
                  onClick={() => setSelectedNode(n)}
                  className={`p-2.5 rounded-lg border cursor-pointer text-xs space-y-1.5 transition-all ${
                    selectedNode?.id === n.id ? 'bg-red-900 text-white border-red-900 font-bold shadow-sm' : 'bg-white text-slate-800 border-red-200 hover:border-red-400'
                  }`}
                >
                  <div className="flex items-center justify-between gap-1 flex-wrap">
                    <span className="font-bold text-[9px] text-red-700 bg-red-50 px-1.5 py-0.5 rounded border border-red-200 uppercase flex items-center gap-1">
                      <AlertTriangle className="h-2.5 w-2.5" /> LOSS OF CONTROL
                    </span>
                    {getProvenanceBadge(n.provenance)}
                  </div>
                  <p className="font-bold text-xs leading-snug text-red-950">{n.label}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Stage 4: Potential Consequences */}
          <div className="bg-blue-50/60 border border-blue-200/80 rounded-lg p-3 space-y-2">
            <div className="flex items-center justify-between border-b border-blue-200 pb-1.5">
              <span className="text-[10px] font-black text-blue-950 uppercase flex items-center gap-1">
                <Flame className="h-3 w-3 text-blue-600" /> 4. Potential Consequences
              </span>
              <span className="text-[10px] text-blue-800 font-mono">Stage 4</span>
            </div>
            <div className="space-y-2">
              {consequences.map((n) => (
                <div
                  key={n.id}
                  onClick={() => setSelectedNode(n)}
                  className={`p-2.5 rounded-lg border cursor-pointer text-xs space-y-1.5 transition-all ${
                    selectedNode?.id === n.id ? 'bg-blue-900 text-white border-blue-900 font-bold shadow-sm' : 'bg-white text-slate-800 border-blue-200 hover:border-blue-400'
                  }`}
                >
                  <div className="flex items-center justify-between gap-1 flex-wrap">
                    <span className="font-bold text-[9px] text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200 uppercase flex items-center gap-1">
                      <Flame className="h-2.5 w-2.5" /> CONSEQUENCE
                    </span>
                    {getProvenanceBadge(n.provenance)}
                  </div>
                  <p className="font-bold text-xs leading-snug text-blue-950">{n.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Selected Node Details Inspector */}
      {selectedNode && (
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm space-y-3">
          <div className="flex items-start justify-between border-b border-slate-100 pb-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-500 uppercase">{selectedNode.type} Node Detail</span>
                {getProvenanceBadge(selectedNode.provenance)}
              </div>
              <h4 className="text-sm font-bold text-slate-900 mt-0.5">{selectedNode.label}</h4>
            </div>
            {selectedNode.canonical_barrier && (
              <span className="font-mono text-[11px] bg-slate-100 text-slate-800 px-2 py-0.5 rounded border border-slate-300">
                {selectedNode.canonical_barrier}
              </span>
            )}
          </div>

          {selectedNode.raw_evidence && (
            <div className="bg-slate-50 border border-slate-200 rounded p-3 text-xs text-slate-800">
              <strong className="text-slate-900 block mb-0.5">Raw Text / Evidence Excerpt:</strong>
              <p className="italic font-serif text-slate-700">"{selectedNode.raw_evidence}"</p>
            </div>
          )}

          {/* Links to Cross-Stage Intelligence */}
          <div className="pt-2 flex flex-wrap gap-2 text-xs">
            {bowTie.barrier_pattern_ids.length > 0 && (
              <button
                onClick={() => navigate('/barrier-patterns')}
                className="flex items-center gap-1 px-3 py-1 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 font-bold rounded transition-colors"
              >
                <ShieldAlert className="h-3.5 w-3.5 text-amber-600" /> Stage 24 Barrier Pattern <ArrowRight className="h-3 w-3" />
              </button>
            )}
            <button
              onClick={() => navigate('/priorities')}
              className="flex items-center gap-1 px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded transition-colors"
            >
              Stage 30 Priority Intelligence <ArrowRight className="h-3 w-3" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
