import type { NavHistory, AnalysisReport, DashboardData } from '../types';

const DASHBOARD_URL = '/api/dashboard';
const HISTORY_URL = '/api/history';
const ANALYSIS_URL = '/api/analysis';

async function fetchJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const resp = await fetch(url, { signal });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
  return resp.json();
}

export async function fetchDashboard(signal?: AbortSignal): Promise<DashboardData | null> {
  try {
    return await fetchJson<DashboardData>(DASHBOARD_URL, signal);
  } catch {
    try {
      const R2_DASHBOARD = 'https://hermes-main-media.devtoy.xyz/fund-system/dashboard.json';
      return await fetchJson<DashboardData>(R2_DASHBOARD, signal);
    } catch {
      return null;
    }
  }
}

export async function fetchHistory(days = 30, signal?: AbortSignal) {
  try {
    return await fetchJson<NavHistory[]>(`${HISTORY_URL}?days=${days}`, signal);
  } catch {
    return [];
  }
}

export async function fetchLatestAnalysis(signal?: AbortSignal) {
  try {
    return await fetchJson<AnalysisReport[]>(ANALYSIS_URL, signal);
  } catch {
    return [];
  }
}

export function cn(...classes: (string | undefined | null | false)[]) {
  return classes.filter(Boolean).join(' ');
}

export function pctColor(p: number): string {
  return p > 0 ? 'text-red-400' : p < 0 ? 'text-green-400' : 'text-gray-400';
}

export function formatPct(p: number): string {
  return `${p > 0 ? '+' : ''}${p.toFixed(2)}%`;
}

export function formatMoney(n: number): string {
  return `¥${n.toFixed(2)}`;
}