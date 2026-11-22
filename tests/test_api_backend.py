"""
AI Trading Operating System (AI-TOS)
FastAPI Backend Integration & Contract Verification Test Suite.
"""

import pytest
from backend.services.data_service import DataService
from backend.services.portfolio_service import PortfolioService
from backend.services.zone_service import ZoneService
from backend.services.thesis_service import ThesisService
from backend.routes.market import get_market_status, get_symbols, get_symbol_bars
from backend.routes.portfolio import get_portfolio_summary
from backend.routes.thesis import get_stock_thesis
from backend.routes.zones import get_mtf_matrix
from backend.schemas import ExecuteTradeRequest


def test_market_status_endpoint():
    status = get_market_status()
    assert status.health_status == "PRISTINE_HEALTH"
    assert status.data_health_score == 100.0
    assert status.total_bars > 0
    assert status.active_symbols > 0
    assert status.as_of_date != ""


def test_symbols_endpoint():
    symbols = get_symbols()
    assert len(symbols) > 0
    assert "RELIANCE" in [s.upper() for s in symbols]


def test_bars_endpoint():
    bars_resp = get_symbol_bars("RELIANCE")
    assert bars_resp.symbol == "RELIANCE"
    assert bars_resp.current_price > 0
    assert len(bars_resp.bars) > 0
    first_bar = bars_resp.bars[0]
    assert hasattr(first_bar, "open")
    assert hasattr(first_bar, "high")
    assert hasattr(first_bar, "low")
    assert hasattr(first_bar, "close")
    assert hasattr(first_bar, "volume")


def test_portfolio_ledger_endpoint():
    ps = PortfolioService.get_instance()
    summary = get_portfolio_summary()
    assert summary.total_equity >= 0
    assert summary.current_cash >= 0
    assert isinstance(summary.positions, list)
    assert isinstance(summary.recent_closed_trades, list)


def test_stock_thesis_endpoint():
    th = get_stock_thesis("RELIANCE")
    assert th.symbol == "RELIANCE"
    assert th.piotroski_f_score >= 0
    assert th.pe_ratio > 0
    assert len(th.why_to_buy) > 0
    assert len(th.why_to_hold) > 0
    assert len(th.why_not_to_buy) > 0
    # 12-Question Tactical Trade Thesis Verification
    assert len(th.tactical_thesis_items) == 12
    assert th.tactical_readiness_score >= 10
    assert th.tactical_thesis_items[0].question == "Is the stock in an uptrend?"
    assert th.tactical_thesis_items[1].question == "Is the sector outperforming Nifty?"
    assert th.tactical_thesis_items[2].question == "Is the stock showing relative strength?"
    assert th.tactical_thesis_items[3].question == "Is there a breakout, pullback or demand-zone entry?"
    assert th.tactical_thesis_items[4].question == "Is the entry supported by volume?"
    assert th.tactical_thesis_items[5].question == "Is the stock trading above important moving averages?"
    assert th.tactical_thesis_items[6].question == "Is the stock close to a favourable entry rather than excessively extended?"
    assert th.tactical_thesis_items[7].question == "Is there any major event within the holding period?"
    assert th.tactical_thesis_items[8].question == "Is the stop-loss technically valid?"
    assert th.tactical_thesis_items[9].question == "Is the reward-to-risk ratio favourable?"
    assert th.tactical_thesis_items[10].question == "Is the stock sufficiently liquid?"
    assert th.tactical_thesis_items[11].question == "Is there a clear reason to exit if the setup fails?"


def test_mtf_matrix_endpoint():
    mtf = get_mtf_matrix("RELIANCE")
    assert mtf.symbol == "RELIANCE"
    assert mtf.current_price > 0
    assert len(mtf.all_active_zones) > 0
    assert mtf.macro_curve_status != ""


def test_trade_execution_and_reset():
    ps = PortfolioService.get_instance()
    ps.reset_portfolio(1_000_000.0)

    req = ExecuteTradeRequest(
        symbol="RELIANCE",
        entry_trigger=1380.0,
        stop_loss=1000.0,
        target_zone=1600.0,
    )
    pos = ps.execute_trade(req)
    assert pos is not None
    assert pos.symbol == "RELIANCE"
    assert pos.quantity > 0

    summary = ps.get_summary()
    assert summary.open_positions_count >= 1

    # Clean reset
    ps.reset_portfolio(1_000_000.0)
    summary_clean = ps.get_summary()
    assert summary_clean.open_positions_count == 0
    assert summary_clean.total_equity == 1_000_000.0


