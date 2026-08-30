import React from 'react';
import { Info } from 'lucide-react';

interface DecisionSupportDisclaimerProps {
  compact?: boolean;
}

export const DecisionSupportDisclaimer: React.FC<DecisionSupportDisclaimerProps> = ({
  compact = false,
}) => {
  if (compact) {
    return (
      <div className="flex items-center gap-2 rounded bg-slate-100 px-3 py-1.5 text-xs text-slate-600 border border-slate-200">
        <Info className="h-3.5 w-3.5 flex-shrink-0 text-slate-500" />
        <span>AI Decision Support: Precursor scores and rules are advisory classifications for HSE investigators.</span>
      </div>
    );
  }

  return (
    <div className="rounded border border-slate-200 bg-slate-50 p-3.5 text-xs text-slate-700">
      <div className="flex items-start gap-2.5">
        <Info className="h-4 w-4 text-slate-600 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-slate-900">Decision-Support Advisory Notice:</span>
          <p className="mt-0.5 leading-relaxed text-slate-600">
            This platform functions as an intelligent decision-support system. All AI classifications, SIF probability scores, IOGP Life-Saving Rule mappings, and precursor extractions are generated to assist qualified HSE safety officers and must not be treated as autonomous statutory safety mandates.
          </p>
        </div>
      </div>
    </div>
  );
};
