import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  FileText,
  Boxes,
  MapPin,
  Flame,
  ShieldAlert,
  AlertTriangle,
  AlertOctagon,
  Grid,
  History,
  Info,
  GitFork,
  Brain,
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
  permission?: 'canViewAuditLogs' | 'canManageInterventions';
  badge?: string;
}

export const Sidebar: React.FC = () => {
  const { hasPermission } = useAuth();

  const navItems: NavItem[] = [
    {
      name: 'Main Dashboard',
      path: '/dashboard',
      icon: LayoutDashboard,
    },
    {
      name: 'Safety Reports',
      path: '/reports',
      icon: FileText,
      badge: '12 New',
    },
    {
      name: 'Knowledge Graph',
      path: '/knowledge-graph',
      icon: GitFork,
      badge: 'Graph RAG',
    },
    {
      name: 'Agentic Investigator',
      path: '/agentic-investigation',
      icon: Brain,
      badge: 'ReAct AI',
    },
    {
      name: 'Pattern Explorer',
      path: '/patterns',
      icon: Boxes,
    },
    {
      name: 'Barrier Explorer',
      path: '/barrier-patterns',
      icon: ShieldAlert,
      badge: 'Stage 24',
    },
    {
      name: 'Site Analytics',
      path: '/sites',
      icon: MapPin,
    },
    {
      name: 'Activity Analytics',
      path: '/activities',
      icon: Flame,
    },
    {
      name: 'Life-Saving Rules',
      path: '/life-saving-rules',
      icon: ShieldAlert,
    },
    {
      name: 'Early Warning',
      path: '/early-warnings',
      icon: AlertOctagon,
      badge: 'Stage 29',
    },
    {
      name: 'HSE Priorities',
      path: '/priorities',
      icon: ShieldAlert,
      badge: 'Stage 30',
    },
    {
      name: 'Risk Matrix',
      path: '/risk-matrix',
      icon: Grid,
      badge: 'Stage 31',
    },
    {
      name: 'Risk & Interventions',
      path: '/interventions',
      icon: AlertTriangle,
      badge: '14 Active',
    },
    {
      name: 'System Audit Log',
      path: '/audit',
      icon: History,
      permission: 'canViewAuditLogs',
    },
  ];

  return (
    <aside className="w-60 flex-shrink-0 border-r border-slate-200 bg-white flex flex-col justify-between select-none">
      <div className="py-4">
        <div className="px-4 mb-3">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
            HSE Intelligence Menu
          </span>
        </div>

        <nav className="space-y-0.5 px-2">
          {navItems.map((item) => {
            if (item.permission && !hasPermission(item.permission)) {
              return null;
            }

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center justify-between rounded px-3 py-2 text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-900 text-white shadow-xs font-semibold'
                      : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900'
                  }`
                }
              >
                <div className="flex items-center gap-2.5">
                  <item.icon className="h-4 w-4 flex-shrink-0" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="rounded bg-slate-200 px-1.5 py-0.5 text-[10px] font-semibold text-slate-700">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Role & Reasoning Chain Info Footer */}
      <div className="p-3 border-t border-slate-200 bg-slate-50 text-[11px] text-slate-600">
        <div className="flex items-center gap-1.5 font-semibold text-slate-800 mb-1">
          <Info className="h-3.5 w-3.5 text-slate-500" />
          <span>SIF Reasoning Chain</span>
        </div>
        <div className="text-[10px] text-slate-500 leading-tight">
          Report → SIF Potential → Activity/Hazard → Barrier Failure → Life-Saving Rule → Pattern → Intervention
        </div>
      </div>
    </aside>
  );
};
