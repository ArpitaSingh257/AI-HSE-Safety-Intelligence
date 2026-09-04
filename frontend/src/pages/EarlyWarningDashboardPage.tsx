import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { earlyWarningsService } from '../api';
import type { EarlyWarningProfile, EarlyWarningListResponse } from '../types/earlyWarnings';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { AlertOctagon, AlertTriangle, TrendingUp, MapPin, Activity, ArrowRight, Info, CheckCircle2 } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

export const EarlyWarningDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [warnings, setWarnings] = useState<EarlyWarningProfile[]>([]);
  const [highPriorityCount, setHighPriorityCount] = useState<number>(0);
  const [earlyWarningCount, setEarlyWarningCount] = useState<number>(0);
  const [watchCount, setWatchCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [selectedWarning, setSelectedWarning] = useState<EarlyWarningProfile | null>(null);

  useEffect(() => {
    const fetchEarlyWarnings = async () => {
      try {
        const data: EarlyWarningListResponse = await earlyWarningsService.getEarlyWarnings();
        const rawList: EarlyWarningProfile[] = data.warning_signals || data.warnings || [];
        
        const levelRank = (level: string) => {
          if (level === 'HIGH_PRIORITY_ESCALATION' || level === 'HIGH_PRIORITY') return 4;
          if (level === 'EARLY_WARNING_ALERT' || level === 'EARLY_WARNING') return 3;
          if (level === 'WATCH_SIGNAL' || level === 'WATCH') return 2;
          return 1;
        };

        const warnList = [...rawList].sort((a, b) => {
          const rankA = levelRank(a.warning_level || a.level || '');
          const rankB = levelRank(b.warning_level || b.level || '');
          if (rankB !== rankA) return rankB - rankA;
          const deltaA = a.delta_rate ?? a.delta_density ?? 0;
          const deltaB = b.delta_rate ?? b.delta_density ?? 0;
          if (deltaB !== deltaA) return deltaB - deltaA;
          return (b.recent_rate ?? 0) - (a.recent_rate ?? 0);
        });

        setWarnings(warnList);
        setHighPriorityCount(data.high_priority_escalations_count ?? data.high_priority_count ?? 0);
        setEarlyWarningCount(data.early_warning_alerts_count ?? data.early_warning_count ?? 0);
        setWatchCount(data.watch_signals_count ?? data.watch_count ?? 0);
        if (warnList.length > 0) {
          setSelectedWarning(warnList[0]);
        }
      } catch (err) {
        console.warn('Failed to load early warning signals:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchEarlyWarnings();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Evaluating Deterministic Time-Series Signals & Sustained Increase Trajectories..." />;
  }

  const getLevelBadge = (level: string, consec?: number, delta?: number) => {
    const periodCnt = consec ?? 0;
    const deltaStr = delta !== undefined ? (delta >= 0 ? `+${Math.round(delta * 100)}%` : `${Math.round(delta * 100)}%`) : '';
    switch (level) {
      case 'HIGH_PRIORITY_ESCALATION':
      case 'HIGH_PRIORITY':
        return (
          <span className="flex items-center gap-1 bg-red-600 text-white font-black text-[10px] px-2 py-0.5 rounded shadow-sm">
            <AlertOctagon className="h-3 w-3" /> HIGH PRIORITY ({deltaStr || `${periodCnt} PERIODS ↑`})
          </span>
        );
      case 'EARLY_WARNING_ALERT':
      case 'EARLY_WARNING':
        return (
          <span className="flex items-center gap-1 bg-amber-500 text-slate-950 font-extrabold text-[10px] px-2 py-0.5 rounded shadow-sm">
            <AlertTriangle className="h-3 w-3" /> EARLY WARNING ({deltaStr || `${periodCnt} PERIODS ↑`})
          </span>
        );
      case 'WATCH_SIGNAL':
      case 'WATCH':
        return (
          <span className="flex items-center gap-1 bg-blue-100 text-blue-800 font-bold text-[10px] px-2 py-0.5 rounded border border-blue-300">
            <TrendingUp className="h-3 w-3 text-blue-600" /> WATCH SIGNAL ({deltaStr || `${periodCnt} PERIODS`})
          </span>
        );
      case 'NORMAL':
        return (
          <span className="flex items-center gap-1 bg-emerald-100 text-emerald-800 font-bold text-[10px] px-2 py-0.5 rounded border border-emerald-300">
            <CheckCircle2 className="h-3 w-3 text-emerald-600" /> NORMAL
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

  const chartData = (selectedWarning?.monthly_trend || selectedWarning?.time_series || []).map((ts: any) => ({
    period: ts.month || ts.period,
    reportCount: ts.total_reports || ts.report_count || 0,
    sifDensity: Math.round((ts.sif_density || 0) * 100),
  }));

  const selectedName = selectedWarning?.category_name || selectedWarning?.signal_name || selectedWarning?.target_name || 'Operational Warning Signal';
  const selectedConsec = selectedWarning?.consecutive_increases ?? selectedWarning?.consecutive_increasing_periods ?? 0;
  const selectedBase = selectedWarning?.baseline_rate ?? selectedWarning?.baseline_value ?? 0;
  const selectedRecent = selectedWarning?.recent_rate ?? selectedWarning?.recent_value ?? 0;
  const selectedDelta = selectedWarning?.delta_rate ?? selectedWarning?.delta ?? 0;

  return (
    <div className="space-y-6 pb-12">
      <PageHeader
        title="Temporal Trend / Early-Warning Intelligence"
        subtitle="Deterministic leading-indicator analytics detecting sustained worsening safety precursor trends requiring HSE attention."
        icon={AlertOctagon}
      />

      <div className="bg-slate-900 text-white rounded-lg p-4 shadow-sm border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Info className="h-5 w-5 text-amber-400 shrink-0" />
          <div className="text-xs space-y-0.5">
            <p className="font-bold text-amber-300">Decision-Support Safety Intelligence Notice</p>
            <p className="text-slate-300">
              Early-warning signals detect persistent historical precursor increases requiring preventative HSE review. Signals do not predict future incidents.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm relative group">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500 font-bold uppercase">Evaluated Warning Signals</span>
            <div className="relative">
              <Info className="h-4 w-4 text-slate-400 group-hover:text-blue-600 transition-colors cursor-pointer" />
              <div className="absolute right-0 top-6 hidden group-hover:block w-60 bg-slate-900 text-white text-xs p-2.5 rounded-lg shadow-xl z-50 leading-tight border border-slate-700">
                Total operational safety categories monitored across all OIL sites.
              </div>
            </div>
          </div>
          <p className="text-2xl font-black text-slate-900 mt-1">{warnings.length}</p>
          <span className="text-[11px] font-medium text-slate-500 block mt-0.5">(Total Safety Areas Checked)</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm relative group">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500 font-bold uppercase">High-Priority Escalations</span>
            <div className="relative">
              <Info className="h-4 w-4 text-red-400 group-hover:text-red-600 transition-colors cursor-pointer" />
              <div className="absolute right-0 top-6 hidden group-hover:block w-64 bg-slate-900 text-white text-xs p-2.5 rounded-lg shadow-xl z-50 leading-tight border border-slate-700">
                Critical safety gaps increasing over consecutive months needing urgent engineering fix.
              </div>
            </div>
          </div>
          <p className="text-2xl font-black text-red-600 mt-1">{highPriorityCount}</p>
          <span className="text-[11px] font-bold text-red-600 block mt-0.5">(Urgent Action Required)</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm relative group">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500 font-bold uppercase">Early-Warning Alerts</span>
            <div className="relative">
              <Info className="h-4 w-4 text-amber-400 group-hover:text-amber-600 transition-colors cursor-pointer" />
              <div className="absolute right-0 top-6 hidden group-hover:block w-64 bg-slate-900 text-white text-xs p-2.5 rounded-lg shadow-xl z-50 leading-tight border border-slate-700">
                Safety categories showing a sudden upward precursor report increase this month.
              </div>
            </div>
          </div>
          <p className="text-2xl font-black text-amber-600 mt-1">{earlyWarningCount}</p>
          <span className="text-[11px] font-semibold text-amber-700 block mt-0.5">(Rising Risk Alerts)</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm relative group">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500 font-bold uppercase">Watch Signals</span>
            <div className="relative">
              <Info className="h-4 w-4 text-blue-400 group-hover:text-blue-600 transition-colors cursor-pointer" />
              <div className="absolute right-0 top-6 hidden group-hover:block w-64 bg-slate-900 text-white text-xs p-2.5 rounded-lg shadow-xl z-50 leading-tight border border-slate-700">
                Safety categories operating safely within historical background baseline limits.
              </div>
            </div>
          </div>
          <p className="text-2xl font-black text-blue-600 mt-1">{watchCount}</p>
          <span className="text-[11px] font-medium text-blue-600 block mt-0.5">(Normal Safety Watch)</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-3">
          <h3 className="text-sm font-bold text-slate-900 flex items-center justify-between">
            <span>Early-Warning Signals</span>
            <span className="text-xs font-mono text-slate-500 font-normal">Highest Risk First</span>
          </h3>
          <p className="text-[11px] text-slate-500">Monitored Safety Categories (Past Avg → Current Month Rate)</p>

          <div className="space-y-2">
            {warnings.map((w) => {
              const name = w.category_name || w.signal_name || w.target_name || 'Warning Signal';
              const consec = w.consecutive_increases ?? w.consecutive_increasing_periods ?? 0;
              const base = w.baseline_rate ?? w.baseline_value ?? 0;
              const rec = w.recent_rate ?? w.recent_value ?? 0;
              const delta = w.delta_rate ?? w.delta ?? 0;

              return (
                <div
                  key={w.warning_id}
                  onClick={() => setSelectedWarning(w)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                    selectedWarning?.warning_id === w.warning_id
                      ? 'bg-slate-900 text-white border-slate-900 shadow-md'
                      : 'bg-white text-slate-900 border-slate-200 hover:border-slate-400'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-bold truncate" title={name}>{name}</span>
                    {getLevelBadge(w.warning_level, consec, delta)}
                  </div>

                  <div className="mt-2 flex items-center justify-between text-xs opacity-90 font-mono">
                    <div className="flex items-center gap-1 relative group/past" title="Past 6-Month Average vs Current Month Rate">
                      <span>Past Avg: {Math.round(base * 100)}% → Recent: {Math.round(rec * 100)}%</span>
                    </div>
                    <div className="flex items-center gap-1 relative group/delta">
                      <span className="font-bold text-amber-400">Delta: {delta > 0 ? `+${Math.round(delta * 100)}%` : `${Math.round(delta * 100)}%`}</span>
                      <div className="relative inline-block">
                        <Info className="h-3 w-3 text-slate-400 group-hover/delta:text-amber-400 transition-colors cursor-pointer" />
                        <div className="absolute right-0 top-5 hidden group-hover/delta:block w-56 bg-slate-900 text-white text-[11px] p-2 rounded shadow-xl z-50 leading-tight border border-slate-700 font-sans">
                          Net percentage change between current month rate and past 6-month average baseline.
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="lg:col-span-2 space-y-4">
          {selectedWarning ? (
            <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm space-y-5">
              <div className="flex items-start justify-between border-b border-slate-100 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <AlertOctagon className="h-5 w-5 text-slate-800" />
                    <h2 className="text-lg font-bold text-slate-900">{selectedName}</h2>
                    {getLevelBadge(selectedWarning.warning_level, selectedConsec)}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Signal Type: <span className="font-semibold text-slate-700">{selectedWarning.signal_type}</span> | Window: {selectedWarning.first_observed || '01 Jun 2025'} → {selectedWarning.last_observed || '30 Nov 2025'}
                  </p>
                </div>
                <div className="text-right">
                  <div className="flex items-center justify-end gap-1.5 relative group/consec">
                    <span className="text-xs text-slate-400 font-mono">Consecutive Increases</span>
                    <Info className="h-3.5 w-3.5 text-slate-400 group-hover/consec:text-red-600 transition-colors cursor-pointer" />
                    <div className="absolute right-0 top-5 hidden group-hover/consec:block w-64 bg-slate-900 text-white text-xs p-2.5 rounded-lg shadow-xl z-50 leading-tight border border-slate-700 font-sans text-left">
                      Tracks persistent back-to-back monthly risk increases rather than a single accidental spike.
                    </div>
                  </div>
                  <span className="text-2xl font-black text-red-600 font-mono block mt-0.5">{selectedConsec} Periods</span>
                  <span className="text-[10px] text-slate-500 block">(Months Worsening in a Row)</span>
                </div>
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-900">
                <strong>Deterministic Early Warning Rationale (Plain-English Summary):</strong> {selectedWarning.rationale || selectedWarning.reason}
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-900 uppercase">Monthly Precursor SIF Density Trajectory (%)</h3>
                  <span className="text-[11px] text-slate-500 font-medium">(Monthly Trend of Critical Hazard Reports)</span>
                </div>
                <div className="h-48 w-full bg-slate-50 p-2 rounded border border-slate-200">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                      <XAxis dataKey="period" stroke="#64748B" fontSize={10} />
                      <YAxis stroke="#64748B" fontSize={10} unit="%" />
                      <Tooltip
                        formatter={(val: number) => [`${val}%`, 'SIF Precursor Density']}
                        contentStyle={{ backgroundColor: '#0F172A', color: '#FFF', borderRadius: '6px', fontSize: '11px' }}
                      />
                      <Line type="monotone" dataKey="sifDensity" stroke="#D97706" strokeWidth={2.5} dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="border border-slate-200 rounded p-3 space-y-2 relative group/base">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-700">Baseline SIF Density</span>
                    <Info className="h-3.5 w-3.5 text-slate-400 group-hover/base:text-blue-600 transition-colors cursor-pointer" />
                    <div className="absolute left-0 bottom-12 hidden group-hover/base:block w-56 bg-slate-900 text-white text-[11px] p-2 rounded shadow-xl z-50 leading-tight border border-slate-700 font-sans">
                      Historical 6-month average precursor report rate before recent changes.
                    </div>
                  </div>
                  <p className="text-lg font-black text-slate-900">{Math.round(selectedBase * 100)}%</p>
                  <span className="text-[10px] text-slate-500 block">(Past 6-Month Average)</span>
                </div>

                <div className="border border-slate-200 rounded p-3 space-y-2 relative group/rec">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-700">Recent SIF Density</span>
                    <Info className="h-3.5 w-3.5 text-slate-400 group-hover/rec:text-blue-600 transition-colors cursor-pointer" />
                    <div className="absolute left-0 bottom-12 hidden group-hover/rec:block w-56 bg-slate-900 text-white text-[11px] p-2 rounded shadow-xl z-50 leading-tight border border-slate-700 font-sans">
                      Precursor report rate recorded over the latest operational period.
                    </div>
                  </div>
                  <p className="text-lg font-black text-slate-900">{Math.round(selectedRecent * 100)}%</p>
                  <span className="text-[10px] text-slate-500 block">(Current Month Rate)</span>
                </div>

                <div className="border border-slate-200 rounded p-3 space-y-2 relative group/net">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-700">Net Growth Delta</span>
                    <Info className="h-3.5 w-3.5 text-slate-400 group-hover/net:text-amber-500 transition-colors cursor-pointer" />
                    <div className="absolute right-0 bottom-12 hidden group-hover/net:block w-56 bg-slate-900 text-white text-[11px] p-2 rounded shadow-xl z-50 leading-tight border border-slate-700 font-sans">
                      Percentage difference between current month rate and historical baseline.
                    </div>
                  </div>
                  <p className="text-lg font-black text-amber-600">
                    {selectedDelta > 0 ? `+${Math.round(selectedDelta * 100)}%` : `${Math.round(selectedDelta * 100)}%`}
                  </p>
                  <span className="text-[10px] text-slate-500 block">(Net Rate Change)</span>
                </div>
              </div>

              {/* 3-Column Breakdown: Facilities, Activities, RAG Interventions */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="border border-slate-200 rounded p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-slate-900 uppercase text-[10px] flex items-center gap-1">
                      <MapPin className="h-3 w-3 text-slate-500" /> Affected Operational Facilities
                    </h4>
                    <button onClick={() => navigate('/sites')} className="text-[10px] text-blue-600 hover:underline font-bold flex items-center gap-0.5">
                      Site Risk <ArrowRight className="h-2.5 w-2.5" />
                    </button>
                  </div>
                  <ul className="space-y-1.5 max-h-44 overflow-y-auto pr-1 custom-scrollbar">
                    {(selectedWarning.site_breakdown || []).map((st) => (
                      <li key={st.name} className="flex justify-between items-center bg-slate-50 p-1.5 rounded border border-slate-100">
                        <div className="flex items-center gap-1.5">
                          <span className="font-semibold text-slate-800">{st.name}</span>
                          {(st.sif_count ?? 0) > 0 && (
                            <span className="w-2 h-2 rounded-full bg-red-600 inline-block" title={`${st.sif_count} High SIF Precursors`} />
                          )}
                        </div>
                        <span className="text-slate-600 font-bold bg-slate-100 px-2 py-0.5 rounded text-[11px]">
                          {st.count} reports {(st.sif_count ?? 0) > 0 ? `(${st.sif_count} SIF)` : ''}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="border border-slate-200 rounded p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-slate-900 uppercase text-[10px] flex items-center gap-1">
                      <Activity className="h-3 w-3 text-slate-500" /> Associated Work Activities
                    </h4>
                    <button onClick={() => navigate('/activities')} className="text-[10px] text-blue-600 hover:underline font-bold flex items-center gap-0.5">
                      Task Risk <ArrowRight className="h-2.5 w-2.5" />
                    </button>
                  </div>
                  <ul className="space-y-1.5 max-h-28 overflow-y-auto pr-1 custom-scrollbar">
                    {(selectedWarning.activity_breakdown || [
                      { name: selectedWarning.lsr_rule || 'Maintenance', count: selectedWarning.total_reports || 45 }
                    ]).map((act) => (
                      <li key={act.name} className="flex justify-between items-center bg-slate-50 p-1.5 rounded border border-slate-100">
                        <span className="font-semibold text-slate-800 truncate max-w-[140px]" title={act.name}>{act.name}</span>
                        <span className="text-slate-600 font-bold bg-slate-100 px-2 py-0.5 rounded text-[11px]">{act.count} reports</span>
                      </li>
                    ))}
                  </ul>

                  {/* Top Barrier Failure Root Cause Callout */}
                  {(selectedWarning.top_barrier_failures || []).length > 0 && (
                    <div className="pt-1.5 border-t border-slate-100">
                      <span className="text-[10px] font-bold text-amber-800 uppercase block mb-1">⚠️ Mined Root Cause Barrier Failures:</span>
                      <ul className="space-y-1 text-[10px] text-slate-700 bg-amber-50/60 p-1.5 rounded border border-amber-200">
                        {selectedWarning.top_barrier_failures?.map((bf, idx) => (
                          <li key={idx} className="leading-tight flex items-start gap-1">
                            <span className="font-bold text-amber-700">•</span>
                            <span>{bf}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* RAG Prescribed Safety Interventions */}
                <div className="border border-purple-200 bg-purple-50/40 rounded p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-purple-950 uppercase text-[10px] flex items-center gap-1">
                      <AlertTriangle className="h-3 w-3 text-purple-600" /> RAG Prescribed Interventions
                    </h4>
                    <span className="text-[9px] font-bold text-purple-700 bg-purple-100 px-1.5 py-0.5 rounded">RAG Stage 15</span>
                  </div>
                  <div className="space-y-2 max-h-44 overflow-y-auto pr-1 custom-scrollbar text-[11px]">
                    {selectedWarning.rag_recommendations?.immediate_actions?.map((act, i) => (
                      <div key={i} className="bg-white p-2 rounded border border-purple-100 text-purple-950 space-y-0.5 shadow-2xs">
                        <span className="font-extrabold text-[10px] text-red-600 uppercase block">🚀 Immediate Action</span>
                        <p className="leading-tight font-medium text-slate-700">{act}</p>
                      </div>
                    ))}
                    {selectedWarning.rag_recommendations?.recommended_controls?.map((ctrl, i) => (
                      <div key={i} className="bg-white p-2 rounded border border-purple-100 text-purple-950 space-y-0.5 shadow-2xs">
                        <span className="font-extrabold text-[10px] text-purple-700 uppercase block">🛡️ Engineering Control</span>
                        <p className="leading-tight font-medium text-slate-700">{ctrl}</p>
                      </div>
                    ))}
                    {selectedWarning.rag_recommendations?.verification_actions?.map((ver, i) => (
                      <div key={i} className="bg-white p-2 rounded border border-purple-100 text-purple-950 space-y-0.5 shadow-2xs">
                        <span className="font-extrabold text-[10px] text-emerald-700 uppercase block">📋 Field Verification</span>
                        <p className="leading-tight font-medium text-slate-700">{ver}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-xs text-slate-900">
                    Traceable Safety Reports ({selectedWarning.total_reports || (selectedWarning.reports_list || selectedWarning.report_ids || []).length})
                  </h4>
                  <span className="text-[11px] text-slate-500">Click any report badge to inspect AI Stage 43 Deep-Dive</span>
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(selectedWarning.reports_list || (selectedWarning.report_ids || []).map((id: string) => ({
                    id,
                    code: id.startsWith('OILPS') ? id : `REP-${id.slice(-5).toUpperCase()}`,
                    is_sif: false,
                  }))).slice(0, 30).map((rep: any) => {
                    const id = typeof rep === 'string' ? rep : rep.id;
                    const code = typeof rep === 'string' ? (rep.startsWith('OILPS') ? rep : `REP-${rep.slice(-5).toUpperCase()}`) : rep.code;
                    const isSif = typeof rep === 'object' && rep.is_sif;

                    return (
                      <button
                        key={id}
                        onClick={() => navigate(`/reports/${id}`)}
                        className="px-2.5 py-1 bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-400 text-slate-800 font-mono text-[11px] font-semibold rounded-md transition-all flex items-center gap-1.5 shadow-2xs"
                        title="Click to view AI Stage 43 Incident Deep-Dive"
                      >
                        <span>{code}</span>
                        {isSif && <span className="w-1.5 h-1.5 rounded-full bg-red-600 inline-block shrink-0" title="SIF Potential Precursor" />}
                      </button>
                    );
                  })}

                  {(selectedWarning.total_reports || 0) > 30 && (
                    <button
                      onClick={() => navigate(`/reports?warning=${encodeURIComponent(selectedWarning.warning_id)}`)}
                      className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white font-sans text-[11px] font-bold rounded-md transition-all flex items-center gap-1 shadow-2xs"
                    >
                      <span>+ {(selectedWarning.total_reports || 0) - 30} More Reports in Register</span>
                      <ArrowRight className="h-3 w-3" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-lg p-6 text-center text-slate-500 text-xs">
              Select an early-warning signal to inspect detailed trajectory analytics.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
