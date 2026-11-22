"""
Unit tests for Module 5: Hierarchical Forecasting and Decision Engine (Section 4 & 9).
"""

from datetime import date, timedelta
import pandas as pd
import pytest

from ai.hierarchical_engine import (
    HierarchicalDecisionEngine,
    MarketRegimeClassification,
    RankedCandidate,
    StockForecast,
    TradePlan,
)
from analytics.index_intelligence import (
    IndexIntelligenceSnapshot,
    MarketBreadthState,
    TrendState,
    VolatilityState,
)
from analytics.sector_intelligence import SectorMetrics
from analytics.support_resistance import SupportResistanceContext


def _make_bullish_stock_df(days=60, start=100.0):
    dates = [date(2026, 7, 1) + timedelta(days=i) for i in range(days)]
    prices = [start * (1 + 0.005 * i) for i in range(days)]
    return pd.DataFrame({
        "trading_date": dates,
        "open": [p * 0.99 for p in prices],
        "high": [p * 1.02 for p in prices],
        "low": [p * 0.98 for p in prices],
        "close": prices,
        "volume": [100000] * days,
        "turnover": [500.0] * days,
    })


def test_layer_a_regime_classification():
    """Verify Layer A classifies market regime with confidence and uncertainty."""
    engine = HierarchicalDecisionEngine()

    nifty_bull = IndexIntelligenceSnapshot(
        index_code="NIFTY 50",
        trading_date=date(2026, 9, 25),
        close=25000.0,
        trend=TrendState(2.0, 5.0, 10.0, "BULLISH_STACK", 0.7, 65.0, True, "STRONG_BULLISH"),
        volatility=VolatilityState(13.0, 180.0, 1.0, 0.2, "NORMAL"),
    )

    breadth_healthy = MarketBreadthState(
        advances=350,
        declines=150,
        unchanged=0,
        ad_ratio=2.33,
        pct_above_20dma=70.0,
        pct_above_50dma=65.0,
        pct_above_200dma=60.0,
        new_20d_highs=40,
        new_20d_lows=2,
        breadth_regime="HEALTHY_EXPANSION",
    )

    regime = engine.classify_market_regime(nifty_bull, breadth_healthy)
    assert regime.regime == "TRENDING_BULLISH"
    assert regime.confidence_score >= 75.0
    assert regime.regime_multiplier == 1.0
    assert len(regime.primary_drivers) >= 3


def test_layer_c_stock_forecasting():
    """Verify Layer C produces stock forecast with sector strength and rationale."""
    engine = HierarchicalDecisionEngine()
    stock_df = _make_bullish_stock_df(days=60, start=1000.0)

    # Fake context and sector lookup
    from ai.hierarchical_engine import IndexSectorContextScore
    ctx = IndexSectorContextScore(
        nifty50_trend="STRONG_BULLISH",
        banknifty_trend="STRONG_BULLISH",
        intermarket_confirmation="CONFIRMED_BULLISH",
        leading_sectors=("Information Technology",),
        lagging_sectors=(),
        breadth_regime="HEALTHY_EXPANSION",
        macro_score=85.0,
    )

    sector_metrics = {
        "IT": SectorMetrics(
            sector_id="IT",
            sector_name="Information Technology",
            index_code="NIFTY IT",
            constituent_count=25,
            ret_5d=2.0,
            ret_20d=5.0,
            ret_60d=10.0,
            relative_strength_20d=3.0,
            relative_strength_60d=5.0,
            breadth_pct_advancing=75.0,
            breadth_pct_above_20dma=75.0,
            participation_quality="BROAD_BASED",
            momentum_rank=1,
            rotation_status="LEADING",
            max_exposure_pct=20.0,
        )
    }

    forecast, sr_ctx = engine.forecast_stock("TCS", stock_df, ctx, sector_metrics)
    assert forecast.symbol == "TCS"
    assert forecast.predicted_opportunity_score >= 60.0
    assert forecast.forecast_direction == "BULLISH"
    assert len(forecast.rationale) >= 3


