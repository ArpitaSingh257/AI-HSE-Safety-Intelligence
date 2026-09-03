import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { activityRiskService } from '../api';
import type { AIActivityRiskProfile } from '../types/activityRisk';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Activity, MapPin, AlertTriangle, ShieldAlert, Layers, ArrowRight, CheckCircle2, ChevronRight, Filter, Flame } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, Cell, LabelList, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

export const ActivityAnalyticsPage: React.FC = () => {
  const navigate = useNavigate();
  const [activityProfiles, setActivityProfiles] = useState<AIActivityRiskProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedActivity, setSelectedActivity] = useState<AIActivityRiskProfile | null>(null);

  useEffect(() => {
    const fetchActivityRisk = async () => {
      try {
        const data = await activityRiskService.getActivityRiskProfiles();
        const profiles: AIActivityRiskProfile[] = data.activity_profiles || [];
        setActivityProfiles(profiles);
        if (profiles.length > 0) {
          setSelectedActivity(profiles[0]);
        }
      } catch (err) {
        console.warn('Failed to load activity risk profiles:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchActivityRisk();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Evaluating Volume-Normalized Activity Risk Intelligence across Operational Tasks..." />;
  }

  const getRiskBadgeColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-red-600 text-white font-extrabold border-red-700';
      case 'HIGH':
        return 'bg-amber-600 text-white font-bold border-amber-700';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-900 font-bold border-yellow-300';
      case 'LOW':
        return 'bg-emerald-100 text-emerald-900 font-bold border-emerald-300';
      default:
        return 'bg-slate-100 text-slate-700 font-medium border-slate-300';
    }
  };

  const getBarFillColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return '#dc2626'; // Red
      case 'HIGH':
        return '#ea580c'; // Orange
      case 'MEDIUM':
        return '#d97706'; // Gold
      case 'LOW':
        return '#059669'; // Emerald Green
      default:
        return '#7c3aed';
    }
  };

  const chartData = activityProfiles.map((a) => ({
    name: a.activity_name,
    sifDensity: Math.round((a.sif_density || 0) * 100),
    riskIndex: Math.round((a.risk_index || 0) * 100),
    sifReports: a.sif_reports || 0,
    totalReports: a.total_reports || 0,
    color: getBarFillColor(a.risk_level || 'MEDIUM'),
  }));

  return (
    <div className="space-y-6 pb-12">
      <PageHeader
        title="Activity-Level Risk Intelligence"
        subtitle="Volume-normalized task safety risk ranking, SIF precursor densities, and control gap concentrations across operational activities."
        icon={Activity}
      />

      {/* Top Banner metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Total Activities Evaluated</span>
          <p className="text-2xl font-black text-slate-900 mt-1">{activityProfiles.length}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">High / Critical Risk Activities</span>
          <p className="text-2xl font-black text-red-600 mt-1">
            {activityProfiles.filter((a) => a.risk_level === 'CRITICAL' || a.risk_level === 'HIGH').length}
          </p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Top SIF Precursor Activity</span>
          <p className="text-sm font-bold text-slate-900 mt-1.5 truncate">
            {activityProfiles.length > 0 ? `${activityProfiles[0].activity_name} (${Math.round(activityProfiles[0].sif_density * 100)}% SIF Rate)` : 'N/A'}
          </p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Min Data Threshold</span>
          <p className="text-2xl font-black text-slate-900 mt-1">3 Reports</p>
        </div>
      </div>

      {/* SIF Density Comparison Chart */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm space-y-3">
        <h3 className="text-sm font-bold text-slate-900">SIF Precursor Rate (% SIF Density) by Operational Activity</h3>
        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
              <XAxis dataKey="name" stroke="#64748B" fontSize={11} />
              <YAxis stroke="#64748B" fontSize={11} unit="%" />
              <Tooltip
                formatter={(val: number) => [`${val}%`, 'SIF Density']}
                contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '6px', fontSize: '12px' }}
                itemStyle={{ color: '#FFFFFF', fontWeight: 'bold' }}
                labelStyle={{ color: '#94A3B8', fontWeight: 'bold' }}
              />
              <Bar dataKey="sifDensity" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
                <LabelList dataKey="sifDensity" position="top" formatter={(v: number) => `${v}%`} style={{ fill: '#0F172A', fontSize: '11px', fontWeight: 'bold' }} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Ranked Activity Profiles & Detail Explorer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Ranked Activity List */}
        <div className="lg:col-span-1 space-y-3">
          <h3 className="text-sm font-bold text-slate-900 flex items-center justify-between">
            <span>Ranked Operational Activities</span>
            <span className="text-xs font-mono text-slate-500 font-normal">R_a Score Order</span>
          </h3>

          <div className="space-y-2">
            {activityProfiles.map((act, idx) => (
              <div
                key={act.activity_id}
                onClick={() => setSelectedActivity(act)}
                className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                  selectedActivity?.activity_id === act.activity_id
                    ? 'bg-slate-900 text-white border-slate-900 shadow-md'
                    : 'bg-white text-slate-900 border-slate-200 hover:border-slate-400'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-black font-mono w-5 h-5 flex items-center justify-center rounded ${
                      selectedActivity?.activity_id === act.activity_id ? 'bg-slate-800 text-white' : 'bg-slate-100 text-slate-600'
                    }`}>
                      #{idx + 1}
                    </span>
                    <span className="text-sm font-bold truncate">{act.activity_name}</span>
                  </div>
                  <span className={`text-[10px] uppercase px-2 py-0.5 rounded border ${getRiskBadgeColor(act.risk_level)}`}>
                    {act.risk_level}
                  </span>
                </div>

                <div className="mt-2 flex items-center justify-between text-xs opacity-90">
                  <span>SIF Rate: <strong>{Math.round((act.sif_density || 0) * 100)}%</strong> ({act.sif_reports}/{act.total_reports})</span>
                  <span className="font-mono">R_a: {(act.risk_index || 0).toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Selected Activity Detailed Breakdown */}
        <div className="lg:col-span-2 space-y-4">
          {selectedActivity ? (
            <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm space-y-5">
              <div className="flex items-start justify-between border-b border-slate-100 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <Activity className="h-5 w-5 text-slate-700" />
                    <h2 className="text-lg font-bold text-slate-900">{selectedActivity.activity_name}</h2>
                    <span className={`text-xs uppercase px-2.5 py-0.5 rounded border ${getRiskBadgeColor(selectedActivity.risk_level)}`}>
                      {selectedActivity.risk_level} RISK
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Observed Window: {selectedActivity.first_observed || '01 Aug 2025'} → {selectedActivity.last_observed || '31 Oct 2025'}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-400 font-mono block">Activity Risk Index (R_a)</span>
                  <span className="text-2xl font-black text-slate-900 font-mono">{(selectedActivity.risk_index || 0).toFixed(2)}</span>
                </div>
              </div>

              {/* Core Activity Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs bg-slate-50 p-3.5 rounded-lg border border-slate-200">
                <div>
                  <span className="text-slate-500 block font-bold uppercase text-[10px]">Total Reports</span>
                  <span className="text-base font-bold text-slate-900">{selectedActivity.total_reports || 0}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-bold uppercase text-[10px]">SIF Reports</span>
                  <span className="text-base font-bold text-red-600">{selectedActivity.sif_reports || 0}</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-bold uppercase text-[10px]">SIF Density</span>
                  <span className="text-base font-bold text-emerald-700">{Math.round((selectedActivity.sif_density || 0) * 100)}%</span>
                </div>
                <div>
                  <span className="text-slate-500 block font-bold uppercase text-[10px]">Risk Patterns & Barrier Gaps</span>
                  <span className="text-sm font-bold text-purple-700">
                    {selectedActivity.recurring_pattern_count ?? selectedActivity.stage23_pattern_ids?.length ?? 1} Patterns / {selectedActivity.barrier_failure_pattern_count ?? selectedActivity.stage24_barrier_ids?.length ?? 1} Barrier Gaps
                  </span>
                </div>
              </div>

              {/* Categorical Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                {/* Associated Sites */}
                <div className="border border-slate-200 rounded p-3 space-y-2">
                  <h4 className="font-bold text-slate-900 uppercase text-[11px] flex items-center justify-between">
                    <span className="flex items-center gap-1.5"><MapPin className="h-3.5 w-3.5 text-slate-500" /> Associated Facilities</span>
                    <span className="text-[10px] text-slate-400 font-normal">{(selectedActivity.associated_sites || selectedActivity.top_sites || []).length} Sites</span>
                  </h4>
                  <ul className="space-y-1.5 max-h-44 overflow-y-auto pr-1 custom-scrollbar">
                    {(selectedActivity.associated_sites || selectedActivity.top_sites || []).map((st: any) => (
                      <li key={st.site_name || st.name} className="flex justify-between items-center bg-slate-50 p-2 rounded border border-slate-100">
                        <div className="min-w-0 pr-2">
                          <span className="font-bold text-slate-900 block text-xs truncate">
                            {st.site_name || st.name}
                          </span>
                          <span className="text-[11px] text-slate-500 font-medium block mt-0.5">
                            {st.report_count ?? st.count ?? 0} Total Reports
                          </span>
                        </div>
                        <div className="text-right shrink-0">
                          <span className="text-[11px] font-bold text-red-600 bg-red-50 px-2 py-0.5 rounded border border-red-100 inline-block">
                            {Math.round((st.sif_density || 0) * 100)}% SIF Rate
                          </span>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Recurring Safety Patterns */}
                <div className="border border-slate-200 rounded p-3 space-y-2">
                  <h4 className="font-bold text-slate-900 uppercase text-[11px] flex items-center justify-between">
                    <span className="flex items-center gap-1.5"><Layers className="h-3.5 w-3.5 text-purple-600" /> Recurring Task Safety Patterns</span>
                    <span className="text-[10px] text-slate-400 font-normal">{(selectedActivity.top_patterns || []).length} Patterns</span>
                  </h4>
                  <ul className="space-y-1.5 max-h-44 overflow-y-auto pr-1 custom-scrollbar">
                    {(selectedActivity.top_patterns || []).map((pat: any) => (
                      <li key={pat.name} className="flex justify-between items-center bg-slate-50 p-2 rounded border border-slate-100" title={pat.name}>
                        <span className="font-bold text-slate-900 text-xs truncate max-w-[160px]" title={pat.name}>
                          {pat.name}
                        </span>
                        <span className="text-purple-700 font-bold text-[11px] shrink-0 ml-2 bg-purple-50 px-2 py-0.5 rounded border border-purple-100">
                          {pat.count} occurrences
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Top Hazards / Barrier Failures */}
                <div className="border border-slate-200 rounded p-3 space-y-2">
                  <h4 className="font-bold text-slate-900 uppercase text-[11px] flex items-center justify-between">
                    <span className="flex items-center gap-1.5"><AlertTriangle className="h-3.5 w-3.5 text-amber-600" /> Primary Control / Barrier Failures</span>
                    <span className="text-[10px] text-slate-400 font-normal">{(selectedActivity.top_barrier_failures || selectedActivity.top_hazards || []).length} Failures</span>
                  </h4>
                  <ul className="space-y-1.5 max-h-44 overflow-y-auto pr-1 custom-scrollbar">
                    {(selectedActivity.top_barrier_failures || selectedActivity.top_hazards || []).map((hz: any) => (
                      <li key={hz.name} className="flex justify-between items-center bg-slate-50 p-2 rounded border border-slate-100" title={hz.name}>
                        <span className="font-bold text-slate-900 text-xs truncate max-w-[160px]" title={hz.name}>
                          {hz.name}
                        </span>
                        <span className="text-amber-700 font-bold text-[11px] shrink-0 ml-2 bg-amber-50 px-2 py-0.5 rounded border border-amber-100">
                          {hz.count ?? hz.occurrence_count ?? 0} occurrences
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Contributing Report IDs Traceability */}
              <div className="pt-3 border-t border-slate-100 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-xs text-slate-900">
                    Traceable Historical Reports ({selectedActivity.total_reports || (selectedActivity.report_ids || selectedActivity.incident_ids || []).length})
                  </h4>
                  <span className="text-[11px] text-slate-500">Click any report badge to inspect AI Stage 43 Deep-Dive</span>
                </div>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(selectedActivity.reports_list || (selectedActivity.report_ids || selectedActivity.incident_ids || []).map((id: string) => ({
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

                  {selectedActivity.total_reports > 30 && (
                    <button
                      onClick={() => navigate(`/reports?activity=${encodeURIComponent(selectedActivity.activity_name)}`)}
                      className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-white font-sans text-[11px] font-bold rounded-md transition-all flex items-center gap-1 shadow-2xs"
                    >
                      <span>+ {selectedActivity.total_reports - 30} More Reports in Register</span>
                      <ArrowRight className="h-3 w-3" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-lg p-6 text-center text-slate-500 text-xs">
              Select an operational activity from the ranking list to view detailed risk breakdown.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
