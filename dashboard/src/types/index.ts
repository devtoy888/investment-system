export interface FundHolding {
  code: string;
  name: string;
  shares: number;
  cost: number;
  nav: number;
  estimatedValue: number;
  profitPct: number;
  profitAmount: number;
  sector: string;
}

export interface IndexQuote {
  code: string;
  name: string;
  price: number;
  changePct: number;
  change: number;
}

export interface SectorData {
  name: string;
  changePct: number;
  netInflow: number;
  rank: number;
}

export interface MarketOverview {
  advance: number;
  decline: number;
  flat: number;
  total: number;
}

export interface KOLSignal {
  id: string;
  author: string;
  time: string;
  content: string;
  direction: 'bullish' | 'bearish' | 'neutral';
  targetSector?: string;
  accuracy?: number;
}

export interface AnalysisReport {
  type: 'morning' | 'noon' | 'closing' | 'weekly';
  date: string;
  summary: string;
}

export interface DashboardData {
  date: string;
  indices: IndexQuote[];
  holdings: FundHolding[];
  sectors: SectorData[];
  marketOverview: MarketOverview;
  totalValue: number;
  totalProfitPct: number;
  deviationPct: number;
  buildingFunds: { code: string; current: number; target: number }[];
}

export interface NavHistory {
  date: string;
  value: number;
  code?: string;
}

export interface Operation {
  date: string;
  fundCode: string;
  fundName: string;
  type: 'buy' | 'sell';
  amount: number;
  reason?: string;
}
