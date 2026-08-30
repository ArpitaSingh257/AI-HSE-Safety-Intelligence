import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardService } from '../api';
import type { HighRiskSiteSummary } from '../types/dashboard';
import { PageHeader } from '../components/common/PageHeader';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Navigation, ArrowRight } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';

export const SiteAnalyticsPage: React.FC = () => {
  const navigate = useNavigate();
  const [sites, setSites] = useState<HighRiskSiteSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSite, setSelectedSite] = useState<HighRiskSiteSummary | null>(null);

  useEffect(() => {
    const fetchSites = async () => {
      try {
        const data = await dashboardService.getSites();
        setSites(data);
        if (data.length > 0) setSelectedSite(data[0]);
      } finally {
        setLoading(false);
      }
    };
    fetchSites();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Evaluating Site Precursor Densities across OIL Assets..." />;
  }

  const chartData = sites.map((s) => ({
    name: s.site.split(' ')[0],
    fullName: s.site,
    sifRate: s.sifRate,
    sifCount: s.sifCount,
    totalReports: s.totalReports,
  }));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Site-Level SIF Precursor Density Analytics"
        subtitle="Geographic risk profiling, precursor density ranking, and localized barrier compliance across OIL operational assets."
        showDemoBadge={true}
      />

      {/* Top Chart & Map Overview */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left: Comparative Site SIF Density Chart (7 Cols) */}
        <div className="hse-card p-5 lg:col-span-7">
          <h2 className="text-sm font-bold text-slate-900 mb-1">
            SIF Precursor Rate (%) by Operational Field
          </h2>
          <p className="text-xs text-slate-500 mb-4">
            Percentage of total site safety submissions containing confirmed high-energy precursor signatures
          </p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={{ stroke: '#cbd5e1' }} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} unit="%" axisLine={{ stroke: '#cbd5e1' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    color: '#ffffff',
                    borderRadius: '4px',
                    fontSize: '12px',
                    border: 'none',
                  }}
                  formatter={(value) => [`${value}% SIF Rate`, 'Precursor Density']}
                />
                <Bar dataKey="sifRate" fill="#dc2626" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: Operational Asset Geographic Cards / Visualizer (5 Cols) */}
        <div className="hse-card p-5 lg:col-span-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-100">
              <div className="flex items-center gap-1.5 font-bold text-sm text-slate-900">
                <Navigation className="h-4 w-4 text-slate-700" />
                <span>OIL Field Asset Radar (Assam)</span>
              </div>
              <span className="text-[10px] text-slate-400">Coordinates Validated</span>
            </div>

            {selectedSite ? (
              <div className="space-y-3 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-900 text-sm">{selectedSite.site}</span>
                  <SeverityBadge priority={selectedSite.riskLevel} size="sm" />
                </div>

                <div className="p-3 rounded bg-slate-50 border border-slate-200 space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Asset Code:</span>
                    <span className="font-mono font-bold text-slate-800">{selectedSite.code}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Total Safety Reports:</span>
                    <span className="font-bold text-slate-800">{selectedSite.totalReports}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">SIF Precursors Detected:</span>
                    <span className="font-bold text-red-600">{selectedSite.sifCount} ({selectedSite.sifRate}%)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Top Barrier Breakdown:</span>
                    <span className="font-semibold text-slate-800">{selectedSite.topRule}</span>
                  </div>
                  {selectedSite.coordinates && (
                    <div className="flex justify-between">
                      <span className="text-slate-500">GPS Coordinates:</span>
                      <span className="font-mono text-[11px] text-slate-600">
                        {selectedSite.coordinates[0]}°N, {selectedSite.coordinates[1]}°E
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ) : null}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100">
            <button
              onClick={() => {
                if (selectedSite) {
                  navigate(`/reports?site=${encodeURIComponent(selectedSite.site)}`);
                }
              }}
              className="flex w-full items-center justify-center gap-1.5 rounded bg-slate-900 py-2 text-xs font-semibold text-white hover:bg-slate-800 transition-colors"
            >
              <span>Drill Down into {selectedSite?.site} Reports</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Full Site Ranking Table */}
      <div className="hse-card overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Operational Asset Precursor Ranking Table
          </h2>
          <span className="text-xs text-slate-500">Ranked by SIF Precursor Rate</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs hse-table">
            <thead>
              <tr>
                <th>Asset Code</th>
                <th>Operational Site Name</th>
                <th className="text-right">Total Submissions</th>
                <th className="text-right">SIF Precursors</th>
                <th className="text-right">SIF Density (%)</th>
                <th>Primary Rule Vulnerability</th>
                <th>Risk Priority</th>
                <th className="text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sites.map((site) => (
                <tr
                  key={site.code}
                  onClick={() => setSelectedSite(site)}
                  className={`hover:bg-slate-50 cursor-pointer transition-colors ${
                    selectedSite?.code === site.code ? 'bg-slate-50/80 font-medium' : ''
                  }`}
                >
                  <td className="font-mono font-bold text-slate-800">{site.code}</td>
                  <td className="font-semibold text-slate-900">{site.site}</td>
                  <td className="text-right font-medium">{site.totalReports}</td>
                  <td className="text-right font-bold text-red-600">{site.sifCount}</td>
                  <td className="text-right">
                    <span className="font-bold text-slate-900">{site.sifRate}%</span>
                  </td>
                  <td>
                    <span className="rounded bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-800 border border-slate-200">
                      {site.topRule}
                    </span>
                  </td>
                  <td>
                    <SeverityBadge priority={site.riskLevel} size="sm" />
                  </td>
                  <td className="text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/reports?site=${encodeURIComponent(site.site)}`);
                      }}
                      className="inline-flex items-center gap-1 text-slate-700 hover:text-slate-950 font-semibold text-xs"
                    >
                      <span>Drill-Down</span>
                      <ArrowRight className="h-3 w-3" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
