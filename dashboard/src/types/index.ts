// Types mirroring the API response (snake_case = from Python)

export interface IndexQuote {
  code: string;
  name: string;
  price: number;
  change_pct: number;
}

export interface FundHolding {
  code: string;
  name: string;
  cost: number;
  nav: number;
  shares: number;
  estimated_value: number;
  profit_pct: number;
  profit_amount: number;
  sector: string;
}

export interface BuildingFund {
  code: string;
  name: string;
  current: number;
  target: number;
  progress_pct: number;
}

export interface Portfolio {
  holdings: FundHolding[];
  total_cost: number;
  total_value: number;
  total_profit_pct: number;
  tech_deviation_pct: number;
  building_funds: BuildingFund[];
}

export interface SectorRanking {
  name: string;
  change_pct: number;
}

export interface SectorFlow {
  name: string;
  change_pct: number;
  net_inflow_yi: number;
}

export interface SectorData {
  rankings: SectorRanking[];
  fund_flow: SectorFlow[];
}

export interface MarketOverview {
  advance: number;
  decline: number;
  flat: number;
  total: number;
}

export interface AnalysisReport {
  type: string;
  date: string;
  summary: string;
  detail_url: string;
}

export interface OperationRecord {
  date: string;
  file: string;
  title: string;
  summary: string;
  detail_url: string;
}

export interface DashboardData {
  date: string;
  time: string;
  updated_at: string;
  indices: IndexQuote[];
  portfolio: Portfolio;
  sectors: SectorData;
  market_overview: MarketOverview;
  latest_analysis: AnalysisReport[];
  operations: OperationRecord[];
}

export interface NavHistory {
  date: string;
  value: number;
  code?: string;
}
