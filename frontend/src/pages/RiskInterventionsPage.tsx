import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { interventionsService } from '../api';
import type { HSEIntervention, InterventionStatus } from '../types/interventions';
import { useAuth } from '../context/AuthContext';
import { PageHeader } from '../components/common/PageHeader';
import { SeverityBadge } from '../components/common/SeverityBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { Modal } from '../components/common/Modal';
import { formatDate } from '../utils/formatters';
import { Plus } from 'lucide-react';

export const RiskInterventionsPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { hasPermission, user } = useAuth();
  const [interventions, setInterventions] = useState<HSEIntervention[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIntervention, setSelectedIntervention] = useState<HSEIntervention | null>(null);

  // Filter by status
  const [statusFilter, setStatusFilter] = useState<InterventionStatus | 'ALL'>('ALL');

  // Create Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newIntervention, setNewIntervention] = useState({
    title: '',
    category: 'Engineering Control' as HSEIntervention['category'],
    description: '',
    triggerSource: 'Pattern Detection' as HSEIntervention['triggerSource'],
    targetSite: 'Duliajan Central Complex',
    targetActivity: 'Maintenance & Overhaul',
    associatedRule: 'Energy Isolation',
    priority: 'CRITICAL' as HSEIntervention['priority'],
    status: 'OPEN' as InterventionStatus,
    assignedOfficer: user?.name || 'Debojit Phukan',
    assignedOfficerRole: 'Lead HSE Engineer',
    dueDate: '2026-03-31',
    relatedReportIds: ['OIL-2026-R001'],
    actionsTaken: ['Initial risk assessment completed'],
  });

  const fetchInterventions = async () => {
    setLoading(true);
    try {
      const data = await interventionsService.getInterventions();
      setInterventions(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInterventions();
  }, []);

  // Handle Deploy RAG Recommendation Auto-Fill
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('deploy') === 'true') {
      const site = params.get('site') || 'Moran';
      const activity = params.get('activity') || 'Maintenance';
      const title = params.get('title') || 'Deploy AI RAG Safety Controls';
      const desc = params.get('desc') || 'Pre-populated from AI RAG Recommendation Engine.';

      setNewIntervention({
        title,
        category: 'Engineering Control',
        description: desc,
        triggerSource: 'Pattern Detection',
        targetSite: site,
        targetActivity: activity,
        associatedRule: 'Safety Controls & Energy Isolation',
        priority: 'CRITICAL',
        status: 'OPEN',
        assignedOfficer: user?.name || 'Lead HSE Engineer',
        assignedOfficerRole: 'Lead HSE Engineer',
        dueDate: '2026-03-31',
        relatedReportIds: ['REP-427F7'],
        actionsTaken: ['RAG Corrective Action Engine recommendation deployed to register'],
      });
      setIsModalOpen(true);
    }
  }, [location.search]);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await interventionsService.createIntervention(newIntervention);
    setIsModalOpen(false);
    fetchInterventions();
  };

  const handleStatusUpdate = async (id: string, newStatus: InterventionStatus) => {
    await interventionsService.updateIntervention(id, { status: newStatus });
    fetchInterventions();
    if (selectedIntervention) {
      setSelectedIntervention({ ...selectedIntervention, status: newStatus });
    }
  };

  const priorityRank: Record<string, number> = {
    CRITICAL: 4,
    HIGH: 3,
    MEDIUM: 2,
    LOW: 1,
  };

  const rawFiltered = statusFilter === 'ALL'
    ? interventions
    : interventions.filter((i) => i.status === statusFilter);

  const filtered = [...rawFiltered].sort((a, b) => {
    const rankA = priorityRank[a.priority] || 0;
    const rankB = priorityRank[b.priority] || 0;
    if (rankB !== rankA) return rankB - rankA;
    return new Date(b.createdDate || 0).getTime() - new Date(a.createdDate || 0).getTime();
  });

  if (loading) {
    return <LoadingSpinner label="Loading HSE Intervention Priority Action Register..." />;
  }

  const getStatusBadge = (status: InterventionStatus) => {
    switch (status) {
      case 'OPEN':
        return <span className="rounded bg-red-100 text-red-800 px-2 py-0.5 text-xs font-semibold border border-red-200">OPEN</span>;
      case 'IN_PROGRESS':
        return <span className="rounded bg-amber-100 text-amber-800 px-2 py-0.5 text-xs font-semibold border border-amber-200">IN PROGRESS</span>;
      case 'UNDER_VERIFICATION':
        return <span className="rounded bg-blue-100 text-blue-800 px-2 py-0.5 text-xs font-semibold border border-blue-200">UNDER VERIFICATION</span>;
      case 'CLOSED':
        return <span className="rounded bg-emerald-100 text-emerald-800 px-2 py-0.5 text-xs font-semibold border border-emerald-200">CLOSED / VERIFIED</span>;
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="High-Priority Risk & Intervention Register"
        subtitle="Operational corrective actions and systemic engineering barriers deployed to eliminate high SIF precursor clusters."
        showDemoBadge={true}
        actions={
          hasPermission('canManageInterventions') && (
            <button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-1.5 rounded bg-slate-900 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-800 transition-colors shadow-xs"
            >
              <Plus className="h-4 w-4" />
              <span>Create HSE Intervention</span>
            </button>
          )
        }
      />

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 text-xs font-medium text-slate-600">
        {(['ALL', 'OPEN', 'IN_PROGRESS', 'UNDER_VERIFICATION', 'CLOSED'] as const).map((st) => (
          <button
            key={st}
            onClick={() => setStatusFilter(st)}
            className={`rounded px-3 py-1.5 transition-colors ${
              statusFilter === st
                ? 'bg-slate-900 text-white font-semibold'
                : 'hover:bg-slate-200 text-slate-700'
            }`}
          >
            {st.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Interventions List */}
      <div className="space-y-4">
        {filtered.map((item) => (
          <div
            key={item.id}
            onClick={() => setSelectedIntervention(item)}
            className="hse-card p-5 hover:border-slate-400 transition-colors cursor-pointer"
          >
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 mb-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-xs font-bold text-slate-500">{item.id}</span>
                  {getStatusBadge(item.status)}
                  <SeverityBadge priority={item.priority} size="sm" />
                </div>
                <h3 className="text-base font-bold text-slate-900">{item.title}</h3>
              </div>

              <div className="text-right text-xs text-slate-500 whitespace-nowrap">
                <div>Due Date: <strong className="text-slate-800">{formatDate(item.dueDate)}</strong></div>
                <div className="text-[11px]">Assigned to: {item.assignedOfficer}</div>
              </div>
            </div>

            <p className="text-xs text-slate-600 mb-4">{item.description}</p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs border-t border-slate-100 pt-3 text-slate-600">
              <div>
                <span className="text-slate-400 text-[10px] uppercase block">Control Hierarchy:</span>
                <span className="font-semibold text-slate-800">{item.category}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[10px] uppercase block">Target Site:</span>
                <span className="font-semibold text-slate-800">{item.targetSite}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[10px] uppercase block">Associated Rule:</span>
                <span className="font-semibold text-slate-800">{item.associatedRule}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[10px] uppercase block">Trigger Origin:</span>
                <span className="font-semibold text-slate-800">{item.triggerSource}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Intervention Detail Modal */}
      {selectedIntervention && (
        <Modal
          isOpen={!!selectedIntervention}
          onClose={() => setSelectedIntervention(null)}
          title={`Intervention ${selectedIntervention.id}: ${selectedIntervention.title}`}
          subtitle={`Target: ${selectedIntervention.targetSite} (${selectedIntervention.category})`}
          maxWidth="2xl"
          footer={
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center gap-2">
                {hasPermission('canManageInterventions') && (
                  <>
                    <span className="text-xs text-slate-500">Update Status:</span>
                    <select
                      value={selectedIntervention.status}
                      onChange={(e) =>
                        handleStatusUpdate(
                          selectedIntervention.id,
                          e.target.value as InterventionStatus
                        )
                      }
                      className="rounded border border-slate-300 bg-white p-1 text-xs text-slate-800"
                    >
                      <option value="OPEN">OPEN</option>
                      <option value="IN_PROGRESS">IN PROGRESS</option>
                      <option value="UNDER_VERIFICATION">UNDER VERIFICATION</option>
                      <option value="CLOSED">CLOSED / VERIFIED</option>
                    </select>
                  </>
                )}
              </div>
              <button
                onClick={() => setSelectedIntervention(null)}
                className="rounded bg-slate-900 px-4 py-1.5 text-xs font-semibold text-white"
              >
                Close
              </button>
            </div>
          }
        >
          <div className="space-y-4 text-xs text-slate-800">
            <div>
              <span className="font-semibold text-slate-700 block mb-1">Intervention Mandate</span>
              <p className="p-3 rounded bg-slate-50 border border-slate-200 text-slate-700 leading-relaxed">
                {selectedIntervention.description}
              </p>
            </div>

            {selectedIntervention.actionsTaken && (
              <div>
                <span className="font-semibold text-slate-700 block mb-1.5">Action Milestones Executed</span>
                <ul className="list-disc list-inside space-y-1 text-slate-600 bg-white p-3 rounded border border-slate-200">
                  {selectedIntervention.actionsTaken.map((act, idx) => (
                    <li key={idx}>{act}</li>
                  ))}
                </ul>
              </div>
            )}

            {selectedIntervention.verificationNotes && (
              <div>
                <span className="font-semibold text-slate-700 block mb-1">Field Verification Evidence</span>
                <p className="p-3 rounded bg-emerald-50/70 border border-emerald-200 text-emerald-900">
                  {selectedIntervention.verificationNotes}
                </p>
              </div>
            )}

            {selectedIntervention.relatedReportIds.length > 0 && (
              <div className="border-t border-slate-200 pt-3">
                <span className="font-semibold text-slate-700 block mb-2">Precursor Reports Triggering this Action:</span>
                <div className="flex gap-2">
                  {selectedIntervention.relatedReportIds.map((rId) => (
                    <button
                      key={rId}
                      onClick={() => {
                        setSelectedIntervention(null);
                        navigate(`/reports/${rId}`);
                      }}
                      className="font-mono text-xs text-slate-800 bg-slate-100 hover:bg-slate-200 px-2.5 py-1 rounded border border-slate-300 font-semibold"
                    >
                      {rId} →
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}

      {/* Create Intervention Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Schedule New HSE Intervention"
        subtitle="Mandate systemic engineering or administrative barriers against recurring SIF precursor trends"
        maxWidth="xl"
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
              form="create-intervention-form"
              className="rounded bg-slate-900 px-4 py-1.5 text-xs font-semibold text-white hover:bg-slate-800"
            >
              Authorize Intervention
            </button>
          </>
        }
      >
        <form id="create-intervention-form" onSubmit={handleCreateSubmit} className="space-y-3 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Intervention Title</label>
            <input
              type="text"
              required
              value={newIntervention.title}
              onChange={(e) => setNewIntervention({ ...newIntervention, title: e.target.value })}
              placeholder="e.g. Automated Continuous Multi-Gas Monitor Installation"
              className="w-full rounded border border-slate-300 p-2 text-xs"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Control Category</label>
              <select
                value={newIntervention.category}
                onChange={(e) => setNewIntervention({ ...newIntervention, category: e.target.value as HSEIntervention['category'] })}
                className="w-full rounded border border-slate-300 p-2 text-xs"
              >
                <option value="Engineering Control">Engineering Control</option>
                <option value="Process Safety Barrier">Process Safety Barrier</option>
                <option value="Administrative Control">Administrative Control</option>
                <option value="Training & Competency">Training & Competency</option>
                <option value="PPE & Equipment">PPE & Equipment</option>
              </select>
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Target Site</label>
              <select
                value={newIntervention.targetSite}
                onChange={(e) => setNewIntervention({ ...newIntervention, targetSite: e.target.value })}
                className="w-full rounded border border-slate-300 p-2 text-xs"
              >
                <option value="Duliajan Central Complex">Duliajan Central Complex</option>
                <option value="Moran Oil & Gas Field">Moran Oil & Gas Field</option>
                <option value="Naharkatiya Production Station">Naharkatiya Production Station</option>
                <option value="Digboi Refinery Asset">Digboi Refinery Asset</option>
                <option value="Jorhat Drilling Block">Jorhat Drilling Block</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Mandate Description & Barrier Specification</label>
            <textarea
              required
              rows={3}
              value={newIntervention.description}
              onChange={(e) => setNewIntervention({ ...newIntervention, description: e.target.value })}
              placeholder="Specify the engineering modifications, inspection protocols, or procedural barriers to be enacted..."
              className="w-full rounded border border-slate-300 p-2 text-xs"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Assigned Safety Lead</label>
              <input
                type="text"
                required
                value={newIntervention.assignedOfficer}
                onChange={(e) => setNewIntervention({ ...newIntervention, assignedOfficer: e.target.value })}
                className="w-full rounded border border-slate-300 p-2 text-xs"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Due Date</label>
              <input
                type="date"
                required
                value={newIntervention.dueDate}
                onChange={(e) => setNewIntervention({ ...newIntervention, dueDate: e.target.value })}
                className="w-full rounded border border-slate-300 p-2 text-xs"
              />
            </div>
          </div>
        </form>
      </Modal>
    </div>
  );
};
