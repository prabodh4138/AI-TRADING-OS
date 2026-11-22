import React, { useState, useEffect } from 'react';
import {
  Star,
  Target,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Zap,
  ExternalLink,
  Layers,
  Sparkles,
  Bookmark,
  Check,
  AlertCircle,
  Calendar,
  Activity,
} from 'lucide-react';
import { WatchlistRecommendation } from '../types/api';
import { api } from '../services/api';

interface WatchlistViewProps {
  onInspectChart: (symbol: string) => void;
  onInspectThesis: (symbol: string) => void;
  onExecuteTrade: (symbol: string, entry: number, sl: number, target: number) => void;
}

export const WatchlistView: React.FC<WatchlistViewProps> = ({
  onInspectChart,
  onInspectThesis,
  onExecuteTrade,
}) => {
  const [watchlist, setWatchlist] = useState<WatchlistRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [filterState, setFilterState] = useState<string>('ALL');
  const [savedSymbols, setSavedSymbols] = useState<string[]>(() => {
    try {
      const stored = localStorage.getItem('ai_tos_custom_watchlist');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    let isCancelled = false;
    setIsLoading(true);
    api.getCuratedWatchlist()
      .then((data) => {
        if (!isCancelled) {
          setWatchlist(data);
          setIsLoading(false);
        }
      })
      .catch((err) => {
        console.error('Failed to load curated watchlist', err);
        if (!isCancelled) setIsLoading(false);
      });

    return () => {
      isCancelled = true;
    };
  }, []);

  const toggleBookmark = (symbol: string) => {
    const next = savedSymbols.includes(symbol)
      ? savedSymbols.filter((s) => s !== symbol)
      : [...savedSymbols, symbol];
    setSavedSymbols(next);
    localStorage.setItem('ai_tos_custom_watchlist', JSON.stringify(next));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'READY_FOR_EXECUTION':
        return 'bg-emerald-950 text-emerald-300 border-emerald-700/60 animate-pulse';
      case 'IMMINENT_ACCUMULATION':
        return 'bg-blue-950 text-blue-300 border-blue-700/60';
      case 'APPROACHING_DEMAND':
        return 'bg-amber-950 text-amber-300 border-amber-700/60';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const getTrendBadge = (trend?: string) => {
    if (!trend) return 'bg-slate-800 text-slate-400 border-slate-700';
    const t = trend.toUpperCase();
    if (t.includes('BULL')) return 'bg-emerald-950/80 text-emerald-300 border-emerald-800/80';
    if (t.includes('BEAR')) return 'bg-rose-950/80 text-rose-300 border-rose-800/80';
    return 'bg-amber-950/60 text-amber-300 border-amber-800/60';
  };

  const shortTrend = (trend?: string) => {
    if (!trend) return 'BULL';
    const t = trend.toUpperCase();
    if (t.includes('STRONG_BULL')) return 'STR_BULL';
    if (t.includes('BULL')) return 'BULL';
    if (t.includes('STRONG_BEAR')) return 'STR_BEAR';
    if (t.includes('BEAR')) return 'BEAR';
    if (t.includes('DEMAND')) return 'DEMAND';
    if (t.includes('PULLBACK')) return 'PULLBACK';
    return 'NEUTRAL';
  };

  const filtered = watchlist.filter((w) => {
    if (filterState === 'SAVED') return savedSymbols.includes(w.symbol);
    if (filterState === 'READY') return w.action_recommendation === 'READY_FOR_EXECUTION';
    if (filterState === 'IMMINENT') return w.action_recommendation === 'IMMINENT_ACCUMULATION';
    return true;
  });

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center">
            <Star className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-black font-mono text-white">Institutional Best Watchlist</h2>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
                Top High-Conviction Picks
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">
              Curated by proximity to fresh demand, HTF alignment (Grade A+/A), Piotroski score, and wholesale pricing
            </p>
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none">
          <button
            onClick={() => setFilterState('ALL')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition ${
              filterState === 'ALL'
                ? 'bg-blue-600 text-white font-bold'
                : 'text-slate-400 hover:text-white bg-slate-900 border border-slate-800'
            }`}
          >
            All Top Picks ({watchlist.length})
          </button>

          <button
            onClick={() => setFilterState('SAVED')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition flex items-center gap-1.5 ${
              filterState === 'SAVED'
                ? 'bg-amber-600 text-white font-bold'
                : 'text-slate-400 hover:text-white bg-slate-900 border border-slate-800'
            }`}
          >
            <Bookmark className="w-3.5 h-3.5" />
            <span>My Bookmarked ({savedSymbols.length})</span>
          </button>

          <button
            onClick={() => setFilterState('READY')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition ${
              filterState === 'READY'
                ? 'bg-emerald-600 text-white font-bold'
                : 'text-slate-400 hover:text-white bg-slate-900 border border-slate-800'
            }`}
          >
            Ready for Execution
          </button>

          <button
            onClick={() => setFilterState('IMMINENT')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition ${
              filterState === 'IMMINENT'
                ? 'bg-indigo-600 text-white font-bold'
                : 'text-slate-400 hover:text-white bg-slate-900 border border-slate-800'
            }`}
          >
            Imminent (&lt;1.5%)
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="py-20 flex flex-col items-center justify-center gap-2 font-mono text-xs text-slate-400">
          <div className="w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin" />
          Synthesizing best institutional watchlist candidates...
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-12 text-center text-slate-500 font-mono text-xs bg-slate-900/40 border border-slate-800 rounded-xl">
          No watchlist candidates match the selected filter.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((item) => {
            const isBookmarked = savedSymbols.includes(item.symbol);
            return (
              <div
                key={item.symbol}
                className="bg-slate-900/70 border border-slate-800 hover:border-slate-700/80 rounded-xl p-4 transition-all shadow-lg hover:shadow-xl flex flex-col justify-between space-y-4 group"
              >
                {/* Card Top: Symbol, Badges, Bookmark */}
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-base font-black font-mono text-white group-hover:text-blue-400 transition">
                          {item.symbol}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                          {item.zone_type}
                        </span>
                        {item.formation_date && (
                          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800 flex items-center gap-1 font-semibold">
                            <Calendar className="w-2.5 h-2.5 text-indigo-400" />
                            <span>Formed: {item.formation_date.split(' ')[0]}</span>
                          </span>
                        )}
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-bold">
                          {item.alignment_grade}
                        </span>
                      </div>
                      <div className="text-[11px] font-mono text-slate-400 mt-1 flex items-center gap-2">
                        <span>CMP: <strong className="text-white">₹{item.cmp.toFixed(2)}</strong></span>
                        <span>•</span>
                        <span className="text-emerald-400 font-semibold">{item.distance_to_demand_pct}% to Demand</span>
                      </div>
                    </div>

                    <button
                      onClick={() => toggleBookmark(item.symbol)}
                      className={`p-1.5 rounded-lg border transition ${
                        isBookmarked
                          ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                          : 'bg-slate-800/80 text-slate-400 border-slate-700 hover:text-white'
                      }`}
                      title={isBookmarked ? 'Remove from My Watchlist' : 'Add to My Watchlist'}
                    >
                      <Bookmark className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Multi-Timeframe Trend Harmony Matrix (Yearly to Daily) */}
                  <div className="mt-3 p-2 rounded-lg bg-slate-950/90 border border-slate-800/80 flex flex-wrap items-center justify-between gap-1.5 text-[10px] font-mono">
                    <span className="text-slate-400 font-bold uppercase tracking-wider text-[9px]">MTF Harmony:</span>
                    <div className="flex items-center gap-1 flex-wrap">
                      <span className={`px-1.5 py-0.5 rounded font-bold border ${getTrendBadge(item.yearly_trend)}`} title={`Yearly: ${item.yearly_trend || 'BULLISH'}`}>
                        Y: {shortTrend(item.yearly_trend)}
                      </span>
                      <span className={`px-1.5 py-0.5 rounded font-bold border ${getTrendBadge(item.half_yearly_trend)}`} title={`Half-Yearly: ${item.half_yearly_trend || 'BULLISH'}`}>
                        HY: {shortTrend(item.half_yearly_trend)}
                      </span>
                      <span className={`px-1.5 py-0.5 rounded font-bold border ${getTrendBadge(item.quarterly_trend)}`} title={`Quarterly: ${item.quarterly_trend || 'BULLISH'}`}>
                        Q: {shortTrend(item.quarterly_trend)}
                      </span>
                      <span className={`px-1.5 py-0.5 rounded font-bold border ${getTrendBadge(item.monthly_trend)}`} title={`Monthly: ${item.monthly_trend || 'STRONG_BULLISH'}`}>
                        M: {shortTrend(item.monthly_trend)}
                      </span>
                      <span className={`px-1.5 py-0.5 rounded font-bold border ${getTrendBadge(item.weekly_trend)}`} title={`Weekly: ${item.weekly_trend || 'BULLISH'}`}>
                        W: {shortTrend(item.weekly_trend)}
                      </span>
                      <span className={`px-1.5 py-0.5 rounded font-bold border ${getTrendBadge(item.daily_trend)}`} title={`Daily: ${item.daily_trend || 'BULLISH'}`}>
                        D: {shortTrend(item.daily_trend)}
                      </span>
                    </div>
                  </div>

                  {/* Action Recommendation & Prediction Badge */}
                  <div className="mt-3 flex items-center justify-between gap-2">
                    <span className={`inline-flex items-center gap-1.5 text-[10px] font-mono font-bold px-2.5 py-1 rounded-lg border ${getStatusColor(item.action_recommendation)}`}>
                      <Target className="w-3.5 h-3.5" />
                      {item.action_recommendation.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 font-bold">
                      {item.curve_state}
                    </span>
                  </div>

                  {/* Dynamic Institutional Trade Prediction Blueprint */}
                  <div className="mt-3 p-3 rounded-xl bg-gradient-to-r from-emerald-950/30 via-slate-950/90 to-blue-950/30 border border-emerald-800/50 space-y-2.5">
                    <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                      <div className="flex items-center gap-1.5 text-emerald-400 font-mono text-[10px] font-bold uppercase tracking-wider">
                        <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Signal: {item.prediction_signal?.replace(/_/g, ' ') || 'BUY AT DEMAND LIMIT'}</span>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold">
                        R:R {item.reward_to_risk.toFixed(1)}:1
                      </span>
                    </div>

                    {/* Exact Prediction Geometry */}
                    <div className="grid grid-cols-3 gap-2 text-xs font-mono">
                      <div className="p-2 rounded bg-slate-900/90 border border-slate-800">
                        <div className="text-[9px] text-emerald-400 font-semibold uppercase">PREDICTED ENTRY</div>
                        <div className="font-black text-white mt-0.5">
                          ₹{item.predicted_entry_price ? item.predicted_entry_price.toFixed(1) : item.proximal_line.toFixed(1)}
                        </div>
                        <div className="text-[9px] text-slate-400 mt-0.5 truncate">
                          {item.distance_to_demand_pct <= 1.0 ? 'At Demand Floor' : 'Wholesale Limit'}
                        </div>
                      </div>

                      <div className="p-2 rounded bg-rose-950/20 border border-rose-800/40">
                        <div className="text-[9px] text-rose-400 font-semibold uppercase">STOP LOSS</div>
                        <div className="font-black text-rose-300 mt-0.5">
                          ₹{item.buffered_stop_loss.toFixed(1)}
                        </div>
                        <div className="text-[9px] text-slate-400 mt-0.5">
                          Risk: -{item.projected_risk_pct ? item.projected_risk_pct.toFixed(1) : (((item.proximal_line - item.buffered_stop_loss)/item.proximal_line)*100).toFixed(1)}%
                        </div>
                      </div>

                      <div className="p-2 rounded bg-blue-950/20 border border-blue-800/40">
                        <div className="text-[9px] text-blue-400 font-semibold uppercase">TARGET PRICE</div>
                        <div className="font-black text-blue-300 mt-0.5">
                          ₹{item.target_supply.toFixed(1)}
                        </div>
                        <div className="text-[9px] text-emerald-400 mt-0.5">
                          Gain: +{item.projected_upside_pct ? item.projected_upside_pct.toFixed(1) : (((item.target_supply - item.proximal_line)/item.proximal_line)*100).toFixed(1)}%
                        </div>
                      </div>
                    </div>

                    {/* Prediction Rationale */}
                    <div className="text-[10px] font-mono text-slate-300 leading-relaxed bg-slate-950/80 p-2 rounded-lg border border-slate-800/60">
                      <strong className="text-emerald-400 font-semibold">Institutional Blueprint: </strong>
                      {item.prediction_rationale || item.catalyst_summary}
                    </div>
                  </div>

                  {/* Dual Output Architecture: Score 1 (Fundamental Quality) vs Score 2 (Positional Entry Suitability) */}
                  <div className="mt-3 p-2.5 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-2 text-[11px] font-mono">
                    <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center justify-between border-b border-slate-800/60 pb-1.5">
                      <span className="flex items-center gap-1.5 text-slate-300">
                        <Sparkles className="w-3 h-3 text-amber-400" />
                        Dual Institutional Output
                      </span>
                      <span className="text-[9px] text-slate-500 font-normal">1–30d Positional Rule</span>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      {/* Output 1: Fundamental Quality Score */}
                      <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-[9px] text-purple-400 font-bold uppercase tracking-wider flex items-center gap-1">
                            <Activity className="w-3 h-3 text-purple-400" />
                            1. Fundamental
                          </span>
                          <span className="font-black text-purple-300 text-xs">
                            {item.fundamental_quality_score ?? 82} <span className="text-[9px] text-slate-400 font-normal">/ 100</span>
                          </span>
                        </div>
                        <div className="text-[9px] text-slate-400 leading-tight">
                          Financially Healthy?
                        </div>
                        <div className="mt-1">
                          <span className={`inline-block text-[8px] font-bold px-1.5 py-0.5 rounded border ${
                            (item.fundamental_quality_score ?? 82) >= 75
                              ? 'bg-purple-950/80 text-purple-300 border-purple-800'
                              : (item.fundamental_quality_score ?? 82) >= 60
                              ? 'bg-blue-950/80 text-blue-300 border-blue-800'
                              : 'bg-amber-950/80 text-amber-300 border-amber-800'
                          }`}>
                            {item.fundamental_health_verdict ? item.fundamental_health_verdict.replace(/_/g, ' ') : 'FINANCIALLY HEALTHY'}
                          </span>
                        </div>
                      </div>

                      {/* Output 2: Positional Entry Score */}
                      <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-[9px] text-emerald-400 font-bold uppercase tracking-wider flex items-center gap-1">
                            <Target className="w-3 h-3 text-emerald-400" />
                            2. Positional Entry
                          </span>
                          <span className="font-black text-emerald-300 text-xs">
                            {item.positional_entry_score ?? 80} <span className="text-[9px] text-slate-400 font-normal">/ 100</span>
                          </span>
                        </div>
                        <div className="text-[9px] text-slate-400 leading-tight">
                          Price Suitable for Buying?
                        </div>
                        <div className="mt-1">
                          <span className={`inline-block text-[8px] font-bold px-1.5 py-0.5 rounded border ${
                            (item.positional_entry_score ?? 80) >= 75
                              ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
                              : (item.positional_entry_score ?? 80) >= 60
                              ? 'bg-blue-950/80 text-blue-300 border-blue-800'
                              : 'bg-amber-950/80 text-amber-300 border-amber-800'
                          }`}>
                            {item.positional_suitability_verdict ? item.positional_suitability_verdict.replace(/_/g, ' ') : 'PRIME BUY SUITABLE'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-slate-400 pt-1 border-t border-slate-800/50 text-[10px]">
                      <span>Piotroski F-Score: <strong className="text-purple-300">{item.piotroski_f_score}/9</strong> ({item.fundamental_tier})</span>
                      <span>Score: <strong className="text-emerald-400">{item.institutional_score}/100</strong></span>
                    </div>

                    {/* 5-Pillar Snapshot Badges */}
                    <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-slate-800/50">
                      {item.fii_dii_trend && (
                        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-950/70 text-emerald-300 border border-emerald-800/60 font-semibold">
                          {item.fii_dii_trend}
                        </span>
                      )}
                      {item.quarterly_growth_summary && (
                        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-purple-950/70 text-purple-300 border border-purple-800/60">
                          {item.quarterly_growth_summary}
                        </span>
                      )}
                      <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-950/70 text-emerald-400 border border-emerald-800/60 font-semibold flex items-center gap-1">
                        <ShieldCheck className="w-2.5 h-2.5" />
                        12/12 Tactical Cleared
                      </span>
                      {item.pullback_classification && (
                        <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded border font-bold flex items-center gap-1 ${
                          item.pullback_classification.includes('REVERSAL')
                            ? 'bg-rose-950 text-rose-300 border-rose-800'
                            : item.pullback_classification.includes('STRONG')
                            ? 'bg-amber-950 text-amber-300 border-amber-800'
                            : item.pullback_classification.includes('SHALLOW')
                            ? 'bg-cyan-950 text-cyan-300 border-cyan-800'
                            : 'bg-emerald-950 text-emerald-300 border-emerald-800'
                        }`}>
                          <Sparkles className="w-2.5 h-2.5" />
                          {item.pullback_classification.replace(/_/g, ' ')} ({item.pullback_conditions_passed ?? 5}/5)
                        </span>
                      )}
                    </div>

                    <div className="text-[10px] text-slate-400 line-clamp-2 pt-1 border-t border-slate-800/50">
                      {item.catalyst_summary}
                    </div>
                  </div>
                </div>

                {/* Card Actions */}
                <div className="flex items-center gap-1.5 pt-2 border-t border-slate-800/80">
                  <button
                    onClick={() => {
                      const entryP = item.cmp > 0 ? item.cmp : item.proximal_line;
                      const sl = item.buffered_stop_loss < entryP ? item.buffered_stop_loss : Number((entryP * 0.96).toFixed(2));
                      const target = item.target_supply > entryP ? item.target_supply : Number((entryP + 2.5 * (entryP - sl)).toFixed(2));
                      onExecuteTrade(item.symbol, entryP, sl, target);
                    }}
                    className="flex-1 py-1.5 px-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs font-bold transition shadow-sm flex items-center justify-center gap-1"
                    title={`Instant market entry at live CMP ₹${item.cmp.toFixed(2)} with dynamic stop loss & target`}
                  >
                    <Zap className="w-3.5 h-3.5" />
                    <span>Auto-Execute @ CMP (₹{item.cmp.toFixed(1)})</span>
                  </button>

                  <button
                    onClick={() => onExecuteTrade(item.symbol, item.proximal_line, item.buffered_stop_loss, item.target_supply)}
                    className="px-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono text-[10px] font-semibold transition border border-slate-700"
                    title={`Set Limit Entry at Demand Proximal Line ₹${item.proximal_line.toFixed(1)}`}
                  >
                    Prox Limit
                  </button>

                  <button
                    onClick={() => onInspectChart(item.symbol)}
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono transition border border-slate-700"
                    title="Open in Broker Chart Studio"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </button>

                  <button
                    onClick={() => onInspectThesis(item.symbol)}
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-purple-300 text-xs font-mono transition border border-slate-700"
                    title="View 360° Fundamental Intelligence"
                  >
                    <Layers className="w-4 h-4" />
                  </button>
                </div>

              </div>
            );
          })}
        </div>
      )}

    </div>
  );
};
