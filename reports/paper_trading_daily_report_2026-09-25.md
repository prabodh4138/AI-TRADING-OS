# AI Trading OS -- Daily Automated Paper Trading Report
**Execution Timestamp**: 2026-10-15 19:52:12  
**Trading Date**: 2026-09-25 | **Data Source**: Historical Multi-Session NIFTY 500 Dataset  

## 1. Portfolio Ledger Summary
- **Initial Capital**: ₹1,000,000.00
- **Current Cash**: ₹1,809.27
- **Total Portfolio Equity**: ₹998,504.96
- **Total Return**: -0.15%
- **Active Open Positions**: 6
- **Total Closed Trades**: 0 (Win Rate: 0.0%, Profit Factor: 0.0)

## 2. Automated Paper Trading Executions
*(No positions exited today - all active positions within risk bounds)*

### Automated Entries (Today)
| Symbol | Sector | Fill Price (with slippage) | Qty | Stop Loss | Target | Capital Allocated |
|---|---|---|---|---|---|---|
| BHARTIARTL | OTHER | ₹1,880.71 | 106 | ₹1,835.38 | ₹1,954.41 | ₹199,355.26 |
| TITAN | OTHER | ₹4,472.75 | 44 | ₹4,409.35 | ₹4,568.11 | ₹196,801.00 |
| RELIANCE | OTHER | ₹2,875.11 | 69 | ₹2,828.68 | ₹2,946.62 | ₹198,382.59 |
| LT | OTHER | ₹4,340.88 | 46 | ₹4,173.00 | ₹4,624.86 | ₹199,680.48 |
| TCS | OTHER | ₹4,425.74 | 45 | ₹4,318.21 | ₹4,600.73 | ₹199,158.30 |
| HDFCBANK | OTHER | ₹1,659.03 | 2 | ₹1,635.61 | ₹1,694.24 | ₹3,318.06 |

## 3. Active Open Paper Positions
| Symbol | Sector | Entry Date | Entry Price | Current Price | Unrealized P&L | Return % | Stop Loss | Target | Days Held |
|---|---|---|---|---|---|---|---|---|---|
| BHARTIARTL | OTHER | 2026-09-25 | ₹1,880.71 | ₹1,880.71 | ₹-299.03 | -0.15% | ₹1,835.38 | ₹1,954.41 | 1d |
| TITAN | OTHER | 2026-09-25 | ₹4,472.75 | ₹4,472.75 | ₹-295.20 | -0.15% | ₹4,409.35 | ₹4,568.11 | 1d |
| RELIANCE | OTHER | 2026-09-25 | ₹2,875.11 | ₹2,875.11 | ₹-297.57 | -0.15% | ₹2,828.68 | ₹2,946.62 | 1d |
| LT | OTHER | 2026-09-25 | ₹4,340.88 | ₹4,340.88 | ₹-299.52 | -0.15% | ₹4,173.00 | ₹4,624.86 | 1d |
| TCS | OTHER | 2026-09-25 | ₹4,425.74 | ₹4,425.74 | ₹-298.74 | -0.15% | ₹4,318.21 | ₹4,600.73 | 1d |
| HDFCBANK | OTHER | 2026-09-25 | ₹1,659.03 | ₹1,659.03 | ₹-298.63 | -9.00% | ₹1,635.61 | ₹1,694.24 | 1d |

