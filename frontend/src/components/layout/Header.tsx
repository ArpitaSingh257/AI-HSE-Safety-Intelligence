import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import type { UserRole } from '../../types/auth';
import { ShieldCheck, LogOut, ChevronDown, Check, Building2, Code } from 'lucide-react';

export const Header: React.FC = () => {
  const { user, role, switchRole, logout } = useAuth();
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);

  const roles: UserRole[] = ['Admin', 'HSE Manager', 'HSE Analyst', 'Viewer'];
  const isDevMode = import.meta.env.DEV;

  return (
    <header className="sticky top-0 z-40 flex h-14 w-full items-center justify-between border-b border-slate-200 bg-slate-900 px-4 sm:px-6 text-white shadow-xs">
      {/* Brand & Organization */}
      <div className="flex items-center gap-3">
        <div className="flex items-center justify-center rounded bg-slate-800 p-1.5 border border-slate-700">
          <ShieldCheck className="h-5 w-5 text-slate-200" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
              OIL INDIA LIMITED
            </span>
            <span className="rounded bg-slate-800 px-1.5 py-0.2 text-[10px] font-semibold text-slate-300 border border-slate-700">
              SIH26165
            </span>
          </div>
          <span className="text-sm font-semibold tracking-tight text-white block -mt-0.5">
            SIF Precursor Intelligence Platform
          </span>
        </div>
      </div>

      {/* Center / Right controls */}
      <div className="flex items-center gap-3">
        {/* Role Display / DEV Mode Role Switcher */}
        {isDevMode ? (
          <div className="relative">
            <button
              onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
              className="flex items-center gap-1.5 rounded border border-amber-500/50 bg-amber-950/40 px-2.5 py-1 text-xs font-medium text-amber-200 hover:bg-amber-900/40 transition-colors"
              title="Dev Mode RBAC Switcher"
            >
              <Code className="h-3 w-3 text-amber-400" />
              <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">[DEV]</span>
              <span className="text-slate-300">Role:</span>
              <span className="font-semibold text-white">{role || 'Unassigned'}</span>
              <ChevronDown className="h-3.5 w-3.5 text-amber-400" />
            </button>

            {roleDropdownOpen && (
              <div
                className="absolute right-0 mt-1.5 w-56 rounded border border-amber-500/40 bg-slate-800 py-1 shadow-xl z-50 text-xs"
                onMouseLeave={() => setRoleDropdownOpen(false)}
              >
                <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-amber-400 border-b border-slate-700 flex items-center justify-between">
                  <span>[DEV MODE] Switch RBAC Role</span>
                </div>
                {roles.map((r) => (
                  <button
                    key={r}
                    onClick={() => {
                      switchRole(r);
                      setRoleDropdownOpen(false);
                    }}
                    className={`flex w-full items-center justify-between px-3 py-2 text-left transition-colors ${
                      role === r
                        ? 'bg-slate-700 text-white font-semibold'
                        : 'text-slate-300 hover:bg-slate-700/50'
                    }`}
                  >
                    <span>{r}</span>
                    {role === r && <Check className="h-3.5 w-3.5 text-emerald-400" />}
                  </button>
                ))}
              </div>
            )}
          </div>
        ) : (
          /* Production Mode: Static non-interactive role badge */
          <div className="flex items-center gap-1.5 rounded border border-slate-700 bg-slate-800 px-2.5 py-1 text-xs font-medium text-slate-200">
            <span className="text-slate-400">Role:</span>
            <span className="font-semibold text-white">{role || 'User'}</span>
          </div>
        )}

        {/* User Profile & Logout */}
        <div className="relative">
          <button
            onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
            className="flex items-center gap-2 rounded border border-slate-700 bg-slate-800/60 p-1 pr-2.5 text-xs text-slate-200 hover:bg-slate-700/80 transition-colors"
          >
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-slate-700 text-xs font-bold text-white">
              {user?.name ? user.name[0] : 'U'}
            </div>
            <div className="text-left hidden md:block">
              <span className="block font-medium leading-none text-white">{user?.name}</span>
              <span className="text-[10px] text-slate-400 leading-tight">{user?.site || 'Duliajan'}</span>
            </div>
            <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
          </button>

          {profileDropdownOpen && (
            <div
              className="absolute right-0 mt-1.5 w-60 rounded border border-slate-700 bg-slate-800 py-1.5 shadow-xl z-50 text-xs"
              onMouseLeave={() => setProfileDropdownOpen(false)}
            >
              <div className="px-3 py-2 border-b border-slate-700">
                <p className="font-semibold text-white">{user?.name}</p>
                <p className="text-[11px] text-slate-400">{user?.email}</p>
                <div className="mt-1 flex items-center gap-1 text-[10px] text-slate-300">
                  <Building2 className="h-3 w-3" />
                  <span>{user?.department}</span>
                </div>
              </div>
              <button
                onClick={() => {
                  logout();
                  setProfileDropdownOpen(false);
                }}
                className="flex w-full items-center gap-2 px-3 py-2 text-left text-red-400 hover:bg-slate-700/60 transition-colors"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span>Sign Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
