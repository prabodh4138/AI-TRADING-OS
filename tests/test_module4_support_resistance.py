"""
Unit tests for Module 4: Support and Resistance Intelligence Engine (Section 5).
"""

from datetime import date, timedelta
import pandas as pd
import pytest

from analytics.support_resistance import (
    PriceZone,
    SupportResistanceContext,
    SupportResistanceEngine,
)


def _generate_bouncing_series():
    """Generates a price series that bounces repeatedly between 100 (support) and 120 (resistance)."""
    dates = [date(2026, 1, 1) + timedelta(days=i) for i in range(40)]
    prices = []
    # 4 oscillation cycles between 100 and 120
    cycle = [100.0, 105.0, 110.0, 115.0, 120.0, 115.0, 110.0, 105.0, 100.0, 102.0]
    for _ in range(4):
        prices.extend(cycle)

    prices = prices[:40]
    df = pd.DataFrame({
        "trading_date": dates,
        "open": prices,
        "high": [p * 1.01 for p in prices],
        "low": [p * 0.99 for p in prices],
        "close": prices,
        "volume": [50000] * len(prices),
    })
    return df


def test_zone_identification_and_clustering():
    """Verify swing highs and lows are clustered into support and resistance zones."""
    df = _generate_bouncing_series()
    engine = SupportResistanceEngine(default_uncertainty_pct=0.5, cost_slippage_buffer_pct=0.25)
    context = engine.identify_zones(df)

    assert len(context.all_zones) >= 2
    # Verify there is at least one support zone near 100 and resistance zone near 120
    support_levels = [z.level for z in context.all_zones if z.zone_type == "SUPPORT"]
    resistance_levels = [z.level for z in context.all_zones if z.zone_type == "RESISTANCE"]

    assert any(98.0 <= s <= 103.0 for s in support_levels)
    assert any(117.0 <= r <= 122.0 for r in resistance_levels)


def test_zone_uncertainty_bands_and_scoring():
    """Verify uncertainty bands are formed around the zone level."""
    df = _generate_bouncing_series()
    engine = SupportResistanceEngine()
    context = engine.identify_zones(df)

    for zone in context.all_zones:
        assert zone.lower_band < zone.level < zone.upper_band
        assert zone.uncertainty_pct > 0.0
        assert 0.0 <= zone.strength_score <= 100.0


def test_breakout_confirmation_net_of_slippage():
    """Verify breakout confirmation evaluates price beyond resistance upper band + buffer."""
    df = _generate_bouncing_series()
    # Modify last row to simulate a sharp breakout above 120 resistance
    df.loc[len(df) - 1, "close"] = 125.0
    df.loc[len(df) - 1, "high"] = 126.0

    engine = SupportResistanceEngine(cost_slippage_buffer_pct=0.25)
    context = engine.identify_zones(df)

    # Current price is 125, above resistance ~120
    assert context.current_price == 125.0
    # Breakout is confirmed
    assert context.is_breakout_confirmed is True
