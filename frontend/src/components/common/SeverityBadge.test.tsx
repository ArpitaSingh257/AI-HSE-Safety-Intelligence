import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SeverityBadge } from './SeverityBadge';

describe('SeverityBadge Component', () => {
  it('renders Critical priority badge with text label and non-color cue icon', () => {
    render(<SeverityBadge priority="CRITICAL" />);
    const badge = screen.getByTestId('priority-badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent(/Critical Priority/i);
    expect(badge).toHaveAttribute('aria-label', 'Priority Level: Critical Priority');
  });

  it('renders High priority badge correctly', () => {
    render(<SeverityBadge priority="HIGH" />);
    const badge = screen.getByTestId('priority-badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent(/High Priority/i);
    expect(badge).toHaveAttribute('aria-label', 'Priority Level: High Priority');
  });

  it('renders Medium and Low priority badges correctly', () => {
    const { rerender } = render(<SeverityBadge priority="MEDIUM" />);
    expect(screen.getByText(/Medium Priority/i)).toBeInTheDocument();

    rerender(<SeverityBadge priority="LOW" />);
    expect(screen.getByText(/Low Priority/i)).toBeInTheDocument();
  });

  it('renders SIF_POTENTIAL classification badge with non-color cue', () => {
    render(<SeverityBadge sifStatus="SIF_POTENTIAL" />);
    const badge = screen.getByTestId('sif-status-badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent(/SIF Potential/i);
    expect(badge).toHaveAttribute('aria-label', 'SIF Classification: SIF Potential');
  });

  it('renders NON_SIF status badge correctly', () => {
    render(<SeverityBadge sifStatus="NON_SIF" />);
    const badge = screen.getByTestId('sif-status-badge');
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent(/Non-SIF/i);
  });
});
