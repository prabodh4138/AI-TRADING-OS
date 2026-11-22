import React, { useState } from 'react';
import {
  Briefcase,
  TrendingUp,
  RotateCcw,
  Zap,
  Play,
  Power,
  ShieldCheck,
  CheckCircle2,
  Clock,
  ArrowUpRight,
  ListCheck,
} from 'lucide-react';
import { PortfolioSummary, AutoTradeStatus, AutoTradeResult } from '../types/api';
import { api } from '../services/api';

interface PortfolioViewProps {
  portfolio: PortfolioSummary | null;
  autoTradeStatus: AutoTradeStatus | null;
  isLoading: boolean;
  onRefresh: () => void;
  onInspectChart: (symbol: string) => void;
}

export const PortfolioView: React.FC<PortfolioViewProps> = ({
  portfolio,
  autoTradeStatus,
  isLoading,
  onRefresh,
  onInspectChart,
}) => {
  const [isResetting, setIsResetting] = useState(false);
  const [resetCapital, setResetCapital] = useState(1000000);
  const [showResetModal, setShowResetModal] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const [isRunningAuto, setIsRunningAuto] = useState(false);
  const [autoResult, setAutoResult] = useState<AutoTradeResult | null>(null);

  const handleReset = async () => {
    try {
      setIsResetting(true);
      const res = await api.resetPortfolio(resetCapital);
      setStatusMsg(res.message);
      setShowResetModal(false);
      onRefresh();
      setTimeout(() => setStatusMsg(null), 4000);
    } catch (err: any) {
      setStatusMsg(`Reset error: ${err.message}`);
    } finally {
      setIsResetting(false);
    }
  };

  const handleRunAutoTrade = async () => {
    try {
      setIsRunningAuto(true);
      const res = await api.runAutoTrade(3);
      setAutoResult(res);
      setStatusMsg(res.message);
      onRefresh();
      setTimeout(() => setStatusMsg(null), 5000);
    } catch (err: any) {
      setStatusMsg(`Auto-trade failed: ${err.message}`);
    } finally {
      setIsRunningAuto(false);
    }
  };

  const handleToggleAuto = async () => {
    try {
      await api.toggleAutoTrade();
      onRefresh();
    } catch (err: any) {
      console.error(err);
    }
  };

  if (isLoading && !portfolio) {
    return (
      <div className="py-20 flex flex-col items-center justify-center gap-2 font-mono text-xs text-slate-400">
        <div className="w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin" />
        Loading paper trading portfolio...
      </div>
    );
  }

  if (!portfolio) {
    return null;
  }

  const isNetPositive = portfolio.total_return_pct >= 0;

  return (
    <div className="space-y-6">
      
      {/* Top Header & Actions */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center">
            <Briefcase className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-black font-mono text-white">Paper Trading Desk & Automated Engine</h2>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold">
                100% Simulated Local Execution
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">
              Mark-to-Market Ledger with Automated Entry, Buffered Stop-Loss & Dynamic Trailing Stop Exits
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleToggleAuto}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition border ${
              autoTradeStatus?.enabled
                ? 'bg-emerald-600/20 text-emerald-300 border-emerald-600/40 hover:bg-emerald-600/30'
                : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
            }`}
          >
            <Power className="w-3.5 h-3.5" />
            <span>Auto-Trading: {autoTradeStatus?.enabled ? 'ACTIVE' : 'PAUSED'}</span>
          </button>

          <button
            onClick={handleRunAutoTrade}
            disabled={isRunningAuto}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white text-xs font-mono font-bold transition shadow-md shadow-emerald-600/20 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 ${isRunningAuto ? 'animate-spin' : ''}`} />
            <span>{isRunningAuto ? 'Evaluating Setups...' : 'Trigger Auto-Trade Now'}</span>
          </button>

          <button
            onClick={() => setShowResetModal(true)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-mono transition border border-slate-700"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Capital</span>
          </button>
        </div>
      </div>

      {statusMsg && (
        <div className="p-3 rounded-xl bg-blue-950/70 border border-blue-700 text-xs font-mono text-blue-200 flex items-center justify-between animate-in fade-in duration-200">
          <span>{statusMsg}</span>
          <button onClick={() => setStatusMsg(null)} className="text-blue-400 font-bold">×</button>
        </div>
      )}

      {/* Financial Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5">
        
        {/* Total Equity */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3.5">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Total Equity</div>
          <div className="text-2xl font-bold font-mono text-white mt-1">
            ₹{portfolio.total_equity.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
          </div>
          <div className={`text-[11px] font-mono font-semibold mt-0.5 flex items-center gap-1 ${
            isNetPositive ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            {isNetPositive ? '+' : ''}{portfolio.total_return_pct.toFixed(2)}% Overall
          </div>
        </div>

        {/* Available Cash */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3.5">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Available Cash</div>
          <div className="text-2xl font-bold font-mono text-slate-200 mt-1">
            ₹{portfolio.current_cash.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">
            {((portfolio.current_cash / (portfolio.total_equity || 1)) * 100).toFixed(1)}% Liquidity
          </div>
        </div>

        {/* Open Positions */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3.5">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Open Positions</div>
          <div className="text-2xl font-bold font-mono text-blue-400 mt-1">
            {portfolio.open_positions_count} <span className="text-xs text-slate-500">/ 15</span>
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">Target: 10–15 Stocks</div>
        </div>

        {/* Win Rate */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3.5">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Win Rate</div>
          <div className={`text-2xl font-bold font-mono mt-1 ${
            portfolio.win_rate_pct >= 60 ? 'text-emerald-400' : 'text-slate-200'
          }`}>
            {portfolio.win_rate_pct.toFixed(1)}%
          </div>
          <div className="text-[10px] font-mono text-slate-500 mt-0.5">
            {portfolio.total_closed_trades} Closed Trades
          </div>
        </div>

        {/* 15-Stock Capital Allocation */}
        <div className="bg-emerald-950/20 border border-emerald-800/40 rounded-xl p-3.5 col-span-2 md:col-span-1">
          <div className="text-[11px] font-mono text-emerald-400 uppercase tracking-wider">Capital Sizing</div>
          <div className="text-lg font-bold font-mono text-emerald-300 mt-1">
            1/15th EQUAL WEIGHT
          </div>
          <div className="text-[10px] font-mono text-emerald-500/80 mt-0.5">
            ~6.7% / ₹66.6K Max Per Stock
          </div>
        </div>

      </div>

      {/* Auto-Trading Execution Log Panel */}
      {autoResult && autoResult.execution_details.length > 0 && (
        <div className="bg-slate-900/80 border border-indigo-700/50 rounded-xl p-4 shadow-xl space-y-2 font-mono text-xs animate-in fade-in duration-300">
          <div className="flex items-center gap-2 text-indigo-400 uppercase font-bold text-xs tracking-wider">
            <ListCheck className="w-4 h-4" />
            Auto-Trading Execution Audit Trail
          </div>
          <div className="space-y-1.5 max-h-36 overflow-y-auto pr-2">
            {autoResult.execution_details.map((detail, idx) => (
              <div key={idx} className="p-2 rounded bg-slate-950/80 border border-slate-800 text-slate-200 flex items-start gap-2">
                <span className="text-emerald-400 font-bold">•</span>
                <span>{detail}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Open Positions Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="px-4 py-3 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="text-xs font-mono uppercase font-bold text-slate-300 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Active Open Positions ({portfolio.positions.length})
          </div>
          <div className="text-[11px] font-mono text-slate-400">
            Smart Trailing Stop Loss Active (Breakeven @ +1.5R, Profit Lock @ +2.5R)
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Symbol</th>
                <th className="py-2.5 px-3">Entry Date</th>
                <th className="py-2.5 px-3 text-right">Shares</th>
                <th className="py-2.5 px-3 text-right">Entry Price</th>
                <th className="py-2.5 px-3 text-right">CMP (₹)</th>
                <th className="py-2.5 px-3 text-right">Stop Loss</th>
                <th className="py-2.5 px-3 text-right">Target</th>
                <th className="py-2.5 px-3 text-right">Unrealized P&L</th>
                <th className="py-2.5 px-3 text-center">Days Held</th>
                <th className="py-2.5 px-4 text-center">Chart</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {portfolio.positions.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-8 text-center text-slate-500 font-mono">
                    No active positions. Click "Trigger Auto-Trade Now" or execute setups from the scan tab.
                  </td>
                </tr>
              ) : (
                portfolio.positions.map((pos) => {
                  const isProfit = pos.unrealized_pnl >= 0;
                  const isTrailingProtected = pos.stop_loss > pos.initial_stop_loss;
                  return (
                    <tr key={pos.position_id} className="hover:bg-slate-800/30 transition">
                      <td className="py-3 px-4 font-bold text-white">
                        <div className="flex items-center gap-2">
                          <span>{pos.symbol}</span>
                          {isTrailingProtected && (
                            <span className="px-1.5 py-0.2 rounded text-[9px] bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold">
                              TRAILING LOCKED
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-3 text-slate-400">
                        {pos.entry_date}
                      </td>
                      <td className="py-3 px-3 text-right text-slate-200">
                        {pos.quantity}
                      </td>
                      <td className="py-3 px-3 text-right text-slate-300">
                        ₹{pos.entry_price.toFixed(2)}
                      </td>
                      <td className="py-3 px-3 text-right font-bold text-white">
                        ₹{pos.current_price.toFixed(2)}
                      </td>
                      <td className="py-3 px-3 text-right text-rose-400">
                        ₹{pos.stop_loss.toFixed(2)}
                      </td>
                      <td className="py-3 px-3 text-right text-blue-400">
                        ₹{pos.target.toFixed(2)}
                      </td>
                      <td className={`py-3 px-3 text-right font-bold ${
                        isProfit ? 'text-emerald-400' : 'text-rose-400'
                      }`}>
                        {isProfit ? '+' : ''}₹{pos.unrealized_pnl.toFixed(2)} ({pos.unrealized_pnl_pct.toFixed(2)}%)
                      </td>
                      <td className="py-3 px-3 text-center text-slate-400">
                        {(() => {
                          try {
                            const entryD = new Date(pos.entry_date).getTime();
                            const nowD = new Date().getTime();
                            const diffDays = Math.max(1, Math.floor((nowD - entryD) / (1000 * 60 * 60 * 24)) + 1);
                            return Math.min(pos.days_held, diffDays);
                          } catch {
                            return Math.min(pos.days_held, 1);
                          }
                        })()}d
                      </td>
                      <td className="py-3 px-4 text-center">
                        <button
                          onClick={() => onInspectChart(pos.symbol)}
                          className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[10px] font-mono transition"
                        >
                          Chart
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Closed Trades History Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="px-4 py-3 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="text-xs font-mono uppercase font-bold text-slate-300 flex items-center gap-2">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            Recent Closed Trades ({portfolio.recent_closed_trades.length})
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-4">Symbol</th>
                <th className="py-2.5 px-3">Entry Date</th>
                <th className="py-2.5 px-3">Exit Date</th>
                <th className="py-2.5 px-3 text-right">Entry (₹)</th>
                <th className="py-2.5 px-3 text-right">Exit (₹)</th>
                <th className="py-2.5 px-3 text-right">Net P&L</th>
                <th className="py-2.5 px-3 text-right">Return %</th>
                <th className="py-2.5 px-4">Exit Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {portfolio.recent_closed_trades.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-6 text-center text-slate-500 font-mono">
                    No trades closed yet in this session.
                  </td>
                </tr>
              ) : (
                portfolio.recent_closed_trades.map((tr) => {
                  const isWin = tr.net_pnl >= 0;
                  return (
                    <tr key={tr.trade_id} className="hover:bg-slate-800/30 transition">
                      <td className="py-2.5 px-4 font-bold text-white">
                        {tr.symbol}
                      </td>
                      <td className="py-2.5 px-3 text-slate-400">
                        {tr.entry_date}
                      </td>
                      <td className="py-2.5 px-3 text-slate-400">
                        {tr.exit_date}
                      </td>
                      <td className="py-2.5 px-3 text-right text-slate-300">
                        ₹{tr.entry_price.toFixed(2)}
                      </td>
                      <td className="py-2.5 px-3 text-right text-white">
                        ₹{tr.exit_price.toFixed(2)}
                      </td>
                      <td className={`py-2.5 px-3 text-right font-bold ${
                        isWin ? 'text-emerald-400' : 'text-rose-400'
                      }`}>
                        {isWin ? '+' : ''}₹{tr.net_pnl.toFixed(2)}
                      </td>
                      <td className={`py-2.5 px-3 text-right font-bold ${
                        isWin ? 'text-emerald-400' : 'text-rose-400'
                      }`}>
                        {isWin ? '+' : ''}{tr.pnl_pct.toFixed(2)}%
                      </td>
                      <td className="py-2.5 px-4">
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                          tr.exit_reason.includes('TARGET')
                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                            : 'bg-rose-950 text-rose-300 border border-rose-800'
                        }`}>
                          {tr.exit_reason}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Reset Modal */}
      {showResetModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <h3 className="text-base font-bold font-mono text-white">Reset Paper Trading Capital</h3>
            <p className="text-xs font-mono text-slate-400">
              This will clear existing open positions and reset your virtual balance to the specified capital.
            </p>

            <div>
              <label className="text-xs font-mono text-slate-300 block mb-1">Starting Capital (INR)</label>
              <input
                type="number"
                value={resetCapital}
                onChange={(e) => setResetCapital(Number(e.target.value))}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm font-mono text-white focus:outline-none focus:border-amber-500"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setShowResetModal(false)}
                className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 text-xs font-mono"
              >
                Cancel
              </button>
              <button
                onClick={handleReset}
                disabled={isResetting}
                className="px-4 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs font-mono transition"
              >
                {isResetting ? 'Resetting...' : 'Confirm Reset'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
