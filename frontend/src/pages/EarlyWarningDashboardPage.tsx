import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { earlyWarningsService } from '../api';
import type { EarlyWarningProfile, EarlyWarningListResponse } from '../types/earlyWarnings';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { AlertOctagon, AlertTriangle, TrendingUp, ShieldAlert, MapPin, Activity, Layers, ArrowRight, Info, CheckCircle2 } from 'lucide-react';
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
        const warnList: EarlyWarningProfile[] = data.warnings || [];
        setWarnings(warnList);
        setHighPriorityCount(data.high_priority_count || 0);
        setEarlyWarningCount(data.early_warning_count || 0);
        setWatchCount(data.watch_count || 0);
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

  const getLevelBadge = (level: string, consec: number) => {
    switch (level) {
      case 'HIGH_PRIORITY':
        return (
          <span className="flex items-center gap-1 bg-red-600 text-white font-black text-[10px] px-2 py-0.5 rounded shadow-sm">
            <AlertOctagon className="h-3 w-3" /> HIGH PRIORITY ({consec} PERIODS ↑)
          </span>
        );
      case 'EARLY_WARNING':
        return (
          <span className="flex items-center gap-1 bg-amber-500 text-slate-950 font-extrabold text-[10px] px-2 py-0.5 rounded shadow-sm">
            <AlertTriangle className="h-3 w-3" /> EARLY WARNING ({consec} PERIODS ↑)
          </span>
        );
      case 'WATCH':
        return (
          <span className="flex items-center gap-1 bg-blue-100 text-blue-800 font-bold text-[10px] px-2 py-0.5 rounded border border-blue-300">
            <TrendingUp className="h-3 w-3 text-blue-600" /> WATCH SIGNAL
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

  const chartData = selectedWarning?.time_series.map((ts) => ({
    period: ts.period,
    reportCount: ts.report_count,
    sifDensity: Math.round(ts.sif_density * 100),
  })) || [];

  return (
    <div className="space-y-6 pb-12">
      <PageHeader
        title="Temporal Trend / Early-Warning Intelligence"
        subtitle="Deterministic leading-indicator analytics detecting sustained worsening safety precursor trends requiring HSE attention."
        icon={AlertOctagon}
      />

      {/* Decision-Support Governance Banner */}
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

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Evaluated Warning Signals</span>
          <p className="text-2xl font-black text-slate-900 mt-1">{warnings.length}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">High-Priority Escalations</span>
          <p className="text-2xl font-black text-red-600 mt-1">{highPriorityCount}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Early-Warning Alerts</span>
          <p className="text-2xl font-black text-amber-600 mt-1">{earlyWarningCount}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Watch Signals</span>
          <p className="text-2xl font-black text-blue-600 mt-1">{watchCount}</p>
        </div>
      </div>

      {/* Main Grid: Left Signals List, Right Detail Explorer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left List of Warning Signals */}
        <div className="lg:col-span-1 space-y-3">
          <h3 className="text-sm font-bold text-slate-900 flex items-center justify-between">
            <span>Early-Warning Signals</span>
            <span className="text-xs font-mono text-slate-500 font-normal">Escalation Order</span>
          </h3>

          <div className="space-y-2">
            {warnings.map((w) => (
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
                  <span className="text-sm font-bold truncate">{w.signal_name}</span>
                  {getLevelBadge(w.warning_level, w.consecutive_increasing_periods)}
                </div>

                <div className="mt-2 flex items-center justify-between text-xs opacity-90">
                  <span className="font-mono">Baseline: {w.baseline_value} → Recent: {w.recent_value}</span>
                  <span className="font-bold text-amber-400 font-mono">Delta: {w.delta > 0 ? `+${w.delta}` : w.delta}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Detail & Time Series Explorer */}
        <div className="lg:col-span-2 space-y-4">
          {selectedWarning ? (
            <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm space-y-5">
              <div className="flex items-start justify-between border-b border-slate-100 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <AlertOctagon className="h-5 w-5 text-slate-800" />
                    <h2 className="text-lg font-bold text-slate-900">{selectedWarning.signal_name}</h2>
                    {getLevelBadge(selectedWarning.warning_level, selectedWarning.consecutive_increasing_periods)}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Signal Type: <span className="font-semibold text-slate-700">{selectedWarning.signal_type}</span> | Window: {selectedWarning.first_observed} → {selectedWarning.last_observed}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-400 block font-mono">Consecutive Increases</span>
                  <span className="text-2xl font-black text-red-600 font-mono">{selectedWarning.consecutive_increasing_periods} Periods</span>
                </div>
              </div>

              {/* Rationale Callout */}
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-900">
                <strong>Deterministic Early Warning Rationale:</strong> {selectedWarning.reason}
              </div>

              {/* Time Series Frequency Chart */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-slate-900 uppercase">Monthly Precursor Frequency Trajectory</h3>
                <div className="h-48 w-full bg-slate-50 p-2 rounded border border-slate-200">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                      <XAxis dataKey="period" stroke="#64748B" fontSize={10} />
                      <YAxis stroke="#64748B" fontSize={10} />
                      <Tooltip
                        formatter={(val: number) => [`${val} Reports`, 'Monthly Count']}
                        contentStyle={{ backgroundColor: '#0F172A', color: '#FFF', borderRadius: '6px', fontSize: '11px' }}
                      />
                      <Line type="monotone" dataKey="reportCount" stroke="#D97706" strokeWidth={2.5} dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Affected Sites & Tasks */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                {/* Top Sites */}
                <div className="border border-slate-200 rounded p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-slate-900 uppercase text-[10px] flex items-center gap-1">
                      <MapPin className="h-3 w-3 text-slate-500" /> Affected Operational Sites
                    </h4>
                    <button onClick={() => navigate('/sites')} className="text-[10px] text-blue-600 hover:underline font-bold flex items-center gap-0.5">
                      Site Risk <ArrowRight className="h-2.5 w-2.5" />
                    </button>
                  </div>
                  <ul className="space-y-1">
                    {selectedWarning.affected_sites.map((st) => (
                      <li key={st.site_name} className="flex justify-between text-slate-700">
                        <span className="font-semibold">{st.site_name}</span>
                        <span>{st.count} reports</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Top Activities */}
                <div className="border border-slate-200 rounded p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-slate-900 uppercase text-[10px] flex items-center gap-1">
                      <Activity className="h-3 w-3 text-slate-500" /> Affected Tasks & Activities
                    </h4>
                    <button onClick={() => navigate('/activities')} className="text-[10px] text-blue-600 hover:underline font-bold flex items-center gap-0.5">
                      Task Risk <ArrowRight className="h-2.5 w-2.5" />
                    </button>
                  </div>
                  <ul className="space-y-1">
                    {selectedWarning.affected_activities.map((act) => (
                      <li key={act.activity_name} className="flex justify-between text-slate-700">
                        <span className="font-semibold">{act.activity_name}</span>
                        <span>{act.count} reports</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Linked Barrier Patterns & Precursor Patterns */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-3 border-t border-slate-100">
                {selectedWarning.barrier_pattern_ids.length > 0 && (
                  <div className="space-y-1.5">
                    <h4 className="font-bold text-slate-900 flex items-center gap-1 text-[11px]">
                      <AlertTriangle className="h-3.5 w-3.5 text-amber-600" /> Linked Stage 24 Barrier Failures
                    </h4>
                    <div className="flex flex-wrap gap-1">
                      {selectedWarning.barrier_pattern_ids.map((bId) => (
                        <button
                          key={bId}
                          onClick={() => navigate('/barrier-patterns')}
                          className="px-2 py-0.5 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 font-mono text-[11px] rounded transition-colors"
                        >
                          {bId}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {selectedWarning.pattern_ids.length > 0 && (
                  <div className="space-y-1.5">
                    <h4 className="font-bold text-slate-900 flex items-center gap-1 text-[11px]">
                      <Layers className="h-3.5 w-3.5 text-purple-600" /> Linked Stage 23 Precursor Patterns
                    </h4>
                    <div className="flex flex-wrap gap-1">
                      {selectedWarning.pattern_ids.map((pId) => (
                        <button
                          key={pId}
                          onClick={() => navigate('/patterns')}
                          className="px-2 py-0.5 bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-200 font-mono text-[11px] rounded transition-colors"
                        >
                          {pId}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Supporting Reports */}
              <div className="pt-3 border-t border-slate-100 space-y-2">
                <h4 className="font-bold text-xs text-slate-900">Traceable Safety Reports ({selectedWarning.supporting_incident_ids.length})</h4>
                <div className="flex flex-wrap gap-1.5">
                  {selectedWarning.supporting_incident_ids.map((id) => (
                    <button
                      key={id}
                      onClick={() => navigate(`/reports/${id}`)}
                      className="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-mono text-[11px] rounded transition-colors"
                    >
                      {id}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-lg p-6 text-center text-slate-500 text-xs">
              Select an early-warning signal to inspect detailed time-series metrics and evidence.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
