import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { reportsService, intelligenceService } from '../api';
import type { SafetyReport, ReportType, SifStatus, PriorityLevel, CreateReportPayload } from '../types/reports';
import type { Stage43IntelligenceResponse } from '../types/intelligence';
import { useAuth } from '../context/AuthContext';
import { PageHeader } from '../components/common/PageHeader';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Modal } from '../components/common/Modal';
import { EmptyState } from '../components/common/EmptyState';
import { IntelligenceResultView } from '../components/reports/IntelligenceResultView';
import { formatDate, formatScore } from '../utils/formatters';
import {
  Search,
  Plus,
  ArrowUpDown,
  Eye,
  Sparkles,
} from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { hasPermission, user } = useAuth();

  const [reports, setReports] = useState<SafetyReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  // Filters State
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [selectedType, setSelectedType] = useState<string>(searchParams.get('type') || 'ALL');
  const [selectedSite, setSelectedSite] = useState<string>(searchParams.get('site') || 'ALL');
  const [selectedSifStatus, setSelectedSifStatus] = useState<string>(searchParams.get('sif_status') || 'ALL');
  const [selectedPriority, setSelectedPriority] = useState<string>(searchParams.get('priority') || 'ALL');
  const [selectedRule, setSelectedRule] = useState<string>(searchParams.get('life_saving_rule') || 'ALL');
  const [selectedActivity, setSelectedActivity] = useState<string>(searchParams.get('activity') || 'ALL');
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(15);
  const [sortBy, setSortBy] = useState<keyof SafetyReport | 'priority'>('priority');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // New Report Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newReport, setNewReport] = useState<CreateReportPayload>({
    title: '',
    type: 'Unsafe Act',
    date: new Date().toISOString().split('T')[0],
    site: 'Duliajan',
    department: 'Operations',
    location_detail: '',
    activity: 'Maintenance',
    reporter_name: user?.name || 'Debojit Phukan',
    description: '',
    immediate_actions_taken: '',
    priority: 'MEDIUM',
  });

  // Stage 43 Intelligence Analysis Modal State
  const [isIntelligenceModalOpen, setIsIntelligenceModalOpen] = useState(false);
  const [intelText, setIntelText] = useState('');
  const [intelSite, setIntelSite] = useState('');
  const [intelActivity, setIntelActivity] = useState('');
  const [intelPtw, setIntelPtw] = useState('');
  const [intelEquipment, setIntelEquipment] = useState('');
  const [intelResult, setIntelResult] = useState<Stage43IntelligenceResponse | null>(null);
  const [analyzingIntel, setAnalyzingIntel] = useState(false);
  const [intelError, setIntelError] = useState<string | null>(null);

  const handleRunIntelligenceAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!intelText.trim() || intelText.trim().length < 5) {
      setIntelError('Incident narrative must be at least 5 characters long.');
      return;
    }
    setAnalyzingIntel(true);
    setIntelError(null);
    try {
      // Build enriched incident text with PTW and Equipment context if provided
      let enrichedText = intelText.trim();
      const metaTags: string[] = [];
      if (intelPtw.trim()) metaTags.push(`PTW: ${intelPtw.trim()}`);
      if (intelEquipment.trim()) metaTags.push(`Equipment: ${intelEquipment.trim()}`);
      if (metaTags.length > 0) {
        enrichedText = `[${metaTags.join(' | ')}] ${enrichedText}`;
      }

      const res = await intelligenceService.analyzeIntelligence({
        incident_text: enrichedText,
        site: intelSite.trim() || undefined,
        activity: intelActivity.trim() || undefined
      });
      setIntelResult(res);
    } catch (err: any) {
      setIntelError(err.message || 'Failed to run Stage 43 AI Intelligence Analysis.');
    } finally {
      setAnalyzingIntel(false);
    }
  };

  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await reportsService.getReports({
        search,
        type: selectedType as ReportType | 'ALL',
        site: selectedSite,
        activity: selectedActivity,
        sif_status: selectedSifStatus as SifStatus | 'ALL',
        priority: selectedPriority as PriorityLevel | 'ALL',
        life_saving_rule: selectedRule,
        sortBy: sortBy as any,
        sortOrder,
        page,
        limit,
      });
      setReports(res.data);
      setTotal(res.total);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [selectedType, selectedSite, selectedSifStatus, selectedPriority, selectedRule, selectedActivity, sortBy, sortOrder, page, limit]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchReports();
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      const created = await reportsService.createReport(newReport);
      setIsModalOpen(false);
      await reportsService.analyzeReport(created.id);
      fetchReports();
      navigate(`/reports/${created.id}`);
    } finally {
      setCreating(false);
    }
  };

  const handleSort = (field: keyof SafetyReport) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const resetFilters = () => {
    setSearch('');
    setSelectedType('ALL');
    setSelectedSite('ALL');
    setSelectedSifStatus('ALL');
    setSelectedPriority('ALL');
    setSelectedRule('ALL');
    setSelectedActivity('ALL');
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Safety & Precursor Incident Reports"
        subtitle="Comprehensive register of Unsafe Acts, Conditions, Near-Misses, and Incidents across OIL operational assets."
        showDemoBadge={true}
        actions={
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsIntelligenceModalOpen(true)}
              className="flex items-center gap-1.5 rounded bg-emerald-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-800 transition-colors shadow-xs"
            >
              <Sparkles className="h-4 w-4 text-emerald-300" />
              <span>Stage 43 AI Analysis</span>
            </button>
            {hasPermission('canCreateReport') && (
              <button
                onClick={() => setIsModalOpen(true)}
                className="flex items-center gap-1.5 rounded bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800 transition-colors shadow-xs"
              >
                <Plus className="h-4 w-4" />
                <span>Submit Safety Report</span>
              </button>
            )}
          </div>
        }
      />

      {/* Filter and Search Bar Card */}
      <div className="hse-card p-4 space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search reports by ID, free-text narrative, site, hazard, or activity..."
              className="w-full rounded border border-slate-300 bg-white py-2 pl-9 pr-3 text-xs text-slate-900 placeholder-slate-400 focus:border-slate-500 focus:outline-hidden"
            />
          </div>
          <button
            type="submit"
            className="w-full sm:w-auto rounded bg-slate-800 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-900 transition-colors"
          >
            Search
          </button>
          <button
            type="button"
            onClick={resetFilters}
            className="w-full sm:w-auto rounded border border-slate-300 px-3 py-2 text-xs font-medium text-slate-600 hover:bg-slate-100 transition-colors"
          >
            Reset Filters
          </button>
        </form>

        {/* Dropdown Filters */}
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-6 pt-2 border-t border-slate-100 text-xs">
          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Type</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full rounded border border-slate-300 bg-white p-1.5 text-xs text-slate-800"
            >
              <option value="ALL">All Types</option>
              <option value="Unsafe Act">Unsafe Act</option>
              <option value="Unsafe Condition">Unsafe Condition</option>
              <option value="Near-Miss">Near-Miss</option>
              <option value="Incident">Incident</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Site</label>
            <select
              value={selectedSite}
              onChange={(e) => setSelectedSite(e.target.value)}
              className="w-full rounded border border-slate-300 bg-white p-1.5 text-xs text-slate-800"
            >
              <option value="ALL">All Operational Sites</option>
              <option value="Duliajan">Duliajan</option>
              <option value="Moran">Moran</option>
              <option value="Naharkatiya">Naharkatiya</option>
              <option value="Digboi">Digboi</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">SIF Potential</label>
            <select
              value={selectedSifStatus}
              onChange={(e) => setSelectedSifStatus(e.target.value)}
              className="w-full rounded border border-slate-300 bg-white p-1.5 text-xs text-slate-800"
            >
              <option value="ALL">All Statuses</option>
              <option value="SIF_POTENTIAL">SIF Potential</option>
              <option value="NON_SIF">Non-SIF Controlled</option>
              <option value="PENDING_ANALYSIS">Pending Analysis</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Priority</label>
            <select
              value={selectedPriority}
              onChange={(e) => setSelectedPriority(e.target.value)}
              className="w-full rounded border border-slate-300 bg-white p-1.5 text-xs text-slate-800"
            >
              <option value="ALL">All Priorities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Life-Saving Rule</label>
            <select
              value={selectedRule}
              onChange={(e) => setSelectedRule(e.target.value)}
              className="w-full rounded border border-slate-300 bg-white p-1.5 text-xs text-slate-800"
            >
              <option value="ALL">All Rules</option>
              <option value="Control of Hazardous Energy">Control of Hazardous Energy</option>
              <option value="Confined Space Entry">Confined Space Entry</option>
              <option value="Hot Work">Hot Work</option>
              <option value="Work at Height">Work at Height</option>
              <option value="Safe Mechanical Lifting">Safe Mechanical Lifting</option>
              <option value="Line of Fire">Line of Fire</option>
              <option value="Driving">Driving</option>
              <option value="Bypassing Safety Controls">Bypassing Safety Controls</option>
              <option value="Work Authorization">Work Authorization</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-500 mb-1">Activity</label>
            <select
              value={selectedActivity}
              onChange={(e) => setSelectedActivity(e.target.value)}
              className="w-full rounded border border-slate-300 bg-white p-1.5 text-xs text-slate-800"
            >
              <option value="ALL">All Activities</option>
              <option value="Maintenance">Maintenance</option>
              <option value="Rig Floor">Rig Floor</option>
              <option value="Hot Work">Hot Work</option>
              <option value="Confined Space">Confined Space</option>
              <option value="Height Works">Height Works</option>
            </select>
          </div>
        </div>
      </div>

      {/* Reports Data Table */}
      <div className="hse-card overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 bg-slate-50">
          <span className="text-xs font-semibold text-slate-700">
            Showing <strong className="text-slate-900">{reports.length}</strong> of {total} Safety Reports
          </span>
          <span className="text-xs text-slate-500">Sorted by: {String(sortBy)} ({sortOrder})</span>
        </div>

        {loading ? (
          <LoadingSpinner label="Fetching filtered safety reports..." />
        ) : reports.length === 0 ? (
          <EmptyState
            title="No matching reports found"
            description="Try adjusting your search criteria or resetting filters."
            action={
              <button
                onClick={resetFilters}
                className="rounded bg-slate-800 px-3 py-1.5 text-xs font-semibold text-white"
              >
                Reset Filters
              </button>
            }
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs hse-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort('id')} className="cursor-pointer hover:bg-slate-100">
                    <div className="flex items-center gap-1">
                      <span>Report ID</span>
                      <ArrowUpDown className="h-3 w-3 text-slate-400" />
                    </div>
                  </th>
                  <th onClick={() => handleSort('type')} className="cursor-pointer hover:bg-slate-100">Type</th>
                  <th onClick={() => handleSort('date')} className="cursor-pointer hover:bg-slate-100">
                    <div className="flex items-center gap-1">
                      <span>Date</span>
                      <ArrowUpDown className="h-3 w-3 text-slate-400" />
                    </div>
                  </th>
                  <th>Site Asset</th>
                  <th>Activity</th>
                  <th>SIF Status</th>
                  <th onClick={() => handleSort('sif_score')} className="cursor-pointer hover:bg-slate-100">
                    <div className="flex items-center gap-1">
                      <span>SIF Score</span>
                      <ArrowUpDown className="h-3 w-3 text-slate-400" />
                    </div>
                  </th>
                  <th>Life-Saving Rule</th>
                  <th onClick={() => handleSort('priority' as any)} className="cursor-pointer hover:bg-slate-100">
                    <div className="flex items-center gap-1">
                      <span>Priority</span>
                      <ArrowUpDown className="h-3 w-3 text-slate-400" />
                    </div>
                  </th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {reports.map((report) => (
                  <tr
                    key={report.id}
                    onClick={() => navigate(`/reports/${report.id}`)}
                    className="hover:bg-slate-50/80 cursor-pointer transition-colors"
                  >
                    <td className="font-mono font-semibold text-slate-900">{report.id}</td>
                    <td>
                      <span className="font-medium text-slate-700">{report.type}</span>
                    </td>
                    <td className="text-slate-600 whitespace-nowrap">{formatDate(report.date)}</td>
                    <td className="font-medium text-slate-900">{report.site}</td>
                    <td className="text-slate-600">{report.activity}</td>
                    <td>
                      <SeverityBadge sifStatus={report.sif_status} size="sm" />
                    </td>
                    <td className="font-bold text-slate-900">
                      {report.sif_score > 0 ? (
                        <span className={report.sif_score >= 0.7 ? 'text-red-600' : 'text-slate-700'}>
                          {formatScore(report.sif_score)}
                        </span>
                      ) : (
                        <span className="text-slate-400 font-normal">--</span>
                      )}
                    </td>
                    <td>
                      <span className="rounded bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-800 border border-slate-200">
                        {report.life_saving_rule}
                      </span>
                    </td>
                    <td>
                      <SeverityBadge priority={report.priority} size="sm" />
                    </td>
                    <td className="text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/reports/${report.id}`);
                        }}
                        className="inline-flex items-center gap-1 rounded border border-slate-300 bg-white px-2 py-1 text-[11px] font-semibold text-slate-700 hover:bg-slate-100 hover:border-slate-400"
                      >
                        <Eye className="h-3.5 w-3.5" />
                        <span>AI Analysis</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        {total > 0 && (
          <div className="flex flex-col sm:flex-row items-center justify-between px-4 py-3 border-t border-slate-200 bg-slate-50 gap-3 text-xs text-slate-600">
            <div className="flex items-center gap-2">
              <span>Show</span>
              <select
                value={limit}
                onChange={(e) => {
                  setLimit(Number(e.target.value));
                  setPage(1);
                }}
                className="rounded border border-slate-300 bg-white p-1 text-xs text-slate-800"
              >
                <option value={15}>15</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
              <span>reports per page (Total {total.toLocaleString()} reports)</span>
            </div>

            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="rounded border border-slate-300 bg-white px-3 py-1 font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-40 disabled:hover:bg-white transition-colors"
              >
                Previous
              </button>

              <span className="font-semibold text-slate-900 px-2">
                Page {page} of {Math.ceil(total / limit) || 1}
              </span>

              <button
                disabled={page >= Math.ceil(total / limit)}
                onClick={() => setPage((p) => Math.min(Math.ceil(total / limit), p + 1))}
                className="rounded border border-slate-300 bg-white px-3 py-1 font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-40 disabled:hover:bg-white transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* New Report Submission Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Submit New Safety & Incident Observation"
        subtitle="Ingest raw field report narrative for automated NLP Precursor & SIF classification"
        maxWidth="2xl"
        footer={
          <>
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="rounded border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              form="create-report-form"
              disabled={creating}
              className="rounded bg-slate-900 px-4 py-1.5 text-xs font-semibold text-white hover:bg-slate-800 disabled:opacity-50 flex items-center gap-1.5"
            >
              <Sparkles className="h-3.5 w-3.5 text-slate-300" />
              <span>{creating ? 'Ingesting & Analyzing...' : 'Submit & Run AI Pipeline'}</span>
            </button>
          </>
        }
      >
        <form id="create-report-form" onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Report Title / Summary</label>
            <input
              type="text"
              required
              value={newReport.title}
              onChange={(e) => setNewReport({ ...newReport, title: e.target.value })}
              placeholder="e.g. Scaffolding unclamped near compressor discharge line"
              className="w-full rounded border border-slate-300 p-2 text-xs text-slate-900"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Report Type</label>
              <select
                value={newReport.type}
                onChange={(e) => setNewReport({ ...newReport, type: e.target.value as ReportType })}
                className="w-full rounded border border-slate-300 p-2 text-xs text-slate-900"
              >
                <option value="Unsafe Act">Unsafe Act</option>
                <option value="Unsafe Condition">Unsafe Condition</option>
                <option value="Near-Miss">Near-Miss</option>
                <option value="Incident">Incident</option>
              </select>
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Observation Date</label>
              <input
                type="date"
                required
                value={newReport.date}
                onChange={(e) => setNewReport({ ...newReport, date: e.target.value })}
                className="w-full rounded border border-slate-300 p-2 text-xs text-slate-900"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Operational Site Asset</label>
              <select
                value={newReport.site}
                onChange={(e) => setNewReport({ ...newReport, site: e.target.value })}
                className="w-full rounded border border-slate-300 p-2 text-xs text-slate-900"
              >
                <option value="Duliajan">Duliajan</option>
                <option value="Moran">Moran</option>
                <option value="Naharkatiya">Naharkatiya</option>
                <option value="Digboi">Digboi</option>
              </select>
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Primary Activity</label>
              <select
                value={newReport.activity}
                onChange={(e) => setNewReport({ ...newReport, activity: e.target.value })}
                className="w-full rounded border border-slate-300 p-2 text-xs text-slate-900"
              >
                <option value="Maintenance">Maintenance</option>
                <option value="Rig Floor">Rig Floor</option>
                <option value="Hot Work">Hot Work</option>
                <option value="Confined Space">Confined Space</option>
                <option value="Height Works">Height Works</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Original Free-Text Report Narrative (NLP Ingestion Input)
            </label>
            <textarea
              required
              rows={4}
              value={newReport.description}
              onChange={(e) => setNewReport({ ...newReport, description: e.target.value })}
              placeholder="Describe the unsafe act, condition, or near-miss observation in detail including equipment involved, barrier failures, and proximity of workers to energy sources..."
              className="w-full rounded border border-slate-300 p-2 text-xs text-slate-900"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Immediate Actions Taken on Site</label>
            <input
              type="text"
              value={newReport.immediate_actions_taken}
              onChange={(e) => setNewReport({ ...newReport, immediate_actions_taken: e.target.value })}
              placeholder="e.g. Work stopped immediately, area barricaded, supervisor alerted"
              className="w-full rounded border border-slate-300 p-2 text-xs text-slate-900"
            />
          </div>
        </form>
      </Modal>

      {/* Stage 43 AI Intelligence Analysis Modal */}
      <Modal
        isOpen={isIntelligenceModalOpen}
        onClose={() => setIsIntelligenceModalOpen(false)}
        title="OILPS Stage 43 End-to-End Safety Intelligence Pipeline"
        maxWidth="max-w-5xl"
      >
        <div className="space-y-4">
          <form onSubmit={handleRunIntelligenceAnalysis} className="space-y-3 bg-slate-50 p-4 rounded border border-slate-200 text-xs">
            <div>
              <label className="block font-semibold text-slate-800 mb-1">Incident Narrative Text (Required, min 5 chars)</label>
              <textarea
                rows={3}
                required
                value={intelText}
                onChange={(e) => setIntelText(e.target.value)}
                placeholder="Enter safety narrative (e.g., 'Worker entered confined space without gas testing...', 'Operator entered line of fire near suspended load...', or Hinglish text)..."
                className="w-full rounded border border-slate-300 bg-white p-2 text-slate-900 font-mono text-xs focus:border-emerald-500 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Asset Site (Optional Context)</label>
                <input
                  type="text"
                  value={intelSite}
                  onChange={(e) => setIntelSite(e.target.value)}
                  placeholder="e.g., Off-shore Rig 4, Duliajan Complex"
                  className="w-full rounded border border-slate-300 bg-white p-2 text-xs text-slate-900"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Activity (Optional Context)</label>
                <input
                  type="text"
                  value={intelActivity}
                  onChange={(e) => setIntelActivity(e.target.value)}
                  placeholder="e.g., Maintenance, Hot Work, Rig Operations"
                  className="w-full rounded border border-slate-300 bg-white p-2 text-xs text-slate-900"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Permit to Work (PTW) Status (Optional)</label>
                <select
                  value={intelPtw}
                  onChange={(e) => setIntelPtw(e.target.value)}
                  className="w-full rounded border border-slate-300 bg-white p-2 text-xs text-slate-900"
                >
                  <option value="">Select PTW Category (Optional)</option>
                  <option value="Hot Work Permit">Hot Work Permit (Spark/Flame Hazard)</option>
                  <option value="Cold Work Permit">Cold Work Permit (General Operations)</option>
                  <option value="Confined Space Entry Permit">Confined Space Entry Permit</option>
                  <option value="Working at Height Permit">Working at Height Permit</option>
                  <option value="Electrical LOTO Permit">Electrical Isolation / LOTO Permit</option>
                  <option value="Unpermitted / Missing PTW">Unpermitted / Missing PTW</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Equipment / Asset Class (Optional)</label>
                <input
                  type="text"
                  value={intelEquipment}
                  onChange={(e) => setIntelEquipment(e.target.value)}
                  placeholder="e.g., Scaffolding, Pressure Valve, Crane, MCC Panel"
                  className="w-full rounded border border-slate-300 bg-white p-2 text-xs text-slate-900"
                />
              </div>
            </div>

            {intelError && (
              <div className="p-2.5 rounded bg-red-50 text-red-700 text-xs font-medium border border-red-200">
                {intelError}
              </div>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => { setIntelText(''); setIntelSite(''); setIntelActivity(''); setIntelPtw(''); setIntelEquipment(''); setIntelResult(null); setIntelError(null); }}
                className="rounded border border-slate-300 px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100"
              >
                Clear
              </button>
              <button
                type="submit"
                disabled={analyzingIntel}
                className="rounded bg-emerald-700 px-4 py-1.5 text-xs font-bold text-white hover:bg-emerald-800 disabled:opacity-50 flex items-center gap-1.5"
              >
                {analyzingIntel ? (
                  <span>Executing 15-Subsystem Pipeline...</span>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    <span>Run Stage 43 Pipeline</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {analyzingIntel && <LoadingSpinner label="Running Stage 43 Safety Intelligence & Historical Integration Pipeline..." />}

          {intelResult && !analyzingIntel && (
            <div className="mt-4 pt-4 border-t border-slate-200">
              <IntelligenceResultView data={intelResult} />
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};
