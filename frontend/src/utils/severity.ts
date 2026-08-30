import type { PriorityLevel, SifStatus } from '../types/reports';

/**
 * STRICT HSE COLOR & SEVERITY DISCIPLINE
 * 
 * Rules:
 * 1. Green = Low (Safe / Controlled / Non-SIF)
 * 2. Amber/Yellow = Medium (Moderate Risk / Pending Review)
 * 3. Orange = High (Significant Risk / Precursor Detected)
 * 4. Red = Critical (Immediate SIF Hazard / Direct Danger)
 * 
 * These 4 colors are reserved strictly for safety risk meaning across the entire platform.
 */

export interface SeverityConfig {
  label: string;
  badgeBg: string;
  badgeText: string;
  badgeBorder: string;
  dotColor: string;
  barColor: string;
  chartColor: string;
}

export const SEVERITY_CONFIG: Record<PriorityLevel, SeverityConfig> = {
  LOW: {
    label: 'Low',
    badgeBg: 'bg-emerald-50 text-emerald-800 border-emerald-300',
    badgeText: 'text-emerald-800',
    badgeBorder: 'border-emerald-300',
    dotColor: 'bg-emerald-500',
    barColor: 'bg-emerald-500',
    chartColor: '#10b981', // Emerald 500
  },
  MEDIUM: {
    label: 'Medium',
    badgeBg: 'bg-amber-50 text-amber-800 border-amber-300',
    badgeText: 'text-amber-800',
    badgeBorder: 'border-amber-300',
    dotColor: 'bg-amber-500',
    barColor: 'bg-amber-500',
    chartColor: '#f59e0b', // Amber 500
  },
  HIGH: {
    label: 'High',
    badgeBg: 'bg-orange-50 text-orange-900 border-orange-300',
    badgeText: 'text-orange-900',
    badgeBorder: 'border-orange-300',
    dotColor: 'bg-orange-600',
    barColor: 'bg-orange-600',
    chartColor: '#ea580c', // Orange 600
  },
  CRITICAL: {
    label: 'Critical',
    badgeBg: 'bg-red-50 text-red-900 border-red-300',
    badgeText: 'text-red-900',
    badgeBorder: 'border-red-300',
    dotColor: 'bg-red-600',
    barColor: 'bg-red-600',
    chartColor: '#dc2626', // Red 600
  },
};

export const SIF_STATUS_CONFIG: Record<SifStatus, SeverityConfig> = {
  SIF_POTENTIAL: {
    label: 'SIF Potential',
    badgeBg: 'bg-red-50 text-red-900 border-red-300 font-semibold',
    badgeText: 'text-red-900',
    badgeBorder: 'border-red-300',
    dotColor: 'bg-red-600',
    barColor: 'bg-red-600',
    chartColor: '#dc2626',
  },
  NON_SIF: {
    label: 'Non-SIF',
    badgeBg: 'bg-emerald-50 text-emerald-800 border-emerald-300',
    badgeText: 'text-emerald-800',
    badgeBorder: 'border-emerald-300',
    dotColor: 'bg-emerald-500',
    barColor: 'bg-emerald-500',
    chartColor: '#10b981',
  },
  PENDING_ANALYSIS: {
    label: 'Pending Analysis',
    badgeBg: 'bg-slate-100 text-slate-700 border-slate-300',
    badgeText: 'text-slate-700',
    badgeBorder: 'border-slate-300',
    dotColor: 'bg-slate-400',
    barColor: 'bg-slate-400',
    chartColor: '#94a3b8',
  },
};

export const MUTED_CHART_PALETTE = [
  '#2b4c7e',
  '#4a6572',
  '#6b7280',
  '#34495e',
  '#546e7a',
  '#475569',
  '#64748b',
  '#334155',
];
