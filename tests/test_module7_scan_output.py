"""
Unit tests for Module 7: Scanner Integration and Section 9 Scan Output Generation.
"""

from datetime import date, timedelta
import pandas as pd
import pytest

from app.application import Application
from scanner.engine import ScanReport, Scanner


def _build_test_multi_stock_market():
    """Builds a realistic 60-day multi-stock market dataset for scanning."""
    dates = [date(2026, 7, 1) + timedelta(days=i) for i in range(60)]
    records = []

    # 1. Broad Market Index: NIFTY 50
    p = 24000.0
    for d in dates:
        p *= 1.002
        records.append({
            "symbol": "NIFTY 50",
            "trading_date": d,
            "open": p * 0.998,
            "high": p * 1.01,
            "low": p * 0.99,
            "close": p,
            "prevclose": p / 1.002,
            "volume": 2000000,
            "turnover": 50000.0,
        })

    # 2. Bullish IT Stock: TCS (Outperformer)
    p = 3800.0
    for d in dates:
        p *= 1.004
        records.append({
            "symbol": "TCS",
            "trading_date": d,
            "open": p * 0.995,
            "high": p * 1.02,
            "low": p * 0.985,
            "close": p,
            "prevclose": p / 1.004,
            "volume": 500000,
            "turnover": 2000.0,
        })

    # 3. Bullish Auto Stock: MARUTI
    p = 11000.0
    for d in dates:
        p *= 1.003
        records.append({
            "symbol": "MARUTI",
            "trading_date": d,
            "open": p * 0.995,
            "high": p * 1.018,
            "low": p * 0.985,
            "close": p,
            "prevclose": p / 1.003,
            "volume": 100000,
            "turnover": 1500.0,
        })

    # 4. Illiquid / Stale Stock (Should be rejected)
    records.append({
        "symbol": "TINY_CO",
        "trading_date": dates[-1],
        "open": 10.0,
        "high": 10.5,
        "low": 9.5,
        "close": 10.0,
        "prevclose": 10.0,
        "volume": 100,
        "turnover": 0.5,  # Too low turnover
    })

    return pd.DataFrame(records)


def test_scanner_end_to_end_and_section_9_output():
    """Verify scanner runs full pipeline and produces complete Section 9 report."""
    market_df = _build_test_multi_stock_market()
    scanner = Scanner(capital=1_000_000.0, min_candidate_score=50.0)
    report = scanner.scan(market_df, top_n=10)

    assert isinstance(report, ScanReport)

    # 1. Section 9.1: Overall market regime and confidence/uncertainty
    assert report.regime.regime in {"TRENDING_BULLISH", "RANGE_BOUND", "HIGH_VOLATILITY"}
    assert report.regime.confidence_score > 0
    assert report.regime.uncertainty_score > 0
    assert len(report.regime.primary_drivers) > 0

    # 2. Section 9.2: NIFTY 50 trend, volatility, and S/R zones
    assert report.nifty50_snap.close > 0
    assert report.nifty50_snap.trend.trend_label is not None
    assert report.nifty50_snap.volatility.volatility_regime is not None
    assert report.nifty50_sr is not None

    # 3. Section 9.3: Sector leaderboard & laggard list with breadth
    assert len(report.all_sectors) > 0
    ranks = [s.momentum_rank for s in report.all_sectors]
    assert 1 in ranks

    # 4 & 5. Section 9.4 & 9.5: NIFTY 500 candidates, sector strength, trade plans
    assert len(report.ranked_candidates) > 0
    top_cand = report.ranked_candidates[0]
    assert top_cand.forecast.stock_vs_sector_strength is not None
    assert len(top_cand.forecast.rationale) > 0

    # Check approved trade plans
    if report.trade_plans:
        p = report.trade_plans[0]
        assert p.entry_trigger > 0
        assert p.stop_loss < p.entry_trigger
        assert p.target_zone > p.entry_trigger
        assert p.reward_to_risk >= 1.8
        assert p.position_size_shares >= 1
        assert p.risk_gate_outcome in {"APPROVED", "RESIZED"}

    # 6. Section 9.6: Rejected candidates with explicit reasons
    assert len(report.rejected_candidates) > 0
    rej_syms = [r.symbol for r in report.rejected_candidates]
    assert "TINY_CO" in rej_syms
    tiny_rej = next(r for r in report.rejected_candidates if r.symbol == "TINY_CO")
    assert tiny_rej.rejection_category in {"POOR_LIQUIDITY", "STALE_DATA"}
    assert len(tiny_rej.reason) > 0

    # Test Section 9 string formatting
    text_output = report.format_section_9_output()
    assert "[1] OVERALL MARKET REGIME" in text_output
    assert "[2] NIFTY 50 & BANK NIFTY TREND" in text_output
    assert "[3] SECTOR LEADERBOARD & LAGGARDS" in text_output
    assert "[4 & 5] NIFTY 500 CANDIDATES & INDEPENDENT RISK-GATED TRADE PLANS" in text_output
    assert "[6] REJECTED CANDIDATES & EXPLICIT AUDIT REASONS" in text_output
    assert "RELIABILITY GUARDRAILS" in text_output


def test_application_facade():
    """Verify Application facade integrates cleanly with scanner."""
    market_df = _build_test_multi_stock_market()
    app = Application()
    report = app.scan_dataframe(market_df, top_n=5)
    assert isinstance(report, ScanReport)
    assert report.as_of_date is not None
