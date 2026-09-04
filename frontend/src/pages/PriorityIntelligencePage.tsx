import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { prioritiesService } from '../api';
import type { HSEPriorityProfile, PriorityListResponse } from '../types/priorities';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  ShieldAlert,
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
  ChevronLeft,
  ChevronRight,
  Filter
} from 'lucide-react';

const ITEMS_PER_PAGE = 20;

export const PriorityIntelligencePage: React.FC = () => {
  const navigate = useNavigate();
  const [priorities, setPriorities] = useState<HSEPriorityProfile[]>([]);
  const [criticalCount, setCriticalCount] = useState<number>(0);
  const [highCount, setHighCount] = useState<number>(0);
  const [mediumCount, setMediumCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [selectedPriority, setSelectedPriority] = useState<HSEPriorityProfile | null>(null);

  // Filters & Pagination State
  const [activeLevelTab, setActiveLevelTab] = useState<string>('ALL');
  const [activeEntityType, setActiveEntityType] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);

  useEffect(() => {
    const fetchPriorities = async () => {
      try {
        const data: PriorityListResponse = await prioritiesService.getPriorities();
        const priList: HSEPriorityProfile[] = data.priorities || [];
        setPriorities(priList);
        setCriticalCount(data.critical_count || 0);
        setHighCount(data.high_count || 0);
        setMediumCount(data.medium_count || 0);
        if (priList.length > 0) {
          setSelectedPriority(priList[0]);
        }
      } catch (err) {
        console.warn('Failed to load HSE priorities:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchPriorities();
  }, []);

  // Filtered & Paginated Priorities
  const filteredPriorities = useMemo(() => {
    return priorities.filter((p) => {
      // Priority Level Filter
      if (activeLevelTab !== 'ALL' && p.priority_level !== activeLevelTab) {
        return false;
      }
      // Entity Type Filter
      if (activeEntityType !== 'ALL' && p.entity_type !== activeEntityType) {
        return false;
      }
      // Search Query Filter
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase();
        const matchName = p.entity_name.toLowerCase().includes(q);
        const matchId = p.entity_id.toLowerCase().includes(q);
        const matchPriId = p.priority_id.toLowerCase().includes(q);
        if (!matchName && !matchId && !matchPriId) return false;
      }
      return true;
    });
  }, [priorities, activeLevelTab, activeEntityType, searchQuery]);

  const totalPages = Math.ceil(filteredPriorities.length / ITEMS_PER_PAGE) || 1;
  const paginatedPriorities = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredPriorities.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredPriorities, currentPage]);

  // Reset to page 1 on filter change
  useEffect(() => {
    setCurrentPage(1);
    if (filteredPriorities.length > 0) {
      setSelectedPriority(filteredPriorities[0]);
    } else {
      setSelectedPriority(null);
    }
  }, [activeLevelTab, activeEntityType, searchQuery]);

  if (loading) {
    return <LoadingSpinner label="Synthesizing SIF Impact, Recurrence, Barrier Failures, Site/Activity Risk Indices, and Early Warnings..." />;
  }

  const getLevelBadge = (level: string, score: number) => {
    switch (level) {
      case 'CRITICAL':
        return (
          <span className="flex items-center gap-1 bg-red-600 text-white font-black text-[10px] px-2 py-0.5 rounded shadow-sm">
            <AlertOctagon className="h-3 w-3" /> CRITICAL (SCORE: {score.toFixed(2)})
          </span>
        );
      case 'HIGH':
        return (
          <span className="flex items-center gap-1 bg-amber-500 text-slate-950 font-extrabold text-[10px] px-2 py-0.5 rounded shadow-sm">
            <AlertTriangle className="h-3 w-3" /> HIGH (SCORE: {score.toFixed(2)})
          </span>
        );
      case 'MEDIUM':
        return (
          <span className="flex items-center gap-1 bg-blue-100 text-blue-800 font-bold text-[10px] px-2 py-0.5 rounded border border-blue-300">
            <BarChart2 className="h-3 w-3 text-blue-600" /> MEDIUM ({score.toFixed(2)})
          </span>
        );
      case 'LOW':
        return (
          <span className="flex items-center gap-1 bg-emerald-100 text-emerald-800 font-bold text-[10px] px-2 py-0.5 rounded border border-emerald-300">
            <CheckCircle2 className="h-3 w-3 text-emerald-600" /> LOW ({score.toFixed(2)})
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
        title="Unified Risk & Priority Intelligence"
        subtitle="Transparent deterministic HSE prioritization synthesizing SIF impact, recurrence, barrier failure severity, site/activity risk indices, and early warnings."
        icon={ShieldAlert}
      />

      {/* Governance Notice */}
      <div className="bg-slate-900 text-white rounded-lg p-4 shadow-sm border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Info className="h-5 w-5 text-amber-400 shrink-0" />
          <div className="text-xs space-y-0.5">
            <p className="font-bold text-amber-300">HSE Prioritization & Governance Notice</p>
            <p className="text-slate-300">
              Priority scores organize preventative HSE focus based on normalized empirical safety intelligence. Scores represent decision-support priorities, not future accident probabilities.
            </p>
          </div>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Total Evaluated Priorities</span>
          <p className="text-2xl font-black text-slate-900 mt-1">{priorities.length}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Critical Priorities</span>
          <p className="text-2xl font-black text-red-600 mt-1">{criticalCount}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">High Priorities</span>
          <p className="text-2xl font-black text-amber-600 mt-1">{highCount}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
          <span className="text-xs text-slate-500 font-bold uppercase">Medium Priorities</span>
          <p className="text-2xl font-black text-blue-600 mt-1">{mediumCount}</p>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          {/* Level Tabs */}
          <div className="flex flex-wrap items-center gap-1.5 text-xs">
            {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INSUFFICIENT_DATA'].map((lvl) => (
              <button
                key={lvl}
                onClick={() => setActiveLevelTab(lvl)}
                className={`px-3 py-1.5 rounded font-bold transition-colors ${
                  activeLevelTab === lvl
                    ? 'bg-slate-900 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {lvl === 'ALL' ? `ALL (${priorities.length})` : lvl}
              </button>
            ))}
          </div>

          {/* Search Box */}
          <div className="relative w-full md:w-64">
            <Search className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search priority entity..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full text-xs pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded focus:outline-none focus:ring-1 focus:ring-slate-900"
            />
          </div>
        </div>

        {/* Entity Type Filter Buttons */}
        <div className="flex items-center gap-2 text-xs pt-2 border-t border-slate-100">
          <Filter className="h-3.5 w-3.5 text-slate-400" />
          <span className="font-semibold text-slate-500">Entity Type:</span>
          {['ALL', 'BARRIER_FAILURE', 'RECURRING_PATTERN', 'SITE', 'ACTIVITY'].map((type) => (
            <button
              key={type}
              onClick={() => setActiveEntityType(type)}
              className={`px-2.5 py-1 rounded text-[11px] font-semibold transition-colors ${
                activeEntityType === type
                  ? 'bg-amber-100 text-amber-900 border border-amber-300 font-bold'
                  : 'bg-slate-50 text-slate-600 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid: Left Priority List (Paginated), Right Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Priority Rankings List */}
        <div className="lg:col-span-1 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-500 font-medium">
            <span>Showing {filteredPriorities.length} items</span>
            <span>Page {currentPage} of {totalPages}</span>
          </div>

          {paginatedPriorities.length > 0 ? (
            <div className="space-y-2">
              {paginatedPriorities.map((p, idx) => {
                const overallIdx = (currentPage - 1) * ITEMS_PER_PAGE + idx + 1;
                return (
                  <div
                    key={p.priority_id}
                    onClick={() => setSelectedPriority(p)}
                    className={`p-3.5 rounded-lg border cursor-pointer transition-all ${
                      selectedPriority?.priority_id === p.priority_id
                        ? 'bg-slate-900 text-white border-slate-900 shadow-md'
                        : 'bg-white text-slate-900 border-slate-200 hover:border-slate-400'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-mono font-bold text-amber-400">#{overallIdx}</span>
                      <span className="text-sm font-bold truncate flex-1">{p.entity_name}</span>
                      {getLevelBadge(p.priority_level, p.priority_score)}
                    </div>

                    <div className="mt-2 flex items-center justify-between text-xs opacity-90">
                      <span className="text-[11px] uppercase tracking-wider font-semibold">{p.entity_type}</span>
                      <span className="font-mono font-bold text-emerald-400">Score: {p.priority_score.toFixed(2)}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-lg p-6 text-center text-slate-500 text-xs">
              No priority items matched the selected filters.
            </div>
          )}

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-2 text-xs">
              <button
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                className="flex items-center gap-1 px-3 py-1.5 bg-white border border-slate-200 rounded disabled:opacity-50 hover:bg-slate-50 font-medium"
              >
                <ChevronLeft className="h-3.5 w-3.5" /> Previous
              </button>
              <span className="font-mono font-semibold text-slate-600">
                {currentPage} / {totalPages}
              </span>
              <button
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                className="flex items-center gap-1 px-3 py-1.5 bg-white border border-slate-200 rounded disabled:opacity-50 hover:bg-slate-50 font-medium"
              >
                Next <ChevronRight className="h-3.5 w-3.5" />
              </button>
            </div>
          )}
        </div>

        {/* Right Detail Explorer */}
        <div className="lg:col-span-2 space-y-4">
          {selectedPriority ? (
            <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm space-y-5">
              <div className="flex items-start justify-between border-b border-slate-100 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <ShieldAlert className="h-5 w-5 text-slate-800" />
                    <h2 className="text-lg font-bold text-slate-900">{selectedPriority.entity_name}</h2>
                    {getLevelBadge(selectedPriority.priority_level, selectedPriority.priority_score)}
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Entity Type: <span className="font-semibold text-slate-700">{selectedPriority.entity_type}</span> | Window: {selectedPriority.first_observed} → {selectedPriority.last_observed}
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-400 block font-mono">Priority Score</span>
                  <span className="text-3xl font-black text-red-600 font-mono">{selectedPriority.priority_score.toFixed(2)}</span>
                </div>
              </div>

              {/* AI Root Cause & Hazard Rationale Callout */}
              <div className="bg-amber-50/70 border border-amber-200 rounded-lg p-4 text-xs space-y-1.5 text-amber-950">
                <div className="flex items-center gap-1.5 font-bold text-amber-900">
                  <ShieldAlert className="h-4 w-4 text-amber-600 shrink-0" />
                  <span>AI Root Cause & Deterministic Prioritization Rationale</span>
                </div>
                <p className="text-slate-800 leading-relaxed">
                  {selectedPriority.reason}
                </p>
              </div>

              {/* Linked Stages & Drill-Down Navigation with Explicit Reasons */}
              <div className="pt-3 border-t border-slate-100 space-y-3">
                <div>
                  <h4 className="font-bold text-xs text-slate-900 uppercase">Cross-Stage Intelligence Navigation & Root Cause Breakdown</h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Click any card below to open its dedicated AI dashboard <strong>pre-filtered for exact root causes</strong> and hazard patterns.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  {/* Barrier Failure Card */}
                  {selectedPriority.barrier_pattern_ids.length > 0 && (
                    <div
                      onClick={() => navigate(`/barrier-patterns?id=${encodeURIComponent(selectedPriority.barrier_pattern_ids[0])}`)}
                      className="p-3 bg-amber-50/70 hover:bg-amber-100/80 border border-amber-300/80 rounded-lg cursor-pointer transition-all space-y-1.5 shadow-sm group"
                    >
                      <div className="flex items-center justify-between font-bold text-amber-900">
                        <span className="flex items-center gap-1.5">
                          <AlertTriangle className="h-4 w-4 text-amber-600 shrink-0" />
                          Barrier Failure ({selectedPriority.barrier_pattern_ids[0]})
                        </span>
                        <ArrowRight className="h-3.5 w-3.5 text-amber-700 group-hover:translate-x-1 transition-transform" />
                      </div>
                      <p className="text-[11px] text-slate-700 leading-snug">
                        <strong>Root Cause Reason:</strong> Breakdown of physical safety controls, permit-to-work protocols, or equipment isolation barriers at {selectedPriority.site_ids[0] || 'site'}.
                      </p>
                    </div>
                  )}

                  {/* Precursor Pattern Card */}
                  {selectedPriority.pattern_ids.length > 0 && (
                    <div
                      onClick={() => navigate(`/patterns?pattern=${encodeURIComponent(selectedPriority.pattern_ids[0])}`)}
                      className="p-3 bg-purple-50/70 hover:bg-purple-100/80 border border-purple-300/80 rounded-lg cursor-pointer transition-all space-y-1.5 shadow-sm group"
                    >
                      <div className="flex items-center justify-between font-bold text-purple-900">
                        <span className="flex items-center gap-1.5">
                          <Layers className="h-4 w-4 text-purple-600 shrink-0" />
                          Precursor Pattern ({selectedPriority.pattern_ids[0]})
                        </span>
                        <ArrowRight className="h-3.5 w-3.5 text-purple-700 group-hover:translate-x-1 transition-transform" />
                      </div>
                      <p className="text-[11px] text-slate-700 leading-snug">
                        <strong>Root Cause Reason:</strong> Recurring cluster of near-misses and unsafe conditions during {selectedPriority.activity_ids[0] || 'activity'} that historically precede SIF events.
                      </p>
                    </div>
                  )}

                  {/* Early Warning Card */}
                  {selectedPriority.warning_ids.length > 0 && (
                    <div
                      onClick={() => navigate(`/early-warnings?id=${encodeURIComponent(selectedPriority.warning_ids[0])}`)}
                      className="p-3 bg-red-50/70 hover:bg-red-100/80 border border-red-300/80 rounded-lg cursor-pointer transition-all space-y-1.5 shadow-sm group"
                    >
                      <div className="flex items-center justify-between font-bold text-red-900">
                        <span className="flex items-center gap-1.5">
                          <AlertOctagon className="h-4 w-4 text-red-600 shrink-0" />
                          Early Warning ({selectedPriority.warning_ids[0]})
                        </span>
                        <ArrowRight className="h-3.5 w-3.5 text-red-700 group-hover:translate-x-1 transition-transform" />
                      </div>
                      <p className="text-[11px] text-slate-700 leading-snug">
                        <strong>Root Cause Reason:</strong> Time-series trend alert triggered due to consecutive escalation spikes in incident reports over recent weeks.
                      </p>
                    </div>
                  )}

                  {/* Site Risk Card */}
                  <div
                    onClick={() => navigate(`/sites?site=${encodeURIComponent(selectedPriority.site_ids[0] || 'Moran')}`)}
                    className="p-3 bg-blue-50/70 hover:bg-blue-100/80 border border-blue-300/80 rounded-lg cursor-pointer transition-all space-y-1.5 shadow-sm group"
                  >
                    <div className="flex items-center justify-between font-bold text-blue-900">
                      <span className="flex items-center gap-1.5">
                        <MapPin className="h-4 w-4 text-blue-600 shrink-0" />
                        Site Risk ({selectedPriority.site_ids[0] || 'Moran'})
                      </span>
                      <ArrowRight className="h-3.5 w-3.5 text-blue-700 group-hover:translate-x-1 transition-transform" />
                    </div>
                    <p className="text-[11px] text-slate-700 leading-snug">
                      <strong>Root Cause Reason:</strong> Operational facility profile evaluated with elevated site-wide hazard index based on worker density and active operations.
                    </p>
                  </div>

                  {/* Task Risk Card */}
                  <div
                    onClick={() => navigate(`/activities?activity=${encodeURIComponent(selectedPriority.activity_ids[0] || 'Maintenance')}`)}
                    className="p-3 bg-emerald-50/70 hover:bg-emerald-100/80 border border-emerald-300/80 rounded-lg cursor-pointer transition-all space-y-1.5 shadow-sm group md:col-span-2"
                  >
                    <div className="flex items-center justify-between font-bold text-emerald-900">
                      <span className="flex items-center gap-1.5">
                        <Activity className="h-4 w-4 text-emerald-600 shrink-0" />
                        Task Risk ({selectedPriority.activity_ids[0] || 'Maintenance'})
                      </span>
                      <ArrowRight className="h-3.5 w-3.5 text-emerald-700 group-hover:translate-x-1 transition-transform" />
                    </div>
                    <p className="text-[11px] text-slate-700 leading-snug">
                      <strong>Root Cause Reason:</strong> Specific high-energy work activity carrying intrinsic task hazards requiring strict Life-Saving Rule compliance.
                    </p>
                  </div>
                </div>
              </div>

              {/* Component Score Breakdown */}
              <div className="space-y-3 pt-3 border-t border-slate-100">
                <h3 className="text-xs font-bold text-slate-900 uppercase">Normalized Component Scores Breakdown</h3>

                {(() => {
                  const getVal = (v: number) => (v > 1 ? Math.min(100, Math.round(v)) : Math.min(100, Math.round(v * 100)));
                  const sifVal = getVal(selectedPriority.components.sif_impact);
                  const recVal = getVal(selectedPriority.components.recurrence);
                  const barVal = getVal(selectedPriority.components.barrier_impact);
                  const siteVal = getVal(selectedPriority.components.site_activity);
                  const warnVal = getVal(selectedPriority.components.early_warning);

                  const sifPts = (sifVal * 0.35).toFixed(1);
                  const recPts = (recVal * 0.25).toFixed(1);
                  const barPts = (barVal * 0.20).toFixed(1);
                  const sitePts = (siteVal * 0.10).toFixed(1);
                  const warnPts = (warnVal * 0.10).toFixed(1);

                  return (
                    <div className="space-y-2.5 text-xs">
                      {/* SIF Impact */}
                      <div>
                        <div className="flex justify-between font-semibold text-slate-700 mb-1">
                          <span>SIF Precursor Impact <span className="text-slate-400 font-normal">(35% Weight)</span></span>
                          <span className="font-mono">
                            <strong className="text-red-600">{sifVal}/100</strong> <span className="text-slate-500 font-normal text-[11px]">(+{sifPts} pts)</span>
                          </span>
                        </div>
                        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-red-600 rounded-full transition-all duration-500" style={{ width: `${sifVal}%` }}></div>
                        </div>
                      </div>

                      {/* Recurrence */}
                      <div>
                        <div className="flex justify-between font-semibold text-slate-700 mb-1">
                          <span>Recurrence Frequency <span className="text-slate-400 font-normal">(25% Weight)</span></span>
                          <span className="font-mono">
                            <strong className="text-amber-600">{recVal}/100</strong> <span className="text-slate-500 font-normal text-[11px]">(+{recPts} pts)</span>
                          </span>
                        </div>
                        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-amber-500 rounded-full transition-all duration-500" style={{ width: `${recVal}%` }}></div>
                        </div>
                      </div>

                      {/* Barrier Failure */}
                      <div>
                        <div className="flex justify-between font-semibold text-slate-700 mb-1">
                          <span>Barrier Failure Severity <span className="text-slate-400 font-normal">(20% Weight)</span></span>
                          <span className="font-mono">
                            <strong className="text-purple-600">{barVal}/100</strong> <span className="text-slate-500 font-normal text-[11px]">(+{barPts} pts)</span>
                          </span>
                        </div>
                        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-purple-600 rounded-full transition-all duration-500" style={{ width: `${barVal}%` }}></div>
                        </div>
                      </div>

                      {/* Site / Activity */}
                      <div>
                        <div className="flex justify-between font-semibold text-slate-700 mb-1">
                          <span>Site / Activity Risk Index <span className="text-slate-400 font-normal">(10% Weight)</span></span>
                          <span className="font-mono">
                            <strong className="text-blue-600">{siteVal}/100</strong> <span className="text-slate-500 font-normal text-[11px]">(+{sitePts} pts)</span>
                          </span>
                        </div>
                        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-blue-600 rounded-full transition-all duration-500" style={{ width: `${siteVal}%` }}></div>
                        </div>
                      </div>

                      {/* Early Warning Signal */}
                      <div>
                        <div className="flex justify-between font-semibold text-slate-700 mb-1">
                          <span>Early-Warning Signal <span className="text-slate-400 font-normal">(10% Weight)</span></span>
                          <span className="font-mono">
                            <strong className="text-emerald-600">{warnVal}/100</strong> <span className="text-slate-500 font-normal text-[11px]">(+{warnPts} pts)</span>
                          </span>
                        </div>
                        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div className="h-full bg-emerald-600 rounded-full transition-all duration-500" style={{ width: `${warnVal}%` }}></div>
                        </div>
                      </div>

                      <p className="text-[10px] text-slate-500 bg-slate-50 p-2 rounded border border-slate-200 mt-2 font-mono">
                        💡 <strong>Mathematical Formula:</strong> Priority Score ({selectedPriority.priority_score.toFixed(2)}) = Sum of weighted points ({sifPts} + {recPts} + {barPts} + {sitePts} + {warnPts}).
                      </p>
                    </div>
                  );
                })()}
              </div>

              {/* AI RAG Safety Recommendation Engine Card (Light Theme, Placed BELOW Normalized Component Scores Breakdown) */}
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
                    {selectedPriority.recommendations?.rag_citations.map((citation) => (
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
                      {selectedPriority.recommendations?.engineering_control || `Enforce mandatory dual gas-calibration, isolation lockout (LOTO), and automated barrier verification for ${selectedPriority.entity_name}.`}
                    </p>
                  </div>

                  {/* Procedural Protocol */}
                  <div className="bg-white/90 p-2.5 rounded border border-emerald-200/80 space-y-0.5 shadow-2xs">
                    <span className="text-blue-800 font-bold text-[10px] uppercase block tracking-wider">📋 Procedural & Field Protocol</span>
                    <p className="text-slate-800 text-[11px] leading-relaxed">
                      {selectedPriority.recommendations?.procedural_protocol || `Enforce 2-person standby rescue teams, continuous multi-gas monitoring, and digital PTW authorization.`}
                    </p>
                  </div>

                  {/* Governance Audit */}
                  <div className="bg-white/90 p-2.5 rounded border border-emerald-200/80 space-y-0.5 shadow-2xs">
                    <span className="text-purple-800 font-bold text-[10px] uppercase block tracking-wider">🔍 Governance & Inspection Audit</span>
                    <p className="text-slate-800 text-[11px] leading-relaxed">
                      {selectedPriority.recommendations?.governance_audit || `Schedule immediate 48-hour Stage 42 HSE supervisory safety audit.`}
                    </p>
                  </div>
                </div>

                {/* Deploy Action Button */}
                <div className="pt-2 flex items-center justify-between border-t border-emerald-200/80 text-xs">
                  <span className="text-[10px] text-emerald-800 font-semibold">Status: Recommended RAG Controls Ready</span>
                  <button
                    onClick={() => {
                      const site = selectedPriority.site_ids[0] || 'Moran';
                      const activity = selectedPriority.activity_ids[0] || 'Maintenance';
                      const title = `Deploy AI RAG Safety Controls for ${selectedPriority.entity_name}`;
                      const desc = selectedPriority.recommendations?.engineering_control || selectedPriority.reason;
                      navigate(`/interventions?deploy=true&site=${encodeURIComponent(site)}&activity=${encodeURIComponent(activity)}&title=${encodeURIComponent(title)}&desc=${encodeURIComponent(desc)}`);
                    }}
                    className="flex items-center gap-1.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold px-3 py-1.5 rounded shadow-sm transition-colors text-[11px]"
                  >
                    🚀 Deploy RAG Recommendation to Interventions <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>

              {/* Supporting Incident Traceability with Dynamic Color Coding */}
              <div className="pt-3 border-t border-slate-100 space-y-2">
                <div>
                  <h4 className="font-bold text-xs text-slate-900 flex items-center gap-2">
                    <span>Traceable Safety Reports ({selectedPriority.supporting_reports?.length || selectedPriority.supporting_report_ids.length})</span>
                    <span className="text-[10px] font-normal text-slate-500 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                      Live MongoDB Atlas Evidence
                    </span>
                  </h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Ground-truth field incident & near-miss reports used by AI to compute score. Red pulsing dots indicate SIF Precursor potential.
                  </p>
                </div>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(selectedPriority.supporting_reports && selectedPriority.supporting_reports.length > 0
                    ? selectedPriority.supporting_reports
                    : selectedPriority.supporting_report_ids.map(id => ({ id, sif_status: 'NON_SIF', priority: 'MEDIUM' }))
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
                  {(selectedPriority.supporting_reports?.length || selectedPriority.supporting_report_ids.length) > 15 && (
                    <span className="text-[11px] text-slate-400 font-mono self-center font-semibold">
                      +{(selectedPriority.supporting_reports?.length || selectedPriority.supporting_report_ids.length) - 15} more
                    </span>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-lg p-6 text-center text-slate-500 text-xs">
              Select an HSE priority entity to inspect detailed component breakdown and evidence.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
