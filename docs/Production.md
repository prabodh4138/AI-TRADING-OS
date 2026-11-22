# AI-TOS Production & Quantitative Intelligence Specification Baseline

## Scope
AI-TOS operates as a multi-layer Indian-equities quantitative intelligence platform. It analyzes broad-market indices (NIFTY 50, NIFTY Bank), sector indices, market breadth, relative strength, volatility, support/resistance zones, and cross-market context to inform stock-level forecasts and independent risk gating for NIFTY 500 constituents.

## Multi-Layer Architecture
1. **Foundation & Data Contracts (`data_engine/contracts.py`, `config/indices.yaml`, `config/sectors.yaml`)**:
   - Configuration-driven index and sector catalogues.
   - Point-in-time constituent mapping from NIFTY 500 (survivorship bias elimination).
   - Freshness verification and safe handling of missing/stale index data.
2. **Market-Index Intelligence (`analytics/index_intelligence.py`)**:
   - Multi-horizon returns (5d, 20d, 50d), trend persistence, and moving average structures.
   - Volatility state: realised volatility, ATR expansion/contraction ratios, gap behavior.
   - Market breadth engine: Advance/Decline ratio, % of constituents above 20/50/200 DMA, new highs/lows.
   - Intermarket leadership confirmation between broad benchmark and key sectors/banks.
3. **Sector Intelligence & Rotation (`analytics/sector_intelligence.py`)**:
   - Sector momentum and relative strength vs NIFTY 50 benchmark.
   - Sector breadth and participation quality (broad-based vs concentrated).
   - 4-Quadrant rotation cycle: LEADING, WEAKENING, LAGGING, IMPROVING.
   - Stock-versus-sector strength estimation.
   - Portfolio sector concentration limits.
4. **Support & Resistance Intelligence (`analytics/support_resistance.py`)**:
   - Probabilistic price zones with uncertainty bands from swing-point clusters.
   - Breakout/retest confirmation net of transaction costs and slippage.
5. **Hierarchical Decision Flow (`ai/hierarchical_engine.py`)**:
   - Layer A: Market Regime Classifier with calibrated confidence & uncertainty.
   - Layer B: Index and Sector Context scoring.
   - Layer C: Stock-level Forecasting.
   - Layer D: Multi-factor candidate ranking.
   - Layer E: Independent Risk Gate and Trade Plan generation.
6. **Validation & Ablation Engine (`analytics/validation_engine.py`)**:
   - Chronological walk-forward test splits with zero lookahead.
   - Ablation testing framework comparing Full AI-TOS vs technical baselines.
   - Transaction costs & slippage modeling; Sharpe, Sortino, max drawdown, profit factor.
   - Objective deployment gate.
7. **Scanner & Section 9 Output (`scanner/engine.py`, `dashboard/app.py`, `main.py`)**:
   - Produces the 6-part standardized scan report mandated by Section 9.

## Commands
- **Run Scan**: `python main.py --scan downloads/raw/market_data_2026-09-25.csv`
- **Launch Command Center UI**: `python main.py --dashboard`
- **Run Complete Test Suite**: `pytest` (233 passing tests)

## Reliability Guardrails (Section 10)
Signals are probabilistic decision inputs; no outcome or profit is guaranteed. Controlled paper-trading risk, transparent uncertainty, and reproducible evidence are standard across all operations.
