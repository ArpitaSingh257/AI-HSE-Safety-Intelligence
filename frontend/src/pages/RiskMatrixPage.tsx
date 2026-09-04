import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { riskMatrixService } from '../api';
import type { RiskMatrixItem, RiskMatrixListResponse } from '../types/riskMatrix';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  Grid,
  AlertTriangle,
  Layers,
  MapPin,
  Activity,
  AlertOctagon,
  ArrowRight,
  Info,
  CheckCircle2,
  BarChart2,
  Search,
  Filter,
  ShieldAlert
} from 'lucide-react';

export const RiskMatrixPage: React.FC = () => {
  const navigate = useNavigate();
  const [matrixItems, setMatrixItems] = useState<RiskMatrixItem[]>([]);
  const [criticalCnt, setCriticalCnt] = useState<number>(0);
  const [highPotRareCnt, setHighPotRareCnt] = useState<number>(0);
  const [freqLowerCnt, setFreqLowerCnt] = useState<number>(0);
  const [lowMonitorCnt, setLowMonitorCnt] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<RiskMatrixItem | null>(null);

  // Filters State
  const [activeQuadrant, setActiveQuadrant] = useState<string>('ALL');
  const [activeEntityType, setActiveEntityType] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    const fetchMatrix = async () => {
      try {
        const data: RiskMatrixListResponse = await riskMatrixService.getRiskMatrix();
        const items: RiskMatrixItem[] = data.matrix_items || [];
        setMatrixItems(items);
        setCriticalCnt(data.critical_priority_count || 0);
        setHighPotRareCnt(data.high_potential_rare_count || 0);
        setFreqLowerCnt(data.frequent_lower_potential_count || 0);
        setLowMonitorCnt(data.low_priority_monitor_count || 0);
        if (items.length > 0) {
          setSelectedItem(items[0]);
        }
      } catch (err) {
        console.warn('Failed to load risk matrix dataset:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMatrix();
  }, []);

  // Filtered Matrix Items
  const filteredItems = useMemo(() => {
    return matrixItems.filter((i) => {
      if (activeQuadrant !== 'ALL' && i.quadrant !== activeQuadrant) return false;
      if (activeEntityType !== 'ALL' && i.entity_type !== activeEntityType) return false;
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase();
        const mName = i.entity_name.toLowerCase().includes(q);
        const mId = i.entity_id.toLowerCase().includes(q);
        if (!mName && !mId) return false;
      }
      return true;
    });
  }, [matrixItems, activeQuadrant, activeEntityType, searchQuery]);

  if (loading) {
    return <LoadingSpinner label="Evaluating 2D Coordinates (Severity vs Recurrence) & Matrix Quadrants..." />;
  }

  const getQuadrantBadge = (quad: string, cls: string) => {
    switch (cls) {
      case 'CRITICAL_PRIORITY':
        return (
          <span className="flex items-center gap-1 bg-red-600 text-white font-black text-[10px] px-2 py-0.5 rounded shadow-sm">
            <AlertOctagon className="h-3 w-3" /> CRITICAL (HIGH/HIGH)
          </span>
        );
      case 'HIGH_POTENTIAL_RARE':
        return (
          <span className="flex items-center gap-1 bg-amber-500 text-slate-950 font-extrabold text-[10px] px-2 py-0.5 rounded shadow-sm">
            <AlertTriangle className="h-3 w-3" /> HIGH-POTENTIAL (RARE)
          </span>
        );
      case 'FREQUENT_LOWER_POTENTIAL':
        return (
          <span className="flex items-center gap-1 bg-blue-100 text-blue-800 font-bold text-[10px] px-2 py-0.5 rounded border border-blue-300">
            <BarChart2 className="h-3 w-3 text-blue-600" /> FREQUENT (LOWER-POTENTIAL)
          </span>
        );
      case 'LOW_PRIORITY_MONITOR':
        return (
          <span className="flex items-center gap-1 bg-emerald-100 text-emerald-800 font-bold text-[10px] px-2 py-0.5 rounded border border-emerald-300">
            <CheckCircle2 className="h-3 w-3 text-emerald-600" /> MONITOR (LOW/LOW)
          </span>
        );
      default:
        return (
          <span className="bg-slate-100 text-slate-600 font-medium text-[10px] px-2 py-0.5 rounded border border-slate-300">
            INSUFFICIENT DATA
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <PageHeader
        title="Severity vs Recurrence Risk Matrix"
        subtitle="2D analytical classification mapping historical SIF potential (y-axis) against recurrence frequency (x-axis)."
        icon={Grid}
      />

      {/* Governance Notice */}
      <div className="bg-slate-900 text-white rounded-lg p-4 shadow-sm border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Info className="h-5 w-5 text-amber-400 shrink-0" />
          <div className="text-xs space-y-0.5">
            <p className="font-bold text-amber-300">2D Matrix & Decision-Support Notice</p>
            <p className="text-slate-300">
              Severity (y-axis) represents historical SIF precursor density; Recurrence (x-axis) represents historical report frequency. Quadrant placements classify preventative focus and do not predict accident probabilities.
            </p>
          </div>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Critical (High / High)</span>
          <p className="text-2xl font-black text-red-600 mt-1">{criticalCnt}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">High-Potential (Rare)</span>
          <p className="text-2xl font-black text-amber-600 mt-1">{highPotRareCnt}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Frequent (Lower-Potential)</span>
          <p className="text-2xl font-black text-blue-600 mt-1">{freqLowerCnt}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Monitor (Low / Low)</span>
          <p className="text-2xl font-black text-emerald-600 mt-1">{lowMonitorCnt}</p>
        </div>
      </div>

      {/* 2D Matrix Interactive Grid Component */}
      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <Grid className="h-4 w-4 text-slate-700" /> 2D Risk Coordinates Grid
          </h3>
          <span className="text-xs text-slate-500 font-mono">y: Severity (SIF Density) | x: Recurrence Score</span>
        </div>

        {/* 4 Quadrants Visual Grid Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {/* Top-Left: High Severity / Low Recurrence (RARE + HIGH SIF) */}
          <div className="bg-amber-50/70 border border-amber-200 rounded-lg p-4 space-y-3 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="border-b border-amber-200 pb-2 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-amber-900 uppercase flex items-center gap-1">
                    <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" /> High-Potential / Rare
                  </span>
                  <span className="text-[10px] font-bold bg-amber-200 text-amber-900 px-2 py-0.5 rounded">
                    Sev &ge; 0.50 | Rec &lt; 0.50
                  </span>
                </div>
                <p className="text-[11px] text-amber-800 font-medium">
                  ⚡ <strong>Quadrant Context:</strong> High SIF potential, low occurrence frequency. Catastrophic risk focus.
                </p>
              </div>

              {/* Scrollable Items List */}
              <div className="max-h-48 overflow-y-auto space-y-2 text-xs pr-1">
                {filteredItems.filter((i) => i.quadrant === 'HIGH_SEVERITY_LOW_RECURRENCE').map((item) => (
                  <div
                    key={item.matrix_item_id}
                    onClick={() => setSelectedItem(item)}
                    className={`p-2.5 rounded-lg border cursor-pointer space-y-1 transition-all shadow-2xs ${
                      selectedItem?.matrix_item_id === item.matrix_item_id
                        ? 'bg-amber-900 text-white border-amber-900 shadow-sm'
                        : 'bg-white text-slate-800 border-amber-200 hover:border-amber-400'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold truncate flex-1 flex items-center gap-1.5">
                        <span className="h-2 w-2 rounded-full bg-amber-500 shrink-0" />
                        {item.entity_name}
                      </span>
                      <span className="font-mono text-[10px] bg-amber-100 text-amber-900 border border-amber-300 px-1.5 py-0.5 rounded font-extrabold">
                        Sev: {item.severity_score.toFixed(2)} | Rec: {item.recurrence_score.toFixed(2)}
                      </span>
                    </div>
                    <p className={`text-[11px] leading-snug ${selectedItem?.matrix_item_id === item.matrix_item_id ? 'text-amber-100' : 'text-slate-600'}`}>
                      High SIF precursor density logged with lower repeat frequency.
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Quadrant-Specific AI RAG Recommendation Box (Scrollable) */}
            <div className="bg-amber-100/90 border border-amber-300/80 rounded-md p-2.5 space-y-1 mt-2">
              <div className="flex items-center justify-between text-[10px] font-bold text-amber-950 uppercase tracking-wider">
                <span className="flex items-center gap-1">🤖 AI Quadrant Strategy</span>
                <span className="bg-white text-amber-900 px-1.5 py-0.5 rounded border border-amber-300 font-mono">[ISO-31000]</span>
              </div>
              <div className="max-h-16 overflow-y-auto pr-1 text-[11px] text-amber-900 leading-snug scrollbar-thin">
                <strong>Catastrophic Prevention Strategy:</strong> Enforce dual-barrier engineering isolation, automated gas monitoring & pre-work Non-Destructive Testing (NDT) for rare high-energy tasks.
              </div>
            </div>
          </div>

          {/* Top-Right: High Severity / High Recurrence (CRITICAL PRIORITY) */}
          <div className="bg-red-50/70 border border-red-200 rounded-lg p-4 space-y-3 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="border-b border-red-200 pb-2 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-red-900 uppercase flex items-center gap-1">
                    <AlertOctagon className="h-4 w-4 text-red-600 shrink-0" /> Critical Priority (Frequent & High)
                  </span>
                  <span className="text-[10px] font-bold bg-red-200 text-red-900 px-2 py-0.5 rounded">
                    Sev &ge; 0.50 | Rec &ge; 0.50
                  </span>
                </div>
                <p className="text-[11px] text-red-800 font-medium">
                  🚨 <strong>Quadrant Context:</strong> High SIF potential AND high repeat frequency. Immediate action required!
                </p>
              </div>

              {/* Scrollable Items List */}
              <div className="max-h-48 overflow-y-auto space-y-2 text-xs pr-1">
                {filteredItems.filter((i) => i.quadrant === 'HIGH_SEVERITY_HIGH_RECURRENCE').map((item) => (
                  <div
                    key={item.matrix_item_id}
                    onClick={() => setSelectedItem(item)}
                    className={`p-2.5 rounded-lg border cursor-pointer space-y-1 transition-all shadow-2xs ${
                      selectedItem?.matrix_item_id === item.matrix_item_id
                        ? 'bg-red-900 text-white border-red-900 shadow-sm'
                        : 'bg-white text-slate-800 border-red-200 hover:border-red-400'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold truncate flex-1 flex items-center gap-1.5">
                        <span className="h-2 w-2 rounded-full bg-red-600 animate-pulse shrink-0" />
                        {item.entity_name}
                      </span>
                      <span className="font-mono text-[10px] bg-red-100 text-red-900 border border-red-300 px-1.5 py-0.5 rounded font-black">
                        Sev: {item.severity_score.toFixed(2)} | Rec: {item.recurrence_score.toFixed(2)}
                      </span>
                    </div>
                    <p className={`text-[11px] leading-snug ${selectedItem?.matrix_item_id === item.matrix_item_id ? 'text-red-100' : 'text-slate-600'}`}>
                      High SIF danger combined with repeat occurrence clusters across reports.
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Quadrant-Specific AI RAG Recommendation Box (Scrollable) */}
            <div className="bg-red-100/90 border border-red-300/80 rounded-md p-2.5 space-y-1 mt-2">
              <div className="flex items-center justify-between text-[10px] font-bold text-red-950 uppercase tracking-wider">
                <span className="flex items-center gap-1">🚨 AI Quadrant Strategy</span>
                <span className="bg-white text-red-900 px-1.5 py-0.5 rounded border border-red-300 font-mono">[IOGP-LSR-2023]</span>
              </div>
              <div className="max-h-16 overflow-y-auto pr-1 text-[11px] text-red-950 leading-snug scrollbar-thin">
                <strong>Immediate Field Intervention Strategy:</strong> Issue safety stand-down order, deploy 2-person standby rescue team, enforce digital PTW re-authorization & 48h supervisory audits.
              </div>
            </div>
          </div>

          {/* Bottom-Left: Low Severity / Low Recurrence (LOW PRIORITY MONITOR) */}
          <div className="bg-emerald-50/70 border border-emerald-200 rounded-lg p-4 space-y-3 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="border-b border-emerald-200 pb-2 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-emerald-900 uppercase flex items-center gap-1">
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" /> Low Priority Monitor
                  </span>
                  <span className="text-[10px] font-bold bg-emerald-200 text-emerald-900 px-2 py-0.5 rounded">
                    Sev &lt; 0.50 | Rec &lt; 0.50
                  </span>
                </div>
                <p className="text-[11px] text-emerald-800 font-medium">
                  ✅ <strong>Quadrant Context:</strong> Low severity impact and low occurrence frequency. Routine safety monitoring.
                </p>
              </div>

              {/* Scrollable Items List */}
              <div className="max-h-48 overflow-y-auto space-y-2 text-xs pr-1">
                {filteredItems.filter((i) => i.quadrant === 'LOW_SEVERITY_LOW_RECURRENCE').map((item) => (
                  <div
                    key={item.matrix_item_id}
                    onClick={() => setSelectedItem(item)}
                    className={`p-2.5 rounded-lg border cursor-pointer space-y-1 transition-all shadow-2xs ${
                      selectedItem?.matrix_item_id === item.matrix_item_id
                        ? 'bg-emerald-900 text-white border-emerald-900 shadow-sm'
                        : 'bg-white text-slate-800 border-emerald-200 hover:border-emerald-400'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold truncate flex-1 flex items-center gap-1.5">
                        <span className="h-2 w-2 rounded-full bg-emerald-500 shrink-0" />
                        {item.entity_name}
                      </span>
                      <span className="font-mono text-[10px] bg-emerald-100 text-emerald-900 border border-emerald-300 px-1.5 py-0.5 rounded font-bold">
                        Sev: {item.severity_score.toFixed(2)} | Rec: {item.recurrence_score.toFixed(2)}
                      </span>
                    </div>
                    <p className={`text-[11px] leading-snug ${selectedItem?.matrix_item_id === item.matrix_item_id ? 'text-emerald-100' : 'text-slate-600'}`}>
                      Low SIF severity and low repeat frequency. Routine safety tracking.
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Quadrant-Specific AI RAG Recommendation Box (Scrollable) */}
            <div className="bg-emerald-100/90 border border-emerald-300/80 rounded-md p-2.5 space-y-1 mt-2">
              <div className="flex items-center justify-between text-[10px] font-bold text-emerald-950 uppercase tracking-wider">
                <span className="flex items-center gap-1">✅ AI Quadrant Strategy</span>
                <span className="bg-white text-emerald-900 px-1.5 py-0.5 rounded border border-emerald-300 font-mono">[ISO-45001]</span>
              </div>
              <div className="max-h-16 overflow-y-auto pr-1 text-[11px] text-emerald-950 leading-snug scrollbar-thin">
                <strong>Routine Baseline Protocol:</strong> Maintain standard pre-shift safety walk-throughs, continuous digital hazard reporting, and monthly preventive equipment inspections.
              </div>
            </div>
          </div>

          {/* Bottom-Right: Low Severity / High Recurrence (FREQUENT LOWER POTENTIAL) */}
          <div className="bg-blue-50/70 border border-blue-200 rounded-lg p-4 space-y-3 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="border-b border-blue-200 pb-2 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-blue-900 uppercase flex items-center gap-1">
                    <BarChart2 className="h-4 w-4 text-blue-600 shrink-0" /> Frequent (Lower-Potential)
                  </span>
                  <span className="text-[10px] font-bold bg-blue-200 text-blue-900 px-2 py-0.5 rounded">
                    Sev &lt; 0.50 | Rec &ge; 0.50
                  </span>
                </div>
                <p className="text-[11px] text-blue-800 font-medium">
                  📈 <strong>Quadrant Context:</strong> High repeat occurrence frequency, lower SIF severity. Track minor near-miss trends.
                </p>
              </div>

              {/* Scrollable Items List */}
              <div className="max-h-48 overflow-y-auto space-y-2 text-xs pr-1">
                {filteredItems.filter((i) => i.quadrant === 'LOW_SEVERITY_HIGH_RECURRENCE').map((item) => (
                  <div
                    key={item.matrix_item_id}
                    onClick={() => setSelectedItem(item)}
                    className={`p-2.5 rounded-lg border cursor-pointer space-y-1 transition-all shadow-2xs ${
                      selectedItem?.matrix_item_id === item.matrix_item_id
                        ? 'bg-blue-900 text-white border-blue-900 shadow-sm'
                        : 'bg-white text-slate-800 border-blue-200 hover:border-blue-400'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold truncate flex-1 flex items-center gap-1.5">
                        <span className="h-2 w-2 rounded-full bg-blue-500 shrink-0" />
                        {item.entity_name}
                      </span>
                      <span className="font-mono text-[10px] bg-blue-100 text-blue-900 border border-blue-300 px-1.5 py-0.5 rounded font-bold">
                        Sev: {item.severity_score.toFixed(2)} | Rec: {item.recurrence_score.toFixed(2)}
                      </span>
                    </div>
                    <p className={`text-[11px] leading-snug ${selectedItem?.matrix_item_id === item.matrix_item_id ? 'text-blue-100' : 'text-slate-600'}`}>
                      High repeat frequency logged for lower-consequence near-misses.
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Quadrant-Specific AI RAG Recommendation Box (Scrollable) */}
            <div className="bg-blue-100/90 border border-blue-300/80 rounded-md p-2.5 space-y-1 mt-2">
              <div className="flex items-center justify-between text-[10px] font-bold text-blue-950 uppercase tracking-wider">
                <span className="flex items-center gap-1">📈 AI Quadrant Strategy</span>
                <span className="bg-white text-blue-900 px-1.5 py-0.5 rounded border border-blue-300 font-mono">[OIL-SOP-TBT]</span>
              </div>
              <div className="max-h-16 overflow-y-auto pr-1 text-[11px] text-blue-950 leading-snug scrollbar-thin">
                <strong>Behavioral Drift Mitigation:</strong> Conduct mandatory weekly Toolbox Talks (TBT), audit rig-floor housekeeping, and enforce PPE compliance refreshers for repeat minor hazards.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Selected Entity Detailed Inspector */}
      {selectedItem && (
        <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm space-y-5">
          <div className="flex items-start justify-between border-b border-slate-100 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <Grid className="h-5 w-5 text-slate-800" />
                <h2 className="text-lg font-bold text-slate-900">{selectedItem.entity_name}</h2>
                {getQuadrantBadge(selectedItem.quadrant, selectedItem.classification)}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Entity Type: <span className="font-semibold text-slate-700">{selectedItem.entity_type}</span> | Window: {selectedItem.first_observed} → {selectedItem.last_observed}
              </p>
            </div>
            <div className="flex items-center gap-4 text-right font-mono">
              <div>
                <span className="text-[10px] text-slate-400 block uppercase">Severity Score</span>
                <span className="text-2xl font-black text-red-600">{selectedItem.severity_score.toFixed(2)}</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 block uppercase">Recurrence Score</span>
                <span className="text-2xl font-black text-amber-600">{selectedItem.recurrence_score.toFixed(2)}</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3.5 text-xs text-slate-800">
            <strong>Deterministic Matrix Rationale:</strong> {selectedItem.reason}
          </div>

          {/* AI RAG Safety Recommendation Engine Card (Light Theme) */}
          <div className="bg-emerald-50/60 border border-emerald-200/80 rounded-lg p-4 shadow-sm space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="bg-emerald-100 text-emerald-800 p-1.5 rounded-md border border-emerald-300">
                  <ShieldAlert className="h-4 w-4 text-emerald-700" />
                </span>
                <div>
                  <h4 className="font-bold text-xs text-emerald-950 uppercase tracking-wide">AI RAG Safety Recommendation Engine</h4>
                  <p className="text-[10px] text-emerald-700 font-medium">ISO 31000 & IOGP LSR Ground-Truth Retrieval Engine</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-1 font-mono text-[10px]">
                {selectedItem.recommendations?.rag_citations.map((citation) => (
                  <span key={citation} className="bg-white text-emerald-900 border border-emerald-300 px-1.5 py-0.5 rounded shadow-2xs">
                    [{citation}]
                  </span>
                )) || (
                  <span className="bg-white text-emerald-900 border border-emerald-300 px-1.5 py-0.5 rounded shadow-2xs">
                    [IOGP-LSR-2023]
                  </span>
                )}
              </div>
            </div>

            {/* Scrollable Container so page height remains fixed & compact */}
            <div className="space-y-2 text-xs max-h-52 overflow-y-auto pr-1 scrollbar-thin">
              {/* Engineering Control */}
              <div className="bg-white/90 p-2.5 rounded border border-emerald-200/80 space-y-0.5 shadow-2xs">
                <span className="text-amber-800 font-bold text-[10px] uppercase block tracking-wider">🛠️ Engineering & Barrier Control</span>
                <p className="text-slate-800 text-[11px] leading-relaxed">
                  {selectedItem.recommendations?.engineering_control || `Deploy automated dual-barrier gas monitoring and isolation lockout (LOTO) verification for ${selectedItem.entity_name}.`}
                </p>
              </div>

              {/* Procedural Protocol */}
              <div className="bg-white/90 p-2.5 rounded border border-emerald-200/80 space-y-0.5 shadow-2xs">
                <span className="text-blue-800 font-bold text-[10px] uppercase block tracking-wider">📋 Procedural & Field Protocol</span>
                <p className="text-slate-800 text-[11px] leading-relaxed">
                  {selectedItem.recommendations?.procedural_protocol || `Enforce mandatory 2-person standby rescue team, continuous atmospheric testing, and digital PTW authorization.`}
                </p>
              </div>

              {/* Governance Audit */}
              <div className="bg-white/90 p-2.5 rounded border border-emerald-200/80 space-y-0.5 shadow-2xs">
                <span className="text-purple-800 font-bold text-[10px] uppercase block tracking-wider">🔍 Governance & Inspection Audit</span>
                <p className="text-slate-800 text-[11px] leading-relaxed">
                  {selectedItem.recommendations?.governance_audit || `Schedule immediate 48-hour Stage 42 HSE supervisory safety audit.`}
                </p>
              </div>
            </div>

            {/* Deploy Action Button */}
            <div className="pt-2 flex items-center justify-between border-t border-emerald-200/80 text-xs">
              <span className="text-[10px] text-emerald-800 font-semibold">Status: Recommended Matrix RAG Controls Ready</span>
              <button
                onClick={() => {
                  const site = selectedItem.site_ids[0] || 'Moran';
                  const activity = selectedItem.activity_ids[0] || 'Maintenance';
                  const title = `Deploy AI RAG Safety Controls for Matrix Item ${selectedItem.entity_name}`;
                  const desc = selectedItem.recommendations?.engineering_control || selectedItem.reason;
                  navigate(`/interventions?deploy=true&site=${encodeURIComponent(site)}&activity=${encodeURIComponent(activity)}&title=${encodeURIComponent(title)}&desc=${encodeURIComponent(desc)}`);
                }}
                className="flex items-center gap-1.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold px-3 py-1.5 rounded shadow-sm transition-colors text-[11px]"
              >
                🚀 Deploy RAG Recommendation to Interventions <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>

          {/* Cross-Stage Intelligence Navigation Links */}
          <div className="pt-3 border-t border-slate-100 space-y-2.5">
            <div>
              <h4 className="font-bold text-xs text-slate-900 uppercase">Cross-Stage Traceability & Drill-Down</h4>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Click any link below to open its dedicated AI module <strong>pre-filtered for exact site & activity root causes</strong>.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 text-xs">
              <button
                onClick={() => navigate('/priorities')}
                className="flex items-center gap-1 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded transition-colors"
                title="Inspect Stage 30 Unified HSE Priorities"
              >
                <ShieldAlert className="h-3.5 w-3.5 text-amber-400" /> Stage 30 Priorities <ArrowRight className="h-3 w-3" />
              </button>

              {selectedItem.barrier_pattern_ids.length > 0 && (
                <button
                  onClick={() => navigate(`/barrier-patterns?id=${encodeURIComponent(selectedItem.barrier_pattern_ids[0])}`)}
                  className="flex items-center gap-1 px-3 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 font-bold rounded transition-colors"
                  title="Inspect exact Barrier Control Failures"
                >
                  <AlertTriangle className="h-3.5 w-3.5 text-amber-600" /> Barrier Failure ({selectedItem.barrier_pattern_ids[0]}) <ArrowRight className="h-3 w-3" />
                </button>
              )}

              {selectedItem.pattern_ids.length > 0 && (
                <button
                  onClick={() => navigate(`/patterns?pattern=${encodeURIComponent(selectedItem.pattern_ids[0])}`)}
                  className="flex items-center gap-1 px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-300 font-bold rounded transition-colors"
                  title="Inspect exact SIF Precursor Hazard Patterns"
                >
                  <Layers className="h-3.5 w-3.5 text-purple-600" /> Precursor Pattern ({selectedItem.pattern_ids[0]}) <ArrowRight className="h-3 w-3" />
                </button>
              )}

              <button
                onClick={() => navigate(`/sites?site=${encodeURIComponent(selectedItem.site_ids[0] || 'Moran')}`)}
                className="flex items-center gap-1 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-900 border border-blue-300 font-bold rounded transition-colors"
                title="Inspect Site Risk Profile"
              >
                <MapPin className="h-3.5 w-3.5 text-blue-600" /> Site Risk ({selectedItem.site_ids[0] || 'Moran'}) <ArrowRight className="h-3 w-3" />
              </button>

              <button
                onClick={() => navigate(`/activities?activity=${encodeURIComponent(selectedItem.activity_ids[0] || 'Maintenance')}`)}
                className="flex items-center gap-1 px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-900 border border-emerald-300 font-bold rounded transition-colors"
                title="Inspect Task & Activity Risk Profile"
              >
                <Activity className="h-3.5 w-3.5 text-emerald-600" /> Task Risk ({selectedItem.activity_ids[0] || 'Maintenance'}) <ArrowRight className="h-3 w-3" />
              </button>
            </div>
          </div>

          {/* Supporting Incident Report Traceability with Color Coding */}
          <div className="pt-3 border-t border-slate-100 space-y-2">
            <div>
              <h4 className="font-bold text-xs text-slate-900 flex items-center gap-2">
                <span>Supporting Historical Reports ({selectedItem.supporting_reports?.length || selectedItem.supporting_report_ids.length})</span>
                <span className="text-[10px] font-normal text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                  Live MongoDB Atlas Evidence
                </span>
              </h4>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Ground-truth field incident & near-miss reports used to position matrix item. Red pulsing dots indicate SIF Precursor potential.
              </p>
            </div>

            <div className="flex flex-wrap gap-1.5 pt-1">
              {(selectedItem.supporting_reports && selectedItem.supporting_reports.length > 0
                ? selectedItem.supporting_reports
                : selectedItem.supporting_report_ids.map(id => ({ id, sif_status: 'NON_SIF', priority: 'MEDIUM' }))
              ).slice(0, 15).map((rep) => {
                const isSif = rep.sif_status === 'SIF_POTENTIAL' || rep.priority === 'CRITICAL';
                const isHigh = rep.priority === 'HIGH';

                return (
                  <button
                    key={rep.id}
                    onClick={() => navigate(`/reports/${rep.id}`)}
                    className={`flex items-center gap-1.5 px-2.5 py-1 font-mono text-[11px] rounded border transition-all shadow-2xs font-semibold ${
                      isSif
                        ? 'bg-red-50 hover:bg-red-100 text-red-900 border-red-300 font-bold'
                        : isHigh
                        ? 'bg-amber-50 hover:bg-amber-100 text-amber-900 border-amber-300 font-bold'
                        : 'bg-slate-50 hover:bg-slate-100 text-slate-800 border-slate-200'
                    }`}
                    title={`View Report ${rep.id} | Site: ${rep.site || 'Site'} | Status: ${isSif ? 'SIF PRECURSOR POTENTIAL' : 'STANDARD'} | Date: ${rep.date || '2026-02-15'}`}
                  >
                    {isSif && (
                      <span className="h-2 w-2 rounded-full bg-red-600 animate-pulse shrink-0" title="SIF Precursor Event" />
                    )}
                    <span>{rep.id}</span>
                    {isSif && (
                      <span className="text-[9px] bg-red-600 text-white px-1 py-0.2 rounded font-sans font-black tracking-tighter">
                        SIF
                      </span>
                    )}
                  </button>
                );
              })}
              {(selectedItem.supporting_reports?.length || selectedItem.supporting_report_ids.length) > 15 && (
                <span className="text-[11px] text-slate-400 font-mono self-center font-semibold">
                  +{(selectedItem.supporting_reports?.length || selectedItem.supporting_report_ids.length) - 15} more
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
