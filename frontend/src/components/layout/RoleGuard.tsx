import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import type { RolePermissions } from '../../types/auth';
import { ShieldAlert } from 'lucide-react';

interface RoleGuardProps {
  children: React.ReactNode;
  requiredPermission?: keyof RolePermissions;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({ children, requiredPermission }) => {
  const { isAuthenticated, hasPermission, role } = useAuth();
  const location = useLocation();

  // 1. Mandatory Session Check: Redirect to /login if unauthenticated on any direct URL visit or refresh
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 2. RBAC Permission Gate: If authenticated but lacking specific permission
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <div className="hse-card p-8 text-center max-w-lg mx-auto my-12" data-testid="access-restricted-card">
        <div className="rounded-full bg-amber-100 p-3 text-amber-700 w-12 h-12 flex items-center justify-center mx-auto mb-3">
          <ShieldAlert className="h-6 w-6" />
        </div>
        <h2 className="text-base font-bold text-slate-900">Access Restricted</h2>
        <p className="mt-1 text-xs text-slate-600">
          Your current role (<span className="font-semibold">{role}</span>) does not have authorization to view or manage this administrative resource.
        </p>
      </div>
    );
  }

  return <>{children}</>;
};
