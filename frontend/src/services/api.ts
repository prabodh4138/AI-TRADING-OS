import {
  AutoTradeResult,
  AutoTradeStatus,
  CandleHistoryResponse,
  DualSourceCheck,
  ExecuteTradeRequest,
  MarketStatus,
  MarketSyncResponse,
  MTFMatrixResponse,
  PortfolioSummary,
  Position,
  StockThesis,
  Master123Response,
  PullbackDiagnosis,
  WatchlistRecommendation,
  ZoneScanResponse,
} from '../types/api';

const API_BASE = '/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorText = await res.text();
    let detail = errorText;
    try {
      const parsed = JSON.parse(errorText);
      detail = parsed.detail || parsed.message || errorText;
    } catch {
      // keep raw text
    }
    throw new Error(detail || `API request failed with status ${res.status}`);
  }

  return res.json();
}

export const api = {
  // Market Data
  getMarketStatus: () => fetchJson<MarketStatus>('/market/status'),
  getSymbols: () => fetchJson<string[]>('/market/symbols'),
  getSymbolBars: (symbol: string, timeframe: string = '1D') =>
    fetchJson<CandleHistoryResponse>(`/market/bars/${symbol}?timeframe=${timeframe}`),
  syncLatestMarketData: (targetDate?: string) =>
    fetchJson<MarketSyncResponse>(
      `/market/sync-latest${targetDate ? `?target_date=${encodeURIComponent(targetDate)}` : ''}`,
      { method: 'POST' }
    ),
  getDualSourceAudit: () => fetchJson<DualSourceCheck[]>('/market/verification-audit'),

  // Demand & Supply Zones
  getZoneScan: (forceRefresh = false) =>
    fetchJson<ZoneScanResponse>(`/zones/scan?force_refresh=${forceRefresh}`),
  getCuratedWatchlist: () =>
    fetchJson<WatchlistRecommendation[]>('/zones/best-watchlist'),
  getMTFMatrix: (symbol: string) => fetchJson<MTFMatrixResponse>(`/zones/mtf/${symbol}`),

  // Stock Thesis & Intelligence
  getStockThesis: (symbol: string) => fetchJson<StockThesis>(`/thesis/${symbol}`),
  getPullbackDiagnosis: (symbol: string) => fetchJson<PullbackDiagnosis>(`/thesis/pullback/${symbol}`),
  getMasterChecklist: (symbol: string) => fetchJson<Master123Response>(`/thesis/master-123/${symbol}`),

  // Paper Trading Portfolio
  getPortfolioSummary: () => fetchJson<PortfolioSummary>('/portfolio/summary'),
  executeTrade: (req: ExecuteTradeRequest) =>
    fetchJson<Position>('/portfolio/execute', {
      method: 'POST',
      body: JSON.stringify(req),
    }),
  executeBatch: (reqs: ExecuteTradeRequest[]) =>
    fetchJson<Position[]>('/portfolio/execute-batch', {
      method: 'POST',
      body: JSON.stringify(reqs),
    }),
  resetPortfolio: (capital = 1000000.0) =>
    fetchJson<{ success: boolean; message: string }>('/portfolio/reset', {
      method: 'POST',
      body: JSON.stringify({ capital }),
    }),

  // Auto-Trading Engine
  getAutoTradeStatus: () => fetchJson<AutoTradeStatus>('/portfolio/auto-trade/status'),
  toggleAutoTrade: (enabled?: boolean) =>
    fetchJson<AutoTradeStatus>(`/portfolio/auto-trade/toggle${enabled !== undefined ? `?enabled=${enabled}` : ''}`, {
      method: 'POST',
    }),
  runAutoTrade: (maxTrades: number = 5) =>
    fetchJson<AutoTradeResult>(`/portfolio/auto-trade/run?max_trades=${maxTrades}`, {
      method: 'POST',
    }),

  // Pipeline
  runPipeline: () =>
    fetchJson<{ success: boolean; message: string; data?: any }>('/pipeline/run', {
      method: 'POST',
    }),
  getPreflight: () => fetchJson<any>('/pipeline/preflight'),
};
