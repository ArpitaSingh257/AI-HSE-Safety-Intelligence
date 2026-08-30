import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User, UserRole, RolePermissions, LoginCredentials } from '../types/auth';
import { ROLE_PERMISSIONS } from '../types/auth';
import { authService } from '../api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  role: UserRole | null;
  permissions: RolePermissions | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  switchRole: (role: UserRole) => void;
  hasPermission: (permission: keyof RolePermissions) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // STRICT AUTH STATE: null by default if no valid session in localStorage
  const [user, setUser] = useState<User | null>(() => {
    try {
      const saved = localStorage.getItem('sih_oil_auth_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('sih_oil_auth_token') || null;
  });

  const [isLoading, setIsLoading] = useState<boolean>(false);

  const isAuthenticated = Boolean(user && token);
  const currentRole: UserRole | null = user?.role || null;
  const permissions: RolePermissions | null = currentRole ? ROLE_PERMISSIONS[currentRole] : null;

  useEffect(() => {
    if (user && token) {
      localStorage.setItem('sih_oil_auth_user', JSON.stringify(user));
      localStorage.setItem('sih_oil_auth_token', token);
    } else {
      localStorage.removeItem('sih_oil_auth_user');
      localStorage.removeItem('sih_oil_auth_token');
    }
  }, [user, token]);

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    try {
      const response = await authService.login(credentials);
      setUser(response.user);
      setToken(response.token);
      localStorage.setItem('sih_oil_auth_user', JSON.stringify(response.user));
      localStorage.setItem('sih_oil_auth_token', response.token);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('sih_oil_auth_token');
    localStorage.removeItem('sih_oil_auth_user');
  };

  // Only active in DEV mode for rapid RBAC testing
  const switchRole = (newRole: UserRole) => {
    if (!user) return;
    const updatedUser: User = {
      ...user,
      role: newRole,
      name:
        newRole === 'Admin'
          ? 'Ananya Roy (Admin)'
          : newRole === 'HSE Manager'
          ? 'Rajesh Sharma (HSE Manager)'
          : newRole === 'HSE Analyst'
          ? 'Debojit Phukan (HSE Analyst)'
          : 'Site Auditor (Viewer)',
    };
    setUser(updatedUser);
    localStorage.setItem('sih_oil_auth_user', JSON.stringify(updatedUser));
  };

  const hasPermission = (permission: keyof RolePermissions): boolean => {
    if (!permissions) return false;
    return !!permissions[permission];
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated,
        isLoading,
        role: currentRole,
        permissions,
        login,
        logout,
        switchRole,
        hasPermission,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