def test_layer_e_risk_gate_approval_and_trade_plan():
    """Verify Layer E approves valid candidate with stop loss, target, and position size."""
    engine = HierarchicalDecisionEngine(capital=1_000_000.0, risk_per_trade_pct=1.0)
    stock_df = _make_bullish_stock_df(days=60, start=100.0)

    regime = MarketRegimeClassification(
        regime="TRENDING_BULLISH",
        confidence_score=80.0,
        uncertainty_score=20.0,
        primary_drivers=("Bullish",),
        regime_multiplier=1.0,
    )

    forecast = StockForecast(
        symbol="TCS",
        trading_date=date(2026, 9, 25),
        sector_id="IT",
        sector_name="Information Technology",
        stock_vs_sector_strength=4.0,
        forecast_horizon_days=20,
        predicted_opportunity_score=85.0,
        forecast_direction="BULLISH",
        uncertainty_pct=18.0,
        rationale=("Bullish",),
    )

    candidate = RankedCandidate(
        rank=1,
        symbol="TCS",
        forecast=forecast,
        composite_score=85.0,
        close_price=float(stock_df["close"].iloc[-1]),
        liquidity_score=100.0,
        is_qualified=True,
    )

    sr_ctx = engine.sr_engine.identify_zones(stock_df)
    trade_plan, rejected = engine.evaluate_risk_gate_and_plan(
        candidate=candidate,
        sr_ctx=sr_ctx,
        stock_df=stock_df,
        regime=regime,
        current_sector_allocations={},
        existing_position_count=0,
    )

    assert rejected is None
    assert trade_plan is not None
    assert trade_plan.action == "BUY"
    assert trade_plan.entry_trigger > 0
    assert trade_plan.stop_loss < trade_plan.entry_trigger
    assert trade_plan.target_zone > trade_plan.entry_trigger
    assert trade_plan.reward_to_risk >= 1.8
    assert trade_plan.position_size_shares >= 1
    assert trade_plan.risk_gate_outcome == "APPROVED"


def test_layer_e_risk_gate_sector_limit_rejection():
    """Verify Layer E rejects trades that violate sector concentration limit."""
    engine = HierarchicalDecisionEngine(max_sector_exposure_pct=20.0)
    stock_df = _make_bullish_stock_df(days=60, start=100.0)

    regime = MarketRegimeClassification(
        regime="TRENDING_BULLISH",
        confidence_score=80.0,
        uncertainty_score=20.0,
        primary_drivers=("Bullish",),
        regime_multiplier=1.0,
    )

    forecast = StockForecast(
        symbol="TCS",
        trading_date=date(2026, 9, 25),
        sector_id="IT",
        sector_name="Information Technology",
        stock_vs_sector_strength=4.0,
        forecast_horizon_days=20,
        predicted_opportunity_score=85.0,
        forecast_direction="BULLISH",
        uncertainty_pct=18.0,
        rationale=("Bullish",),
    )

    candidate = RankedCandidate(
        rank=1,
        symbol="TCS",
        forecast=forecast,
        composite_score=85.0,
        close_price=float(stock_df["close"].iloc[-1]),
        liquidity_score=100.0,
        is_qualified=True,
    )

    # Current IT allocation already 20% (ceiling)
    allocations = {"IT": 20.0}
    sr_ctx = engine.sr_engine.identify_zones(stock_df)
    trade_plan, rejected = engine.evaluate_risk_gate_and_plan(
        candidate=candidate,
        sr_ctx=sr_ctx,
        stock_df=stock_df,
        regime=regime,
        current_sector_allocations=allocations,
        existing_position_count=0,
    )

    assert trade_plan is None
    assert rejected is not None
    assert rejected.rejection_category == "CORRELATED_EXPOSURE"
