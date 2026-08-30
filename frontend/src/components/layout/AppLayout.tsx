import React from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { DecisionSupportDisclaimer } from '../common/DecisionSupportDisclaimer';

export const AppLayout: React.FC = () => {
  return (
    <div className="flex min-h-screen flex-col bg-slate-100 font-sans">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-5 sm:p-6 bg-slate-50 flex flex-col justify-between">
          <div className="flex-1">
            <Outlet />
          </div>
          <div className="mt-8 pt-4 border-t border-slate-200">
            <DecisionSupportDisclaimer />
          </div>
        </main>
      </div>
    </div>
  );
};
