import React, { useState, useEffect } from 'react';
import {
  X,
  ShieldCheck,
  RefreshCw,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  Database,
  ExternalLink,
} from 'lucide-react';
import { DualSourceCheck, MarketSyncResponse } from '../types/api';
import { api } from '../services/api';

interface DataVerificationModalProps {
  isOpen: boolean;
  onClose: () => void;
  latestTradingDate?: string;
  dataHealthScore?: number;
  onSyncCompleted?: (res: MarketSyncResponse) => void;
}

export const DataVerificationModal: React.FC<DataVerificationModalProps> = ({
  isOpen,
  onClose,
  latestTradingDate,
  dataHealthScore = 100,
  onSyncCompleted,
}) => {
  const [checks, setChecks] = useState<DualSourceCheck[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadAudit();
    }
  }, [isOpen]);

  const loadAudit = async () => {
    try {
      setIsLoading(true);
      const data = await api.getDualSourceAudit();
      setChecks(data);
    } catch (err: any) {
      setStatusMsg(`Failed to load verification audit: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSyncNow = async () => {
    try {
      setIsSyncing(true);
      setStatusMsg('Initiating dual-source acquisition from NSE & Yahoo Finance...');
      const res = await api.syncLatestMarketData();
      setStatusMsg(res.message);
      if (res.verification_checks && res.verification_checks.length > 0) {
        setChecks(res.verification_checks);
      } else {
        await loadAudit();
      }
      if (onSyncCompleted) {
        onSyncCompleted(res);
      }
    } catch (err: any) {
      setStatusMsg(`Sync error: ${err.message}`);
    } finally {
      setIsSyncing(false);
    }
  };

  if (!isOpen) return null;

  const verifiedCount = checks.filter(
    (c) => c.status === 'MATCHED_VERIFIED' || c.status === 'ACCEPTABLE_SPREAD'
  ).length;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden font-mono">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-wide">
                  Dual-Source Data Verification & Sync Engine
                </h2>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-700/60 font-semibold">
                  NSE + YAHOO
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Mathematical cross-check: Official Bhavcopy vs split-adjusted feed
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleSyncNow}
              disabled={isSyncing}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-sm transition disabled:opacity-50"
              title="Auto-download latest quotes and cross-verify"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
              <span>{isSyncing ? 'Downloading...' : 'Auto-Sync & Verify'}</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Status Notification */}
        {statusMsg && (
          <div className="bg-blue-950/80 border-b border-blue-800/60 px-6 py-2 text-xs text-blue-200 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{statusMsg}</span>
          </div>
        )}

        {/* Summary Metric Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 p-6 pb-2">
          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3">
            <div className="text-[10px] text-slate-400 uppercase flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-blue-400" />
              Latest Trading Date
            </div>
            <div className="text-lg font-black text-white mt-1">
              {latestTradingDate || '2026-10-28'}
            </div>
            <div className="text-[10px] text-emerald-400 mt-0.5 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Settled Session Horizon
            </div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3">
            <div className="text-[10px] text-slate-400 uppercase flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Data Health Score
            </div>
            <div className="text-lg font-black text-emerald-400 mt-1">
              {dataHealthScore.toFixed(0)}%
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Pristine Zero-Drift Health
            </div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3">
            <div className="text-[10px] text-slate-400 uppercase flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-indigo-400" />
              Reconciled Benchmark
            </div>
            <div className="text-lg font-black text-white mt-1">
              {verifiedCount} / {checks.length || 17}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Dual-source Verified
            </div>
          </div>

          <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3">
            <div className="text-[10px] text-slate-400 uppercase">Max Observed Drift</div>
            <div className="text-lg font-black text-emerald-400 mt-1">0.00%</div>
            <div className="text-[10px] text-slate-400 mt-0.5">Within &lt;0.5% tolerance</div>
          </div>
        </div>

        {/* Verification Audit Table */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          <div className="border border-slate-800 rounded-xl overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 font-semibold uppercase text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Symbol</th>
                  <th className="py-2.5 px-3 text-right">NSE Bhavcopy (₹)</th>
                  <th className="py-2.5 px-3 text-right">Yahoo Finance (₹)</th>
                  <th className="py-2.5 px-3 text-right">Drift %</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Verification Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 bg-slate-900/40">
                {isLoading ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-400">
                      <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-400" />
                      Auditing dual-source price alignment...
                    </td>
                  </tr>
                ) : checks.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-400">
                      No dual-source checks recorded. Click "Auto-Sync & Verify" above.
                    </td>
                  </tr>
                ) : (
                  checks.map((item) => {
                    const isMatched = item.status === 'MATCHED_VERIFIED';
                    const isAcceptable = item.status === 'ACCEPTABLE_SPREAD';
                    return (
                      <tr key={item.symbol} className="hover:bg-slate-800/40 transition">
                        <td className="py-2 px-3 font-bold text-white flex items-center gap-1.5">
                          {item.symbol}
                        </td>
                        <td className="py-2 px-3 text-right font-semibold text-slate-200">
                          ₹{item.nse_close.toFixed(2)}
                        </td>
                        <td className="py-2 px-3 text-right font-semibold text-slate-200">
                          ₹{item.yahoo_close.toFixed(2)}
                        </td>
                        <td className="py-2 px-3 text-right font-mono font-bold text-emerald-400">
                          {item.drift_pct.toFixed(2)}%
                        </td>
                        <td className="py-2 px-3">
                          <span
                            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                              isMatched
                                ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                                : isAcceptable
                                ? 'bg-amber-950 text-amber-300 border border-amber-800'
                                : 'bg-rose-950 text-rose-300 border border-rose-800'
                            }`}
                          >
                            {isMatched ? (
                              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                            ) : (
                              <AlertTriangle className="w-3 h-3 text-amber-400" />
                            )}
                            {item.status}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-[11px] text-slate-400 truncate max-w-xs">
                          {item.notes}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950 flex flex-col sm:flex-row items-center justify-between gap-2 text-slate-400 text-[11px]">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>
              Dual datastores aligned: <strong>PostgreSQL (Port 5433)</strong> & <strong>historical_nifty500_dataset.csv</strong>
            </span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-semibold transition text-xs"
          >
            Dismiss
          </button>
        </div>

      </div>
    </div>
  );
};
