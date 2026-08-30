import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardService } from '../api';
import type { DashboardOverviewResponse } from '../types/dashboard';
import { PageHeader } from '../components/common/PageHeader';
import { MetricCard } from '../components/common/MetricCard';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  ShieldAlert,
  FileText,
  AlertTriangle,
  MapPin,
  Flame,
  ArrowRight,
  Boxes,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardOverviewResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await dashboardService.getOverview();
        setData(res);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading || !data) {
    return <LoadingSpinner label="Compiling SIF Precursor Intelligence Dashboard..." />;
  }

  const { kpis, highRiskSites, highRiskActivities, topLifeSavingRules, precursorFailures, trends } = data;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Executive HSE & SIF Precursor Dashboard"
        subtitle="Real-time Serious Injury & Fatality precursor detection, barrier failure metrics, and IOGP Life-Saving Rule analytics."
        showDemoBadge={true}
        actions={
          <button
            onClick={() => navigate('/reports')}
            className="flex items-center gap-1.5 rounded bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800 transition-colors"
          >
            <span>View All Reports</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        }
      />

      {/* KPI Top Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Total Safety Reports"
          value={kpis.totalReports.toLocaleString()}
          subValue="Reports Ingested"
          trend={kpis.totalReportsTrend}
          trendLabel="vs previous cycle"
          icon={FileText}
          clickable={true}
          onClick={() => navigate('/reports')}
        />
        <MetricCard
          label="SIF Potential Detected"
          value={`${(kpis.sifPotentialPercentage * 100).toFixed(1)}%`}
          subValue={`${kpis.sifPotentialCount} high-risk reports`}
          trend={kpis.sifTrend}
          trendLabel="SIF density change"
          icon={ShieldAlert}
          riskAccent="CRITICAL"
          clickable={true}
          onClick={() => navigate('/reports?sif_status=SIF_POTENTIAL')}
        />
        <MetricCard
          label="Critical Precursor Clusters"
          value={kpis.criticalPrecursorsCount}
          subValue="Active high-risk patterns"
          icon={Boxes}
          riskAccent="HIGH"
          clickable={true}
          onClick={() => navigate('/patterns')}
        />
        <MetricCard
          label="Active HSE Interventions"
          value={kpis.activeInterventionsCount}
          subValue="Open & in-progress actions"
          icon={AlertTriangle}
          clickable={true}
          onClick={() => navigate('/interventions')}
        />
      </div>

      {/* SIF Monthly Ingestion & Detection Trends Chart */}
      <div className="hse-card p-5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 pb-2 border-b border-slate-100">
          <div>
            <h2 className="text-sm font-bold text-slate-900">
              SIF Precursor Detection Trends (6-Month Horizon)
            </h2>
            <p className="text-xs text-slate-500">
              Distribution of Ingested Reports vs. Confirmed SIF-Potential Precursors
            </p>
          </div>
          <div className="mt-2 sm:mt-0 flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="h-3 w-3 rounded-xs bg-red-600" />
              <span className="text-slate-700 font-medium">SIF Potential</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="h-3 w-3 rounded-xs bg-slate-400" />
              <span className="text-slate-700 font-medium">Non-SIF Controlled</span>
            </div>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="sifColor" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#dc2626" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#dc2626" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="nonSifColor" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#64748b" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#64748b" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={{ stroke: '#cbd5e1' }} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={{ stroke: '#cbd5e1' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  color: '#ffffff',
                  borderRadius: '4px',
                  fontSize: '12px',
                  border: 'none',
                }}
              />
              <Area type="monotone" dataKey="sifPotential" name="SIF Potential" stroke="#dc2626" strokeWidth={2} fillOpacity={1} fill="url(#sifColor)" />
              <Area type="monotone" dataKey="nonSif" name="Non-SIF" stroke="#64748b" strokeWidth={2} fillOpacity={1} fill="url(#nonSifColor)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Two Column Grid: High-Risk Sites & High-Risk Activities */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* High Risk Sites Ranking */}
        <div className="hse-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-slate-700" />
                <h2 className="text-sm font-bold text-slate-900">High-Risk Operational Sites</h2>
              </div>
              <button
                onClick={() => navigate('/sites')}
                className="text-xs font-semibold text-slate-700 hover:text-slate-950 flex items-center gap-1"
              >
                <span>Full Site Analytics</span>
                <ArrowRight className="h-3 w-3" />
              </button>
            </div>

            <div className="space-y-3">
              {highRiskSites.slice(0, 4).map((site) => (
                <div
                  key={site.code}
                  onClick={() => navigate(`/reports?site=${encodeURIComponent(site.site)}`)}
                  className="flex items-center justify-between p-3 rounded border border-slate-200 bg-slate-50/50 hover:bg-slate-100 hover:border-slate-300 transition-colors cursor-pointer"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-xs text-slate-900">{site.site}</span>
                      <SeverityBadge priority={site.riskLevel} size="sm" />
                    </div>
                    <div className="mt-1 text-[11px] text-slate-500">
                      Top Rule Failure: <span className="font-medium text-slate-700">{site.topRule}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-slate-900">{site.sifRate}%</div>
                    <div className="text-[10px] text-slate-500">{site.sifCount} SIF / {site.totalReports} total</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-right">
            <span className="text-[11px] text-slate-500">Click any site to drill down to filtered reports</span>
          </div>
        </div>

        {/* High Risk Activities Ranking */}
        <div className="hse-card p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
              <div className="flex items-center gap-2">
                <Flame className="h-4 w-4 text-slate-700" />
                <h2 className="text-sm font-bold text-slate-900">Precursor Density by Activity</h2>
              </div>
              <button
                onClick={() => navigate('/activities')}
                className="text-xs font-semibold text-slate-700 hover:text-slate-950 flex items-center gap-1"
              >
                <span>Full Activity Analytics</span>
                <ArrowRight className="h-3 w-3" />
              </button>
            </div>

            <div className="space-y-3">
              {highRiskActivities.slice(0, 4).map((act) => (
                <div
                  key={act.activity}
                  onClick={() => navigate(`/reports?activity=${encodeURIComponent(act.activity)}`)}
                  className="p-3 rounded border border-slate-200 bg-slate-50/50 hover:bg-slate-100 hover:border-slate-300 transition-colors cursor-pointer"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-semibold text-xs text-slate-900">{act.activity}</span>
                    <SeverityBadge priority={act.riskLevel} size="sm" />
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 mb-1.5">
                    <span>Hazard: {act.primaryHazard}</span>
                    <span className="font-semibold text-slate-800">{act.sifRate}% SIF Rate</span>
                  </div>
                  {/* Progress bar */}
                  <div className="h-1.5 w-full rounded-full bg-slate-200 overflow-hidden">
                    <div
                      className={`h-full ${
                        act.riskLevel === 'CRITICAL'
                          ? 'bg-red-600'
                          : act.riskLevel === 'HIGH'
                          ? 'bg-orange-600'
                          : act.riskLevel === 'MEDIUM'
                          ? 'bg-amber-500'
                          : 'bg-emerald-500'
                      }`}
                      style={{ width: `${act.sifRate}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-right">
            <span className="text-[11px] text-slate-500">Click any activity to inspect specific safety narratives</span>
          </div>
        </div>
      </div>

      {/* Bottom Section: Top Life-Saving Rules Breakdown & Precursor Failure Matrix */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* IOGP Life-Saving Rules Ranking */}
        <div className="hse-card p-5 lg:col-span-1">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
            <h2 className="text-sm font-bold text-slate-900">IOGP Life-Saving Rules</h2>
            <button
              onClick={() => navigate('/life-saving-rules')}
              className="text-xs font-semibold text-slate-700 hover:text-slate-950 flex items-center gap-1"
            >
              <span>View All 9</span>
              <ArrowRight className="h-3 w-3" />
            </button>
          </div>

          <div className="space-y-2.5">
            {topLifeSavingRules.slice(0, 5).map((rule) => (
              <div
                key={rule.rule}
                onClick={() => navigate(`/reports?life_saving_rule=${encodeURIComponent(rule.rule)}`)}
                className="flex items-center justify-between p-2 rounded hover:bg-slate-100 cursor-pointer transition-colors"
              >
                <div>
                  <div className="font-semibold text-xs text-slate-900">{rule.rule}</div>
                  <div className="text-[10px] text-slate-500">{rule.count} total reports recorded</div>
                </div>
                <div className="text-right">
                  <span className="inline-block rounded bg-red-50 text-red-800 border border-red-200 px-1.5 py-0.5 text-[11px] font-bold">
                    {rule.sifCount} SIF ({rule.percentage}%)
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Precursor Barrier Failure Matrix */}
        <div className="hse-card p-5 lg:col-span-2">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Precursor & Barrier Breakdown Matrix</h2>
              <p className="text-xs text-slate-500">Core operational failures driving high SIF potential</p>
            </div>
            <button
              onClick={() => navigate('/patterns')}
              className="text-xs font-semibold text-slate-700 hover:text-slate-950 flex items-center gap-1"
            >
              <span>Pattern Explorer</span>
              <ArrowRight className="h-3 w-3" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-semibold">
                  <th className="py-2 px-3">Activity</th>
                  <th className="py-2 px-3">Barrier Failure</th>
                  <th className="py-2 px-3">Hazard Energy</th>
                  <th className="py-2 px-3 text-right">Reports</th>
                  <th className="py-2 px-3 text-right">SIF Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {precursorFailures.map((pf, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-semibold text-slate-900">{pf.activity}</td>
                    <td className="py-2.5 px-3">{pf.barrierFailure}</td>
                    <td className="py-2.5 px-3 text-slate-600">{pf.hazard}</td>
                    <td className="py-2.5 px-3 text-right font-medium">{pf.incidentCount}</td>
                    <td className="py-2.5 px-3 text-right">
                      <span className="font-bold text-red-600">{pf.sifRate}%</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
