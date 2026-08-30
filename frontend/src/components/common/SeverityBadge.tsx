import React from 'react';
import type { PriorityLevel, SifStatus } from '../../types/reports';
import { SEVERITY_CONFIG, SIF_STATUS_CONFIG } from '../../utils/severity';
import {
  ShieldAlert,
  ShieldCheck,
  Clock,
  AlertOctagon,
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';

interface SeverityBadgeProps {
  priority?: PriorityLevel;
  sifStatus?: SifStatus;
  size?: 'sm' | 'md';
  showDot?: boolean;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({
  priority,
  sifStatus,
  size = 'md',
  showDot = true,
}) => {
  const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-xs px-2.5 py-1';
  const iconSize = size === 'sm' ? 'h-3 w-3' : 'h-3.5 w-3.5';

  if (sifStatus) {
    const config = SIF_STATUS_CONFIG[sifStatus] || SIF_STATUS_CONFIG.PENDING_ANALYSIS;
    
    // Non-color cue icon
    const StatusIcon =
      sifStatus === 'SIF_POTENTIAL'
        ? ShieldAlert
        : sifStatus === 'NON_SIF'
        ? ShieldCheck
        : Clock;

    return (
      <span
        className={`inline-flex items-center gap-1.5 rounded-sm border font-medium uppercase tracking-wider ${config.badgeBg} ${sizeClasses}`}
        aria-label={`SIF Classification: ${config.label}`}
        data-testid="sif-status-badge"
      >
        <StatusIcon className={`${iconSize} flex-shrink-0`} aria-hidden="true" />
        {showDot && <span className={`h-1.5 w-1.5 rounded-full ${config.dotColor}`} aria-hidden="true" />}
        <span>{config.label}</span>
      </span>
    );
  }

  if (priority) {
    const config = SEVERITY_CONFIG[priority] || SEVERITY_CONFIG.LOW;

    // Non-color cue icon
    const PriorityIcon =
      priority === 'CRITICAL'
        ? AlertOctagon
        : priority === 'HIGH'
        ? AlertTriangle
        : priority === 'MEDIUM'
        ? AlertCircle
        : CheckCircle2;

    return (
      <span
        className={`inline-flex items-center gap-1.5 rounded-sm border font-medium tracking-wide ${config.badgeBg} ${sizeClasses}`}
        aria-label={`Priority Level: ${config.label} Priority`}
        data-testid="priority-badge"
      >
        <PriorityIcon className={`${iconSize} flex-shrink-0`} aria-hidden="true" />
        {showDot && <span className={`h-1.5 w-1.5 rounded-full ${config.dotColor}`} aria-hidden="true" />}
        <span>{config.label} Priority</span>
      </span>
    );
  }

  return null;
};
