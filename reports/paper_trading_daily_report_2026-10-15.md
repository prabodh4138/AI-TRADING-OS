# AI Trading OS -- Daily Automated Paper Trading Report
**Execution Timestamp**: 2026-10-15 20:11:29  
**Trading Date**: 2026-10-15 | **Data Source**: Live NSE Bhavcopy Download (bhavcopy_20261015.csv) (Combined with 1-Year History)  

## 1. Portfolio Ledger Summary
- **Initial Capital**: ₹1,000,000.00
- **Current Cash**: ₹364,404.01
- **Total Portfolio Equity**: ₹974,186.07
- **Total Return**: -2.58%
- **Active Open Positions**: 5
- **Total Closed Trades**: 5 (Win Rate: 0.0%, Profit Factor: 0.0)

## 2. Automated Paper Trading Executions
*(No positions exited today - all active positions within risk bounds)*

### Automated Entries (Today)
| Symbol | Sector | Fill Price (with slippage) | Qty | Stop Loss | Target | Capital Allocated |
|---|---|---|---|---|---|---|
| NIFTY IT | OTHER | ₹40,143.94 | 4 | ₹39,396.59 | ₹41,320.81 | ₹160,575.76 |
| BHARTIARTL | OTHER | ₹1,856.78 | 72 | ₹1,798.67 | ₹1,953.59 | ₹133,688.16 |
| ICICIBANK | OTHER | ₹1,391.48 | 63 | ₹1,326.22 | ₹1,503.12 | ₹87,663.24 |
| SUNPHARMA | OTHER | ₹1,766.65 | 18 | ₹1,541.78 | ₹2,164.00 | ₹31,799.70 |

## 3. Active Open Paper Positions
| Symbol | Sector | Entry Date | Entry Price | Current Price | Unrealized P&L | Return % | Stop Loss | Target | Days Held |
|---|---|---|---|---|---|---|---|---|---|
| TITAN | OTHER | 2026-09-25 | ₹4,472.75 | ₹4,455.80 | ₹-745.80 | -0.38% | ₹4,409.35 | ₹4,568.11 | 3d |
| NIFTY IT | OTHER | 2026-09-11 | ₹40,143.94 | ₹40,143.94 | ₹-240.86 | -0.15% | ₹39,396.59 | ₹41,320.81 | 1d |
| BHARTIARTL | OTHER | 2026-10-15 | ₹1,856.78 | ₹1,856.78 | ₹-200.53 | -0.15% | ₹1,798.67 | ₹1,953.59 | 1d |
| ICICIBANK | OTHER | 2026-10-15 | ₹1,391.48 | ₹1,391.48 | ₹-131.49 | -0.15% | ₹1,326.22 | ₹1,503.12 | 1d |
| SUNPHARMA | OTHER | 2026-10-15 | ₹1,766.65 | ₹1,766.65 | ₹-47.70 | -0.15% | ₹1,541.78 | ₹2,164.00 | 1d |

