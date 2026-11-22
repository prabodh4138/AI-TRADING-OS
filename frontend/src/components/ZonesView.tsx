import React, { useState } from 'react';
import {
  Target,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  Search,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Layers,
  ArrowRight,
  CheckCircle2,
  Calendar,
} from 'lucide-react';
import { ZoneCandidate, ZoneScanResponse } from '../types/api';

interface ZonesViewProps {
  scanData: ZoneScanResponse | null;
  isLoading: boolean;
  onSelectCandidate: (candidate: ZoneCandidate) => void;
  onInspectScorecard: (candidate: ZoneCandidate) => void;
  onExecuteTrade: (candidate: ZoneCandidate) => void;
  onInspectChart: (symbol: string) => void;
  onInspectThesis: (symbol: string) => void;
}

export const ZonesView: React.FC<ZonesViewProps> = ({
  scanData,
  isLoading,
  onInspectScorecard,
  onExecuteTrade,
  onInspectChart,
  onInspectThesis,
}) => {
  const [activeSubTab, setActiveSubTab] = useState<'actionable' | 'watchlist' | 'aligned' | 'traps'>('actionable');
  const [searchQuery, setSearchQuery] = useState('');

  if (isLoading && !scanData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] text-slate-400 font-mono space-y-3">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <div className="text-sm">Scanning institutional demand zones across universe...</div>
      </div>
    );
  }

  const getActiveList = (): ZoneCandidate[] => {
    if (!scanData) return [];
    switch (activeSubTab) {
      case 'actionable':
        return scanData.actionable_candidates;
      case 'watchlist':
        return scanData.watchlist_candidates;
      case 'aligned':
        return scanData.best_aligned_candidates;
      case 'traps':
        return scanData.avoid_trap_candidates;
      default:
        return scanData.actionable_candidates;
    }
  };

  const list = getActiveList();
  const filteredList = list.filter((c) =>
    c.symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      
      {/* Metric Stat Cards */}
      {scanData && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3.5">
            <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Universe Scanned</div>
            <div className="text-2xl font-bold font-mono text-white mt-1">
              {scanData.total_symbols_scanned.toLocaleString()}
            </div>
            <div className="text-[10px] font-mono text-slate-500 mt-0.5">Equities in Local Cache</div>
          </div>

          <div className="bg-emerald-950/20 border border-emerald-800/40 rounded-xl p-3.5">
            <div className="text-[11px] font-mono text-emerald-400 uppercase tracking-wider">Actionable (At Demand)</div>
            <div className="text-2xl font-bold font-mono text-emerald-300 mt-1">
              {scanData.at_demand_count}
            </div>
            <div className="text-[10px] font-mono text-emerald-500/80 mt-0.5">Ready for Entry Model</div>
          </div>

          <div className="bg-blue-950/20 border border-blue-800/40 rounded-xl p-3.5">
            <div className="text-[11px] font-mono text-blue-400 uppercase tracking-wider">Priority Watchlist</div>
            <div className="text-2xl font-bold font-mono text-blue-300 mt-1">
              {scanData.approaching_demand_count}
            </div>
            <div className="text-[10px] font-mono text-blue-500/80 mt-0.5">Within 3% of Proximal</div>
          </div>

          <div className="bg-indigo-950/20 border border-indigo-800/40 rounded-xl p-3.5">
            <div className="text-[11px] font-mono text-indigo-400 uppercase tracking-wider">Total Demand Zones</div>
            <div className="text-2xl font-bold font-mono text-indigo-300 mt-1">
              {scanData.total_demand_zones_found}
            </div>
            <div className="text-[10px] font-mono text-indigo-400/80 mt-0.5">Identified Institutional Footprints</div>
          </div>

          <div className="bg-purple-950/20 border border-purple-800/40 rounded-xl p-3.5 col-span-2 md:col-span-1">
            <div className="text-[11px] font-mono text-purple-400 uppercase tracking-wider">Fresh Unbreached</div>
            <div className="text-2xl font-bold font-mono text-purple-300 mt-1">
              {scanData.fresh_demand_zones_count}
            </div>
            <div className="text-[10px] font-mono text-purple-400/80 mt-0.5">0 or 1 Prior Touch</div>
          </div>
        </div>
      )}

      {/* Filter and Sub-Tabs */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 bg-slate-900/40 p-2.5 rounded-xl border border-slate-800">
        
        {/* Sub-Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto scrollbar-none">
          <button
            onClick={() => setActiveSubTab('actionable')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition whitespace-nowrap flex items-center gap-1.5 ${
              activeSubTab === 'actionable'
                ? 'bg-emerald-600 text-white font-semibold shadow-md shadow-emerald-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Actionable Setups ({scanData?.actionable_candidates.length ?? 0})</span>
          </button>

          <button
            onClick={() => setActiveSubTab('watchlist')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition whitespace-nowrap flex items-center gap-1.5 ${
              activeSubTab === 'watchlist'
                ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <Target className="w-3.5 h-3.5" />
            <span>Priority Watchlist ({scanData?.watchlist_candidates.length ?? 0})</span>
          </button>

          <button
            onClick={() => setActiveSubTab('aligned')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition whitespace-nowrap flex items-center gap-1.5 ${
              activeSubTab === 'aligned'
                ? 'bg-indigo-600 text-white font-semibold shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Best Aligned A+ ({scanData?.best_aligned_candidates.length ?? 0})</span>
          </button>

          <button
            onClick={() => setActiveSubTab('traps')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition whitespace-nowrap flex items-center gap-1.5 ${
              activeSubTab === 'traps'
                ? 'bg-rose-600 text-white font-semibold shadow-md shadow-rose-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Avoid / Traps ({scanData?.avoid_trap_candidates.length ?? 0})</span>
          </button>
        </div>

        {/* Search Input */}
        <div className="relative min-w-[240px]">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Filter by symbol (e.g. RELIANCE)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-700/80 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-blue-500 placeholder:text-slate-600"
          />
        </div>

      </div>

      {/* Main Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Symbol</th>
                <th className="py-3 px-3">Structure</th>
                <th className="py-3 px-3 text-center text-indigo-400 font-bold bg-indigo-950/30 border-x border-indigo-900/40">
                  <div className="flex items-center justify-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Formation Date</span>
                  </div>
                </th>
                <th className="py-3 px-3 text-right">CMP (₹)</th>
                <th className="py-3 px-3 text-right">Proximal (Entry)</th>
                <th className="py-3 px-3 text-right">Distal (Base)</th>
                <th className="py-3 px-3 text-right">Target</th>
                <th className="py-3 px-3 text-center">R:R</th>
                <th className="py-3 px-3">Freshness & Test Audit</th>
                <th className="py-3 px-3 text-center">Curve %</th>
                <th className="py-3 px-3 text-center">Score</th>
                <th className="py-3 px-4 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filteredList.length === 0 ? (
                <tr>
                  <td colSpan={12} className="py-12 text-center text-slate-500 font-mono">
                    No candidates found for this criteria in the current dataset.
                  </td>
                </tr>
              ) : (
                filteredList.map((cand) => {
                  const isActionable = cand.is_actionable;
                  const isTested = cand.touch_count > 0;
                  const fDate = cand.formation_date ? cand.formation_date.split(' ')[0] : 'N/A';
                  return (
                    <tr
                      key={cand.symbol}
                      className="hover:bg-slate-800/40 transition group cursor-pointer"
                      onClick={() => onInspectScorecard(cand)}
                    >
                      {/* Symbol & State */}
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white group-hover:text-blue-400 transition">
                            {cand.symbol}
                          </span>
                          {isActionable && (
                            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                          )}
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                          {cand.location_state}
                        </div>
                      </td>

                      {/* Pattern Structure */}
                      <td className="py-3 px-3">
                        <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[11px]">
                          {cand.zone_type}
                        </span>
                      </td>

                      {/* Formation Date - Dedicated Highlighted Column */}
                      <td className="py-3 px-3 text-center bg-indigo-950/15 border-x border-indigo-900/30">
                        <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-700/60 font-bold font-mono text-xs shadow-sm">
                          <Calendar className="w-3 h-3 text-indigo-400" />
                          <span>{fDate}</span>
                        </div>
                      </td>

                      {/* CMP */}
                      <td className="py-3 px-3 text-right font-bold text-slate-100">
                        ₹{cand.current_price.toFixed(2)}
                      </td>

                      {/* Proximal Line */}
                      <td className="py-3 px-3 text-right font-semibold text-emerald-400">
                        ₹{cand.proximal_line.toFixed(2)}
                      </td>

                      {/* Distal Line */}
                      <td className="py-3 px-3 text-right text-rose-300">
                        ₹{cand.distal_line.toFixed(2)}
                      </td>

                      {/* Target Supply */}
                      <td className="py-3 px-3 text-right text-blue-300">
                        ₹{cand.target_supply.toFixed(2)}
                      </td>

                      {/* R:R Ratio */}
                      <td className="py-3 px-3 text-center">
                        <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                          cand.reward_to_risk >= 3.0
                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                            : cand.reward_to_risk >= 2.0
                            ? 'bg-blue-950 text-blue-300 border border-blue-800'
                            : 'bg-amber-950 text-amber-300 border border-amber-800'
                        }`}>
                          {cand.reward_to_risk.toFixed(1)}:1
                        </span>
                      </td>

                      {/* Freshness & Tested Dates */}
                      <td className="py-3 px-3">
                        <div className="flex items-center gap-1.5">
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                            !isTested
                              ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                              : cand.touch_count === 1
                              ? 'bg-blue-950 text-blue-300 border border-blue-800'
                              : 'bg-amber-950 text-amber-300 border border-amber-800'
                          }`}>
                            {cand.freshness}
                          </span>
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                          {!isTested ? 'Unbreached' : `Tested: ${cand.last_tested_date}`}
                        </div>
                      </td>

                      {/* Curve % */}
                      <td className="py-3 px-3 text-center">
                        <div className="text-[11px] font-semibold text-slate-300">
                          {cand.curve_location_pct.toFixed(0)}%
                        </div>
                        <div className="text-[9px] text-slate-500 uppercase">
                          {cand.curve_state}
                        </div>
                      </td>

                      {/* Score */}
                      <td className="py-3 px-3 text-center">
                        <div className={`inline-block px-2 py-0.5 rounded font-black text-xs ${
                          cand.institutional_score_100 >= 80
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                            : cand.institutional_score_100 >= 65
                            ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40'
                            : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                        }`}>
                          {cand.institutional_score_100.toFixed(0)}
                        </div>
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 text-center" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-center gap-1.5">
                          <button
                            onClick={() => onExecuteTrade(cand)}
                            className="px-2.5 py-1 rounded bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-semibold transition shadow-sm"
                            title="Execute 1-click paper trading order"
                          >
                            Execute
                          </button>
                          <button
                            onClick={() => onInspectChart(cand.symbol)}
                            className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
                            title="Open in Chart Studio"
                          >
                            <ExternalLink className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => onInspectThesis(cand.symbol)}
                            className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-purple-300 hover:text-white transition"
                            title="View 360° Stock Intelligence"
                          >
                            <Layers className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};
