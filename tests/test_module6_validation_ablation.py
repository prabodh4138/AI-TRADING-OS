"""
Unit tests for Module 6: Validation, Walk-Forward Testing & Ablation Engine (Section 7).
"""

from datetime import date, timedelta
import numpy as np
import pandas as pd
import pytest

from analytics.validation_engine import (
    AblationConfig,
    ValidationEngine,
    WalkForwardWindow,
)


def _generate_synthetic_stock_history(days=180, start_price=100.0):
    np.random.seed(42)
    dates = [date(2026, 1, 1) + timedelta(days=i) for i in range(days)]
    prices = [start_price]
    for _ in range(days - 1):
        ret = 0.0015 + np.random.normal(0, 0.012)
        prices.append(prices[-1] * (1 + ret))

    df = pd.DataFrame({
        "trading_date": dates,
        "open": [p * 0.995 for p in prices],
        "high": [p * 1.015 for p in prices],
        "low": [p * 0.985 for p in prices],
        "close": prices,
        "volume": [100000] * days,
    })
    return df


def test_walk_forward_split_generation():
    """Verify walk-forward splits are strictly non-overlapping and chronologically ordered."""
    dates = [date(2026, 1, 1) + timedelta(days=i) for i in range(200)]
    splits = ValidationEngine.generate_walk_forward_splits(dates, train_bars=100, test_bars=30)

    assert len(splits) >= 3
    for s in splits:
        assert s.train_start < s.train_end < s.test_start < s.test_end
        # Ensure zero lookahead: train_end is before test_start
        assert (s.test_start - s.train_end).days >= 1


def test_backtest_with_slippage_and_brokerage():
    """Verify that slippage and brokerage are deducted from trades and equity."""
    df = _generate_synthetic_stock_history(days=120)
    engine = ValidationEngine(capital=1_000_000.0, slippage_bps=10.0, brokerage_bps=5.0)

    cfg = AblationConfig(name="TEST_RUN", use_index_context=True, use_sr_zones=True)
    equity, trades, metrics = engine.run_backtest(df, cfg)

    assert not equity.empty
    assert len(equity) == len(df)
    assert metrics.total_costs_deducted >= 0.0
    if metrics.total_trades > 0:
        assert metrics.total_costs_deducted > 0.0


def test_ablation_study_and_deployment_gate():
    """Verify ablation study evaluates all feature families and reports deployment gate status."""
    df = _generate_synthetic_stock_history(days=120)
    engine = ValidationEngine(capital=1_000_000.0)

    ablation_results = engine.run_ablation_study(df)
    assert len(ablation_results) == 5

    names = [r.ablation_name for r in ablation_results]
    assert "BASELINE_TECHNICALS_ONLY" in names
    assert "FULL_AI_TOS_SYSTEM" in names

    # Deployment gate flag must be a boolean
    for r in ablation_results:
        assert isinstance(r.passes_deployment_gate, bool)
        assert -100.0 <= r.metrics.max_drawdown_pct <= 0.0
