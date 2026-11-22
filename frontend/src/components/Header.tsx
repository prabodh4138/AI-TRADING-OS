import React, { useState } from 'react';
import {
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  ShieldCheck,
  RefreshCw,
  Wallet,
  Radio,
  CheckCircle2,
  Zap,
  Power,
  Play,
  Calendar,
} from 'lucide-react';
import { MarketStatus, PortfolioSummary, AutoTradeStatus } from '../types/api';
import { api } from '../services/api';
import { DataVerificationModal } from './DataVerificationModal';

interface HeaderProps {
  marketStatus: MarketStatus | null;
  portfolio: PortfolioSummary | null;
  autoTradeStatus: AutoTradeStatus | null;
  isConnected: boolean;
  onRefresh: () => void;
  onAutoTradeTriggered?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  marketStatus,
  portfolio,
  autoTradeStatus,
  isConnected,
  onRefresh,
  onAutoTradeTriggered,
}) => {
  const [isRunningPipeline, setIsRunningPipeline] = useState(false);
  const [isRunningAutoTrade, setIsRunningAutoTrade] = useState(false);
  const [isVerificationOpen, setIsVerificationOpen] = useState(false);
  const [noticeMsg, setNoticeMsg] = useState<string | null>(null);

  const handleRunPipeline = async () => {
    try {
      setIsRunningPipeline(true);
      setNoticeMsg('Running full Stage 0 - 10 institutional pipeline...');
      const res = await api.runPipeline();
      setNoticeMsg(res.message);
      onRefresh();
      setTimeout(() => setNoticeMsg(null), 5000);
    } catch (err: any) {
      setNoticeMsg(`Pipeline error: ${err.message}`);
      setTimeout(() => setNoticeMsg(null), 6000);
    } finally {
      setIsRunningPipeline(false);
    }
  };

  const handleTriggerAutoTrade = async () => {
    try {
      setIsRunningAutoTrade(true);
      setNoticeMsg('Executing institutional Auto-Trade scan, entries, and trailing stops...');
      const res = await api.runAutoTrade(3);
      setNoticeMsg(res.message);
      onRefresh();
      if (onAutoTradeTriggered) onAutoTradeTriggered();
      setTimeout(() => setNoticeMsg(null), 6000);
    } catch (err: any) {
      setNoticeMsg(`Auto-trade error: ${err.message}`);
      setTimeout(() => setNoticeMsg(null), 6000);
    } finally {
      setIsRunningAutoTrade(false);
    }
  };

  const handleToggleAuto = async () => {
    try {
      await api.toggleAutoTrade();
      onRefresh();
    } catch (e: any) {
      console.error(e);
    }
  };

  const getPostureBadgeColor = (posture?: string) => {
    if (!posture) return 'bg-slate-800 text-slate-300 border-slate-700';
    if (posture.includes('BULLISH')) return 'bg-emerald-950/70 text-emerald-300 border-emerald-700/50';
    if (posture.includes('BEARISH')) return 'bg-rose-950/70 text-rose-300 border-rose-700/50';
    return 'bg-amber-950/70 text-amber-300 border-amber-700/50';
  };

  const renderTrend = (trend?: string) => {
    if (!trend) return <span className="text-slate-500">N/A</span>;
    const isBull = trend.includes('BULLISH');
    const isBear = trend.includes('BEARISH');
    return (
      <span className={`inline-flex items-center gap-0.5 text-xs font-semibold ${
        isBull ? 'text-emerald-400' : isBear ? 'text-rose-400' : 'text-amber-400'
      }`}>
        {isBull ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
        {trend}
      </span>
    );
  };

  const isProfit = (portfolio?.total_return_pct ?? 0) >= 0;

  return (
    <header className="border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-md sticky top-0 z-50">
      {/* Top Banner Notice */}
      {noticeMsg && (
        <div className="bg-blue-900/80 border-b border-blue-600/50 px-4 py-1.5 text-xs font-mono text-blue-100 flex items-center justify-between animate-in slide-in-from-top duration-200">
          <span className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 animate-pulse" />
            {noticeMsg}
          </span>
          <button onClick={() => setNoticeMsg(null)} className="text-blue-300 hover:text-white font-bold text-sm">×</button>
        </div>
      )}

      <div className="max-w-[1920px] mx-auto px-4 lg:px-6 py-2.5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          
          {/* Brand & Market Posture */}
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 via-indigo-600 to-emerald-500 flex items-center justify-center font-black text-white shadow-lg shadow-blue-500/20">
                ⚡
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-base font-extrabold tracking-tight text-white font-mono">
                    AI TRADING OS
                  </h1>
                  <span className="text-[10px] uppercase font-bold tracking-widest px-1.5 py-0.5 rounded bg-blue-950 border border-blue-700/60 text-blue-300">
                    GTF v3.1
                  </span>
                </div>
                <p className="text-[10px] text-slate-400 font-mono">Institutional Demand & Supply Terminal</p>
              </div>
            </div>

            <div className="h-6 w-px bg-slate-800 hidden sm:block" />

            {/* Live Market Posture */}
            {marketStatus && (
              <div className="flex items-center gap-2">
                <div className={`px-2.5 py-1 rounded-md text-xs font-mono font-medium border flex items-center gap-1.5 ${getPostureBadgeColor(marketStatus.market_posture)}`}>
                  <Activity className="w-3.5 h-3.5 animate-pulse" />
                  <span className="font-semibold">{marketStatus.market_posture}</span>
                </div>

                {/* Macro Horizons */}
                <div className="hidden xl:flex items-center gap-3 px-3 py-1 rounded-md bg-slate-900/60 border border-slate-800/80 text-xs font-mono">
                  <span className="text-slate-400">Y: {renderTrend(marketStatus.yearly_trend)}</span>
                  <span className="text-slate-700">•</span>
                  <span className="text-slate-400">Q: {renderTrend(marketStatus.quarterly_trend)}</span>
                  <span className="text-slate-700">•</span>
                  <span className="text-slate-400">M: {renderTrend(marketStatus.monthly_trend)}</span>
                </div>
              </div>
            )}
          </div>

          {/* Dynamic Metrics & Quick Controls */}
          <div className="flex items-center gap-3 sm:gap-4 flex-wrap justify-between lg:justify-end">
            
            {/* Prominent Latest Trading Date Badge */}
            <button
              onClick={() => setIsVerificationOpen(true)}
              className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-blue-950/70 hover:bg-blue-900/80 border border-blue-600/50 text-xs font-mono shadow-md shadow-blue-950/50 transition cursor-pointer group text-left"
              title="Click to view Dual-Source Data Verification Audit (NSE Bhavcopy vs Yahoo Finance)"
            >
              <div className="w-7 h-7 rounded-md bg-blue-600/30 border border-blue-400/40 flex items-center justify-center text-blue-300 group-hover:scale-105 transition shrink-0">
                <Calendar className="w-4 h-4 text-blue-400" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-[9px] text-blue-300 font-bold uppercase tracking-wider">
                    LATEST TRADING DATE
                  </span>
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                </div>
                <div className="text-xs font-black text-white tracking-wide flex items-center gap-1.5">
                  <span>{marketStatus?.latest_trading_date || marketStatus?.as_of_date || '2026-10-28'}</span>
                  <span className="text-[9px] font-normal text-emerald-300 bg-emerald-950/90 px-1.5 py-0.2 rounded border border-emerald-700/60">
                    VERIFIED
                  </span>
                </div>
              </div>
            </button>

            {/* Dual-Source Auto-Sync & Verification Trigger */}
            <button
              onClick={() => setIsVerificationOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-950/80 hover:bg-indigo-900/90 border border-indigo-700/60 text-indigo-200 text-xs font-mono font-bold transition shadow-sm"
              title="Audit and cross-check prices between NSE Bhavcopy and Yahoo Finance"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
              <span>Dual-Source Sync</span>
            </button>

            {/* Dynamic Data Health Score */}
            <div className="flex items-center gap-2 text-xs font-mono bg-slate-900/80 border border-slate-800 rounded-lg px-2.5 py-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-slate-400 text-[10px]">HEALTH</span>
                  <span className="font-black text-emerald-400">
                    {(marketStatus?.data_health_score ?? 100).toFixed(0)}%
                  </span>
                  <span className="text-[9px] px-1 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                    {marketStatus?.health_status ?? 'PRISTINE'}
                  </span>
                </div>
                <div className="text-[9px] text-slate-500">
                  {marketStatus?.as_of_date ? `Session: ${marketStatus.as_of_date}` : 'Historical Horizon'}
                </div>
              </div>
            </div>

            {/* Dynamic Paper Portfolio Financial Glance */}
            {portfolio && (
              <div className="flex items-center gap-3 bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-1 text-xs font-mono shadow-inner">
                <Wallet className="w-4 h-4 text-blue-400" />
                <div>
                  <div className="text-[9px] text-slate-400 uppercase">Total Equity</div>
                  <div className="font-black text-white flex items-center gap-1">
                    ₹{portfolio.total_equity.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                    <span className={`text-[10px] font-bold ${isProfit ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {isProfit ? '+' : ''}{portfolio.total_return_pct.toFixed(2)}%
                    </span>
                  </div>
                </div>
                <div className="h-5 w-px bg-slate-800" />
                <div>
                  <div className="text-[9px] text-slate-400 uppercase">Available Cash</div>
                  <div className="font-semibold text-slate-200">
                    ₹{portfolio.current_cash.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                  </div>
                </div>
                <div className="h-5 w-px bg-slate-800" />
                <div>
                  <div className="text-[9px] text-slate-400 uppercase">Win Rate</div>
                  <div className={`font-bold ${portfolio.win_rate_pct >= 60 ? 'text-emerald-400' : 'text-slate-300'}`}>
                    {portfolio.win_rate_pct.toFixed(1)}% <span className="text-[10px] text-slate-500">({portfolio.open_positions_count} Open)</span>
                  </div>
                </div>
              </div>
            )}

            {/* Auto-Trading Controls */}
            <div className="flex items-center gap-1.5 bg-slate-900/90 border border-slate-800 rounded-lg p-1">
              <button
                onClick={handleToggleAuto}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-mono font-bold transition ${
                  autoTradeStatus?.enabled
                    ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-500/20'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
                title="Toggle Automated Institutional Paper Trading Engine"
              >
                <Power className="w-3.5 h-3.5" />
                <span>AUTO-TRADE: {autoTradeStatus?.enabled ? 'ON' : 'OFF'}</span>
              </button>

              <button
                onClick={handleTriggerAutoTrade}
                disabled={isRunningAutoTrade}
                className="flex items-center gap-1 px-2 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-mono font-semibold transition disabled:opacity-50"
                title="Execute 1-click Auto-Trade cycle (Scans, Entries & Trailing Stops)"
              >
                <Play className={`w-3 h-3 ${isRunningAutoTrade ? 'animate-spin' : ''}`} />
                <span>{isRunningAutoTrade ? 'Running...' : 'Run Auto'}</span>
              </button>
            </div>

            {/* WebSocket Stream Live Pulse */}
            <div className="flex items-center gap-1 text-[11px] font-mono">
              <Radio className={`w-3.5 h-3.5 ${isConnected ? 'text-emerald-400 animate-pulse' : 'text-slate-500'}`} />
              <span className={isConnected ? 'text-emerald-400 font-semibold' : 'text-slate-500'}>
                {isConnected ? 'LIVE' : 'SYNCING'}
              </span>
            </div>

            {/* OS Refresh Button */}
            <button
              onClick={handleRunPipeline}
              disabled={isRunningPipeline}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono font-semibold transition border border-slate-700 disabled:opacity-50"
              title="Refresh local dataset and governance audit"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRunningPipeline ? 'animate-spin' : ''}`} />
              <span>Refresh OS</span>
            </button>

          </div>
        </div>
      </div>

      {/* Dual-Source Verification Modal */}
      <DataVerificationModal
        isOpen={isVerificationOpen}
        onClose={() => setIsVerificationOpen(false)}
        latestTradingDate={marketStatus?.latest_trading_date || marketStatus?.as_of_date}
        dataHealthScore={marketStatus?.data_health_score ?? 100}
        onSyncCompleted={() => {
          onRefresh();
        }}
      />
    </header>
  );
};
