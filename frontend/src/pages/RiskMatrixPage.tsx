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
          <div className="bg-amber-50/60 border border-amber-200 rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between border-b border-amber-200 pb-2">
              <span className="text-xs font-black text-amber-900 uppercase flex items-center gap-1">
                <AlertTriangle className="h-3.5 w-3.5 text-amber-600" /> High-Potential / Rare
              </span>
              <span className="text-[10px] font-bold bg-amber-200 text-amber-900 px-2 py-0.5 rounded">
                Sev &ge; 0.50 | Rec &lt; 0.50
              </span>
            </div>
            <div className="max-h-40 overflow-y-auto space-y-1.5 text-xs pr-1">
              {filteredItems.filter((i) => i.quadrant === 'HIGH_SEVERITY_LOW_RECURRENCE').map((item) => (
                <div
                  key={item.matrix_item_id}
                  onClick={() => setSelectedItem(item)}
                  className={`p-2 rounded border cursor-pointer flex items-center justify-between transition-colors ${
                    selectedItem?.matrix_item_id === item.matrix_item_id
                      ? 'bg-amber-900 text-white border-amber-900 font-bold'
                      : 'bg-white text-slate-800 border-amber-200 hover:border-amber-400'
                  }`}
                >
                  <span className="truncate flex-1 pr-2">{item.entity_name}</span>
                  <span className="font-mono text-[11px]">Sev:{item.severity_score.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Top-Right: High Severity / High Recurrence (CRITICAL PRIORITY) */}
          <div className="bg-red-50/60 border border-red-200 rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between border-b border-red-200 pb-2">
              <span className="text-xs font-black text-red-900 uppercase flex items-center gap-1">
                <AlertOctagon className="h-3.5 w-3.5 text-red-600" /> Critical Priority (Frequent & High)
              </span>
              <span className="text-[10px] font-bold bg-red-200 text-red-900 px-2 py-0.5 rounded">
                Sev &ge; 0.50 | Rec &ge; 0.50
              </span>
            </div>
            <div className="max-h-40 overflow-y-auto space-y-1.5 text-xs pr-1">
              {filteredItems.filter((i) => i.quadrant === 'HIGH_SEVERITY_HIGH_RECURRENCE').map((item) => (
                <div
                  key={item.matrix_item_id}
                  onClick={() => setSelectedItem(item)}
                  className={`p-2 rounded border cursor-pointer flex items-center justify-between transition-colors ${
                    selectedItem?.matrix_item_id === item.matrix_item_id
                      ? 'bg-red-900 text-white border-red-900 font-bold'
                      : 'bg-white text-slate-800 border-red-200 hover:border-red-400'
                  }`}
                >
                  <span className="truncate flex-1 pr-2">{item.entity_name}</span>
                  <span className="font-mono text-[11px]">Sev:{item.severity_score.toFixed(2)} | Rec:{item.recurrence_score.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Bottom-Left: Low Severity / Low Recurrence (LOW PRIORITY MONITOR) */}
          <div className="bg-emerald-50/60 border border-emerald-200 rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between border-b border-emerald-200 pb-2">
              <span className="text-xs font-black text-emerald-900 uppercase flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> Low Priority Monitor
              </span>
              <span className="text-[10px] font-bold bg-emerald-200 text-emerald-900 px-2 py-0.5 rounded">
                Sev &lt; 0.50 | Rec &lt; 0.50
              </span>
            </div>
            <div className="max-h-40 overflow-y-auto space-y-1.5 text-xs pr-1">
              {filteredItems.filter((i) => i.quadrant === 'LOW_SEVERITY_LOW_RECURRENCE').map((item) => (
                <div
                  key={item.matrix_item_id}
                  onClick={() => setSelectedItem(item)}
                  className={`p-2 rounded border cursor-pointer flex items-center justify-between transition-colors ${
                    selectedItem?.matrix_item_id === item.matrix_item_id
                      ? 'bg-emerald-900 text-white border-emerald-900 font-bold'
                      : 'bg-white text-slate-800 border-emerald-200 hover:border-emerald-400'
                  }`}
                >
                  <span className="truncate flex-1 pr-2">{item.entity_name}</span>
                  <span className="font-mono text-[11px]">Rec:{item.recurrence_score.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Bottom-Right: Low Severity / High Recurrence (FREQUENT LOWER POTENTIAL) */}
          <div className="bg-blue-50/60 border border-blue-200 rounded-lg p-4 space-y-2">
            <div className="flex items-center justify-between border-b border-blue-200 pb-2">
              <span className="text-xs font-black text-blue-900 uppercase flex items-center gap-1">
                <BarChart2 className="h-3.5 w-3.5 text-blue-600" /> Frequent (Lower-Potential)
              </span>
              <span className="text-[10px] font-bold bg-blue-200 text-blue-900 px-2 py-0.5 rounded">
                Sev &lt; 0.50 | Rec &ge; 0.50
              </span>
            </div>
            <div className="max-h-40 overflow-y-auto space-y-1.5 text-xs pr-1">
              {filteredItems.filter((i) => i.quadrant === 'LOW_SEVERITY_HIGH_RECURRENCE').map((item) => (
                <div
                  key={item.matrix_item_id}
                  onClick={() => setSelectedItem(item)}
                  className={`p-2 rounded border cursor-pointer flex items-center justify-between transition-colors ${
                    selectedItem?.matrix_item_id === item.matrix_item_id
                      ? 'bg-blue-900 text-white border-blue-900 font-bold'
                      : 'bg-white text-slate-800 border-blue-200 hover:border-blue-400'
                  }`}
                >
                  <span className="truncate flex-1 pr-2">{item.entity_name}</span>
                  <span className="font-mono text-[11px]">Rec:{item.recurrence_score.toFixed(2)}</span>
                </div>
              ))}
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

          {/* Cross-Stage Intelligence Navigation Links */}
          <div className="pt-3 border-t border-slate-100 space-y-3">
            <h4 className="font-bold text-xs text-slate-900 uppercase">Cross-Stage Traceability & Drill-Down</h4>
            <div className="flex flex-wrap gap-2 text-xs">
              <button
                onClick={() => navigate('/priorities')}
                className="flex items-center gap-1 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded transition-colors"
              >
                <ShieldAlert className="h-3.5 w-3.5 text-amber-400" /> Stage 30 Priorities <ArrowRight className="h-3 w-3" />
              </button>

              {selectedItem.barrier_pattern_ids.length > 0 && (
                <button
                  onClick={() => navigate('/barrier-patterns')}
                  className="flex items-center gap-1 px-3 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 font-bold rounded transition-colors"
                >
                  <AlertTriangle className="h-3.5 w-3.5 text-amber-600" /> Barrier Failure ({selectedItem.barrier_pattern_ids.length}) <ArrowRight className="h-3 w-3" />
                </button>
              )}

              {selectedItem.pattern_ids.length > 0 && (
                <button
                  onClick={() => navigate('/patterns')}
                  className="flex items-center gap-1 px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-300 font-bold rounded transition-colors"
                >
                  <Layers className="h-3.5 w-3.5 text-purple-600" /> Precursor Pattern ({selectedItem.pattern_ids.length}) <ArrowRight className="h-3 w-3" />
                </button>
              )}

              <button
                onClick={() => navigate('/sites')}
                className="flex items-center gap-1 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-900 border border-blue-300 font-bold rounded transition-colors"
              >
                <MapPin className="h-3.5 w-3.5 text-blue-600" /> Site Risk <ArrowRight className="h-3 w-3" />
              </button>

              <button
                onClick={() => navigate('/activities')}
                className="flex items-center gap-1 px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-900 border border-emerald-300 font-bold rounded transition-colors"
              >
                <Activity className="h-3.5 w-3.5 text-emerald-600" /> Task Risk <ArrowRight className="h-3 w-3" />
              </button>
            </div>
          </div>

          {/* Supporting Incident Report Traceability */}
          <div className="pt-3 border-t border-slate-100 space-y-2">
            <h4 className="font-bold text-xs text-slate-900">Supporting Historical Reports ({selectedItem.supporting_report_ids.length})</h4>
            <div className="flex flex-wrap gap-1.5">
              {selectedItem.supporting_report_ids.slice(0, 15).map((id) => (
                <button
                  key={id}
                  onClick={() => navigate(`/reports/${id}`)}
                  className="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-mono text-[11px] rounded transition-colors"
                >
                  {id}
                </button>
              ))}
              {selectedItem.supporting_report_ids.length > 15 && (
                <span className="text-[11px] text-slate-400 font-mono self-center">
                  +{selectedItem.supporting_report_ids.length - 15} more
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
