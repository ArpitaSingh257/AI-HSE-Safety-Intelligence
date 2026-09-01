import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { reportsService } from '../api';
import { formatPercentage } from '../utils/formatters';
import { Layers, ArrowRight, Sparkles, MapPin, Activity, ShieldAlert, AlertTriangle, FileText, CheckCircle2 } from 'lucide-react';

interface SimilarReportItem {
  report_id: string;
  similarity_score: number;
  similarity_percentage: number;
  report_date: string;
  location: string;
  activity: string;
  hazard: string;
  barrier_failure: string;
  primary_life_saving_rule: string;
  is_sif: boolean;
  narrative_excerpt: string;
  explanation: string;
  stage23_pattern_id?: string;
  stage24_barrier_id?: string;
}

interface SimilarReportsViewProps {
  reportId: string;
}

export const SimilarReportsView: React.FC<SimilarReportsViewProps> = ({ reportId }) => {
  const navigate = useNavigate();
  const [similarReports, setSimilarReports] = useState<SimilarReportItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadSimilarReports = async () => {
      setLoading(true);
      try {
        const data = await reportsService.getSimilarReports(reportId);
        setSimilarReports(data.similar_reports || []);
      } catch (err) {
        console.warn('Failed to load similar reports:', err);
      } finally {
        setLoading(false);
      }
    };
    loadSimilarReports();
  }, [reportId]);

  if (loading) {
    return (
      <div className="p-4 text-center text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded">
        Searching FAISS vector index for semantically similar historical safety reports...
      </div>
    );
  }

  if (similarReports.length === 0) {
    return (
      <div className="p-4 text-center text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded">
        No sufficiently similar historical safety reports identified above similarity threshold.
      </div>
    );
  }

  return (
    <div className="space-y-4 pt-4 border-t border-slate-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded bg-slate-900 text-white">
            <Layers className="h-4 w-4 text-slate-200" />
          </div>
          <h3 className="text-sm font-bold text-slate-900">
            Semantically Similar Historical Reports ({similarReports.length})
          </h3>
        </div>
        <span className="text-xs font-mono text-slate-500">FAISS 384-D Vector Search</span>
      </div>

      <div className="space-y-3">
        {similarReports.map((item) => (
          <div
            key={item.report_id}
            className="p-4 bg-white border border-slate-200 rounded-lg hover:border-slate-400 transition-colors space-y-2.5"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                  {item.report_id}
                </span>
                {item.is_sif && (
                  <span className="bg-red-100 text-red-800 text-[10px] font-extrabold px-2 py-0.5 rounded">
                    SIF PRECURSOR
                  </span>
                )}
                {item.stage23_pattern_id && (
                  <span className="bg-purple-100 text-purple-900 font-mono text-[10px] font-bold px-2 py-0.5 rounded">
                    Pattern: {item.stage23_pattern_id}
                  </span>
                )}
                {item.stage24_barrier_id && (
                  <span className="bg-amber-100 text-amber-900 font-mono text-[10px] font-bold px-2 py-0.5 rounded">
                    Barrier: {item.stage24_barrier_id}
                  </span>
                )}
              </div>

              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                {item.similarity_percentage}% Semantic Similarity
              </span>
            </div>

            <p className="text-xs text-slate-600 italic bg-slate-50 p-2.5 rounded border border-slate-150 leading-relaxed">
              &quot;{item.narrative_excerpt}&quot;
            </p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-[11px] text-slate-700 pt-1">
              <div><span className="text-slate-400 block text-[10px] uppercase">Activity</span> <span className="font-semibold">{item.activity}</span></div>
              <div><span className="text-slate-400 block text-[10px] uppercase">Hazard</span> <span className="font-semibold">{item.hazard}</span></div>
              <div><span className="text-slate-400 block text-[10px] uppercase">Barrier Failure</span> <span className="font-semibold text-amber-700">{item.barrier_failure}</span></div>
              <div><span className="text-slate-400 block text-[10px] uppercase">LSR</span> <span className="font-semibold">{item.primary_life_saving_rule}</span></div>
            </div>

            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="text-slate-500 font-sans text-[11px]">{item.explanation}</span>
              <button
                onClick={() => navigate(`/reports/${item.report_id}`)}
                className="flex items-center gap-1 font-bold text-slate-900 hover:text-slate-600 transition-colors"
              >
                Inspect Report <ArrowRight className="h-3 w-3" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
