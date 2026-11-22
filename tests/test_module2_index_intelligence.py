"""
Unit tests for Module 2: Market-Index Intelligence Layer (Section 2).
"""

from datetime import date, timedelta
import numpy as np
import pandas as pd
import pytest

from analytics.index_intelligence import (
    IndexIntelligenceEngine,
    IndexIntelligenceSnapshot,
    MarketBreadthState,
    TrendState,
    VolatilityState,
)


def _generate_synthetic_series(days=60, start_price=100.0, daily_trend=0.005, vol=0.01):
    np.random.seed(42)
    dates = [date(2026, 1, 1) + timedelta(days=i) for i in range(days)]
    prices = [start_price]
    for _ in range(days - 1):
        ret = daily_trend + np.random.normal(0, vol)
        prices.append(prices[-1] * (1 + ret))

    df = pd.DataFrame({
        "trading_date": dates,
        "open": [p * 0.998 for p in prices],
        "high": [p * 1.015 for p in prices],
        "low": [p * 0.985 for p in prices],
        "close": prices,
        "volume": [1_000_000] * days,
    })
    return df


def test_trend_state_bullish():
    """Verify strong bullish trend state detection."""
    df = _generate_synthetic_series(days=60, start_price=100.0, daily_trend=0.008, vol=0.005)
    trend = IndexIntelligenceEngine.calculate_trend_state(df)

    assert trend.ret_5d > 0
    assert trend.ret_20d > 0
    assert trend.ret_50d > 0
    assert trend.ma_alignment in {"BULLISH_STACK", "MIXED"}
    assert trend.trend_persistence >= 0.5
    assert trend.trend_label in {"STRONG_BULLISH", "MODERATE_BULLISH"}


def test_trend_state_bearish():
    """Verify bearish trend state detection."""
    df = _generate_synthetic_series(days=60, start_price=100.0, daily_trend=-0.008, vol=0.005)
    trend = IndexIntelligenceEngine.calculate_trend_state(df)

    assert trend.ret_20d < 0
    assert trend.trend_persistence < 0.5
    assert trend.trend_label in {"BEARISH", "STRONG_BEARISH"}


def test_volatility_state_normal_vs_high():
    """Verify volatility state calculation and regime classification."""
    # Low/normal volatility series
    df_normal = _generate_synthetic_series(days=60, start_price=100.0, daily_trend=0.001, vol=0.008)
    vol_normal = IndexIntelligenceEngine.calculate_volatility_state(df_normal)
    assert vol_normal.realised_vol_20d_ann < 25.0
    assert vol_normal.volatility_regime in {"LOW", "NORMAL"}

    # High stress volatility series
    df_stress = _generate_synthetic_series(days=60, start_price=100.0, daily_trend=-0.01, vol=0.035)
    vol_stress = IndexIntelligenceEngine.calculate_volatility_state(df_stress)
    assert vol_stress.realised_vol_20d_ann > 25.0
    assert vol_stress.volatility_regime in {"HIGH", "EXTREME_STRESS"}


def test_market_breadth_evaluation():
    """Verify market breadth advances, declines, and AD ratio."""
    # Synthesize 100 constituent stocks: 75 advancing, 25 declining
    data = []
    t_date = date(2026, 9, 25)
    for i in range(75):
        data.append({"symbol": f"ADV_{i}", "trading_date": t_date, "open": 100.0, "close": 105.0, "prevclose": 100.0})
    for i in range(25):
        data.append({"symbol": f"DEC_{i}", "trading_date": t_date, "open": 100.0, "close": 95.0, "prevclose": 100.0})

    universe_df = pd.DataFrame(data)
    breadth = IndexIntelligenceEngine.calculate_market_breadth(universe_df)

    assert breadth.advances == 75
    assert breadth.declines == 25
    assert breadth.ad_ratio == 3.0
    assert breadth.breadth_regime == "HEALTHY_EXPANSION"


def test_intermarket_leadership_confirmation():
    """Verify intermarket leadership confirmation and divergence logic."""
    snap_nifty_bull = IndexIntelligenceSnapshot(
        index_code="NIFTY 50",
        trading_date=date(2026, 9, 25),
        close=25000.0,
        trend=TrendState(2.0, 5.0, 10.0, "BULLISH_STACK", 0.7, 65.0, True, "STRONG_BULLISH"),
        volatility=VolatilityState(14.0, 200.0, 1.0, 0.2, "NORMAL"),
    )

    snap_bank_bull = IndexIntelligenceSnapshot(
        index_code="NIFTY BANK",
        trading_date=date(2026, 9, 25),
        close=53000.0,
        trend=TrendState(2.5, 6.0, 12.0, "BULLISH_STACK", 0.75, 68.0, True, "STRONG_BULLISH"),
        volatility=VolatilityState(16.0, 500.0, 1.05, 0.3, "NORMAL"),
    )

    snap_bank_bear = IndexIntelligenceSnapshot(
        index_code="NIFTY BANK",
        trading_date=date(2026, 9, 25),
        close=50000.0,
        trend=TrendState(-1.5, -4.0, -2.0, "BEARISH_STACK", 0.3, 40.0, False, "BEARISH"),
        volatility=VolatilityState(22.0, 700.0, 1.3, -0.5, "HIGH"),
    )

    # Both bullish -> CONFIRMED_BULLISH
    assert IndexIntelligenceEngine.evaluate_intermarket_leadership(snap_nifty_bull, snap_bank_bull) == "CONFIRMED_BULLISH"

    # Nifty bullish, Bank Nifty bearish -> DIVERGING_BEARISH
    assert IndexIntelligenceEngine.evaluate_intermarket_leadership(snap_nifty_bull, snap_bank_bear) == "DIVERGING_BEARISH"
