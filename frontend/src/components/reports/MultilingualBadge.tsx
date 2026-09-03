import React, { useState, useEffect } from 'react';
import { multilingualService } from '../../api';
import type { MultilingualNormalizationResult } from '../../types/multilingual';
import { Languages, Check, RefreshCw, FileText, Globe } from 'lucide-react';

interface MultilingualBadgeProps {
  description: string;
}

export const MultilingualBadge: React.FC<MultilingualBadgeProps> = ({ description }) => {
  const [data, setData] = useState<MultilingualNormalizationResult | null>(null);
  const [showNormalized, setShowNormalized] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const processText = async () => {
      if (!description) return;
      setLoading(true);
      try {
        const res = await multilingualService.normalizeText(description);
        if (res) setData(res);
      } catch (err) {
        console.warn('Failed to process multilingual text:', err);
      } finally {
        setLoading(false);
      }
    };

    processText();
  }, [description]);

  if (!data) return null;

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2.5 text-xs">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 font-bold text-slate-700">
          <Globe className="h-4 w-4 text-blue-600" />
          <span>Stage 35 — Multilingual & Field Language Handling</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold bg-blue-100 text-blue-900 border border-blue-300 px-2 py-0.5 rounded uppercase">
            Lang: {data.language_code} ({data.is_code_mixed ? 'Code-Mixed' : 'Standard'})
          </span>
          <span className="text-[10px] font-bold bg-indigo-100 text-indigo-900 border border-indigo-300 px-2 py-0.5 rounded uppercase">
            Method: {data.normalization_method}
          </span>

          <button
            onClick={() => setShowNormalized(!showNormalized)}
            className="text-[10px] font-bold bg-slate-200 hover:bg-slate-300 text-slate-800 px-2 py-0.5 rounded transition-colors flex items-center gap-1"
          >
            <FileText className="h-3 w-3" />
            {showNormalized ? 'View Original' : 'View Normalized'}
          </button>
        </div>
      </div>

      {/* Processed Text Output Box */}
      <div className="bg-white p-2.5 rounded border border-slate-200 text-slate-800 text-xs font-mono leading-relaxed">
        {showNormalized ? data.normalized_text : data.original_text}
      </div>

      {/* Applied Corrections & Domain Abbreviation Expansion Metadata */}
      {(data.corrections_applied.length > 0 || data.abbreviations_expanded.length > 0) && (
        <div className="flex flex-wrap items-center gap-1.5 text-[10px]">
          <span className="font-semibold text-slate-500">Normalizations Applied:</span>
          {data.abbreviations_expanded.map((abbr, i) => (
            <span key={i} className="bg-amber-100 text-amber-900 px-1.5 py-0.5 rounded font-mono font-bold">
              {abbr}
            </span>
          ))}
          {data.corrections_applied.map((corr, i) => (
            <span key={i} className="bg-slate-200 text-slate-800 px-1.5 py-0.5 rounded font-mono">
              {corr}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};
