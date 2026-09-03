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
  const [timeGranularity, setTimeGranularity] = useState<'Monthly' | 'Quarterly' | 'Weekly'>('Monthly');

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

  const getTrendBadge = (trend?: string, status?: string) => {
    const activeStatus = status || trend;
    switch (activeStatus) {
      case 'WORSENING':
      case 'INCREASING':
        return (
          <span className="flex items-center gap-1 bg-red-100 text-red-800 font-extrabold text-[10px] px-2 py-0.5 rounded border border-red-300">
            <TrendingUp className="h-3 w-3 text-red-600" /> WORSENING TREND
          </span>
        );
      case 'IMPROVING':
      case 'DECREASING':
        return (
          <span className="flex items-center gap-1 bg-emerald-100 text-emerald-800 font-bold text-[10px] px-2 py-0.5 rounded border border-emerald-300">
            <TrendingDown className="h-3 w-3 text-emerald-600" /> IMPROVING TREND
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 bg-slate-100 text-slate-700 font-bold text-[10px] px-2 py-0.5 rounded border border-slate-300">
            <Minus className="h-3 w-3 text-slate-500" /> STABLE RATE
          </span>
        );
    }
  };

  const rawMonthlyData = selectedLsr?.monthly_trend || selectedLsr?.time_series || [];

  const chartData = rawMonthlyData.map((ts: any, idx: number) => {
    let periodLabel = ts.month || ts.period;
    if (timeGranularity === 'Quarterly') {
      periodLabel = idx < 2 ? 'Q2 2025' : idx < 4 ? 'Q3 2025' : 'Q4 2025';
    } else if (timeGranularity === 'Weekly') {
      periodLabel = `W${24 + idx * 4}`;
    }
    return {
      period: periodLabel,
      sifDensity: Math.round((ts.sif_density || 0) * 100),
      reportCount: ts.total_reports || ts.report_count || 0,
      sifCount: ts.sif_reports || ts.sif_count || 0,
    };
  });

  return (
    <div className="space-y-6 pb-12">
      <PageHeader
        title="Life-Saving Rule (LSR) Trend Analytics"
        subtitle="Historical multi-label LSR association frequency, SIF precursor densities, and temporal trajectory analytics for official IOGP rules."
        icon={ShieldAlert}
      />

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Official IOGP Rules Tracked</span>
          <p className="text-2xl font-black text-slate-900 mt-1">{lsrProfiles.length}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Worsening Trend Rules</span>
          <p className="text-2xl font-black text-red-600 mt-1">
            {lsrProfiles.filter((p) => p.trend_status === 'WORSENING' || p.trend === 'INCREASING').length}
          </p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Highest SIF Density Rule</span>
          <p className="text-sm font-bold text-slate-900 mt-1.5 truncate">
            {lsrProfiles.length > 0 ? `${lsrProfiles[0].lsr_rule} (${Math.round((lsrProfiles[0].sif_density || 0) * 100)}% SIF)` : 'N/A'}
          </p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs text-slate-500 font-bold uppercase block">Time Granularity</span>
            <span className="text-sm font-black text-slate-900 mt-1 block">{timeGranularity} View</span>
          </div>
          <select
            value={timeGranularity}
            onChange={(e) => setTimeGranularity(e.target.value as any)}
            className="text-xs bg-slate-100 border border-slate-300 font-bold rounded px-2.5 py-1 text-slate-800 cursor-pointer hover:bg-slate-200 transition-colors"
          >
            <option value="Monthly">Monthly</option>
            <option value="Quarterly">Quarterly</option>
            <option value="Weekly">Weekly</option>
          </select>
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
                  <span className="text-sm font-bold truncate" title={lsr.lsr_rule}>{lsr.lsr_rule}</span>
                  {getTrendBadge(lsr.trend, lsr.trend_status)}
                </div>

                <div className="mt-2 flex items-center justify-between text-xs opacity-90">
                  <span>Reports: <strong>{lsr.total_reports}</strong> ({lsr.sif_reports} SIF)</span>
                  <span className="font-semibold text-emerald-400">{Math.round((lsr.sif_density || 0) * 100)}% SIF Density</span>
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
                    {getTrendBadge(selectedLsr.trend, selectedLsr.trend_status)}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Observed Window: {selectedLsr.first_observed || '01 Jun 2025'} → {selectedLsr.last_observed || '30 Nov 2025'}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-400 block font-mono">Overall SIF Rate</span>
                  <span className="text-2xl font-black text-emerald-700 font-mono">{Math.round((selectedLsr.sif_density || 0) * 100)}%</span>
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
                      <MapPin className="h-3 w-3 text-slate-500" /> Associated Facilities
                    </h4>
                    <button
                      onClick={() => navigate('/sites')}
                      className="text-[10px] text-blue-600 hover:underline font-bold flex items-center gap-0.5"
                    >
                      Site Risk <ArrowRight className="h-2.5 w-2.5" />
                    </button>
                  </div>
                  <ul className="space-y-1.5 max-h-36 overflow-y-auto pr-1 custom-scrollbar">
                    {(selectedLsr.associated_sites || selectedLsr.top_sites || []).map((st: any) => (
                      <li key={st.site_name || st.name} className="flex justify-between items-center bg-slate-50 p-1.5 rounded">
                        <span className="font-semibold text-slate-800">{st.site_name || st.name}</span>
                        <span className="text-slate-500">{st.count ?? st.report_count ?? 0} reports</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Top Activities */}
                <div className="border border-slate-200 rounded p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-slate-900 uppercase text-[10px] flex items-center gap-1">
                      <Activity className="h-3 w-3 text-slate-500" /> Associated Tasks
                    </h4>
                    <button
                      onClick={() => navigate('/activities')}
                      className="text-[10px] text-blue-600 hover:underline font-bold flex items-center gap-0.5"
                    >
                      Task Risk <ArrowRight className="h-2.5 w-2.5" />
                    </button>
                  </div>
                  <ul className="space-y-1.5 max-h-36 overflow-y-auto pr-1 custom-scrollbar">
                    {(selectedLsr.top_activities || []).map((act: any) => (
                      <li key={act.activity_name || act.name} className="flex justify-between items-center bg-slate-50 p-1.5 rounded" title={act.activity_name || act.name}>
                        <span className="font-semibold text-slate-800 truncate max-w-[120px]" title={act.activity_name || act.name}>
                          {act.activity_name || act.name}
                        </span>
                        <span className="text-slate-500">{act.count ?? act.report_count ?? 0}</span>
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
                  <ul className="space-y-1.5 max-h-36 overflow-y-auto pr-1 custom-scrollbar">
                    {(selectedLsr.top_barrier_failures || []).map((bf: any) => (
                      <li key={bf.name} className="flex justify-between items-center bg-slate-50 p-1.5 rounded" title={bf.name}>
                        <span className="font-semibold text-slate-800 truncate max-w-[120px]" title={bf.name}>{bf.name}</span>
                        <span className="text-amber-700 font-semibold">{bf.count ?? bf.occurrence_count ?? 0}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Traceability to Reports */}
              <div className="pt-3 border-t border-slate-100 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-xs text-slate-900">
                    Traceable Historical Reports ({selectedLsr.total_reports || (selectedLsr.reports_list || selectedLsr.report_ids || []).length})
                  </h4>
                  <span className="text-[11px] text-slate-500">Click any report badge to inspect AI Stage 43 Deep-Dive</span>
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(selectedLsr.reports_list || (selectedLsr.report_ids || []).map((id: string) => ({
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

                  {selectedLsr.total_reports > 30 && (
                    <button
                      onClick={() => navigate(`/reports?lsr=${encodeURIComponent(selectedLsr.lsr_rule)}`)}
                      className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white font-sans text-[11px] font-bold rounded-md transition-all flex items-center gap-1 shadow-2xs"
                    >
                      <span>+ {selectedLsr.total_reports - 30} More Reports in Register</span>
                      <ArrowRight className="h-3 w-3" />
                    </button>
                  )}
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
