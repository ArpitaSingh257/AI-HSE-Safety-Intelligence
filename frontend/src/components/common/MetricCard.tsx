import React from 'react';
import { type LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { PriorityLevel } from '../../types/reports';

interface MetricCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  trend?: number;
  trendLabel?: string;
  icon?: LucideIcon;
  riskAccent?: PriorityLevel;
  onClick?: () => void;
  clickable?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subValue,
  trend,
  trendLabel = 'vs last period',
  icon: Icon,
  riskAccent,
  onClick,
  clickable = false,
}) => {
  const accentBorder = riskAccent
    ? `border-l-4 ${
        riskAccent === 'CRITICAL'
          ? 'border-l-red-600'
          : riskAccent === 'HIGH'
          ? 'border-l-orange-600'
          : riskAccent === 'MEDIUM'
          ? 'border-l-amber-500'
          : 'border-l-emerald-600'
      }`
    : 'border-slate-200';

  return (
    <div
      onClick={onClick}
      className={`hse-card p-4 transition-colors ${accentBorder} ${
        clickable ? 'cursor-pointer hover:border-slate-400 hover:bg-slate-50/50' : ''
      }`}
    >
      <div className="flex items-start justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {label}
        </span>
        {Icon && (
          <div className="rounded bg-slate-100 p-1.5 text-slate-700">
            <Icon className="h-4 w-4" />
          </div>
        )}
      </div>

      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-slate-900">{value}</span>
        {subValue && <span className="text-xs font-medium text-slate-500">{subValue}</span>}
      </div>

      {trend !== undefined && (
        <div className="mt-3 flex items-center gap-1.5 text-xs">
          {trend > 0 ? (
            <span className="inline-flex items-center font-medium text-slate-700">
              <TrendingUp className="mr-0.5 h-3.5 w-3.5 text-slate-600" />
              +{trend}%
            </span>
          ) : trend < 0 ? (
            <span className="inline-flex items-center font-medium text-slate-700">
              <TrendingDown className="mr-0.5 h-3.5 w-3.5 text-slate-600" />
              {trend}%
            </span>
          ) : (
            <span className="inline-flex items-center font-medium text-slate-500">
              <Minus className="mr-0.5 h-3.5 w-3.5 text-slate-400" />
              0%
            </span>
          )}
          <span className="text-slate-500">{trendLabel}</span>
        </div>
      )}
    </div>
  );
};
