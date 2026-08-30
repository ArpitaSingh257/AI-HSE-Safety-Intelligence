import React, { useEffect, useState } from 'react';
import { auditService } from '../api';
import type { AuditLogEntry } from '../types/audit';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { formatDateTime } from '../utils/formatters';
import { CheckCircle2, AlertTriangle, XCircle, Search, RefreshCw } from 'lucide-react';

export const AuditLogPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filterQuery, setFilterQuery] = useState('');

  const fetchLogs = async (isManual: boolean = false) => {
    if (isManual) setRefreshing(true);
    try {
      const data = await auditService.getAuditLogs();
      setLogs(data);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Loading System Audit Traceability Log..." />;
  }

  const filteredLogs = logs.filter(
    (l) =>
      l.userName.toLowerCase().includes(filterQuery.toLowerCase()) ||
      l.action.toLowerCase().includes(filterQuery.toLowerCase()) ||
      l.details.toLowerCase().includes(filterQuery.toLowerCase()) ||
      (l.entityId && l.entityId.toLowerCase().includes(filterQuery.toLowerCase()))
  );

  const getActionBadge = (action: string) => {
    if (action.includes('LOGIN') || action.includes('LOGOUT')) {
      return <span className="rounded bg-slate-100 text-slate-800 px-2 py-0.5 text-[11px] font-mono font-semibold">{action}</span>;
    }
    if (action.includes('AI_')) {
      return <span className="rounded bg-indigo-50 text-indigo-800 px-2 py-0.5 text-[11px] font-mono font-semibold">{action}</span>;
    }
    if (action.includes('REPORT_')) {
      return <span className="rounded bg-slate-200 text-slate-900 px-2 py-0.5 text-[11px] font-mono font-semibold">{action}</span>;
    }
    return <span className="rounded bg-amber-50 text-amber-800 px-2 py-0.5 text-[11px] font-mono font-semibold">{action}</span>;
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="System Audit & Traceability Log"
        subtitle="Live immutable chronological audit trail recording report submissions, AI NLP classification runs, user sessions, and intervention state changes."
        showDemoBadge={true}
        actions={
          <button
            onClick={() => fetchLogs(true)}
            disabled={refreshing}
            className="flex items-center gap-1.5 rounded bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800 disabled:opacity-50 transition-colors shadow-xs"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>{refreshing ? 'Syncing...' : 'Refresh Live Log'}</span>
          </button>
        }
      />

      {/* Search and Filters */}
      <div className="hse-card p-4">
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            placeholder="Search audit trail by user, action type, entity ID, or activity description..."
            className="w-full rounded border border-slate-300 bg-white py-2 pl-9 pr-3 text-xs text-slate-900 placeholder-slate-400 focus:border-slate-500 focus:outline-hidden"
          />
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="hse-card overflow-hidden">
        <div className="px-5 py-3 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-700">
              Total Recorded Actions: <strong className="text-slate-900">{filteredLogs.length}</strong>
            </span>
            <span className="inline-flex items-center gap-1 text-[10px] text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" /> Live Stream
            </span>
          </div>
          <span className="text-xs text-slate-500">Traceability Standard: ISO 27001 / Oil Industry Safety Directorate</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs hse-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>User / Authority</th>
                <th>Role</th>
                <th>Action Type</th>
                <th>Entity Target</th>
                <th>IP Address</th>
                <th>Status</th>
                <th>Activity Narrative & Trace Evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50">
                  <td className="font-mono text-slate-600 whitespace-nowrap">{formatDateTime(log.timestamp)}</td>
                  <td className="font-semibold text-slate-900">{log.userName}</td>
                  <td className="text-slate-600">{log.userRole}</td>
                  <td>{getActionBadge(log.action)}</td>
                  <td className="font-mono text-slate-700">{log.entityId || '--'}</td>
                  <td className="font-mono text-slate-500">{log.ipAddress}</td>
                  <td>
                    {log.status === 'SUCCESS' ? (
                      <span className="inline-flex items-center gap-1 text-emerald-700 font-semibold text-[11px]">
                        <CheckCircle2 className="h-3.5 w-3.5" /> Success
                      </span>
                    ) : log.status === 'WARNING' ? (
                      <span className="inline-flex items-center gap-1 text-amber-700 font-semibold text-[11px]">
                        <AlertTriangle className="h-3.5 w-3.5" /> Warning
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-red-700 font-semibold text-[11px]">
                        <XCircle className="h-3.5 w-3.5" /> Failed
                      </span>
                    )}
                  </td>
                  <td className="text-slate-700 max-w-sm">
                    <div>{log.details}</div>
                    {log.changesSummary && (
                      <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                        {log.changesSummary.before && <div>{log.changesSummary.before}</div>}
                        {log.changesSummary.after && <div className="text-emerald-700">{log.changesSummary.after}</div>}
                      </div>
                    )}
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
