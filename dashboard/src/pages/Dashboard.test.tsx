import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import Dashboard from '../pages/Dashboard';
import * as api from '../lib/api';
import type { DashboardData } from '../types';

// Mock ECharts — requires real Canvas, crashes in jsdom
vi.mock('echarts', () => {
  const mockChart = {
    setOption: vi.fn(),
    dispose: vi.fn(),
  };
  const mockInstance = () => mockChart;
  mockChart.dispose.mockReturnValue(undefined);
  return {
    default: {
      init: vi.fn(() => mockChart),
      graphic: { LinearGradient: vi.fn(() => ({})) },
    },
    init: vi.fn(() => mockChart),
    graphic: { LinearGradient: vi.fn(() => ({})) },
  };
});

const MOCK: DashboardData = {
  date: '2026-07-21', time: '10:00', updated_at: '2026-07-21T10:00:00',
  indices: [
    { code: 'sh000001', name: '上证指数', price: 3864.37, change_pct: 1.79 },
    { code: 'sz399006', name: '创业板指', price: 3685.97, change_pct: 7.05 },
  ],
  portfolio: {
    holdings: [{ code: '003096', name: '中欧医疗C', cost: 280, nav: 1.93, shares: 145,
      estimated_value: 279.71, profit_pct: -0.1, profit_amount: -0.29, sector: '医疗' }],
    total_cost: 6425.78, total_value: 5713.05, total_profit_pct: -11.09,
    tech_deviation_pct: 15.9,
    building_funds: [{ code: '003096', name: '中欧医疗C', current: 279.71, target: 370, progress_pct: 75.6 }],
  },
  sectors: { rankings: [{ name: '半导体', change_pct: 9.8 }], fund_flow: [{ name: '电子', change_pct: 7.4, net_inflow_yi: 275.0 }] },
  market_overview: { advance: 6809, decline: 179, flat: 319, total: 7307 },
  latest_analysis: [{ type: 'morning', date: '2026-07-21', summary: '市场强力反弹' }],
  operations: [{ date: '2026-07-20', file: 'op.md' }],
};

beforeEach(() => vi.restoreAllMocks());
afterEach(() => cleanup());

describe('Dashboard page', () => {
  it('shows loading state initially', () => {
    vi.spyOn(api, 'fetchDashboard').mockImplementation(() => new Promise(() => {}));
    render(<Dashboard />);
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });

  it('renders dashboard data after loading', async () => {
    vi.spyOn(api, 'fetchDashboard').mockResolvedValue(MOCK);
    render(<Dashboard />);
    await waitFor(() => { expect(screen.getByText('📊 投资看板')).toBeInTheDocument(); });
    expect(screen.getByText('上证指数')).toBeInTheDocument();
    expect(screen.getByText('3864.37')).toBeInTheDocument();
    expect(screen.getByText('¥5713')).toBeInTheDocument();
    expect(screen.getByText('-11.09%')).toBeInTheDocument();
    expect(screen.getByText('6809')).toBeInTheDocument();
    expect(screen.getByText('179')).toBeInTheDocument();
    expect(screen.getByText('市场强力反弹')).toBeInTheDocument();
  });

  it('shows empty state when data is null', async () => {
    vi.spyOn(api, 'fetchDashboard').mockResolvedValue(null);
    render(<Dashboard />);
    await waitFor(() => { expect(screen.getByText(/暂无数据/)).toBeInTheDocument(); });
  });

  it('shows error when fetchDashboard throws', async () => {
    vi.spyOn(api, 'fetchDashboard').mockRejectedValue(new Error('fail'));
    render(<Dashboard />);
    await waitFor(() => { expect(screen.getByText(/数据加载失败/)).toBeInTheDocument(); });
  });

  it('displays building funds', async () => {
    vi.spyOn(api, 'fetchDashboard').mockResolvedValue(MOCK);
    render(<Dashboard />);
    await waitFor(() => { expect(screen.getByText(/中欧医疗C/)).toBeInTheDocument(); });
  });
});