## 4. Market-Index & Sector Intelligence Context (Section 9)
```
================================================================================
  AI TRADING OPERATING SYSTEM (AI-TOS) -- QUANTITATIVE SCAN REPORT
  As of: 2026-10-15 | Safe Decision Status: SAFE
================================================================================

[1] OVERALL MARKET REGIME & CONFIDENCE/UNCERTAINTY STATUS
--------------------------------------------------------------------------------
  Regime State      : HIGH_VOLATILITY
  Confidence Score  : 75.0%
  Uncertainty Score : 40.0%
  Sizing Multiplier : 0.40x
  Primary Drivers   :
    * NIFTY 50 Trend is STRONG_BULLISH (RSI: 62.4)
    * Volatility regime is HIGH (Realized: 21.0%)
    * Market Breadth AD Ratio: 0.56 (DETERIORATING)
    * ML Classifier Prediction: HIGH_VOLATILITY (40.0% confidence, 93.5% entropy uncertainty)

[2] NIFTY 50 & BANK NIFTY TREND, VOLATILITY & S/R ZONES
--------------------------------------------------------------------------------
  NIFTY 50 Close    : 25,219.23
  NIFTY 50 Trend    : STRONG_BULLISH (20d: +4.96%, RSI: 62.4)
  NIFTY 50 Vol      : HIGH (Realised Vol: 21.0%)
  NIFTY 50 Support  : Zone [24,804.18 - 25,103.62] (Dist: 0.5%, Strength: 48/100)
  NIFTY 50 Resist.  : Zone [25,377.53 - 25,683.89] (Dist: 0.6%, Strength: 83/100)
  BANK NIFTY Close  : 56,710.01
  BANK NIFTY Trend  : STRONG_BULLISH (20d: +10.30%)
  Leadership State  : CONFIRMED_BULLISH

[3] SECTOR LEADERBOARD & LAGGARDS (ROTATION & BREADTH CONTEXT)
--------------------------------------------------------------------------------
  Rank  Sector                         Status       20d RS     Adv%     Quality        Ceiling 
  #1    Realty                         IMPROVING     -2.26%    72.7%   BROAD_BASED    10%
  #2    Telecommunication              IMPROVING     -4.71%    52.3%   WEAK           10%
  #3    Automobile & Auto Components   IMPROVING     -5.16%    48.9%   WEAK           20%
  #4    Financial Services             IMPROVING     -5.27%    47.3%   WEAK           25%
  #5    Healthcare & Pharmaceuticals   IMPROVING     -5.31%    47.6%   WEAK           20%
  #6    Construction & Materials       IMPROVING     -5.32%    47.9%   WEAK           15%
  #7    Consumer Services              IMPROVING     -5.40%    48.6%   WEAK           15%
  #8    Metals & Mining                IMPROVING     -5.68%    50.0%   WEAK           15%
  #9    Oil Gas & Consumable Fuels     IMPROVING     -5.70%    45.0%   WEAK           15%
  #10   Information Technology         IMPROVING     -5.86%    44.3%   WEAK           20%
  #11   Fast Moving Consumer Goods     IMPROVING     -6.06%    41.6%   WEAK           20%
  #12   Broad Market / Other           IMPROVING     -7.43%    36.1%   WEAK           15%
  #13   Capital Goods & Manufacturin   IMPROVING    -11.24%    25.9%   WEAK           15%

[4 & 5] NIFTY 500 CANDIDATES & INDEPENDENT RISK-GATED TRADE PLANS
--------------------------------------------------------------------------------

  Candidate: NIFTY IT | Action: BUY | Outcome: RESIZED
    Sector Strength : +13.5% vs Broad Market / Other
    Horizon/Uncert  : 20-day horizon | Uncertainty: 6.4%
    Trade Execution : Entry @ 40083.81 | Stop: 39396.59 | Target: 41320.81 (R:R 1.80)
    Position Sizing : 4 shares (Value: Rs. 160,335.24 | Risk: Rs. 2,748.88)
    Rationale       : Price above EMA20; EMA20 > EMA50 bullish structure; SuperTrend is positive; RSI(64.3) in optimal bullish expansion zone; Outperforming sector (Broad Market / Other) by +13.5%; Retest bounce from verified support zone; ML Outperformance Probability: 99.6%

  Candidate: BHARTIARTL | Action: BUY | Outcome: APPROVED
    Sector Strength : +18.7% vs Telecommunication
    Horizon/Uncert  : 20-day horizon | Uncertainty: 18.4%
    Trade Execution : Entry @ 1854.00 | Stop: 1798.67 | Target: 1953.59 (R:R 1.80)
    Position Sizing : 72 shares (Value: Rs. 133,488.00 | Risk: Rs. 3,983.76)
    Rationale       : Price above EMA20; EMA20 > EMA50 bullish structure; SuperTrend is positive; Volume confirms price action (rel_vol >= 1.0); Outperforming sector (Telecommunication) by +18.7%; Confirmed breakout above resistance zone net of slippage; ML Outperformance Probability: 87.5%

  Candidate: TITAN | Action: BUY | Outcome: APPROVED
    Sector Strength : +11.8% vs Consumer Services
    Horizon/Uncert  : 20-day horizon | Uncertainty: 6.5%
    Trade Execution : Entry @ 4455.80 | Stop: 4330.40 | Target: 4681.52 (R:R 1.80)
    Position Sizing : 31 shares (Value: Rs. 138,129.80 | Risk: Rs. 3,887.40)
    Rationale       : Price above EMA20; EMA20 > EMA50 bullish structure; SuperTrend is positive; RSI(63.5) in optimal bullish expansion zone; Outperforming sector (Consumer Services) by +11.8%; ML Outperformance Probability: 99.4%

  Candidate: ICICIBANK | Action: BUY | Outcome: APPROVED
    Sector Strength : +25.2% vs Financial Services
    Horizon/Uncert  : 20-day horizon | Uncertainty: 29.6%
    Trade Execution : Entry @ 1389.40 | Stop: 1326.22 | Target: 1503.12 (R:R 1.80)
    Position Sizing : 63 shares (Value: Rs. 87,532.20 | Risk: Rs. 3,980.34)
    Rationale       : Price above EMA20; EMA20 > EMA50 bullish structure; SuperTrend is positive; Volume confirms price action (rel_vol >= 1.0); Outperforming sector (Financial Services) by +25.2%; Confirmed breakout above resistance zone net of slippage; ML Outperformance Probability: 76.4%

  Candidate: SUNPHARMA | Action: BUY | Outcome: APPROVED
    Sector Strength : +21.2% vs Healthcare & Pharmaceuticals
    Horizon/Uncert  : 20-day horizon | Uncertainty: 22.4%
    Trade Execution : Entry @ 1764.00 | Stop: 1541.78 | Target: 2164.00 (R:R 1.80)
    Position Sizing : 18 shares (Value: Rs. 31,752.00 | Risk: Rs. 3,999.96)
    Rationale       : Price above EMA20; EMA20 > EMA50 bullish structure; SuperTrend is positive; MACD histogram expanding; Volume confirms price action (rel_vol >= 1.0); Outperforming sector (Healthcare & Pharmaceuticals) by +21.2%; ML Outperformance Probability: 83.6%

[6] REJECTED CANDIDATES & EXPLICIT AUDIT REASONS
--------------------------------------------------------------------------------
  Total Excluded Candidates: 3508
  * 20MICRONS    [STALE_DATA]: Insufficient historical bars (1 bars < 20 required)
  * 21STCENMGM   [STALE_DATA]: Insufficient historical bars (1 bars < 20 required)
  * 360ONE       [STALE_DATA]: Insufficient historical bars (1 bars < 20 required)
  * 3BBLACKBIO   [STALE_DATA]: Insufficient historical bars (1 bars < 20 required)
  * 3IINFOLTD    [STALE_DATA]: Insufficient historical bars (1 bars < 20 required)
  * 3MINDIA      [STALE_DATA]: Insufficient historical bars (1 bars < 20 required)
  * 3PLAND       [STALE_DATA]: Insufficient historical bars (1 bars < 20 required)
  * 591GS2028    [STALE_DATA]: Insufficient historical bars (1 bars < 20 required)
  * 5PAISA       [STALE_DATA]: Insufficient historical bars (1 bars < 20 required)
  * 610GS2031    [STALE_DATA]: Insufficient historical bars (1 bars < 20 required)
  * 619GS2034    [STALE_DATA]: Insufficient historical bars (1 bars < 20 required)
  * 622GS2035    [STALE_DATA]: Insufficient historical bars (1 bars < 20 required)
    ... and 3496 additional excluded instruments.
================================================================================
  RELIABILITY GUARDRAILS (Section 10): Signals are probabilistic decision inputs;
  no outcome is guaranteed. Risk must be strictly controlled at portfolio level.
================================================================================
```