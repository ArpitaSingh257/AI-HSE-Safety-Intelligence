import React from 'react';
import { Database } from 'lucide-react';

export const DemoDataBadge: React.FC = () => {
  return (
    <span className="inline-flex items-center gap-1.5 rounded bg-slate-200/80 px-2 py-0.5 text-xs font-medium text-slate-700 border border-slate-300">
      <Database className="h-3 w-3 text-slate-500" />
      <span>Synthetic OIL Dataset (SIH26165 Demo)</span>
    </span>
  );
};
