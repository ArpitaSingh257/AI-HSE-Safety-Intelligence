import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MetricCard } from './MetricCard';
import { ShieldAlert } from 'lucide-react';

describe('MetricCard Component', () => {
  it('renders label, value, and subValue accurately', () => {
    render(
      <MetricCard
        label="Total Safety Reports"
        value="1,428"
        subValue="Reports Ingested"
      />
    );

    expect(screen.getByText(/Total Safety Reports/i)).toBeInTheDocument();
    expect(screen.getByText('1,428')).toBeInTheDocument();
    expect(screen.getByText(/Reports Ingested/i)).toBeInTheDocument();
  });

  it('renders positive trend indicator with correct sign', () => {
    render(
      <MetricCard
        label="SIF Precursors"
        value="384"
        trend={8.4}
        trendLabel="vs last month"
      />
    );

    expect(screen.getByText('+8.4%')).toBeInTheDocument();
    expect(screen.getByText(/vs last month/i)).toBeInTheDocument();
  });

  it('renders negative trend indicator with correct sign', () => {
    render(
      <MetricCard
        label="Near Miss Rate"
        value="12%"
        trend={-3.2}
      />
    );

    expect(screen.getByText('-3.2%')).toBeInTheDocument();
  });

  it('triggers onClick callback when clickable card is clicked', () => {
    const handleClick = vi.fn();
    render(
      <MetricCard
        label="Drill Down Metric"
        value="42"
        clickable={true}
        onClick={handleClick}
        icon={ShieldAlert}
      />
    );

    const card = screen.getByText(/Drill Down Metric/i).closest('.hse-card');
    expect(card).toBeInTheDocument();
    if (card) {
      fireEvent.click(card);
      expect(handleClick).toHaveBeenCalledTimes(1);
    }
  });
});
