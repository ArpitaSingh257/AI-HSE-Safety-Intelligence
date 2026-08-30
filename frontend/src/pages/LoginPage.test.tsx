import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { LoginPage } from './LoginPage';

describe('LoginPage Form & Validation Tests', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders all form input controls, role selector, and quick presets', () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByLabelText(/Official Email ID/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Enterprise Password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Select RBAC Authority Role/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign In with SSO \/ JWT/i })).toBeInTheDocument();
  });

  it('allows user to change email and role in the login form', () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </MemoryRouter>
    );

    const emailInput = screen.getByLabelText(/Official Email ID/i) as HTMLInputElement;
    const roleSelect = screen.getByLabelText(/Select RBAC Authority Role/i) as HTMLSelectElement;

    fireEvent.change(emailInput, { target: { value: 'manager@oilindia.in' } });
    fireEvent.change(roleSelect, { target: { value: 'HSE Manager' } });

    expect(emailInput.value).toBe('manager@oilindia.in');
    expect(roleSelect.value).toBe('HSE Manager');
  });

  it('successfully authenticates and saves session to localStorage upon form submission', async () => {
    render(
      <MemoryRouter initialEntries={['/login']}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/dashboard" element={<div>Dashboard Landed</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    const submitBtn = screen.getByRole('button', { name: /Sign In with SSO \/ JWT/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(localStorage.getItem('sih_oil_auth_token')).toBeTruthy();
      expect(localStorage.getItem('sih_oil_auth_user')).toBeTruthy();
      expect(screen.getByText('Dashboard Landed')).toBeInTheDocument();
    });
  });

  it('one-click preset sets role and authenticates', async () => {
    render(
      <MemoryRouter initialEntries={['/login']}>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/dashboard" element={<div>Dashboard Landed</div>} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );

    const adminPresetBtn = screen.getByText('Admin').closest('button');
    expect(adminPresetBtn).toBeInTheDocument();
    if (adminPresetBtn) {
      fireEvent.click(adminPresetBtn);
    }

    await waitFor(() => {
      const user = JSON.parse(localStorage.getItem('sih_oil_auth_user') || '{}');
      expect(user.role).toBe('Admin');
      expect(screen.getByText('Dashboard Landed')).toBeInTheDocument();
    });
  });
});
