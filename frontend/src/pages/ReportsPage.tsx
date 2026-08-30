import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { reportsService } from '../api';
import type { SafetyReport, ReportType, SifStatus, PriorityLevel, CreateReportPayload } from '../types/reports';
import { useAuth } from '../context/AuthContext';
import { PageHeader } from '../components/common/PageHeader';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Modal } from '../components/common/Modal';
import { EmptyState } from '../components/common/EmptyState';
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
  const [sortBy, setSortBy] = useState<keyof SafetyReport>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // New Report Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newReport, setNewReport] = useState<CreateReportPayload>({
    title: '',
    type: 'Unsafe Act',
    date: new Date().toISOString().split('T')[0],
    site: 'Duliajan Central Complex',
    department: 'Operations',
    location_detail: '',
    activity: 'Maintenance',
    reporter_name: user?.name || 'Debojit Phukan',
    description: '',
    immediate_actions_taken: '',
    priority: 'MEDIUM',
  });

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
        sortBy,
        sortOrder,
      });
      setReports(res.data);
      setTotal(res.total);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [selectedType, selectedSite, selectedSifStatus, selectedPriority, selectedRule, selectedActivity, sortBy, sortOrder]);

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
              <option value="Duliajan Central Complex">Duliajan Central</option>
              <option value="Moran Oil & Gas Field">Moran Field</option>
              <option value="Naharkatiya Production Station">Naharkatiya</option>
              <option value="Digboi Refinery Asset">Digboi Asset</option>
              <option value="Jorhat Drilling Block">Jorhat Block</option>
              <option value="Kumchai Exploration Field">Kumchai Field</option>
              <option value="Numaligarh Pipeline Corridor">Numaligarh</option>
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
              <option value="Energy Isolation">Energy Isolation</option>
              <option value="Hot Work">Hot Work</option>
              <option value="Safe Mechanical Lifting">Safe Mechanical Lifting</option>
              <option value="Confined Space">Confined Space</option>
              <option value="Working at Height">Working at Height</option>
              <option value="Line of Fire">Line of Fire</option>
              <option value="Bypassing Safety Controls">Bypassing Safety Controls</option>
              <option value="Driving">Driving</option>
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
              <option value="Hot Work">Hot Work</option>
              <option value="Rig Floor Operations">Rig Floor Operations</option>
              <option value="Confined Space Tank Cleaning">Tank Cleaning</option>
              <option value="Working at Height">Working at Height</option>
              <option value="Pipeline Pressure Testing">Pipeline Testing</option>
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
                  <th>Priority</th>
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
                <option value="Duliajan Central Complex">Duliajan Central Complex</option>
                <option value="Moran Oil & Gas Field">Moran Oil & Gas Field</option>
                <option value="Naharkatiya Production Station">Naharkatiya Production Station</option>
                <option value="Digboi Refinery Asset">Digboi Refinery Asset</option>
                <option value="Jorhat Drilling Block">Jorhat Drilling Block</option>
                <option value="Kumchai Exploration Field">Kumchai Exploration Field</option>
                <option value="Numaligarh Pipeline Corridor">Numaligarh Pipeline Corridor</option>
              </select>
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Primary Activity</label>
              <select
                value={newReport.activity}
                onChange={(e) => setNewReport({ ...newReport, activity: e.target.value })}
                className="w-full rounded border border-slate-300 p-2 text-xs text-slate-900"
              >
                <option value="Maintenance">Maintenance & Overhaul</option>
                <option value="Hot Work">Hot Work & Welding</option>
                <option value="Rig Floor Operations">Rig Floor Operations</option>
                <option value="Confined Space Tank Cleaning">Confined Space Tank Cleaning</option>
                <option value="Working at Height">Working at Height</option>
                <option value="Pipeline Pressure Testing">Pipeline Pressure Testing</option>
                <option value="Driving & Transport">Driving & Transport</option>
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
    </div>
  );
};
