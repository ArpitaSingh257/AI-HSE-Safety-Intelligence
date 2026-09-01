import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { lsrTrendsService } from '../api';
import type { AILsrTrendProfile, LsrTrendListResponse } from '../types/lsrTrends';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ShieldAlert, TrendingUp, TrendingDown, Minus, MapPin, Activity, AlertTriangle, ArrowRight, Layers, Info } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

export const LifeSavingRulesPage: React.FC = () => {
  const navigate = useNavigate();
  const [lsrProfiles, setLsrProfiles] = useState<AILsrTrendProfile[]>([]);
  const [unknownLsrCount, setUnknownLsrCount] = useState<number>(0);
  const [unknownLsrRate, setUnknownLsrRate] = useState<number>(0.0);
  const [loading, setLoading] = useState(true);
  const [selectedLsr, setSelectedLsr] = useState<AILsrTrendProfile | null>(null);

  useEffect(() => {
    const fetchLsrTrends = async () => {
      try {
        const data: LsrTrendListResponse = await lsrTrendsService.getLsrTrendProfiles();
        const profiles: AILsrTrendProfile[] = data.lsr_profiles || [];
        setLsrProfiles(profiles);
        setUnknownLsrCount(data.unknown_lsr_records || 0);
        setUnknownLsrRate(data.unknown_lsr_rate || 0.0);
        if (profiles.length > 0) {
          setSelectedLsr(profiles[0]);
        }
      } catch (err) {
        console.warn('Failed to load LSR trend profiles:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchLsrTrends();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Analyzing Temporal Trajectories & SIF Rates across Official IOGP Life-Saving Rules..." />;
  }

  const getTrendBadge = (trend: string, delta: number) => {
    switch (trend) {
      case 'INCREASING':
        return (
          <span className="flex items-center gap-1 bg-red-100 text-red-800 font-extrabold text-[10px] px-2 py-0.5 rounded border border-red-300">
            <TrendingUp className="h-3 w-3 text-red-600" /> WORSENING (+{Math.round(delta * 100)}%)
          </span>
        );
      case 'DECREASING':
        return (
          <span className="flex items-center gap-1 bg-emerald-100 text-emerald-800 font-bold text-[10px] px-2 py-0.5 rounded border border-emerald-300">
            <TrendingDown className="h-3 w-3 text-emerald-600" /> IMPROVING ({Math.round(delta * 100)}%)
          </span>
        );
      case 'STABLE':
        return (
          <span className="flex items-center gap-1 bg-slate-100 text-slate-700 font-bold text-[10px] px-2 py-0.5 rounded border border-slate-300">
            <Minus className="h-3 w-3 text-slate-500" /> STABLE RATE
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

  const chartData = selectedLsr?.time_series.map((ts) => ({
    period: ts.period,
    sifDensity: Math.round(ts.sif_density * 100),
    reportCount: ts.report_count,
    sifCount: ts.sif_count,
  })) || [];

  return (
    <div className="space-y-6 pb-12">
      <PageHeader
        title="Life-Saving Rule (LSR) Trend Analytics"
        subtitle="Historical multi-label LSR association frequency, SIF precursor densities, and temporal trajectory analytics for official IOGP rules."
        icon={ShieldAlert}
      />

      {/* Data Quality Notice */}
      {unknownLsrCount > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Info className="h-4 w-4 text-amber-600 shrink-0" />
            <span>
              <strong>Data Quality Notice:</strong> {unknownLsrCount} safety reports ({Math.round(unknownLsrRate * 100)}% of dataset) have unclassified or missing Life-Saving Rule labels. They are tracked separately for data quality and excluded from official IOGP rule trend analytics.
            </span>
          </div>
        </div>
      )}

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Official IOGP Rules Tracked</span>
          <p className="text-2xl font-black text-slate-900 mt-1">{lsrProfiles.length}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Worsening Trend Rules</span>
          <p className="text-2xl font-black text-red-600 mt-1">
            {lsrProfiles.filter((p) => p.trend === 'INCREASING').length}
          </p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Highest SIF Density Rule</span>
          <p className="text-sm font-bold text-slate-900 mt-1.5 truncate">
            {lsrProfiles.length > 0 ? `${lsrProfiles[0].lsr_rule} (${Math.round(lsrProfiles[0].sif_density * 100)}% SIF)` : 'N/A'}
          </p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Time Granularity</span>
          <p className="text-2xl font-black text-slate-900 mt-1">Monthly (YYYY-MM)</p>
        </div>
      </div>

      {/* Main Grid: Left Rules List, Right Detail Explorer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left List of LSR Rules */}
        <div className="lg:col-span-1 space-y-3">
          <h3 className="text-sm font-bold text-slate-900 flex items-center justify-between">
            <span>Official IOGP Life-Saving Rules</span>
            <span className="text-xs font-mono text-slate-500 font-normal">Report Count Order</span>
          </h3>

          <div className="space-y-2">
            {lsrProfiles.map((lsr) => (
              <div
                key={lsr.lsr_rule}
                onClick={() => setSelectedLsr(lsr)}
                className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                  selectedLsr?.lsr_rule === lsr.lsr_rule
                    ? 'bg-slate-900 text-white border-slate-900 shadow-md'
                    : 'bg-white text-slate-900 border-slate-200 hover:border-slate-400'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-bold truncate">{lsr.lsr_rule}</span>
                  {getTrendBadge(lsr.trend, lsr.trend_delta)}
                </div>

                <div className="mt-2 flex items-center justify-between text-xs opacity-90">
                  <span>Reports: <strong>{lsr.total_reports}</strong> ({lsr.sif_reports} SIF)</span>
                  <span className="font-semibold text-emerald-400">{Math.round(lsr.sif_density * 100)}% SIF Density</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Detail & Time Series Chart */}
        <div className="lg:col-span-2 space-y-4">
          {selectedLsr ? (
            <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm space-y-5">
              <div className="flex items-start justify-between border-b border-slate-100 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="h-5 w-5 text-slate-800" />
                    <h2 className="text-lg font-bold text-slate-900">{selectedLsr.lsr_rule}</h2>
                    {getTrendBadge(selectedLsr.trend, selectedLsr.trend_delta)}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Observed Window: {selectedLsr.first_observed} → {selectedLsr.last_observed}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-400 block font-mono">Overall SIF Rate</span>
                  <span className="text-2xl font-black text-emerald-700 font-mono">{Math.round(selectedLsr.sif_density * 100)}%</span>
                </div>
              </div>

              {/* Time Series SIF Density Chart */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-slate-900 uppercase">Monthly SIF Precursor Density Trajectory</h3>
                <div className="h-48 w-full bg-slate-50 p-2 rounded border border-slate-200">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                      <XAxis dataKey="period" stroke="#64748B" fontSize={10} />
                      <YAxis stroke="#64748B" fontSize={10} unit="%" />
                      <Tooltip
                        formatter={(val: number) => [`${val}%`, 'SIF Density']}
                        contentStyle={{ backgroundColor: '#0F172A', color: '#FFF', borderRadius: '6px', fontSize: '11px' }}
                      />
                      <Line type="monotone" dataKey="sifDensity" stroke="#DC2626" strokeWidth={2.5} dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Cross-Stage Associations Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                {/* Top Sites */}
                <div className="border border-slate-200 rounded p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-slate-900 uppercase text-[10px] flex items-center gap-1">
                      <MapPin className="h-3 w-3 text-slate-500" /> Top Associated Sites
                    </h4>
                    <button
                      onClick={() => navigate('/sites')}
                      className="text-[10px] text-blue-600 hover:underline font-bold flex items-center gap-0.5"
                    >
                      Site Risk <ArrowRight className="h-2.5 w-2.5" />
                    </button>
                  </div>
                  <ul className="space-y-1">
                    {selectedLsr.top_sites.map((st) => (
                      <li key={st.site_name} className="flex justify-between text-slate-700">
                        <span className="font-semibold">{st.site_name}</span>
                        <span>{st.count}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Top Activities */}
                <div className="border border-slate-200 rounded p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-slate-900 uppercase text-[10px] flex items-center gap-1">
                      <Activity className="h-3 w-3 text-slate-500" /> Top Associated Tasks
                    </h4>
                    <button
                      onClick={() => navigate('/activities')}
                      className="text-[10px] text-blue-600 hover:underline font-bold flex items-center gap-0.5"
                    >
                      Task Risk <ArrowRight className="h-2.5 w-2.5" />
                    </button>
                  </div>
                  <ul className="space-y-1">
                    {selectedLsr.top_activities.map((act) => (
                      <li key={act.activity_name} className="flex justify-between text-slate-700">
                        <span className="font-semibold">{act.activity_name}</span>
                        <span>{act.count}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Top Barrier Failures */}
                <div className="border border-slate-200 rounded p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-slate-900 uppercase text-[10px] flex items-center gap-1">
                      <AlertTriangle className="h-3 w-3 text-amber-600" /> Barrier Failure Gaps
                    </h4>
                    <button
                      onClick={() => navigate('/barrier-patterns')}
                      className="text-[10px] text-purple-600 hover:underline font-bold flex items-center gap-0.5"
                    >
                      Barriers <ArrowRight className="h-2.5 w-2.5" />
                    </button>
                  </div>
                  <ul className="space-y-1">
                    {selectedLsr.top_barrier_failures.map((bf) => (
                      <li key={bf.name} className="flex justify-between text-slate-700">
                        <span className="font-semibold truncate max-w-[120px]">{bf.name}</span>
                        <span className="text-amber-700 font-semibold">{bf.count}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Linked Stage 23 Recurring Patterns */}
              {selectedLsr.recurring_pattern_ids && selectedLsr.recurring_pattern_ids.length > 0 && (
                <div className="pt-3 border-t border-slate-100 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-xs text-slate-900 flex items-center gap-1.5">
                      <Layers className="h-3.5 w-3.5 text-purple-600" /> Linked Stage 23 Precursor Patterns ({selectedLsr.recurring_pattern_ids.length})
                    </h4>
                    <button
                      onClick={() => navigate('/patterns')}
                      className="text-[11px] text-purple-700 hover:underline font-bold flex items-center gap-1"
                    >
                      Pattern Explorer <ArrowRight className="h-3 w-3" />
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {selectedLsr.recurring_pattern_ids.map((patId) => (
                      <button
                        key={patId}
                        onClick={() => navigate('/patterns')}
                        className="px-2 py-0.5 bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-200 font-mono text-[11px] rounded transition-colors"
                      >
                        {patId}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Traceability to Reports */}
              <div className="pt-3 border-t border-slate-100 space-y-2">
                <h4 className="font-bold text-xs text-slate-900">Traceable Safety Reports ({selectedLsr.report_ids.length})</h4>
                <div className="flex flex-wrap gap-1.5">
                  {selectedLsr.report_ids.map((id) => (
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
              Select an official Life-Saving Rule to inspect detailed temporal trend trajectory.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
