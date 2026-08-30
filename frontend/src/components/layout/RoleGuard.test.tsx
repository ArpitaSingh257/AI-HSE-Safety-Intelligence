import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../../context/AuthContext';
import { RoleGuard } from './RoleGuard';

describe('RoleGuard Component', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('redirects unauthenticated users to /login', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<div>Login Page Target</div>} />
            <Route
              path="/dashboard"
              element={
                <RoleGuard>
                  <div>Protected Dashboard Content</div>
                </RoleGuard>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByText('Login Page Target')).toBeInTheDocument();
    expect(screen.queryByText('Protected Dashboard Content')).not.toBeInTheDocument();
  });

  it('renders children when user is authenticated with proper permissions', () => {
    const mockUser = {
      id: 'USR-001',
      name: 'Test Officer',
      email: 'test@oilindia.in',
      role: 'Admin',
      department: 'HSE',
    };
    localStorage.setItem('sih_oil_auth_user', JSON.stringify(mockUser));
    localStorage.setItem('sih_oil_auth_token', 'valid-test-token');

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <AuthProvider>
          <Routes>
            <Route
              path="/dashboard"
              element={
                <RoleGuard>
                  <div>Authorized Dashboard Area</div>
                </RoleGuard>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByText('Authorized Dashboard Area')).toBeInTheDocument();
  });

  it('renders Access Restricted when user lacks required permission', () => {
    const viewerUser = {
      id: 'USR-002',
      name: 'Viewer User',
      email: 'viewer@oilindia.in',
      role: 'Viewer',
      department: 'Audit',
    };
    localStorage.setItem('sih_oil_auth_user', JSON.stringify(viewerUser));
    localStorage.setItem('sih_oil_auth_token', 'valid-test-token');

    render(
      <MemoryRouter initialEntries={['/audit']}>
        <AuthProvider>
          <Routes>
            <Route
              path="/audit"
              element={
                <RoleGuard requiredPermission="canViewAuditLogs">
                  <div>Secret Audit Records</div>
                </RoleGuard>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByTestId('access-restricted-card')).toBeInTheDocument();
    expect(screen.getByText(/Access Restricted/i)).toBeInTheDocument();
    expect(screen.queryByText('Secret Audit Records')).not.toBeInTheDocument();
  });
});
