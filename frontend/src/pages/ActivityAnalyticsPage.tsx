import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardService } from '../api';
import type { HighRiskActivitySummary } from '../types/dashboard';
import { PageHeader } from '../components/common/PageHeader';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ArrowRight } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';

export const ActivityAnalyticsPage: React.FC = () => {
  const navigate = useNavigate();
  const [activities, setActivities] = useState<HighRiskActivitySummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        const data = await dashboardService.getActivities();
        setActivities(data);
      } finally {
        setLoading(false);
      }
    };
    fetchActivities();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Analyzing Activity-Level Precursor Distributions..." />;
  }

  const chartData = activities.map((a) => ({
    name: a.activity.split(' ')[0],
    fullName: a.activity,
    sifRate: a.sifRate,
    sifCount: a.sifCount,
    totalReports: a.totalReports,
  }));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Activity-Level Precursor Density Analytics"
        subtitle="Identifying high-energy operational workflows with elevated vulnerability to barrier breakdowns and severe injuries."
        showDemoBadge={true}
      />

      {/* Overview Chart */}
      <div className="hse-card p-5">
        <h2 className="text-sm font-bold text-slate-900 mb-1">
          SIF Precursor Rate (%) by Operational Activity
        </h2>
        <p className="text-xs text-slate-500 mb-4">
          Comparative risk density showing which field activities produce the highest ratio of Serious Injury precursors
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
                formatter={(val) => [`${val}% SIF Rate`, 'Precursor Density']}
              />
              <Bar dataKey="sifRate" fill="#ea580c" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Activity Breakdown Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {activities.map((act) => (
          <div
            key={act.activity}
            onClick={() => navigate(`/reports?activity=${encodeURIComponent(act.activity)}`)}
            className="hse-card p-5 hover:border-slate-400 transition-colors cursor-pointer flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between gap-2 mb-2">
                <h3 className="text-sm font-bold text-slate-900">{act.activity}</h3>
                <SeverityBadge priority={act.riskLevel} size="sm" />
              </div>

              <div className="space-y-2 text-xs border-t border-slate-100 pt-3">
                <div className="flex justify-between">
                  <span className="text-slate-500">Total Reports:</span>
                  <span className="font-semibold text-slate-800">{act.totalReports}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">SIF Precursors:</span>
                  <span className="font-bold text-red-600">{act.sifCount} ({act.sifRate}%)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Primary Hazard Energy:</span>
                  <span className="font-medium text-slate-800 text-right truncate max-w-[150px]">
                    {act.primaryHazard}
                  </span>
                </div>
              </div>

              {/* Density Bar */}
              <div className="mt-3">
                <div className="flex justify-between text-[11px] text-slate-500 mb-1">
                  <span>SIF Vulnerability</span>
                  <span className="font-semibold">{act.sifRate}%</span>
                </div>
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
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-slate-700">
              <span>View Activity Incident Log</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