def test_timeframe_bars_and_indicators():
    bars_1d = get_symbol_bars("RELIANCE", timeframe="1D")
    assert bars_1d.timeframe == "1D"
    assert len(bars_1d.bars) > 0
    assert bars_1d.high_52w > 0
    assert bars_1d.low_52w > 0

    bars_1w = get_symbol_bars("RELIANCE", timeframe="1W")
    assert bars_1w.timeframe == "1W"
    assert len(bars_1w.bars) > 0
    # Check EMA indicators on weekly
    last_w = bars_1w.bars[-1]
    assert hasattr(last_w, "ema20")
    assert hasattr(last_w, "change_pct")


def test_curated_watchlist_endpoint():
    from backend.routes.zones import get_curated_watchlist
    watchlist = get_curated_watchlist()
    assert isinstance(watchlist, list)
    assert len(watchlist) > 0
    first = watchlist[0]
    assert first.symbol != ""
    assert first.cmp > 0
    assert first.proximal_line > 0
    assert first.buffered_stop_loss > 0
    assert first.target_supply > 0
    assert first.action_recommendation != ""
    # Multi-Timeframe Trend Harmony Verification (All 6 Horizons)
    assert first.yearly_trend != ""
    assert first.half_yearly_trend != ""
    assert first.quarterly_trend != ""
    assert first.monthly_trend != ""
    assert first.weekly_trend != ""
    assert first.daily_trend != ""
    # Dual Output Architecture Verification
    assert hasattr(first, "fundamental_quality_score")
    assert first.fundamental_quality_score > 0
    assert hasattr(first, "fundamental_health_verdict")
    assert first.fundamental_health_verdict != ""
    assert hasattr(first, "positional_entry_score")
    assert first.positional_entry_score > 0
    assert hasattr(first, "positional_suitability_verdict")
    assert first.positional_suitability_verdict != ""


def test_dual_score_output_architecture():
    from data_engine.fundamental_data import FundamentalDataProvider
    from analytics.institutional_scorecard import (
        calculate_fundamental_quality_score,
        calculate_positional_entry_score,
    )
    fp = FundamentalDataProvider()

    # Test Fundamental Quality Score on premier compounder (ICICIBANK)
    f_icici = fp.get_fundamentals("ICICIBANK")
    f_score, f_verdict, f_rationale = calculate_fundamental_quality_score(f_icici)
    assert 0 <= f_score <= 100
    assert f_verdict in ["FINANCIALLY_EXCELLENT", "FINANCIALLY_HEALTHY"]
    assert "balance sheet" in f_rationale.lower() or "institutional" in f_rationale.lower()

    # Test Positional Entry Score: At Demand (Wholesale discount) vs Extended
    pos_score_at_demand, pos_verdict_at_demand, _ = calculate_positional_entry_score(
        current_price=1000.0,
        proximal_line=1000.0, # 0% away
        distal_line=960.0,
        buffered_stop_loss=955.0,
        target_supply=1120.0,
        curve_location_pct=20.0, # Wholesale low
        alignment_grade="GRADE_A_PLUS",
        rsi_14=58.0, # Preferred 50-70 range
        touch_count=0,
        reward_to_risk=3.0,
    )
    assert pos_score_at_demand >= 75.0
    assert pos_verdict_at_demand == "PRIME_BUY_SUITABLE"

    # Extended stock: 25% away from demand with high RSI (>80)
    pos_score_extended, pos_verdict_extended, _ = calculate_positional_entry_score(
        current_price=1250.0,
        proximal_line=1000.0, # 25% away
        distal_line=960.0,
        buffered_stop_loss=955.0,
        target_supply=1300.0,
        curve_location_pct=75.0, # High curve
        alignment_grade="GRADE_A",
        rsi_14=84.0, # Overbought >80
        touch_count=1,
        reward_to_risk=1.2,
    )
    assert pos_score_extended < 50.0
    assert pos_verdict_extended == "AVOID_CHASING_EXTENDED"


def test_positional_rules_industry_debt_and_promoter():
    from backend.routes.thesis import get_master_123_checklist

    # Test ICICIBANK: 0% promoter holding must PASS as board-governed premier compounder
    res_icici = get_master_123_checklist("ICICIBANK")
    prom_item = next(i for i in res_icici.all_123_items if i.sl_no == 9)
    assert prom_item.passed is True
    assert "board-governed" in prom_item.audit_note.lower() or "institutional" in prom_item.audit_note.lower()

    # Test Industry-specific D/E threshold for Banking
    de_item = next(i for i in res_icici.all_123_items if i.sl_no == 3)
    assert de_item.passed is True
    assert "Banking" in de_item.preferred_criteria

    # Test RSI 14 hierarchy item (Item 21)
    rsi_item = next(i for i in res_icici.all_123_items if i.sl_no == 21)
    assert "50–70 Preferred" in rsi_item.preferred_criteria


