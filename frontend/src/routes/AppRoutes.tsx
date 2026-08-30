import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { AppLayout } from '../components/layout/AppLayout';
import { RoleGuard } from '../components/layout/RoleGuard';

// Pages
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import { ReportsPage } from '../pages/ReportsPage';
import { ReportDetailPage } from '../pages/ReportDetailPage';
import { PatternExplorerPage } from '../pages/PatternExplorerPage';
import { SiteAnalyticsPage } from '../pages/SiteAnalyticsPage';
import { ActivityAnalyticsPage } from '../pages/ActivityAnalyticsPage';
import { LifeSavingRulesPage } from '../pages/LifeSavingRulesPage';
import { RiskInterventionsPage } from '../pages/RiskInterventionsPage';
import { AuditLogPage } from '../pages/AuditLogPage';

// Helper component for public /login route
const PublicLoginRoute: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const from = (location.state as { from?: { pathname?: string } })?.from?.pathname || '/dashboard';

  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  return <LoginPage />;
};

// Root index redirector based on authentication state
const RootRedirector: React.FC = () => {
  const { isAuthenticated } = useAuth();
  return <Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />;
};

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Root Path: Redirects to /login if unauthenticated, or /dashboard if authenticated */}
      <Route path="/" element={<RootRedirector />} />

      {/* Public Login Route */}
      <Route path="/login" element={<PublicLoginRoute />} />

      {/* All Protected Routes wrapped in RoleGuard + AppLayout */}
      <Route
        element={
          <RoleGuard>
            <AppLayout />
          </RoleGuard>
        }
      >
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="reports/:id" element={<ReportDetailPage />} />
        <Route path="patterns" element={<PatternExplorerPage />} />
        <Route path="sites" element={<SiteAnalyticsPage />} />
        <Route path="activities" element={<ActivityAnalyticsPage />} />
        <Route path="life-saving-rules" element={<LifeSavingRulesPage />} />
        <Route path="interventions" element={<RiskInterventionsPage />} />
        <Route
          path="audit"
          element={
            <RoleGuard requiredPermission="canViewAuditLogs">
              <AuditLogPage />
            </RoleGuard>
          }
        />
        <Route
          path="audit-log"
          element={
            <RoleGuard requiredPermission="canViewAuditLogs">
              <AuditLogPage />
            </RoleGuard>
          }
        />
      </Route>

      {/* Catch-all route */}
      <Route path="*" element={<RootRedirector />} />
    </Routes>
  );
};
