import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { UserRole } from '../types/auth';
import { ShieldCheck, Lock, Mail, ArrowRight, UserCheck, Shield } from 'lucide-react';
import { DemoDataBadge } from '../components/common/DemoDataBadge';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState('officer@oilindia.in');
  const [password, setPassword] = useState('••••••••');
  const [selectedRole, setSelectedRole] = useState<UserRole>('HSE Analyst');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login({ email, password, role: selectedRole });
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (role: UserRole) => {
    setLoading(true);
    try {
      await login({ email: `${role.toLowerCase().replace(' ', '.')}@oilindia.in`, role });
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-900 px-4 py-12 text-slate-100">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Banner */}
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded bg-slate-800 border border-slate-700 shadow-inner">
            <ShieldCheck className="h-7 w-7 text-white" />
          </div>
          <div className="mt-3 flex items-center justify-center gap-2">
            <span className="text-xs font-bold uppercase tracking-widest text-slate-400">
              OIL INDIA LIMITED
            </span>
            <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] font-semibold text-slate-300 border border-slate-700">
              SIH26165
            </span>
          </div>
          <h1 className="mt-1 text-xl font-bold tracking-tight text-white">
            SIF Precursor Intelligence Platform
          </h1>
          <p className="mt-1 text-xs text-slate-400">
            AI-Powered Serious Injury & Fatality Detection System
          </p>
        </div>

        {/* Login Form Card */}
        <div className="hse-card overflow-hidden border-slate-700 bg-slate-800/90 p-6 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email-input" className="block text-xs font-medium text-slate-300">
                Official Email ID
              </label>
              <div className="mt-1 relative rounded shadow-xs">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Mail className="h-4 w-4 text-slate-400" />
                </div>
                <input
                  id="email-input"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="block w-full rounded border border-slate-600 bg-slate-900/80 py-2 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:border-slate-400 focus:outline-hidden"
                  placeholder="name@oilidentity.in"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password-input" className="block text-xs font-medium text-slate-300">
                Enterprise Password / Token
              </label>
              <div className="mt-1 relative rounded shadow-xs">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Lock className="h-4 w-4 text-slate-400" />
                </div>
                <input
                  id="password-input"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="block w-full rounded border border-slate-600 bg-slate-900/80 py-2 pl-9 pr-3 text-xs text-white placeholder-slate-500 focus:border-slate-400 focus:outline-hidden"
                />
              </div>
            </div>

            <div>
              <label htmlFor="role-select" className="block text-xs font-medium text-slate-300">
                Select RBAC Authority Role
              </label>
              <select
                id="role-select"
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value as UserRole)}
                className="mt-1 block w-full rounded border border-slate-600 bg-slate-900/80 py-2 px-3 text-xs text-white focus:border-slate-400 focus:outline-hidden"
              >
                <option value="Admin">Admin (Full System & Audit Access)</option>
                <option value="HSE Manager">HSE Manager (Interventions & Analysis)</option>
                <option value="HSE Analyst">HSE Analyst (Report Ingestion & AI Inspection)</option>
                <option value="Viewer">Viewer (Read-Only Analytics)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded bg-slate-100 py-2.5 px-4 text-xs font-semibold text-slate-900 hover:bg-white transition-colors disabled:opacity-50"
            >
              <span>{loading ? 'Authenticating...' : 'Sign In with SSO / JWT'}</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          </form>

          {/* Quick Login Presets for Evaluation */}
          <div className="mt-6 border-t border-slate-700 pt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
                <UserCheck className="h-3.5 w-3.5" /> One-Click Role Presets:
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {(['Admin', 'HSE Manager', 'HSE Analyst', 'Viewer'] as UserRole[]).map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => handleQuickLogin(r)}
                  className="rounded border border-slate-700 bg-slate-900/60 p-2 text-left text-[11px] font-medium text-slate-300 hover:border-slate-500 hover:bg-slate-700/60 transition-colors"
                >
                  <div className="font-semibold text-white">{r}</div>
                  <div className="text-[10px] text-slate-400">
                    {r === 'Admin' ? 'All Privileges' : r === 'HSE Manager' ? 'Intervention Lead' : r === 'HSE Analyst' ? 'NLP Pipeline' : 'Read-Only'}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Security Notice */}
        <div className="text-center text-[11px] text-slate-500 flex flex-col items-center gap-1.5">
          <div className="flex items-center gap-1">
            <Shield className="h-3.5 w-3.5" />
            <span>Authorized for Oil India Limited HSE Personnel Only</span>
          </div>
          <DemoDataBadge />
        </div>
      </div>
    </div>
  );
};