## 4. Market-Index & Sector Intelligence Context (Section 9)
```
================================================================================
  AI TRADING OPERATING SYSTEM (AI-TOS) -- QUANTITATIVE SCAN REPORT
  As of: 2026-09-25 | Safe Decision Status: SAFE
================================================================================

[1] OVERALL MARKET REGIME & CONFIDENCE/UNCERTAINTY STATUS
--------------------------------------------------------------------------------
  Regime State      : TRENDING_BULLISH
  Confidence Score  : 82.0%
  Uncertainty Score : 20.0%
  Sizing Multiplier : 1.00x
  Primary Drivers   :
    * NIFTY 50 Trend is MODERATE_BULLISH (RSI: 54.92)
    * Volatility regime is NORMAL (Realized: 14.4%)
    * Market Breadth AD Ratio: 2.60 (HEALTHY_EXPANSION)
    * ML Classifier Prediction: TRENDING_BULLISH (69.0% confidence, 55.6% entropy uncertainty)

[2] NIFTY 50 & BANK NIFTY TREND, VOLATILITY & S/R ZONES
--------------------------------------------------------------------------------
  NIFTY 50 Close    : 25,335.73
  NIFTY 50 Trend    : MODERATE_BULLISH (20d: +0.75%, RSI: 54.9)
  NIFTY 50 Vol      : NORMAL (Realised Vol: 14.4%)
  NIFTY 50 Support  : Zone [24,366.14 - 24,660.30] (Dist: 2.7%, Strength: 95/100)
  NIFTY 50 Resist.  : Zone [25,467.56 - 25,775.02] (Dist: 0.5%, Strength: 62/100)
  BANK NIFTY Close  : 57,236.24
  BANK NIFTY Trend  : MODERATE_BULLISH (20d: +1.90%)
  Leadership State  : CONFIRMED_BULLISH

[3] SECTOR LEADERBOARD & LAGGARDS (ROTATION & BREADTH CONTEXT)
--------------------------------------------------------------------------------
  Rank  Sector                         Status       20d RS     Adv%     Quality        Ceiling 
  #1    Telecommunication              LEADING       +0.19%    56.0%   BROAD_BASED    10%
  #2    Consumer Services              LEADING       +0.07%    54.4%   BROAD_BASED    15%
  #3    Broad Market / Other           IMPROVING     -0.29%    52.8%   WEAK           15%
  #4    Construction & Materials       IMPROVING     -0.36%    52.4%   WEAK           15%
  #5    Automobile & Auto Components   IMPROVING     -0.45%    53.2%   WEAK           20%
  #6    Financial Services             IMPROVING     -0.46%    52.1%   WEAK           25%
  #7    Healthcare & Pharmaceuticals   IMPROVING     -0.46%    52.0%   WEAK           20%
  #8    Oil Gas & Consumable Fuels     IMPROVING     -0.58%    50.8%   WEAK           15%
  #9    Fast Moving Consumer Goods     IMPROVING     -0.60%    50.8%   WEAK           20%
  #10   Information Technology         IMPROVING     -0.65%    50.4%   WEAK           20%

[4 & 5] NIFTY 500 CANDIDATES & INDEPENDENT RISK-GATED TRADE PLANS
--------------------------------------------------------------------------------

  Candidate: BHARTIARTL | Action: BUY | Outcome: RESIZED
    Sector Strength : +8.8% vs Telecommunication
    Horizon/Uncert  : 20-day horizon | Uncertainty: 8.0%
    Trade Execution : Entry @ 1877.89 | Stop: 1835.38 | Target: 1954.41 (R:R 1.80)
    Position Sizing : 106 shares (Value: Rs. 199,056.34 | Risk: Rs. 4,506.06)
    Rationale       : Price above EMA20; EMA20 > EMA50 bullish structure; SuperTrend is positive; RSI(68.0) in optimal bullish expansion zone; MACD histogram expanding; Volume confirms price action (rel_vol >= 1.0); Outperforming sector (Telecommunication) by +8.8%; Confirmed breakout above resistance zone net of slippage; ML Outperformance Probability: 98.0%

  Candidate: TITAN | Action: BUY | Outcome: RESIZED
    Sector Strength : +0.1% vs Consumer Services
    Horizon/Uncert  : 20-day horizon | Uncertainty: 9.6%
    Trade Execution : Entry @ 4466.05 | Stop: 4409.35 | Target: 4568.11 (R:R 1.80)
    Position Sizing : 44 shares (Value: Rs. 196,506.20 | Risk: Rs. 2,494.80)
    Rationale       : Price above EMA20; EMA20 > EMA50 bullish structure; SuperTrend is positive; RSI(54.0) in optimal bullish expansion zone; Volume confirms price action (rel_vol >= 1.0); In-line with sector (Consumer Services); Retest bounce from verified support zone; ML Outperformance Probability: 96.4%

  Candidate: RELIANCE | Action: BUY | Outcome: RESIZED
    Sector Strength : +3.8% vs Oil Gas & Consumable Fuels
    Horizon/Uncert  : 20-day horizon | Uncertainty: 7.5%
    Trade Execution : Entry @ 2870.80 | Stop: 2828.68 | Target: 2946.62 (R:R 1.80)
    Position Sizing : 69 shares (Value: Rs. 198,085.20 | Risk: Rs. 2,906.28)
    Rationale       : Price above EMA20; EMA20 > EMA50 bullish structure; SuperTrend is positive; RSI(55.5) in optimal bullish expansion zone; MACD histogram expanding; Outperforming sector (Oil Gas & Consumable Fuels) by +3.8%; ML Outperformance Probability: 98.5%

  Candidate: LT | Action: BUY | Outcome: RESIZED
    Sector Strength : +1.2% vs Construction & Materials
    Horizon/Uncert  : 20-day horizon | Uncertainty: 9.8%
    Trade Execution : Entry @ 4334.38 | Stop: 4173.00 | Target: 4624.86 (R:R 1.80)
    Position Sizing : 46 shares (Value: Rs. 199,381.48 | Risk: Rs. 7,423.48)
    Rationale       : Price above EMA20; EMA20 > EMA50 bullish structure; SuperTrend is positive; RSI(55.8) in optimal bullish expansion zone; MACD histogram expanding; Volume confirms price action (rel_vol >= 1.0); In-line with sector (Construction & Materials); ML Outperformance Probability: 96.2%

  Candidate: TCS | Action: BUY | Outcome: RESIZED
    Sector Strength : +0.9% vs Information Technology
    Horizon/Uncert  : 20-day horizon | Uncertainty: 10.2%
    Trade Execution : Entry @ 4419.11 | Stop: 4318.21 | Target: 4600.73 (R:R 1.80)
    Position Sizing : 45 shares (Value: Rs. 198,859.95 | Risk: Rs. 4,540.50)
    Rationale       : Price above EMA20; EMA20 > EMA50 bullish structure; SuperTrend is positive; RSI(57.6) in optimal bullish expansion zone; MACD histogram expanding; In-line with sector (Information Technology); Retest bounce from verified support zone; ML Outperformance Probability: 95.9%

  Candidate: NIFTY IT | Action: BUY | Outcome: RESIZED
    Sector Strength : +1.6% vs Broad Market / Other
    Horizon/Uncert  : 20-day horizon | Uncertainty: 6.5%
    Trade Execution : Entry @ 40619.70 | Stop: 39380.46 | Target: 42850.33 (R:R 1.80)
    Position Sizing : 4 shares (Value: Rs. 162,478.80 | Risk: Rs. 4,956.96)
    Rationale       : Price above EMA20; EMA20 > EMA50 bullish structure; SuperTrend is positive; RSI(54.9) in optimal bullish expansion zone; Volume confirms price action (rel_vol >= 1.0); In-line with sector (Broad Market / Other); ML Outperformance Probability: 99.5%

  Candidate: HDFCBANK | Action: BUY | Outcome: RESIZED
    Sector Strength : +2.4% vs Financial Services
    Horizon/Uncert  : 20-day horizon | Uncertainty: 13.6%
    Trade Execution : Entry @ 1656.55 | Stop: 1635.61 | Target: 1694.24 (R:R 1.80)
    Position Sizing : 120 shares (Value: Rs. 198,786.00 | Risk: Rs. 2,512.80)
    Rationale       : EMA20 > EMA50 bullish structure; SuperTrend is positive; RSI(50.7) in optimal bullish expansion zone; Volume confirms price action (rel_vol >= 1.0); Outperforming sector (Financial Services) by +2.4%; Retest bounce from verified support zone; ML Outperformance Probability: 92.4%

  Candidate: SUNPHARMA | Action: BUY | Outcome: RESIZED
    Sector Strength : -0.2% vs Healthcare & Pharmaceuticals
    Horizon/Uncert  : 20-day horizon | Uncertainty: 34.6%
    Trade Execution : Entry @ 1685.67 | Stop: 1633.45 | Target: 1779.67 (R:R 1.80)
    Position Sizing : 118 shares (Value: Rs. 198,909.06 | Risk: Rs. 6,161.96)
    Rationale       : Price above EMA20; EMA20 > EMA50 bullish structure; SuperTrend is positive; RSI(54.2) in optimal bullish expansion zone; In-line with sector (Healthcare & Pharmaceuticals); ML Outperformance Probability: 71.4%

[6] REJECTED CANDIDATES & EXPLICIT AUDIT REASONS
--------------------------------------------------------------------------------
  Total Excluded Candidates: 8
  * ICICIBANK    [CORRELATED_EXPOSURE]: Sector concentration breach: FIN_SERVICE current 19.9% + 55.1% exceeds limit of 20.0%
  * AXISBANK     [CORRELATED_EXPOSURE]: Sector concentration breach: FIN_SERVICE current 19.9% + 64.7% exceeds limit of 20.0%
  * BAJFINANCE   [CORRELATED_EXPOSURE]: Sector concentration breach: FIN_SERVICE current 19.9% + 66.0% exceeds limit of 20.0%
  * ITC          [WEAK_EVIDENCE]: Composite score 56.7 below minimum 65.0
  * MARUTI       [WEAK_EVIDENCE]: Composite score 43.9 below minimum 65.0
  * TATAMOTORS   [WEAK_EVIDENCE]: Composite score 39.3 below minimum 65.0
  * KOTAKBANK    [WEAK_EVIDENCE]: Composite score 37.3 below minimum 65.0
  * INFY         [WEAK_EVIDENCE]: Composite score 14.6 below minimum 65.0
================================================================================
  RELIABILITY GUARDRAILS (Section 10): Signals are probabilistic decision inputs;
  no outcome is guaranteed. Risk must be strictly controlled at portfolio level.
================================================================================
```