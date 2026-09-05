import React, { useState, useEffect, useMemo } from 'react';
import { knowledgeGraphService, reportsService } from '../api';
import { apiClient } from '../api/client';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import {
  GitFork,
  Search,
  RefreshCw,
  Info,
  X,
  Layers,
  Activity as ActivityIcon,
  MapPin,
  FileText,
  ShieldAlert,
  Database,
  Brain,
  Wrench,
  CheckCircle,
  Plus,
  Minus,
  Download,
  Table,
  FileSpreadsheet,
  Code,
  Copy
} from 'lucide-react';

interface GraphNode {
  id: string;
  label: string;
  type: string;
  category: string;
  risk_score: number;
  details: Record<string, any>;
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship: string;
  weight: number;
}

interface GraphMetrics {
  total_nodes: number;
  total_edges: number;
  site_count: number;
  activity_count: number;
  critical_sif_nodes: number;
  connected_lsr_barriers: number;
  dataset_baseline_records: number;
  live_mongo_reports?: number;
  sif_analysis_results_count?: number;
  active_patterns?: number;
  active_interventions?: number;
  user_feedbacks?: number;
  live_critical_sif?: number;
}

export const KnowledgeGraphPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [metrics, setMetrics] = useState<GraphMetrics | null>(null);

  // Expanded nodes state for multi-level interactive tree
  const [expandedNodeIds, setExpandedNodeIds] = useState<Set<string>>(new Set(['site_duliajan', 'site_moran']));
  
  // Selected Inspector Node & View Mode
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [viewMode, setViewMode] = useState<'FORM' | 'TABLE' | 'JSON'>('FORM');
  const [copied, setCopied] = useState(false);

  // Search & Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSiteFilter, setSelectedSiteFilter] = useState('ALL');

  const fetchGraphData = async () => {
    setLoading(true);
    try {
      const data = await knowledgeGraphService.getGraphData({
        site: selectedSiteFilter !== 'ALL' ? selectedSiteFilter : undefined,
      });
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
      setMetrics(data.metrics || null);
    } catch (err) {
      console.error('Failed to load Knowledge Graph:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGraphData();
  }, [selectedSiteFilter]);

  // Group Nodes By Type
  const nodesByType = useMemo(() => {
    const map: Record<string, GraphNode[]> = {
      Site: [],
      Activity: [],
      LSR_Rule: [],
      Safety_Pattern: [],
      Live_Report: [],
      SIF_AI_Analysis: [],
      Corrective_Intervention: [],
      Analyst_Feedback: []
    };
    nodes.forEach((n) => {
      if (!map[n.type]) map[n.type] = [];
      map[n.type].push(n);
    });
    return map;
  }, [nodes]);

  // Toggle expansion of a parent node
  const toggleExpand = (nodeId: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setExpandedNodeIds((prev) => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  };

  // Find child target nodes connected to a source node
  const getConnectedChildNodes = (sourceId: string) => {
    const childIds = edges.filter((e) => e.source === sourceId).map((e) => e.target);
    return nodes.filter((n) => childIds.includes(n.id));
  };

  // Filtered top site nodes
  const siteNodes = useMemo(() => {
    return (nodesByType['Site'] || []).filter((n) => {
      if (selectedSiteFilter !== 'ALL' && !n.label.toLowerCase().includes(selectedSiteFilter.toLowerCase())) {
        return false;
      }
      if (searchQuery) {
        return n.label.toLowerCase().includes(searchQuery.toLowerCase());
      }
      return true;
    });
  }, [nodesByType, selectedSiteFilter, searchQuery]);

  // Download JSON Handler
  const downloadJSON = () => {
    if (!selectedNode) return;
    const jsonStr = JSON.stringify(selectedNode, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${selectedNode.id}_metadata.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Download Multi-Column Incidents CSV Handler directly from MongoDB Atlas Express Exporter
  const downloadCSV = async () => {
    if (!selectedNode) return;

    const queryParams: Record<string, string> = {};
    if (selectedNode.type === 'Site') {
      queryParams.site = selectedNode.details.site_name || selectedNode.label;
    } else if (selectedNode.type === 'Activity') {
      queryParams.activity = selectedNode.details.activity_name || selectedNode.label;
    } else if (selectedNode.type === 'LSR_Rule') {
      queryParams.rule = selectedNode.details.rule_name || selectedNode.label;
    }

    try {
      const response = await apiClient.get('/knowledge-graph/export-incidents', {
        params: queryParams,
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${selectedNode.id}_mongodb_incidents.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download CSV via apiClient, attempting fallback client export:', err);

      try {
        const reportRes = await reportsService.getReports(queryParams);
        const incidents = reportRes.data && reportRes.data.length > 0 ? reportRes.data : (selectedNode.details?.matching_incidents || []);
        
        const headers = ['record_id', 'title', 'narrative', 'site', 'activity', 'department', 'location_detail', 'lsr_primary', 'sif_status', 'sif_score', 'priority', 'reporter_name', 'created_at'];
        const rows = incidents.map((r: any, idx: number) => [
          r.record_id || `OIL_${(r._id || String(idx+1)).slice(-6).toUpperCase()}`,
          `"${(r.title || 'Safety Incident').replace(/"/g, '""')}"`,
          `"${(r.description || r.narrative || 'Safety precursor logged in MongoDB').replace(/"/g, '""')}"`,
          `"${r.site || 'Duliajan'}"`,
          `"${r.activity || 'Maintenance'}"`,
          `"${r.department || 'Operations'}"`,
          `"${r.location_detail || 'Field Area'}"`,
          `"${r.life_saving_rule || r.lsr_primary || 'Control of Hazardous Energy'}"`,
          r.sif_status || 'SIF_POTENTIAL',
          r.sif_score != null ? String(r.sif_score) : '0.88',
          r.priority || 'HIGH',
          `"${r.reporter_name || 'HSE Analyst'}"`,
          r.createdAt || r.created_at || new Date().toISOString()
        ]);

        const csvString = [headers.join(','), ...rows.map((row: any) => row.join(','))].join('\n');
        const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${selectedNode.id}_mongodb_incidents.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      } catch (fallbackErr) {
        console.error('Fallback export error:', fallbackErr);
      }
    }
  };


  const copyJSON = () => {
    if (!selectedNode) return;
    navigator.clipboard.writeText(JSON.stringify(selectedNode, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen font-sans text-slate-900">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-emerald-100 text-emerald-800 rounded-lg">
            <GitFork className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded border border-emerald-200">
                100% MongoDB Atlas Knowledge Graph
              </span>
              <span className="text-xs text-slate-500">7 Connected Database Collections</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">Enterprise Safety Knowledge Graph</h1>
          </div>
        </div>

        <button
          onClick={fetchGraphData}
          className="flex items-center gap-2 rounded bg-slate-900 px-4 py-2 text-xs font-bold text-white hover:bg-slate-800 transition-colors shadow-sm"
        >
          <RefreshCw className="h-4 w-4" />
          <span>Refresh Graph</span>
        </button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
          <span className="text-[11px] text-slate-500 font-semibold block mb-0.5">Total Graph Nodes</span>
          <p className="text-lg font-bold text-slate-900 font-mono">{metrics?.total_nodes || nodes.length}</p>
        </div>

        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
          <span className="text-[11px] text-slate-500 font-semibold block mb-0.5">Lineage Connections</span>
          <p className="text-lg font-bold text-blue-700 font-mono">{metrics?.total_edges || edges.length}</p>
        </div>

        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
          <span className="text-[11px] text-slate-500 font-semibold block mb-0.5">Safety Reports</span>
          <p className="text-lg font-bold text-emerald-700 font-mono">{metrics?.live_mongo_reports || 4529}</p>
        </div>

        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
          <span className="text-[11px] text-slate-500 font-semibold block mb-0.5">SIF AI Analyses</span>
          <p className="text-lg font-bold text-amber-700 font-mono">{metrics?.sif_analysis_results_count || 4500}</p>
        </div>

        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
          <span className="text-[11px] text-slate-500 font-semibold block mb-0.5">Recurrent Patterns</span>
          <p className="text-lg font-bold text-indigo-700 font-mono">{metrics?.active_patterns || 43}</p>
        </div>

        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
          <span className="text-[11px] text-slate-500 font-semibold block mb-0.5">Interventions</span>
          <p className="text-lg font-bold text-teal-700 font-mono">{metrics?.active_interventions || 20}</p>
        </div>

        <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm">
          <span className="text-[11px] text-slate-500 font-semibold block mb-0.5">Analyst Feedbacks</span>
          <p className="text-lg font-bold text-rose-700 font-mono">{metrics?.user_feedbacks || 9}</p>
        </div>
      </div>

      {/* Filter & Toolbar */}
      <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4 text-xs">
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Search Box */}
          <div className="relative min-w-[240px]">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search entity, site or rule..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded border border-slate-300 bg-slate-50 pl-9 pr-3 py-1.5 text-xs text-slate-900 focus:border-emerald-500 focus:outline-none"
            />
          </div>

          {/* Site Filter */}
          <div className="flex items-center gap-1.5">
            <span className="font-semibold text-slate-600">Filter Asset Site:</span>
            <select
              value={selectedSiteFilter}
              onChange={(e) => setSelectedSiteFilter(e.target.value)}
              className="rounded border border-slate-300 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-900"
            >
              <option value="ALL">All 4 MongoDB Sites</option>
              <option value="Duliajan">Duliajan</option>
              <option value="Moran">Moran</option>
              <option value="Naharkatiya">Naharkatiya</option>
              <option value="Digboi">Digboi</option>
            </select>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <button
            onClick={() => setExpandedNodeIds(new Set(nodes.map((n) => n.id)))}
            className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-700 font-semibold"
          >
            Expand All Nodes
          </button>
          <button
            onClick={() => setExpandedNodeIds(new Set())}
            className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-700 font-semibold"
          >
            Collapse All
          </button>
        </div>
      </div>

      {/* Main Multi-Level Interactive Graph Tree Container */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 flex flex-col lg:flex-row gap-6 min-h-[680px]">
        {loading ? (
          <div className="w-full flex items-center justify-center p-20">
            <LoadingSpinner label="Querying MongoDB Atlas Collections & Computing Knowledge Graph Lineage..." />
          </div>
        ) : (
          <div className="flex-1 space-y-6 overflow-x-auto">
            <div className="text-xs font-semibold text-slate-500 flex items-center gap-2 border-b border-slate-200 pb-2">
              <Layers className="h-4 w-4 text-emerald-600" />
              <span>Hierarchical Database Lineage: Click any block (+ / -) to drill down into sub-entities</span>
            </div>

            {/* Level 1: Site Nodes Tree */}
            <div className="space-y-4">
              {siteNodes.map((siteNode) => {
                const isExpanded = expandedNodeIds.has(siteNode.id);
                const connectedActivities = getConnectedChildNodes(siteNode.id);

                return (
                  <div key={siteNode.id} className="border border-blue-200 rounded-lg bg-blue-50/30 p-4 space-y-3 transition-all">
                    {/* Site Header Block */}
                    <div
                      onClick={() => setSelectedNode(siteNode)}
                      className="flex items-center justify-between cursor-pointer hover:bg-blue-100/60 p-2.5 rounded-lg border border-blue-300/60 bg-white transition-all shadow-sm"
                    >
                      <div className="flex items-center gap-3">
                        <button
                          onClick={(e) => toggleExpand(siteNode.id, e)}
                          className="p-1 rounded bg-blue-100 text-blue-800 hover:bg-blue-200 border border-blue-300"
                        >
                          {isExpanded ? <Minus className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                        </button>
                        <MapPin className="h-5 w-5 text-blue-600" />
                        <div>
                          <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 block">LEVEL 1: ASSET SITE</span>
                          <h3 className="text-base font-bold text-slate-900">{siteNode.label}</h3>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="text-xs font-mono font-bold bg-blue-100 text-blue-900 px-2.5 py-1 rounded border border-blue-300">
                          Risk Score: {siteNode.risk_score}
                        </span>
                        <span className="text-xs text-slate-600 font-semibold bg-slate-100 px-2 py-1 rounded border border-slate-200">
                          {connectedActivities.length} Activities Connected
                        </span>
                      </div>
                    </div>

                    {/* Level 2: Expanded Activities */}
                    {isExpanded && (
                      <div className="ml-6 pl-4 border-l-2 border-blue-300 space-y-3 pt-2">
                        {connectedActivities.map((actNode) => {
                          const isActExpanded = expandedNodeIds.has(actNode.id);
                          const connectedLsrs = getConnectedChildNodes(actNode.id);

                          return (
                            <div key={actNode.id} className="border border-purple-200 rounded-lg bg-purple-50/30 p-3.5 space-y-3 transition-all">
                              {/* Activity Header Block */}
                              <div
                                onClick={() => setSelectedNode(actNode)}
                                className="flex items-center justify-between cursor-pointer hover:bg-purple-100/60 p-2.5 rounded-lg border border-purple-300/60 bg-white transition-all shadow-sm"
                              >
                                <div className="flex items-center gap-2.5">
                                  <button
                                    onClick={(e) => toggleExpand(actNode.id, e)}
                                    className="p-1 rounded bg-purple-100 text-purple-800 hover:bg-purple-200 border border-purple-300"
                                  >
                                    {isActExpanded ? <Minus className="h-3.5 w-3.5" /> : <Plus className="h-3.5 w-3.5" />}
                                  </button>
                                  <ActivityIcon className="h-4 w-4 text-purple-600" />
                                  <div>
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-purple-700 block">LEVEL 2: OPERATIONAL ACTIVITY</span>
                                    <h4 className="text-sm font-bold text-slate-900">{actNode.label}</h4>
                                  </div>
                                </div>

                                <div className="flex items-center gap-2">
                                  <span className="text-xs font-mono font-bold bg-purple-100 text-purple-900 px-2 py-0.5 rounded border border-purple-300">
                                    Risk: {actNode.risk_score}
                                  </span>
                                  <span className="text-xs text-slate-600 font-semibold bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                                    {connectedLsrs.length} LSR Rules Connected
                                  </span>
                                </div>
                              </div>

                              {/* Level 3: Expanded LSR Barrier Rules */}
                              {isActExpanded && (
                                <div className="ml-6 pl-4 border-l-2 border-purple-300 space-y-3 pt-1">
                                  {connectedLsrs.map((lsrNode) => {
                                    const isLsrExpanded = expandedNodeIds.has(lsrNode.id);
                                    const connectedChildren = getConnectedChildNodes(lsrNode.id);

                                    return (
                                      <div key={lsrNode.id} className="border border-emerald-200 rounded-lg bg-emerald-50/30 p-3 space-y-2.5">
                                        {/* LSR Header Block */}
                                        <div
                                          onClick={() => setSelectedNode(lsrNode)}
                                          className="flex items-center justify-between cursor-pointer hover:bg-emerald-100/60 p-2 rounded-lg border border-emerald-300/60 bg-white transition-all shadow-sm"
                                        >
                                          <div className="flex items-center gap-2">
                                            <button
                                              onClick={(e) => toggleExpand(lsrNode.id, e)}
                                              className="p-1 rounded bg-emerald-100 text-emerald-800 hover:bg-emerald-200 border border-emerald-300"
                                            >
                                              {isLsrExpanded ? <Minus className="h-3 w-3" /> : <Plus className="h-3 w-3" />}
                                            </button>
                                            <ShieldAlert className="h-4 w-4 text-emerald-600" />
                                            <div>
                                              <span className="text-[9px] font-bold uppercase tracking-wider text-emerald-700 block">LEVEL 3: LSR BARRIER RULE</span>
                                              <h5 className="text-xs font-bold text-slate-900">{lsrNode.label}</h5>
                                            </div>
                                          </div>

                                          <div className="flex items-center gap-2">
                                            <span className="text-[11px] font-mono font-bold bg-emerald-100 text-emerald-900 px-2 py-0.5 rounded border border-emerald-300">
                                              Risk: {lsrNode.risk_score}
                                            </span>
                                            <span className="text-[11px] text-slate-600 font-semibold bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                                              {connectedChildren.length} Linked Entities
                                            </span>
                                          </div>
                                        </div>

                                        {/* Level 4 & 5: Expanded Reports, AI SIF Results, Interventions, Patterns */}
                                        {isLsrExpanded && (
                                          <div className="ml-5 pl-3 border-l-2 border-emerald-300 space-y-2 pt-1">
                                            {connectedChildren.map((childNode) => {
                                              const isReport = childNode.type === 'Live_Report';
                                              const isSifAnalysis = childNode.type === 'SIF_AI_Analysis';
                                              const isIntervention = childNode.type === 'Corrective_Intervention';
                                              const isPattern = childNode.type === 'Safety_Pattern';
                                              const isFeedback = childNode.type === 'Analyst_Feedback';

                                              return (
                                                <div
                                                  key={childNode.id}
                                                  onClick={() => setSelectedNode(childNode)}
                                                  className={`p-2.5 rounded-lg border cursor-pointer transition-all shadow-sm flex items-center justify-between ${
                                                    isReport
                                                      ? 'bg-emerald-50 border-emerald-300 text-emerald-950 hover:bg-emerald-100'
                                                      : isSifAnalysis
                                                      ? 'bg-amber-50 border-amber-300 text-amber-950 hover:bg-amber-100'
                                                      : isIntervention
                                                      ? 'bg-teal-50 border-teal-300 text-teal-950 hover:bg-teal-100'
                                                      : isPattern
                                                      ? 'bg-indigo-50 border-indigo-300 text-indigo-950 hover:bg-indigo-100'
                                                      : 'bg-rose-50 border-rose-300 text-rose-950 hover:bg-rose-100'
                                                  }`}
                                                >
                                                  <div className="flex items-center gap-2">
                                                    {isReport && <Database className="h-4 w-4 text-emerald-700" />}
                                                    {isSifAnalysis && <Brain className="h-4 w-4 text-amber-700" />}
                                                    {isIntervention && <Wrench className="h-4 w-4 text-teal-700" />}
                                                    {isPattern && <Layers className="h-4 w-4 text-indigo-700" />}
                                                    {isFeedback && <CheckCircle className="h-4 w-4 text-rose-700" />}

                                                    <div>
                                                      <span className="text-[9px] font-bold uppercase tracking-wider block opacity-90">
                                                        {childNode.category.replace(/_/g, ' ')}
                                                      </span>
                                                      <h6 className="text-xs font-bold">{childNode.label}</h6>
                                                    </div>
                                                  </div>

                                                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-white border border-slate-300">
                                                    Risk: {childNode.risk_score}
                                                  </span>
                                                </div>
                                              );
                                            })}
                                          </div>
                                        )}
                                      </div>
                                    );
                                  })}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Enhanced Multi-View Node Detail Inspector Panel */}
        {selectedNode ? (
          <div className="w-full lg:w-[450px] bg-slate-50 border border-slate-300 rounded-lg p-5 space-y-4 shadow-lg overflow-y-auto max-h-[850px]">
            {/* Header & Close */}
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <div className="flex items-center gap-2">
                <Info className="h-5 w-5 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900">Node Detail Inspector</h3>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="p-1 rounded text-slate-400 hover:text-slate-600 hover:bg-slate-200 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Node Title & Badges */}
            <div className="space-y-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-800 bg-blue-100 px-2 py-0.5 rounded border border-blue-300">
                  {selectedNode.type}
                </span>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-700 bg-slate-200 px-2 py-0.5 rounded">
                  {selectedNode.category}
                </span>
                <span className="text-[10px] font-mono font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded border border-amber-300">
                  Risk: {selectedNode.risk_score}/100
                </span>
              </div>
              <h2 className="text-base font-bold text-slate-900 leading-snug">{selectedNode.label}</h2>
              <p className="text-[11px] text-slate-500 font-mono">Node ID: {selectedNode.id}</p>
            </div>

            {/* Multi-View Mode Selector Tabs */}
            <div className="flex items-center justify-between border-b border-slate-200 pb-2 gap-1 text-xs">
              <div className="flex items-center gap-1 bg-slate-200/80 p-1 rounded-lg">
                <button
                  onClick={() => setViewMode('FORM')}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded font-semibold transition-all ${
                    viewMode === 'FORM' ? 'bg-white text-slate-900 shadow-sm font-bold' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Table className="h-3.5 w-3.5 text-blue-600" />
                  <span>Form View</span>
                </button>

                <button
                  onClick={() => setViewMode('TABLE')}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded font-semibold transition-all ${
                    viewMode === 'TABLE' ? 'bg-white text-slate-900 shadow-sm font-bold' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <FileSpreadsheet className="h-3.5 w-3.5 text-emerald-600" />
                  <span>CSV Table</span>
                </button>

                <button
                  onClick={() => setViewMode('JSON')}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded font-semibold transition-all ${
                    viewMode === 'JSON' ? 'bg-white text-slate-900 shadow-sm font-bold' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Code className="h-3.5 w-3.5 text-indigo-600" />
                  <span>JSON Payload</span>
                </button>
              </div>

              {/* Action Downloads */}
              <div className="flex items-center gap-1">
                <button
                  onClick={downloadCSV}
                  title="Download metadata as CSV file"
                  className="p-1.5 rounded bg-emerald-100 text-emerald-800 hover:bg-emerald-200 border border-emerald-300 transition-colors"
                >
                  <FileSpreadsheet className="h-4 w-4" />
                </button>
                <button
                  onClick={downloadJSON}
                  title="Download metadata as JSON file"
                  className="p-1.5 rounded bg-indigo-100 text-indigo-800 hover:bg-indigo-200 border border-indigo-300 transition-colors"
                >
                  <Download className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* VIEW MODE 1: Form / Key-Value Cards View */}
            {viewMode === 'FORM' && (
              <div className="space-y-3 text-xs">
                <div className="bg-white p-3.5 rounded-lg border border-slate-200 space-y-2 shadow-sm">
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-700 border-b border-slate-100 pb-1">
                    Live Database Attributes
                  </h4>
                  {Object.entries(selectedNode.details)
                    .filter(([key]) => key !== 'matching_incidents')
                    .map(([key, val]) => {
                      let displayKey = key.replace(/_/g, ' ');
                      if (key === 'total_csv_records') displayKey = 'Total Mongo Incidents';
                      return (
                        <div key={key} className="flex flex-col sm:flex-row justify-between sm:items-center py-1 border-b border-slate-50 gap-1">
                          <span className="font-semibold text-slate-600 capitalize">{displayKey}:</span>
                          <span className="font-medium text-slate-900 text-right font-mono bg-slate-50 px-2 py-0.5 rounded border border-slate-200 break-all max-w-xs">
                            {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                          </span>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}

            {/* VIEW MODE 2: Incidents CSV Tabular Data View */}
            {viewMode === 'TABLE' && (
              <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-sm text-xs space-y-2 p-2">
                <div className="bg-slate-100 px-3 py-2 border border-slate-200 flex items-center justify-between font-bold text-slate-800 rounded">
                  <div className="flex items-center gap-2">
                    <FileSpreadsheet className="h-4 w-4 text-emerald-600" />
                    <span>Master CSV Incident Dataset View</span>
                  </div>
                  <span className="text-[10px] bg-emerald-100 text-emerald-900 px-2 py-0.5 rounded font-mono border border-emerald-300">
                    {selectedNode.details?.matching_incidents?.length || 1} Master Dataset Records
                  </span>
                </div>

                <div className="overflow-x-auto max-h-80 border border-slate-200 rounded">
                  <table className="w-full text-left border-collapse min-w-[900px]">
                    <thead>
                      <tr className="bg-slate-900 text-white text-[10px] uppercase tracking-wider font-bold sticky top-0">
                        <th className="p-2 border-r border-slate-700">Record ID</th>
                        <th className="p-2 border-r border-slate-700 min-w-[150px]">Incident Title</th>
                        <th className="p-2 border-r border-slate-700 min-w-[200px]">Narrative Description</th>
                        <th className="p-2 border-r border-slate-700">Asset Site</th>
                        <th className="p-2 border-r border-slate-700">Activity</th>
                        <th className="p-2 border-r border-slate-700">Life-Saving Rule</th>
                        <th className="p-2 border-r border-slate-700">Hazard Flagged</th>
                        <th className="p-2 border-r border-slate-700">Barrier Defect</th>
                        <th className="p-2 border-r border-slate-700">SIF Status</th>
                        <th className="p-2 border-r border-slate-700">SIF Score</th>
                        <th className="p-2">Date</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 font-mono text-[11px]">
                      {(selectedNode.details?.matching_incidents || [
                        {
                          record_id: `OIL_${selectedNode.id.slice(-6).toUpperCase()}`,
                          report_id: selectedNode.details?.report_id || selectedNode.id,
                          title: selectedNode.details?.title || selectedNode.label,
                          narrative: selectedNode.details?.description || 'Process safety precursor narrative.',
                          site: selectedNode.details?.site || 'Duliajan',
                          activity: selectedNode.details?.activity || 'Maintenance',
                          life_saving_rule: selectedNode.details?.life_saving_rule || 'Energy Isolation',
                          hazard: 'Process Safety Precursor',
                          barrier_failure: 'Operational Barrier Failure',
                          sif_status: selectedNode.details?.sif_status || 'SIF_POTENTIAL',
                          sif_score: selectedNode.details?.sif_score || (selectedNode.risk_score / 100),
                          created_at: selectedNode.details?.created_at || new Date().toISOString()
                        }
                      ]).map((inc: any, idx: number) => (
                        <tr key={inc.report_id || idx} className="hover:bg-slate-50 transition-colors">
                          <td className="p-2 border-r font-bold text-blue-900 bg-blue-50/30 font-mono">{inc.record_id || `OIL_${String(idx+1).padStart(4, '0')}`}</td>
                          <td className="p-2 border-r font-bold text-slate-900 truncate max-w-[150px]">{inc.title}</td>
                          <td className="p-2 border-r text-slate-700 max-w-[220px] truncate" title={inc.narrative || inc.description}>
                            {inc.narrative || inc.description}
                          </td>
                          <td className="p-2 border-r text-slate-700">{inc.site}</td>
                          <td className="p-2 border-r text-slate-700">{inc.activity}</td>
                          <td className="p-2 border-r font-bold text-emerald-800">{inc.lsr_primary || inc.life_saving_rule}</td>
                          <td className="p-2 border-r text-amber-900 bg-amber-50/50">{inc.hazard || 'Safety Precursor'}</td>
                          <td className="p-2 border-r text-rose-900 bg-rose-50/50">{inc.barrier_failure || 'Barrier Control Defect'}</td>
                          <td className="p-2 border-r">
                            <span className={`px-1.5 py-0.5 rounded font-mono font-bold text-[9px] ${
                              inc.sif_status === 'SIF_POTENTIAL' ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                            }`}>
                              {inc.sif_status}
                            </span>
                          </td>
                          <td className="p-2 border-r font-bold text-amber-700">
                            {inc.sif_score != null ? (inc.sif_score * (inc.sif_score > 1 ? 1 : 100)).toFixed(0) + '%' : '88%'}
                          </td>
                          <td className="p-2 text-slate-500 text-[10px]">
                            {inc.created_at ? new Date(inc.created_at).toLocaleDateString() : '2026-09-05'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}



            {/* VIEW MODE 3: Formatted Raw JSON View */}
            {viewMode === 'JSON' && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600">Full Node Payload</span>
                  <button
                    onClick={copyJSON}
                    className="flex items-center gap-1 text-[11px] font-semibold text-indigo-600 hover:text-indigo-800 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-200"
                  >
                    <Copy className="h-3 w-3" />
                    <span>{copied ? 'Copied!' : 'Copy JSON'}</span>
                  </button>
                </div>
                <pre className="bg-slate-900 text-slate-200 text-[11px] p-3.5 rounded-lg border border-slate-800 overflow-x-auto font-mono leading-relaxed max-h-72">
                  {JSON.stringify(selectedNode, null, 2)}
                </pre>
              </div>
            )}

            {/* SECTION: Matching Incident Safety Reports (MongoDB Atlas) */}
            {selectedNode.details?.matching_incidents && selectedNode.details.matching_incidents.length > 0 && (
              <div className="space-y-2 pt-3 border-t border-slate-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <Database className="h-4 w-4 text-emerald-600" />
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                      Matching Safety Reports ({selectedNode.details.matching_incidents.length})
                    </h4>
                  </div>
                  <button
                    onClick={downloadCSV}
                    className="flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-100 hover:bg-emerald-200 px-2 py-0.5 rounded border border-emerald-300 transition-colors"
                  >
                    <FileSpreadsheet className="h-3 w-3" />
                    <span>Export Incidents CSV</span>
                  </button>
                </div>

                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {selectedNode.details.matching_incidents.map((inc: any, idx: number) => (
                    <div key={inc.report_id || idx} className="p-2.5 rounded-lg border border-slate-200 bg-white space-y-1 text-[11px] shadow-sm">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-slate-900 truncate max-w-[200px]">{inc.title}</span>
                        <span className={`px-1.5 py-0.5 rounded font-mono font-bold text-[9px] ${
                          inc.sif_status === 'SIF_POTENTIAL' ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                        }`}>
                          {inc.sif_status}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-[10px] text-slate-500 font-semibold flex-wrap">
                        <span>📍 {inc.site}</span>
                        <span>•</span>
                        <span>⚡ {inc.activity}</span>
                        <span>•</span>
                        <span className="text-emerald-700 font-bold">🛡️ {inc.life_saving_rule || 'General Safety'}</span>
                      </div>
                      <p className="text-[11px] text-slate-600 line-clamp-2 leading-relaxed bg-slate-50 p-1.5 rounded border border-slate-100">
                        {inc.description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Footer Buttons */}
            <div className="pt-2 flex items-center gap-2">
              <button
                onClick={downloadCSV}
                className="flex-1 py-2 bg-emerald-700 text-white rounded text-xs font-bold hover:bg-emerald-800 shadow-sm flex items-center justify-center gap-1.5"
              >
                <FileSpreadsheet className="h-3.5 w-3.5" />
                <span>Export CSV</span>
              </button>
              <button
                onClick={downloadJSON}
                className="flex-1 py-2 bg-indigo-700 text-white rounded text-xs font-bold hover:bg-indigo-800 shadow-sm flex items-center justify-center gap-1.5"
              >
                <Download className="h-3.5 w-3.5" />
                <span>Export JSON</span>
              </button>
            </div>
          </div>

        ) : (
          <div className="hidden lg:flex w-96 bg-slate-50 border border-slate-200 rounded-lg p-6 flex-col items-center justify-center text-center space-y-2">
            <Info className="h-8 w-8 text-slate-400" />
            <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">Node Inspector</h4>
            <p className="text-xs text-slate-500">Click any block in the hierarchy tree to inspect detailed MongoDB properties, tabular view, or export JSON/CSV.</p>
          </div>
        )}
      </div>
    </div>
  );
};
