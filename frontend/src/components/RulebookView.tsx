import React from 'react';
import { BookOpen, ShieldCheck, Target, Layers, AlertTriangle, Zap, CheckCircle2 } from 'lucide-react';

export const RulebookView: React.FC = () => {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      
      {/* Title Header */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center">
          <BookOpen className="w-6 h-6 text-blue-400" />
        </div>
        <div>
          <h2 className="text-xl font-black font-mono text-white">
            GTF Trader 2.0 Institutional Rulebook
          </h2>
          <p className="text-xs text-slate-400 font-mono">
            Document v1.0 & Master Specification v3.1 Operational Standard
          </p>
        </div>
      </div>

      {/* Rule 6: The 12 Golden Tactical Trade Thesis Questions */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-bold uppercase tracking-wider">
            <CheckCircle2 className="w-4 h-4" />
            6. The 12 High-Conviction Tactical Trade Thesis Questions
          </div>
          <span className="text-[11px] font-mono px-2.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold">
            Pre-Execution Tactical Readiness
          </span>
        </div>

        <p className="text-xs font-mono text-slate-300 leading-relaxed">
          Before taking any live or simulated market execution, the system audits the candidate stock against the 12 core tactical questions to eliminate retail traps:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs font-mono">
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">1. Uptrend Integrity:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the stock in an uptrend with higher highs and higher lows on daily and weekly charts?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">2. Sector Outperformance:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the sector index outperforming NIFTY 50 on 20-day and 60-day relative strength?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">3. Stock Relative Strength:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the stock generating positive alpha and leading its benchmark?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">4. Actionable Entry Geometry:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is there a confirmed breakout, orderly pullback, or fresh DBR/RBR demand zone?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">5. Volume Confirmation:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Are institutional buyers expanding volume on rallies while volume dries up on pullbacks?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">6. Key Moving Averages:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is price trading above essential benchmark MAs (20 EMA, 50 EMA, and 200 SMA)?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">7. Wholesale Pricing vs Extension:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the stock close to a favourable wholesale floor rather than an extended retail chase?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">8. Event &amp; Earnings Runway:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the upcoming holding period free from binary earnings surprises or regulatory inquiries?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">9. Technically Valid Stop-Loss:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the stop-loss anchored below the distal base with a 0.25x ATR volatility cushion?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">10. Asymmetric Reward-to-Risk:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Does the distance to target supply exceed risk by at least 2.0:1 (or 2.5:1 preferred)?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">11. Institutional Liquidity:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the stock sufficiently liquid with high delivery % (&gt;40%) and low bid-ask spread?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">12. Structural Invalidation:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is there a non-negotiable exit rule (daily candle close below distal floor) if the setup fails?</p>
          </div>
        </div>
      </div>

      {/* Grid of Rules */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Rule 1: Structural Patterns */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-blue-400 font-mono text-xs font-bold uppercase tracking-wider">
            <Target className="w-4 h-4" />
            1. Institutional Price Action Patterns
          </div>
          <div className="space-y-2 text-xs font-mono text-slate-300">
            <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80">
              <span className="font-bold text-emerald-400">DBR (Drop-Base-Rally):</span>
              <p className="text-slate-400 mt-0.5">Reversal Demand Zone. Extreme institutional accumulation following a liquidity sweep of retail stop losses.</p>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80">
              <span className="font-bold text-emerald-300">RBR (Rally-Base-Rally):</span>
              <p className="text-slate-400 mt-0.5">Continuation Demand Zone. Fast trend acceleration where institutional algorithms add sizing during pause.</p>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80">
              <span className="font-bold text-rose-400">RBD / DBD (Supply Zones):</span>
              <p className="text-slate-400 mt-0.5">Reversal and continuation supply used as strict profit targets (Target Supply Line) for paper trade exits.</p>
            </div>
          </div>
        </div>

        {/* Rule 2: Freshness & Exact Testing Audit */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-bold uppercase tracking-wider">
            <CheckCircle2 className="w-4 h-4" />
            2. Freshness Hierarchy & Testing Dates
          </div>
          <div className="space-y-2 text-xs font-mono text-slate-300">
            <div className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-800/40">
              <span className="font-bold text-emerald-300">Pristine Fresh (0 Touches):</span>
              <p className="text-slate-400 mt-0.5">100% of unfilled institutional buy orders intact. Highest statistical edge for explosive displacement.</p>
            </div>
            <div className="p-2.5 rounded-lg bg-blue-950/20 border border-blue-800/40">
              <span className="font-bold text-blue-300">Tested 1X (Tested on Exact Date):</span>
              <p className="text-slate-400 mt-0.5">Zone bounced cleanly once. The exact date of test must be recorded. Secondary entry allowed with reduced sizing.</p>
            </div>
            <div className="p-2.5 rounded-lg bg-rose-950/20 border border-rose-800/40">
              <span className="font-bold text-rose-300">Tested 2X+ or Breached:</span>
              <p className="text-slate-400 mt-0.5">Institutional liquidity exhausted. HIGH RISK TRAP. Hard gate automatically blocks entries.</p>
            </div>
          </div>
        </div>

        {/* Rule 3: Macro Curve Location */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-purple-400 font-mono text-xs font-bold uppercase tracking-wider">
            <Layers className="w-4 h-4" />
            3. Macro Curve Location Standard
          </div>
          <p className="text-xs font-mono text-slate-400">
            Calculated between HTF Supply (top of curve 100%) and HTF Demand (bottom of curve 0%):
          </p>
          <div className="space-y-2 text-xs font-mono text-slate-300">
            <div className="p-2 rounded bg-slate-950 border border-slate-800 flex justify-between items-center">
              <span>0% - 33% (Very Low on Curve)</span>
              <span className="text-emerald-400 font-bold">AGGRESSIVE BUY AUTHORIZED</span>
            </div>
            <div className="p-2 rounded bg-slate-950 border border-slate-800 flex justify-between items-center">
              <span>34% - 66% (Equilibrium)</span>
              <span className="text-blue-400 font-bold">GRADE A+ ONLY</span>
            </div>
            <div className="p-2 rounded bg-slate-950 border border-slate-800 flex justify-between items-center">
              <span>67% - 100% (High on Curve)</span>
              <span className="text-rose-400 font-bold">LONG PROHIBITED</span>
            </div>
          </div>
        </div>

        {/* Rule 4: Hard Risk Gates & Capital Sizing */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-amber-400 font-mono text-xs font-bold uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4" />
            4. Hard Risk Gates & Sizing Rules
          </div>
          <div className="space-y-2 text-xs font-mono text-slate-300">
            <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80">
              <span className="font-bold text-amber-300">Reward-to-Risk Threshold:</span>
              <p className="text-slate-400 mt-0.5">Trades with less than 2.0:1 reward-to-risk are instantly rejected by the core risk engine.</p>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80">
              <span className="font-bold text-amber-300">Buffered Stop Loss:</span>
              <p className="text-slate-400 mt-0.5">Stop loss is NEVER placed on the distal line. An institutional volatility buffer of 0.25x ATR is added beneath.</p>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80">
              <span className="font-bold text-amber-300">Capital Protection Rule:</span>
              <p className="text-slate-400 mt-0.5">Maximum 15 simultaneous open positions. Maximum 2% risk of total equity per position.</p>
            </div>
          </div>
        </div>

      </div>

      {/* Rule 5: Master 123-Point Specification Matrix */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2 text-purple-400 font-mono text-xs font-bold uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4" />
            5. Master 123-Point Institutional Confluence Specification (v3.2)
          </div>
          <span className="text-[11px] font-mono px-2.5 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 font-bold">
            10 Categories • 100% Auditable
          </span>
        </div>

        <p className="text-xs font-mono text-slate-300 leading-relaxed">
          The institutional qualification engine subjects every candidate stock to an exhaustive 123-point audit across 10 distinct institutional dimensions before qualifying capital allocation:
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5 text-xs font-mono">
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="text-purple-400 font-bold">1. Fundamental (12)</div>
            <div className="text-[11px] text-slate-400 mt-1">ROE/ROCE &gt;15%, D/E &lt;0.5, Piotroski 6-9, EPS &amp; Sales growth</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="text-blue-400 font-bold">2. Technical (20)</div>
            <div className="text-[11px] text-slate-400 mt-1">M/W/D Bullish, 20/50/200 EMA, RSI 50-70, Fresh Demand, R:R &gt;2:1</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="text-emerald-400 font-bold">3. Sector (12)</div>
            <div className="text-[11px] text-slate-400 mt-1">Sector Trend, Outperformance vs Nifty, Advance/Decline Breadth</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="text-amber-400 font-bold">4. Institutional (11)</div>
            <div className="text-[11px] text-slate-400 mt-1">FII/DII Net Buying, Mutual Fund Inflows, Delivery &gt;40%, Block Deals</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="text-cyan-400 font-bold">5. News &amp; Events (13)</div>
            <div className="text-[11px] text-slate-400 mt-1">Earnings Proximity, Order Wins, Zero Regulatory / Tax Probes</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="text-indigo-400 font-bold">6. Global Macro (13)</div>
            <div className="text-[11px] text-slate-400 mt-1">US Fed Policy, Dollar Index (DXY), Crude Oil Stability, US 10Y Yield</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="text-pink-400 font-bold">7. Market Regimes (10)</div>
            <div className="text-[11px] text-slate-400 mt-1">India VIX &lt;18, Market Breadth &gt;60%, PCR 0.8-1.3, Nifty &gt; 50 EMA</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="text-teal-400 font-bold">8. Volume Behavior (8)</div>
            <div className="text-[11px] text-slate-400 mt-1">Volume on Breakout &gt;1.5x, Low Volume Pullbacks, OBV Trend</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="text-orange-400 font-bold">9. Risk Parameters (12)</div>
            <div className="text-[11px] text-slate-400 mt-1">Max 2% Risk, Position Sizing formula, Trailing Stops, Portfolio Correl</div>
          </div>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
            <div className="text-lime-400 font-bold">10. Execution Quality (12)</div>
            <div className="text-[11px] text-slate-400 mt-1">Limit Orders Only, Liquidity Spread &lt;0.1%, Zero FOMO, Buffer Stop</div>
          </div>
        </div>

        {/* Scoring Tiers */}
        <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/90 text-xs font-mono space-y-2">
          <div className="text-slate-400 text-[10px] uppercase font-bold tracking-wider">
            Institutional Qualification Tiers
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
            <div className="p-2 rounded bg-emerald-950/40 border border-emerald-800/40">
              <span className="font-bold text-emerald-400">AAA (&gt;90% Pass Rate):</span>
              <p className="text-slate-400 text-[11px] mt-0.5">Secular Compounder. High conviction auto-execution authorized.</p>
            </div>
            <div className="p-2 rounded bg-blue-950/40 border border-blue-800/40">
              <span className="font-bold text-blue-400">AA (80% - 90%):</span>
              <p className="text-slate-400 text-[11px] mt-0.5">Strong Conviction. Standard position sizing with buffered trailing stop.</p>
            </div>
            <div className="p-2 rounded bg-indigo-950/40 border border-indigo-800/40">
              <span className="font-bold text-indigo-400">A (70% - 79%):</span>
              <p className="text-slate-400 text-[11px] mt-0.5">Qualified Setup. Requires pristine demand zone confirmation.</p>
            </div>
            <div className="p-2 rounded bg-amber-950/40 border border-amber-800/40">
              <span className="font-bold text-amber-400">Conditional (&lt;70%):</span>
              <p className="text-slate-400 text-[11px] mt-0.5">Watchlist pullback floor only. Execution suspended until gates clear.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Rule 6: The 12 Golden Tactical Trade Thesis Questions */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-bold uppercase tracking-wider">
            <CheckCircle2 className="w-4 h-4" />
            6. The 12 High-Conviction Tactical Trade Thesis Questions
          </div>
          <span className="text-[11px] font-mono px-2.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-bold">
            Pre-Execution Tactical Readiness
          </span>
        </div>

        <p className="text-xs font-mono text-slate-300 leading-relaxed">
          Before taking any live or simulated market execution, the system audits the candidate stock against the 12 core tactical questions to eliminate retail traps:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs font-mono">
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">1. Uptrend Integrity:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the stock in an uptrend with higher highs and higher lows on daily and weekly charts?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">2. Sector Outperformance:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the sector index outperforming NIFTY 50 on 20-day and 60-day relative strength?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">3. Stock Relative Strength:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the stock generating positive alpha and leading its benchmark?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">4. Actionable Entry Geometry:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is there a confirmed breakout, orderly pullback, or fresh DBR/RBR demand zone?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">5. Volume Confirmation:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Are institutional buyers expanding volume on rallies while volume dries up on pullbacks?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">6. Key Moving Averages:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is price trading above essential benchmark MAs (20 EMA, 50 EMA, and 200 SMA)?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">7. Wholesale Pricing vs Extension:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the stock close to a favourable wholesale floor rather than an extended retail chase?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">8. Event &amp; Earnings Runway:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the upcoming holding period free from binary earnings surprises or regulatory inquiries?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">9. Technically Valid Stop-Loss:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the stop-loss anchored below the distal base with a 0.25x ATR volatility cushion?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">10. Asymmetric Reward-to-Risk:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Does the distance to target supply exceed risk by at least 2.0:1 (or 2.5:1 preferred)?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">11. Institutional Liquidity:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is the stock sufficiently liquid with high delivery % (&gt;40%) and low bid-ask spread?</p>
          </div>
          <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
            <span className="text-emerald-400 font-bold">12. Structural Invalidation:</span>
            <p className="text-slate-400 text-[11px] mt-0.5">Is there a non-negotiable exit rule (daily candle close below distal floor) if the setup fails?</p>
          </div>
        </div>
      </div>

    </div>
  );
};
