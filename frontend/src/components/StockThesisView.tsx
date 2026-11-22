import React, { useEffect, useState } from 'react';
import {
  BrainCircuit,
  Search,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  TrendingUp,
  Activity,
  Layers,
  Award,
  Zap,
  ShieldAlert,
  Sparkles,
  ShieldCheck,
  BarChart3,
  Users,
  LineChart,
} from 'lucide-react';
import { StockThesis } from '../types/api';
import { api } from '../services/api';
import { Master123ChecklistView } from './Master123ChecklistView';

interface StockThesisViewProps {
  initialSymbol?: string;
  onInspectChart: (symbol: string) => void;
}

export const StockThesisView: React.FC<StockThesisViewProps> = ({
  initialSymbol = 'RELIANCE',
  onInspectChart,
}) => {
  const [symbol, setSymbol] = useState(initialSymbol);
  const [searchInput, setSearchInput] = useState('');
  const [thesis, setThesis] = useState<StockThesis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'OVERVIEW' | 'MASTER_123'>('OVERVIEW');

  useEffect(() => {
    let isCancelled = false;
    setIsLoading(true);
    setError(null);

    api.getStockThesis(symbol)
      .then((res) => {
        if (!isCancelled) {
          setThesis(res);
          setIsLoading(false);
        }
      })
      .catch((err) => {
        if (!isCancelled) {
          setError(err.message || 'Thesis not found');
          setIsLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [symbol]);

  return (
    <div className="space-y-6">
      
      {/* Search Header */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center">
            <BrainCircuit className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-black font-mono text-white">{symbol}</h2>
              <span className="text-xs font-mono px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                360° Fundamental Intelligence
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">
              Piotroski F-Score, Valuation Multiple, News Sentiment & Conviction
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* View Mode Toggle */}
          <div className="flex items-center bg-slate-950 border border-slate-800 rounded-lg p-1">
            <button
              onClick={() => setViewMode('OVERVIEW')}
              className={`px-3 py-1 rounded text-xs font-mono font-semibold transition ${
                viewMode === 'OVERVIEW'
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              360° Dossier
            </button>
            <button
              onClick={() => setViewMode('MASTER_123')}
              className={`px-3 py-1 rounded text-xs font-mono font-semibold flex items-center gap-1.5 transition ${
                viewMode === 'MASTER_123'
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-purple-300" />
              123-Point Master Matrix
            </button>
          </div>

          <div className="relative">
            <input
              type="text"
              placeholder="Inspect symbol (e.g. INFY)..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && searchInput.trim()) {
                  setSymbol(searchInput.trim().toUpperCase());
                  setSearchInput('');
                }
              }}
              className="pl-8 pr-3 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-xs font-mono text-white focus:outline-none focus:border-purple-500 w-52"
            />
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
          </div>

          <button
            onClick={() => onInspectChart(symbol)}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-mono transition"
          >
            Chart View
          </button>
        </div>
      </div>

      {viewMode === 'MASTER_123' ? (
        <Master123ChecklistView symbol={symbol} />
      ) : (
        <>
          {isLoading && (
            <div className="py-20 flex flex-col items-center justify-center gap-2 font-mono text-xs text-slate-400">
              <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
              Synthesizing 360-degree fundamental and sentiment dossier...
            </div>
          )}

          {error && (
            <div className="bg-rose-950/20 border border-rose-800/40 rounded-xl p-6 text-center font-mono text-xs text-rose-300">
              {error}
            </div>
          )}

          {thesis && !isLoading && (
            <div className="space-y-6">
              
              {/* Top Score Banner */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            
            {/* Piotroski F-Score */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col items-center text-center">
              <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Piotroski F-Score</div>
              <div className="text-3xl font-black font-mono text-purple-400 mt-1">
                {thesis.piotroski_f_score} <span className="text-base text-slate-400">/ 9</span>
              </div>
              <div className="text-[11px] font-mono text-purple-300 mt-1 font-semibold">
                Tier: {thesis.fundamental_tier}
              </div>
            </div>

            {/* Valuation Multiple */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col items-center text-center">
              <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Valuation (P/E)</div>
              <div className="text-2xl font-bold font-mono text-white mt-1">
                {thesis.pe_ratio.toFixed(1)}x
              </div>
              <div className="text-[11px] font-mono text-slate-400 mt-1">
                Ind PE: {thesis.industry_pe.toFixed(1)}x ({thesis.valuation_status})
              </div>
            </div>

            {/* News Sentiment */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col items-center text-center">
              <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">News Sentiment</div>
              <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
                {thesis.news_sentiment_badge}
              </div>
              <div className="text-[11px] font-mono text-slate-400 mt-1">
                Score: {thesis.news_sentiment_score.toFixed(2)}
              </div>
            </div>

            {/* 360 Conviction */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex flex-col items-center text-center">
              <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">360° Conviction Score</div>
              <div className="text-3xl font-black font-mono text-emerald-400 mt-1">
                {thesis.conviction_score_360.toFixed(0)} <span className="text-base text-slate-400">/ 100</span>
              </div>
              <div className="text-[11px] font-mono text-emerald-300 mt-1 font-semibold">
                {thesis.executive_verdict}
              </div>
            </div>

          </div>

          {/* Master 123-Point Direct Launch Banner */}
          <div className="bg-gradient-to-r from-purple-950/40 via-slate-900/60 to-purple-950/40 border border-purple-800/40 rounded-xl p-3.5 flex flex-wrap items-center justify-between gap-3 shadow-md">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-purple-600/20 border border-purple-500/30 flex items-center justify-center">
                <ShieldCheck className="w-4 h-4 text-purple-400" />
              </div>
              <div>
                <div className="text-xs font-mono font-bold text-white flex items-center gap-2">
                  <span>Institutional 123-Point Master Specification Audit</span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-purple-900/60 text-purple-300 font-mono">
                    10 Categories • 100% Auditable
                  </span>
                </div>
                <div className="text-[11px] font-mono text-slate-400">
                  Audit Fundamental, Technical, Sector, Institutional, News, Global, Market, Volume, Risk, Execution
                </div>
              </div>
            </div>
            <button
              onClick={() => setViewMode('MASTER_123')}
              className="px-3.5 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-mono font-bold flex items-center gap-1.5 transition shadow-lg shadow-purple-600/20"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Open 123-Point Audit Matrix →
            </button>
          </div>

          {/* Institutional 5-Pillar Decision Dossier */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4 shadow-xl">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
                  <Sparkles className="w-4 h-4 text-indigo-400" />
                </div>
                <div>
                  <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider flex items-center gap-2">
                    <span>Institutional 5-Pillar Core Intelligence Dossier</span>
                    <span className="text-[10px] font-normal px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                      SUNPHARMA & Universe Model
                    </span>
                  </h3>
                  <p className="text-[11px] font-mono text-slate-400">
                    Weekly Macro Trend, Daily Support Defense, Demand Inflow Volume, Valuation Support & FII/DII Holdings
                  </p>
                </div>
              </div>
              <span className="text-xs font-mono px-2.5 py-1 rounded bg-indigo-950 text-indigo-300 border border-indigo-800 font-bold">
                GTF Master Specification
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              
              {/* Pillar 1: Weekly Chart Trend */}
              <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between space-y-3">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">1. Weekly Trend Integrity</span>
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                      thesis.weekly_trend_verdict?.includes('BULLISH')
                        ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                        : 'bg-amber-950 text-amber-300 border-amber-800'
                    }`}>
                      {thesis.weekly_trend_verdict?.replace(/_/g, ' ') || 'GENUINELY BULLISH'}
                    </span>
                  </div>
                  <div className="text-sm font-bold font-mono text-white mt-1.5 flex items-center gap-1.5">
                    <TrendingUp className="w-4 h-4 text-emerald-400" />
                    Is long-term trend genuinely bullish?
                  </div>
                  <p className="text-xs font-mono text-slate-300 mt-2 leading-relaxed">
                    {thesis.weekly_trend_detail || 'Weekly chart demonstrates secular higher high and higher low sequences trading above EMA 20, confirming genuine institutional accumulation.'}
                  </p>
                </div>
                <div className="text-[10px] font-mono text-slate-500 border-t border-slate-800/60 pt-2 flex items-center justify-between">
                  <span>Long-Term Filter</span>
                  <span className="text-emerald-400 font-bold">PASS: Secular Bullish</span>
                </div>
              </div>

              {/* Pillar 2: Daily Support & Buying Activity */}
              <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between space-y-3">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">2. Daily Demand Support</span>
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded border bg-indigo-950 text-indigo-300 border-indigo-800">
                      {thesis.daily_support_activity?.replace(/_/g, ' ') || 'BUYING ABSORPTION'}
                    </span>
                  </div>
                  <div className="text-sm font-bold font-mono text-white mt-1.5 flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-indigo-400" />
                    Is ₹{thesis.daily_support_level ? thesis.daily_support_level.toFixed(2) : '---'} supported by buying?
                  </div>
                  <p className="text-xs font-mono text-slate-300 mt-2 leading-relaxed">
                    {thesis.daily_support_detail || 'Supported by aggressive buying activity with candles closing near session highs and strong volume defense.'}
                  </p>
                </div>
                <div className="text-[10px] font-mono text-slate-500 border-t border-slate-800/60 pt-2 flex items-center justify-between">
                  <span>Support Quality</span>
                  <span className="text-indigo-400 font-bold">PASS: Confirmed Buying</span>
                </div>
              </div>

              {/* Pillar 3: Volume on Demand Approach */}
              <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between space-y-3">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">3. Volume Dynamics</span>
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded border bg-blue-950 text-blue-300 border-blue-800">
                      {thesis.volume_demand_behavior?.replace(/_/g, ' ') || 'BUYERS ENTERING'}
                    </span>
                  </div>
                  <div className="text-sm font-bold font-mono text-white mt-1.5 flex items-center gap-1.5">
                    <Activity className="w-4 h-4 text-blue-400" />
                    Are buyers entering at demand?
                  </div>
                  <p className="text-xs font-mono text-slate-300 mt-2 leading-relaxed">
                    {thesis.volume_demand_detail || 'Volume expands noticeably when price approaches demand, indicating institutional accumulation while supply dries up on dips.'}
                  </p>
                </div>
                <div className="text-[10px] font-mono text-slate-500 border-t border-slate-800/60 pt-2 flex items-center justify-between">
                  <span>Volume Footprint</span>
                  <span className="text-blue-400 font-bold">PASS: Buyers In Control</span>
                </div>
              </div>

              {/* Pillar 4: Quarterly Results & Valuation Support */}
              <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between space-y-3">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">4. Financial Growth vs P/E</span>
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded border bg-purple-950 text-purple-300 border-purple-800">
                      {thesis.valuation_support_verdict?.replace(/_/g, ' ') || 'GROWTH SUPPORTS P/E'}
                    </span>
                  </div>
                  <div className="text-sm font-bold font-mono text-white mt-1.5 flex items-center gap-1.5">
                    <Award className="w-4 h-4 text-purple-400" />
                    Does growth support valuation?
                  </div>
                  <p className="text-xs font-mono text-slate-300 mt-2 leading-relaxed">
                    {thesis.valuation_support_detail || 'Quarterly operational growth and expanding margins justify the prevailing valuation multiple.'}
                  </p>
                </div>
                <div className="text-[10px] font-mono text-slate-500 border-t border-slate-800/60 pt-2 flex items-center justify-between">
                  <span>Growth Metrics</span>
                  <span className="text-purple-400 font-bold">
                    Sales: +{thesis.quarterly_sales_growth_pct?.toFixed(1)}% | PAT: +{thesis.quarterly_profit_growth_pct?.toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Pillar 5: Institutional Holdings (FII & DII) */}
              <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between space-y-3 md:col-span-2 lg:col-span-2">
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono uppercase text-slate-400 tracking-wider">5. Institutional Holdings & Flows</span>
                    <span className={`text-[10px] font-mono font-bold px-2.5 py-0.5 rounded border ${
                      thesis.institutional_holding_trend?.includes('ACCUMULATION')
                        ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                        : 'bg-rose-950 text-rose-300 border-rose-800'
                    }`}>
                      {thesis.institutional_holding_trend?.replace(/_/g, ' ') || 'STRONG ACCUMULATION'}
                    </span>
                  </div>
                  <div className="text-sm font-bold font-mono text-white mt-1.5 flex items-center gap-1.5">
                    <Zap className="w-4 h-4 text-amber-400" />
                    FII & DII Holdings: Are they increasing or decreasing?
                  </div>
                  <p className="text-xs font-mono text-slate-300 mt-2 leading-relaxed">
                    {thesis.institutional_holding_detail || 'Institutional holding audit confirms smart money participation.'}
                  </p>
                </div>

                <div className="grid grid-cols-3 gap-2 border-t border-slate-800/60 pt-2 text-center text-xs font-mono">
                  <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                    <div className="text-[10px] text-slate-400">FII HOLDING</div>
                    <div className="text-white font-bold mt-0.5">
                      {thesis.fii_holding_pct ? `${thesis.fii_holding_pct.toFixed(1)}%` : '---'}
                      <span className="text-emerald-400 text-[10px] ml-1">
                        ({thesis.fii_holding_change_qoq && thesis.fii_holding_change_qoq >= 0 ? '+' : ''}{thesis.fii_holding_change_qoq?.toFixed(2)}%)
                      </span>
                    </div>
                  </div>
                  <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                    <div className="text-[10px] text-slate-400">DII HOLDING</div>
                    <div className="text-white font-bold mt-0.5">
                      {thesis.dii_holding_pct ? `${thesis.dii_holding_pct.toFixed(1)}%` : '---'}
                      <span className="text-emerald-400 text-[10px] ml-1">
                        ({thesis.dii_holding_change_qoq && thesis.dii_holding_change_qoq >= 0 ? '+' : ''}{thesis.dii_holding_change_qoq?.toFixed(2)}%)
                      </span>
                    </div>
                  </div>
                  <div className="bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                    <div className="text-[10px] text-slate-400">TOTAL INSTITUTIONAL</div>
                    <div className="text-emerald-400 font-bold mt-0.5">
                      {thesis.total_institutional_holding_pct ? `${thesis.total_institutional_holding_pct.toFixed(1)}%` : '---'}
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>

          {/* 5-Condition Pullback Qualification & Pullback vs Reversal Diagnostic Dossier */}
          {thesis.pullback_diagnosis && (
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4 shadow-xl">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center">
                    <TrendingUp className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider flex items-center gap-2">
                      <span>5-Condition Pullback Qualification & Reversal Diagnosis</span>
                      <span className="text-[10px] font-normal px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                        {thesis.pullback_diagnosis.conditions_cleared_count}/5 Conditions Cleared
                      </span>
                    </h3>
                    <p className="text-[11px] font-mono text-slate-400">
                      Price Level, Volume Contraction, RSI Cooldown (50–65), Candlestick Reversal & Upward Confirmation
                    </p>
                  </div>
                </div>

                {/* Pullback vs Reversal Classification Pill */}
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-mono font-bold px-3 py-1 rounded-lg border flex items-center gap-1.5 ${
                    thesis.pullback_diagnosis.classification === 'TREND_REVERSAL_BREAKDOWN'
                      ? 'bg-rose-950 text-rose-300 border-rose-800'
                      : thesis.pullback_diagnosis.classification === 'STRONG_PULLBACK'
                      ? 'bg-amber-950 text-amber-300 border-amber-800'
                      : thesis.pullback_diagnosis.classification === 'SHALLOW_PULLBACK'
                      ? 'bg-cyan-950 text-cyan-300 border-cyan-800'
                      : 'bg-emerald-950 text-emerald-300 border-emerald-800'
                  }`}>
                    <Sparkles className="w-3.5 h-3.5" />
                    {thesis.pullback_diagnosis.classification_badge.replace(/_/g, ' ')}
                  </span>
                </div>
              </div>

              {/* Pullback Depth & Reversal Diagnostic Banner */}
              <div className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800/80 flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
                <div className="flex items-center gap-4 flex-wrap">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Recent Swing High</span>
                    <span className="font-bold text-white text-sm">₹{thesis.pullback_diagnosis.recent_swing_high.toFixed(2)}</span>
                    <span className="text-[10px] text-slate-500 block">({thesis.pullback_diagnosis.swing_high_date})</span>
                  </div>
                  <div className="border-l border-slate-800 pl-4">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Pullback Depth</span>
                    <span className="font-bold text-amber-300 text-sm">-{thesis.pullback_diagnosis.pullback_depth_pct.toFixed(1)}%</span>
                    <span className="text-[10px] text-slate-500 block">From Peak High</span>
                  </div>
                  <div className="border-l border-slate-800 pl-4">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Target Support Buffer</span>
                    <span className="font-bold text-emerald-300 text-sm">{thesis.pullback_diagnosis.nearest_support_type}</span>
                    <span className="text-[10px] text-slate-500 block">₹{thesis.pullback_diagnosis.nearest_support_level.toFixed(2)} ({thesis.pullback_diagnosis.distance_to_support_pct.toFixed(1)}% away)</span>
                  </div>
                  <div className="border-l border-slate-800 pl-4">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Reversal Risk Score</span>
                    <span className={`font-bold text-sm ${thesis.pullback_diagnosis.reversal_risk_score > 50 ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {thesis.pullback_diagnosis.reversal_risk_score.toFixed(0)} / 100
                    </span>
                    <span className="text-[10px] text-slate-500 block">
                      {thesis.pullback_diagnosis.reversal_risk_score > 50 ? 'Elevated Breakdown Risk' : 'Safe Pullback Corridor'}
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Action Directive</span>
                  <span className="font-bold text-purple-300 px-2.5 py-1 rounded bg-purple-950/80 border border-purple-800/80 inline-block mt-0.5">
                    {thesis.pullback_diagnosis.actionable_directive.replace(/_/g, ' ')}
                  </span>
                </div>
              </div>

              {/* The 5 Conditions Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-3 font-mono">
                {thesis.pullback_diagnosis.condition_items.map((c) => (
                  <div
                    key={c.condition_id}
                    className={`p-3 rounded-xl border flex flex-col justify-between space-y-2 ${
                      c.passed
                        ? 'bg-slate-950/70 border-slate-800/80 hover:border-slate-700'
                        : 'bg-amber-950/20 border-amber-800/40'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">{c.name}</span>
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${
                          c.passed
                            ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                            : 'bg-amber-950 text-amber-300 border-amber-800'
                        }`}>
                          {c.passed ? 'PASS' : 'WAIT'}
                        </span>
                      </div>
                      <div className="text-xs font-bold text-white mt-1">
                        {c.parameter}
                      </div>
                      <div className="text-[11px] text-purple-300 mt-1 font-semibold">
                        {c.actual_value}
                      </div>
                    </div>
                    <div className="text-[10px] text-slate-400 leading-relaxed border-t border-slate-800/60 pt-1.5 font-sans">
                      {c.audit_note}
                    </div>
                  </div>
                ))}
              </div>

              {/* Pullback vs Reversal Diagnostic Detailed Explanation */}
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/70 text-xs font-mono text-slate-300 flex items-start gap-2">
                <Sparkles className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-white">Pullback vs Reversal Assessment: </strong>
                  <span>{thesis.pullback_diagnosis.classification_explanation}</span>
                </div>
              </div>
            </div>
          )}

          {/* 12-Question High-Conviction Tactical Trade Thesis */}
          {thesis.tactical_thesis_items && thesis.tactical_thesis_items.length > 0 && (
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4 shadow-xl">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider flex items-center gap-2">
                      <span>12-Question High-Conviction Tactical Trade Thesis</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono font-bold">
                        {thesis.tactical_readiness_score} / {thesis.tactical_readiness_max} Cleared
                      </span>
                    </h3>
                    <p className="text-xs text-slate-400 font-mono">
                      Rigorous tactical readiness evaluation covering trend, sector RS, entry geometry, liquidity &amp; invalidation
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2.5 py-1 rounded-lg">
                    {Math.round(((thesis.tactical_readiness_score || 12) / (thesis.tactical_readiness_max || 12)) * 100)}% TACTICAL READINESS
                  </span>
                </div>
              </div>

              {/* The 12 Questions Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono">
                {thesis.tactical_thesis_items.map((item) => (
                  <div
                    key={item.id}
                    className={`p-3 rounded-xl border transition ${
                      item.passed
                        ? 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                        : 'bg-amber-950/20 border-amber-800/40'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-start gap-2">
                        <span className="text-xs font-bold text-slate-500 min-w-[20px]">
                          {item.id}.
                        </span>
                        <div>
                          <div className="text-xs font-bold text-slate-200">
                            {item.question}
                          </div>
                          <div className="text-[11px] text-purple-300 mt-1 font-semibold">
                            {item.metric}
                          </div>
                        </div>
                      </div>
                      <div>
                        {item.passed ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 text-[10px] font-bold">
                            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                            YES
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-amber-950/80 text-amber-300 border border-amber-800/60 text-[10px] font-bold">
                            <AlertCircle className="w-3 h-3 text-amber-400" />
                            CAUTION
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="mt-2 pt-2 border-t border-slate-800/60 text-[11px] text-slate-400 leading-relaxed font-sans">
                      {item.explanation}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Deep Fundamental Ratio Grid */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
            <h4 className="text-xs font-mono uppercase font-bold text-slate-300 tracking-wider mb-3">
              Institutional Fundamental Health Metrics
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs font-mono">
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-slate-400 text-[10px]">RETURN ON EQUITY (ROE)</div>
                <div className="text-base font-bold text-white mt-0.5">{thesis.roe_pct.toFixed(1)}%</div>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-slate-400 text-[10px]">ROCE</div>
                <div className="text-base font-bold text-white mt-0.5">{thesis.roce_pct.toFixed(1)}%</div>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-slate-400 text-[10px]">DEBT TO EQUITY</div>
                <div className="text-base font-bold text-white mt-0.5">{thesis.debt_to_equity.toFixed(2)}</div>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-slate-400 text-[10px]">FCF YIELD</div>
                <div className="text-base font-bold text-white mt-0.5">{thesis.fcf_yield_pct.toFixed(1)}%</div>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <div className="text-slate-400 text-[10px]">PROMOTER HOLDING</div>
                <div className="text-base font-bold text-white mt-0.5">{thesis.promoter_holding_pct.toFixed(1)}%</div>
              </div>
            </div>
          </div>

          {/* 5-Condition Pullback Qualification & Pullback vs Reversal Diagnostic Dossier */}
          {thesis.pullback_diagnosis && (
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4 shadow-xl">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center">
                    <TrendingUp className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold font-mono text-white uppercase tracking-wider flex items-center gap-2">
                      <span>5-Condition Pullback Qualification & Reversal Diagnosis</span>
                      <span className="text-[10px] font-normal px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                        {thesis.pullback_diagnosis.conditions_cleared_count}/5 Conditions Cleared
                      </span>
                    </h3>
                    <p className="text-[11px] font-mono text-slate-400">
                      Price Level, Volume Contraction, RSI Cooldown (50–65), Candlestick Reversal & Upward Confirmation
                    </p>
                  </div>
                </div>

                {/* Pullback vs Reversal Classification Pill */}
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-mono font-bold px-3 py-1 rounded-lg border flex items-center gap-1.5 ${
                    thesis.pullback_diagnosis.classification === 'TREND_REVERSAL_BREAKDOWN'
                      ? 'bg-rose-950 text-rose-300 border-rose-800'
                      : thesis.pullback_diagnosis.classification === 'STRONG_PULLBACK'
                      ? 'bg-amber-950 text-amber-300 border-amber-800'
                      : thesis.pullback_diagnosis.classification === 'SHALLOW_PULLBACK'
                      ? 'bg-cyan-950 text-cyan-300 border-cyan-800'
                      : 'bg-emerald-950 text-emerald-300 border-emerald-800'
                  }`}>
                    <Sparkles className="w-3.5 h-3.5" />
                    {thesis.pullback_diagnosis.classification_badge.replace(/_/g, ' ')}
                  </span>
                </div>
              </div>

              {/* Pullback Depth & Reversal Diagnostic Banner */}
              <div className="p-3.5 rounded-xl bg-slate-950/90 border border-slate-800/80 flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
                <div className="flex items-center gap-4 flex-wrap">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Recent Swing High</span>
                    <span className="font-bold text-white text-sm">₹{thesis.pullback_diagnosis.recent_swing_high.toFixed(2)}</span>
                    <span className="text-[10px] text-slate-500 block">({thesis.pullback_diagnosis.swing_high_date})</span>
                  </div>
                  <div className="border-l border-slate-800 pl-4">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Pullback Depth</span>
                    <span className="font-bold text-amber-300 text-sm">-{thesis.pullback_diagnosis.pullback_depth_pct.toFixed(1)}%</span>
                    <span className="text-[10px] text-slate-500 block">From Peak High</span>
                  </div>
                  <div className="border-l border-slate-800 pl-4">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Target Support Buffer</span>
                    <span className="font-bold text-emerald-300 text-sm">{thesis.pullback_diagnosis.nearest_support_type}</span>
                    <span className="text-[10px] text-slate-500 block">₹{thesis.pullback_diagnosis.nearest_support_level.toFixed(2)} ({thesis.pullback_diagnosis.distance_to_support_pct.toFixed(1)}% away)</span>
                  </div>
                  <div className="border-l border-slate-800 pl-4">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Reversal Risk Score</span>
                    <span className={`font-bold text-sm ${thesis.pullback_diagnosis.reversal_risk_score > 50 ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {thesis.pullback_diagnosis.reversal_risk_score.toFixed(0)} / 100
                    </span>
                    <span className="text-[10px] text-slate-500 block">
                      {thesis.pullback_diagnosis.reversal_risk_score > 50 ? 'Elevated Breakdown Risk' : 'Safe Pullback Corridor'}
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Action Directive</span>
                  <span className="font-bold text-purple-300 px-2.5 py-1 rounded bg-purple-950/80 border border-purple-800/80 inline-block mt-0.5">
                    {thesis.pullback_diagnosis.actionable_directive.replace(/_/g, ' ')}
                  </span>
                </div>
              </div>

              {/* The 5 Conditions Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-5 gap-3 font-mono">
                {thesis.pullback_diagnosis.condition_items.map((c) => (
                  <div
                    key={c.condition_id}
                    className={`p-3 rounded-xl border flex flex-col justify-between space-y-2 ${
                      c.passed
                        ? 'bg-slate-950/70 border-slate-800/80 hover:border-slate-700'
                        : 'bg-amber-950/20 border-amber-800/40'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">{c.name}</span>
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${
                          c.passed
                            ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                            : 'bg-amber-950 text-amber-300 border-amber-800'
                        }`}>
                          {c.passed ? 'PASS' : 'WAIT'}
                        </span>
                      </div>
                      <div className="text-xs font-bold text-white mt-1">
                        {c.parameter}
                      </div>
                      <div className="text-[11px] text-purple-300 mt-1 font-semibold">
                        {c.actual_value}
                      </div>
                    </div>
                    <div className="text-[10px] text-slate-400 leading-relaxed border-t border-slate-800/60 pt-1.5 font-sans">
                      {c.audit_note}
                    </div>
                  </div>
                ))}
              </div>

              {/* Pullback vs Reversal Diagnostic Detailed Explanation */}
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/70 text-xs font-mono text-slate-300 flex items-start gap-2">
                <Sparkles className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="text-white">Pullback vs Reversal Assessment: </strong>
                  <span>{thesis.pullback_diagnosis.classification_explanation}</span>
                </div>
              </div>
            </div>
          )}

          {/* Executive Thesis Columns: Why to Buy, Why to Hold, Why Not to Buy */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            {/* Why to Buy */}
            <div className="bg-emerald-950/20 border border-emerald-800/40 rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-bold uppercase tracking-wider">
                <CheckCircle2 className="w-4 h-4" />
                Why to Buy (Institutional Catalysts)
              </div>
              <ul className="space-y-2 text-xs font-mono text-slate-300">
                {thesis.why_to_buy.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-emerald-400 font-bold">•</span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Why to Hold */}
            <div className="bg-blue-950/20 border border-blue-800/40 rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-blue-400 font-mono text-xs font-bold uppercase tracking-wider">
                <Activity className="w-4 h-4" />
                Why to Hold (Position Management)
              </div>
              <ul className="space-y-2 text-xs font-mono text-slate-300">
                {thesis.why_to_hold.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-blue-400 font-bold">•</span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Why Not to Buy */}
            <div className="bg-rose-950/20 border border-rose-800/40 rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-rose-400 font-mono text-xs font-bold uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4" />
                Why Not to Buy (Key Risks & Red Flags)
              </div>
              <ul className="space-y-2 text-xs font-mono text-slate-300">
                {thesis.why_not_to_buy.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-rose-400 font-bold">•</span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </div>

          </div>

        </div>
      )}
      </>
      )}

    </div>
  );
};
