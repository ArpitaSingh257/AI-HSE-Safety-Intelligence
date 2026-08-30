import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardService } from '../api';
import type { LifeSavingRuleDistribution } from '../types/dashboard';
import { PageHeader } from '../components/common/PageHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { IOGP_LIFE_SAVING_RULES } from '../utils/iogpRules';
import {
  ShieldAlert,
  ZapOff,
  Flame,
  Box,
  Crosshair,
  ArrowUpCircle,
  Anchor,
  Truck,
  FileCheck,
  ArrowRight,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';

export const LifeSavingRulesPage: React.FC = () => {
  const navigate = useNavigate();
  const [ruleStats, setRuleStats] = useState<LifeSavingRuleDistribution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRules = async () => {
      try {
        const data = await dashboardService.getLifeSavingRules();
        setRuleStats(data);
      } finally {
        setLoading(false);
      }
    };
    fetchRules();
  }, []);

  if (loading) {
    return <LoadingSpinner label="Evaluating IOGP Life-Saving Rules Compliance Matrix..." />;
  }

  const getRuleIcon = (name: string) => {
    switch (name) {
      case 'Energy Isolation': return ZapOff;
      case 'Hot Work': return Flame;
      case 'Confined Space': return Box;
      case 'Line of Fire': return Crosshair;
      case 'Working at Height': return ArrowUpCircle;
      case 'Bypassing Safety Controls': return ShieldAlert;
      case 'Safe Mechanical Lifting': return Anchor;
      case 'Driving': return Truck;
      default: return FileCheck;
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="IOGP Life-Saving Rules Compliance Analytics"
        subtitle="Distribution, violation frequencies, and SIF precursor trends mapped across the 9 International Oil & Gas Producers Life-Saving Rules."
        showDemoBadge={true}
      />

      {/* Rules Grid */}
      <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3">
        {ruleStats.map((item) => {
          const meta = IOGP_LIFE_SAVING_RULES[item.rule];
          const Icon = getRuleIcon(item.rule);

          return (
            <div
              key={item.rule}
              onClick={() => navigate(`/reports?life_saving_rule=${encodeURIComponent(item.rule)}`)}
              className="hse-card p-5 hover:border-slate-400 transition-colors cursor-pointer flex flex-col justify-between"
            >
              <div>
                {/* Header */}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <div className="rounded bg-slate-900 p-2 text-white">
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <span className="font-mono text-[10px] font-bold text-slate-400">
                        {meta?.id || 'LSR'}
                      </span>
                      <h3 className="text-sm font-bold text-slate-900 leading-none">{item.rule}</h3>
                    </div>
                  </div>

                  <div className="flex items-center gap-1 text-xs">
                    {item.trend === 'increasing' ? (
                      <span className="flex items-center font-bold text-red-600">
                        <TrendingUp className="h-3.5 w-3.5 mr-0.5" /> Surging
                      </span>
                    ) : item.trend === 'decreasing' ? (
                      <span className="flex items-center font-bold text-emerald-600">
                        <TrendingDown className="h-3.5 w-3.5 mr-0.5" /> Declining
                      </span>
                    ) : (
                      <span className="flex items-center font-medium text-slate-500">
                        <Minus className="h-3.5 w-3.5 mr-0.5" /> Stable
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-xs text-slate-600 mt-2 line-clamp-2">
                  {meta?.description || 'Mandatory standard safety rule.'}
                </p>

                {/* Metrics */}
                <div className="mt-4 p-3 rounded bg-slate-50 border border-slate-200 text-xs space-y-1.5">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Total Observations:</span>
                    <span className="font-semibold text-slate-800">{item.count}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">SIF Precursor Breaches:</span>
                    <span className="font-bold text-red-600">{item.sifCount} ({item.percentage}%)</span>
                  </div>
                </div>

                {meta && (
                  <div className="mt-3 border-t border-slate-100 pt-2 text-[11px] text-slate-500">
                    <span className="font-semibold text-slate-700 block mb-1">Key Mandatory Barrier:</span>
                    <span className="italic">{meta.mandatoryRequirements[0]}</span>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-slate-700">
                <span>View Filtered Reports ({item.count})</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
