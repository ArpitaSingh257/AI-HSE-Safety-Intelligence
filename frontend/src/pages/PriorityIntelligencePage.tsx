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

              {/* Rationale Callout */}
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3.5 text-xs text-slate-800">
                <strong>Deterministic Priority Rationale:</strong> {selectedPriority.reason}
              </div>

              {/* Component Score Breakdown */}
              <div className="space-y-3 pt-2">
                <h3 className="text-xs font-bold text-slate-900 uppercase">Normalized Component Scores Breakdown</h3>

                <div className="space-y-2 text-xs">
                  {/* SIF Impact */}
                  <div>
                    <div className="flex justify-between font-semibold text-slate-700 mb-1">
                      <span>SIF Precursor Impact (35% Weight)</span>
                      <span className="font-mono">{Math.round(selectedPriority.components.sif_impact * 100)}%</span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-red-600 rounded-full" style={{ width: `${selectedPriority.components.sif_impact * 100}%` }}></div>
                    </div>
                  </div>

                  {/* Recurrence */}
                  <div>
                    <div className="flex justify-between font-semibold text-slate-700 mb-1">
                      <span>Recurrence Frequency (25% Weight)</span>
                      <span className="font-mono">{Math.round(selectedPriority.components.recurrence * 100)}%</span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-amber-500 rounded-full" style={{ width: `${selectedPriority.components.recurrence * 100}%` }}></div>
                    </div>
                  </div>

                  {/* Barrier Failure */}
                  <div>
                    <div className="flex justify-between font-semibold text-slate-700 mb-1">
                      <span>Barrier Failure Severity (20% Weight)</span>
                      <span className="font-mono">{Math.round(selectedPriority.components.barrier_impact * 100)}%</span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-purple-600 rounded-full" style={{ width: `${selectedPriority.components.barrier_impact * 100}%` }}></div>
                    </div>
                  </div>

                  {/* Site / Activity */}
                  <div>
                    <div className="flex justify-between font-semibold text-slate-700 mb-1">
                      <span>Site / Activity Risk Index (10% Weight)</span>
                      <span className="font-mono">{Math.round(selectedPriority.components.site_activity * 100)}%</span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-blue-600 rounded-full" style={{ width: `${selectedPriority.components.site_activity * 100}%` }}></div>
                    </div>
                  </div>

                  {/* Early Warning Signal */}
                  <div>
                    <div className="flex justify-between font-semibold text-slate-700 mb-1">
                      <span>Early-Warning Signal (10% Weight)</span>
                      <span className="font-mono">{Math.round(selectedPriority.components.early_warning * 100)}%</span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-600 rounded-full" style={{ width: `${selectedPriority.components.early_warning * 100}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Linked Stages & Drill-Down Navigation */}
              <div className="pt-3 border-t border-slate-100 space-y-3">
                <h4 className="font-bold text-xs text-slate-900 uppercase">Cross-Stage Intelligence Navigation</h4>
                <div className="flex flex-wrap gap-2 text-xs">
                  {selectedPriority.barrier_pattern_ids.length > 0 && (
                    <button
                      onClick={() => navigate('/barrier-patterns')}
                      className="flex items-center gap-1 px-3 py-1.5 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 font-bold rounded transition-colors"
                    >
                      <AlertTriangle className="h-3.5 w-3.5 text-amber-600" /> Barrier Failure ({selectedPriority.barrier_pattern_ids.length}) <ArrowRight className="h-3 w-3" />
                    </button>
                  )}

                  {selectedPriority.pattern_ids.length > 0 && (
                    <button
                      onClick={() => navigate('/patterns')}
                      className="flex items-center gap-1 px-3 py-1.5 bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-300 font-bold rounded transition-colors"
                    >
                      <Layers className="h-3.5 w-3.5 text-purple-600" /> Precursor Pattern ({selectedPriority.pattern_ids.length}) <ArrowRight className="h-3 w-3" />
                    </button>
                  )}

                  {selectedPriority.warning_ids.length > 0 && (
                    <button
                      onClick={() => navigate('/early-warnings')}
                      className="flex items-center gap-1 px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-900 border border-red-300 font-bold rounded transition-colors"
                    >
                      <AlertOctagon className="h-3.5 w-3.5 text-red-600" /> Early Warning ({selectedPriority.warning_ids.length}) <ArrowRight className="h-3 w-3" />
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

              {/* Supporting Incident Traceability */}
              <div className="pt-3 border-t border-slate-100 space-y-2">
                <h4 className="font-bold text-xs text-slate-900">Traceable Safety Reports ({selectedPriority.supporting_report_ids.length})</h4>
                <div className="flex flex-wrap gap-1.5">
                  {selectedPriority.supporting_report_ids.slice(0, 15).map((id) => (
                    <button
                      key={id}
                      onClick={() => navigate(`/reports/${id}`)}
                      className="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-mono text-[11px] rounded transition-colors"
                    >
                      {id}
                    </button>
                  ))}
                  {selectedPriority.supporting_report_ids.length > 15 && (
                    <span className="text-[11px] text-slate-400 font-mono self-center">
                      +{selectedPriority.supporting_report_ids.length - 15} more
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
