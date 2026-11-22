"""
Unit tests for InstitutionalScorecardEngine (Document v1.0)
Testing 100-point scorecard, hard gates, 4 entry models, and 12-point checklist.
"""

from datetime import date, timedelta
import pandas as pd
import pytest

from analytics.institutional_scorecard import (
    BOSClassification,
    EntryModel,
    HardGateStatus,
    InstitutionalScorecardEngine,
    InstitutionalScorecardResult,
)


@pytest.fixture
def sample_price_series():
    """Generates synthetic price data for testing BOS and Liquidity Sweeps."""
    base_date = date(2026, 1, 1)
    rows = []
    # 0 to 10: Swing down from 120 to 100 (Swing high at 120 on day 0)
    for i in range(10):
        rows.append({
            "trading_date": base_date + timedelta(days=i),
            "open": 120.0 - i * 2,
            "high": 121.0 - i * 2,
            "low": 118.0 - i * 2,
            "close": 119.0 - i * 2,
            "volume": 10000,
        })
    # Day 10: Sweep low to 95.0 (prior low was 98.0)
    rows.append({
        "trading_date": base_date + timedelta(days=10),
        "open": 100.0,
        "high": 101.0,
        "low": 95.0,  # Swept!
        "close": 99.0,
        "volume": 25000,
    })
    # Days 11-12: Basing candles around 98-100
    rows.append({
        "trading_date": base_date + timedelta(days=11),
        "open": 99.0,
        "high": 100.0,
        "low": 98.0,
        "close": 99.5,
        "volume": 8000,
    })
    rows.append({
        "trading_date": base_date + timedelta(days=12),
        "open": 99.5,
        "high": 100.5,
        "low": 98.5,
        "close": 100.0,
        "volume": 7500,
    })
    # Day 13: Explosive green candle closing at 125.0 (Breaks 121.0 swing high!)
    rows.append({
        "trading_date": base_date + timedelta(days=13),
        "open": 100.0,
        "high": 126.0,
        "low": 100.0,
        "close": 125.0,
        "volume": 60000,
    })
    df = pd.DataFrame(rows)
    return df


def test_bos_and_liquidity_sweep_detection(sample_price_series):
    """Verifies that Swing BOS and Liquidity Sweeps are objectively detected."""
    engine = InstitutionalScorecardEngine()

    # BOS check: Leg out at idx 13 closes at 125.0, breaking swing high 121.0
    bos_type, broken_level = engine.evaluate_bos(
        sample_price_series,
        base_start_idx=11,
        leg_out_close=125.0,
        lookback=15,
    )
    assert bos_type == BOSClassification.SWING_BOS
    assert broken_level == 121.0

    # Liquidity Sweep check: Day 10 low reached 95.0, sweeping previous low 100.0
    has_sweep, desc = engine.evaluate_liquidity_sweep(
        sample_price_series,
        base_start_idx=11,
        base_lowest_low=95.0,
        lookback=10,
    )
    assert has_sweep is True
    assert "Swept prior swing low" in desc


def test_100_point_scorecard_calculation():
    """Verifies 100-point scorecard arithmetic and component score bounds."""
    engine = InstitutionalScorecardEngine(min_reward_to_risk=2.0)

    res = engine.score_zone(
        symbol="TEST_STOCK",
        zone_id="DEMAND_TEST",
        timeframe="Daily",
        proximal=100.0,
        distal=96.0,
        target_supply=115.0,
        current_price=101.0,
        leg_out_gain_pct=5.0,
        atr_14=2.0,
        freshness_detail="FRESH (Virgin - 0 Tests)",
        touch_count=0,
        penetration_pct=0.0,
        alignment_grade="GRADE_A_PLUS",
        curve_location_pct=15.0,
        curve_state="VERY_LOW",
        bos_type=BOSClassification.SWING_BOS,
        has_sweep=True,
        sweep_desc="Swept prior low",
        market_posture_bullish=True,
        sector_bullish=True,
    )

    # Check component scores
    assert res.structure_score == 20.0       # Swing BOS = 20
    assert res.departure_score == 15.0       # 5% of 100 = 5.0, 5.0 / 2.0 ATR = 2.5x ATR = 15
    assert res.freshness_score == 15.0       # Fresh = 15
    assert res.htf_confluence_score == 15.0  # Grade A+ = 15
    assert res.curve_location_score == 10.0  # Very Low (15%) = 10
    assert res.liquidity_sweep_score == 10.0 # Sweep confirmed = 10
    assert res.sector_market_score == 5.0    # Both bullish = 5
    assert res.reward_risk_score == 10.0     # Target 115, stop 95.6 (buffered), R:R > 3.0 = 10

    # Total score must equal 100.0
    assert res.total_score == 100.0
    assert res.gate_passed is True
    assert res.hard_gate_status == HardGateStatus.APPROVED
    assert res.recommended_entry_model == EntryModel.MODEL_A_DIRECT_LIMIT
    assert len(res.checklist_12_points) == 12
    assert all(c.passed for c in res.checklist_12_points)


def test_hard_gates_override_score():
    """Verifies that failing a hard gate vetoes the trade setup regardless of high score."""
    engine = InstitutionalScorecardEngine(min_reward_to_risk=2.0)

    # Test 1: Low R:R (< 2.0) must fail hard gate
    res_low_rr = engine.score_zone(
        symbol="TEST_BAD_RR",
        zone_id="DEMAND_BAD_RR",
        timeframe="Daily",
        proximal=100.0,
        distal=95.0,
        target_supply=105.0,  # R:R = 5.0 / 5.0 = 1.0 (fails required 2.0:1)
        current_price=101.0,
        leg_out_gain_pct=5.0,
        atr_14=2.0,
        freshness_detail="FRESH",
        touch_count=0,
        penetration_pct=0.0,
        alignment_grade="GRADE_A",
        curve_location_pct=20.0,
        curve_state="VERY_LOW",
        bos_type=BOSClassification.SWING_BOS,
        has_sweep=True,
        sweep_desc="",
        market_posture_bullish=True,
        sector_bullish=True,
    )
    assert res_low_rr.gate_passed is False
    assert res_low_rr.hard_gate_status == HardGateStatus.NO_TRADE_RR_BELOW_THRESHOLD

    # Test 2: Premium location (>66%) must fail hard gate (Retail Trap)
    res_premium = engine.score_zone(
        symbol="TEST_PREMIUM",
        zone_id="DEMAND_PREMIUM",
        timeframe="Daily",
        proximal=100.0,
        distal=96.0,
        target_supply=120.0,
        current_price=101.0,
        leg_out_gain_pct=4.0,
        atr_14=2.0,
        freshness_detail="FRESH",
        touch_count=0,
        penetration_pct=0.0,
        alignment_grade="GRADE_A",
        curve_location_pct=85.0,  # 85% high on curve!
        curve_state="VERY_HIGH",
        bos_type=BOSClassification.SWING_BOS,
        has_sweep=False,
        sweep_desc="",
        market_posture_bullish=True,
        sector_bullish=True,
    )
    assert res_premium.gate_passed is False
    assert res_premium.hard_gate_status == HardGateStatus.NO_TRADE_PREMIUM_LOCATION
