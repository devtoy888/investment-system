import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchDashboard, fetchHistory, pctColor, formatPct, cn } from './api';
import type { DashboardData } from '../types';

const MOCK_DASHBOARD: DashboardData = {
  date: '2026-07-21',
  time: '10:00',
  updated_at: '2026-07-21T10:00:00',
  indices: [
    { code: 'sh000001', name: '上证指数', price: 3864.37, change_pct: 1.79 },
    { code: 'sz399006', name: '创业板指', price: 3685.97, change_pct: 7.05 },
  ],
  portfolio: {
    holdings: [
      { code: '003096', name: '中欧医疗C', cost: 280, nav: 1.93, shares: 145,
        estimated_value: 279.71, profit_pct: -0.1, profit_amount: -0.29, sector: '医疗' },
    ],
    total_cost: 6425.78,
    total_value: 5713.05,
    total_profit_pct: -11.09,
    tech_deviation_pct: 15.9,
    building_funds: [
      { code: '003096', name: '中欧医疗C', current: 279.71, target: 370, progress_pct: 75.6 },
    ],
  },
  sectors: {
    rankings: [{ name: '半导体', change_pct: 9.8 }],
    fund_flow: [{ name: '电子', change_pct: 7.4, net_inflow_yi: 275.0 }],
  },
  market_overview: { advance: 6809, decline: 179, flat: 319, total: 7307 },
  latest_analysis: [{ type: 'morning', date: '2026-07-21', summary: '市场反弹' }],
  operations: [{ date: '2026-07-20', file: 'operation_2026-07-20.md' }],
};

beforeEach(() => {
  vi.restoreAllMocks();
});

describe('fetchDashboard', () => {
  it('returns DashboardData when API succeeds', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_DASHBOARD),
    });
    const data = await fetchDashboard();
    expect(data).not.toBeNull();
    expect(data!.date).toBe('2026-07-21');
    expect(data!.indices).toHaveLength(2);
    expect(data!.portfolio.total_value).toBe(5713.05);
    expect(data!.market_overview.advance).toBe(6809);
  });

  it('falls back to R2 when Worker API fails', async () => {
    globalThis.fetch = vi.fn()
      .mockRejectedValueOnce(new Error('Worker down'))
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(MOCK_DASHBOARD),
      });
    const data = await fetchDashboard();
    expect(data).not.toBeNull();
    expect(data!.date).toBe('2026-07-21');
    expect(globalThis.fetch).toHaveBeenCalledTimes(2);
  });

  it('returns null when all sources fail', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('Network error'));
    const data = await fetchDashboard();
    expect(data).toBeNull();
  });
});

describe('fetchHistory', () => {
  it('returns data on success', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([{ date: '2026-07-20', value: 5713 }]),
    });
    const data = await fetchHistory(30);
    expect(data).toHaveLength(1);
    expect(data[0].date).toBe('2026-07-20');
  });

  it('returns empty array on failure', async () => {
    globalThis.fetch = vi.fn().mockRejectedValue(new Error('error'));
    const data = await fetchHistory(7);
    expect(data).toEqual([]);
  });
});

describe('pctColor', () => {
  it('returns red for positive', () => expect(pctColor(5)).toBe('text-red-400'));
  it('returns green for negative', () => expect(pctColor(-3)).toBe('text-green-400'));
  it('returns gray for zero', () => expect(pctColor(0)).toBe('text-gray-400'));
});

describe('formatPct', () => {
  it('formats positive', () => expect(formatPct(3.06)).toBe('+3.06%'));
  it('formats negative', () => expect(formatPct(-11.09)).toBe('-11.09%'));
  it('formats zero', () => expect(formatPct(0)).toBe('0.00%'));
});

describe('cn', () => {
  it('merges class names', () => expect(cn('a', 'b')).toBe('a b'));
  it('filters falsy values', () => expect(cn('a', false && 'b', 'c')).toBe('a c'));
});