def test_auto_trading_engine():
    ps = PortfolioService.get_instance()
    status = ps.get_auto_trade_status()
    assert status.max_positions >= 10
    assert status.min_cash_reserve_pct >= 0.0

    # Run auto-trade cycle directly on service
    cycle_res = ps.run_auto_trading(max_new_trades=2)
    assert cycle_res.success is True
    assert isinstance(cycle_res.execution_details, list)


def test_pullback_qualification_5_conditions():
    from backend.routes.thesis import get_pullback_diagnosis
    diag = get_pullback_diagnosis("SUNPHARMA")
    assert diag.symbol == "SUNPHARMA"
    assert diag.conditions_max == 5
    assert len(diag.condition_items) == 5
    assert diag.conditions_cleared_count >= 2

    # Check Condition 1: Price Approach
    c1 = diag.condition_items[0]
    assert c1.condition_id == 1
    assert "Price" in c1.name
    assert "EMA" in c1.parameter or "Support" in c1.parameter

    # Check Condition 2: Volume Contraction
    c2 = diag.condition_items[1]
    assert c2.condition_id == 2
    assert "Volume" in c2.name
    assert "Selling Volume Contraction" in c2.parameter

    # Check Condition 3: RSI Cooldown towards 50-65
    c3 = diag.condition_items[2]
    assert c3.condition_id == 3
    assert "RSI" in c3.name
    assert "50–65" in c3.parameter

    # Check Condition 4: Candlestick Reversal
    c4 = diag.condition_items[3]
    assert c4.condition_id == 4
    assert "Candlestick" in c4.name

    # Check Condition 5: Confirmation Turn
    c5 = diag.condition_items[4]
    assert c5.condition_id == 5
    assert "Confirmation" in c5.name

    # Verify classification matrix
    assert diag.classification in [
        "SHALLOW_PULLBACK",
        "HEALTHY_PULLBACK",
        "STRONG_PULLBACK",
        "TREND_REVERSAL_BREAKDOWN",
    ]


def test_pullback_vs_reversal_matrix():
    from analytics.pullback_analyzer import PullbackQualityEngine, PullbackClassification
    import pandas as pd
    import numpy as np

    engine = PullbackQualityEngine()

    # 1. Test Shallow Pullback scenario (tight consolidation above 20 EMA, dip < 5%)
    n = 30
    dates = pd.date_range("2026-01-01", periods=n)
    # Strong uptrend: 100 to 150, small dip to 148
    closes = np.linspace(100, 150, n)
    closes[-1] = 148.0 # only 1.3% dip
    df_shallow = pd.DataFrame({
        "trading_date": dates,
        "open": closes * 0.99,
        "high": closes * 1.01,
        "low": closes * 0.98,
        "close": closes,
        "volume": [100000] * n,
    })
    res_shallow = engine.analyze_pullback("SHALLOW_TEST", df_shallow)
    assert res_shallow.classification == PullbackClassification.SHALLOW_PULLBACK
    assert res_shallow.pullback_depth_pct <= 5.0

    # 2. Test Trend Reversal Breakdown scenario (breakdown below 50 EMA, dip > 22%, heavy selling vol)
    closes_rev = np.linspace(150, 100, n) # severe downward distribution
    vols_rev = [100000] * (n - 5) + [300000] * 5 # heavy selling volume
    df_rev = pd.DataFrame({
        "trading_date": dates,
        "open": closes_rev * 1.01,
        "high": closes_rev * 1.02,
        "low": closes_rev * 0.98,
        "close": closes_rev,
        "volume": vols_rev,
    })
    res_rev = engine.analyze_pullback("REVERSAL_TEST", df_rev)
    assert res_rev.classification == PullbackClassification.TREND_REVERSAL_BREAKDOWN
    assert res_rev.reversal_risk_score >= 60.0
    assert "REVERSAL" in res_rev.actionable_directive


def test_master_123_checklist_endpoint():
    from backend.routes.thesis import get_master_123_checklist
    res = get_master_123_checklist("SUNPHARMA")
    assert res.symbol == "SUNPHARMA"
    assert res.max_score_123 == 123
    assert res.total_score_123 >= 100
    assert len(res.all_123_items) == 123
    assert len(res.category_summaries) == 10
    assert res.composite_pass_rate_pct > 80.0
    assert res.institutional_tier in ["AAA_SECULAR_COMPOUNDER", "AA_STRONG_CONVICTION"]

    # Verify first and last checklist items
    item_1 = res.all_123_items[0]
    assert item_1.sl_no == 1
    assert item_1.category == "Fundamental"
    assert item_1.parameter == "ROE"

    item_123 = res.all_123_items[122]
    assert item_123.sl_no == 123
    assert item_123.category == "Execution"
    assert item_123.parameter == "Exit Conditions"

