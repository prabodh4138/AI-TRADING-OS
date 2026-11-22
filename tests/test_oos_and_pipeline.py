"""
Unit tests for Section 10 Out-of-Sample Paper Trading Simulator
and Automated End-to-End Pipeline (portfolio/oos_paper_trading.py, portfolio/automated_pipeline.py).
"""

from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import pytest

from portfolio.automated_pipeline import AutomatedPaperTradingPipeline
from portfolio.oos_paper_trading import OutOfSamplePaperTrader


@pytest.fixture
def sample_multi_day_dataset():
    """Generates 40 trading days of multi-symbol OHLCV bars."""
    symbols = ["RELIANCE", "TCS", "INFY", "NIFTY 50", "BANK NIFTY"]
    base_date = date(2026, 1, 1)
    rows = []

    prices = {
        "RELIANCE": 2500.0,
        "TCS": 3800.0,
        "INFY": 1600.0,
        "NIFTY 50": 22000.0,
        "BANK NIFTY": 48000.0,
    }

    for d in range(40):
        cur_date = base_date + timedelta(days=d)
        for sym in symbols:
            p = prices[sym] * (1.0 + 0.002 * (d % 5 - 2))
            rows.append({
                "symbol": sym,
                "trading_date": cur_date,
                "open": round(p * 0.998, 2),
                "high": round(p * 1.015, 2),
                "low": round(p * 0.985, 2),
                "close": round(p, 2),
                "volume": 250000,
                "turnover": 500.0,
                "sector": "Information Technology" if sym in {"TCS", "INFY"} else "Financial Services",
            })

    return pd.DataFrame(rows)


def test_oos_paper_trader_execution(sample_multi_day_dataset):
    """Verifies OutOfSamplePaperTrader runs walk-forward split and generates metrics."""
    trader = OutOfSamplePaperTrader(
        initial_capital=500_000.0,
        train_ratio=0.70,
        max_positions=3,
    )

    report = trader.run_oos_simulation(sample_multi_day_dataset)

    assert report.in_sample_sessions > 0
    assert report.out_of_sample_sessions > 0
    assert report.initial_capital == 500_000.0
    assert report.final_equity > 0
    assert len(report.equity_curve) == report.out_of_sample_sessions
    assert isinstance(report.gate_audit_reasons, list)

    term_output = report.format_terminal_report()
    assert "SECTION 10: AUTOMATED PAPER TRADING" in term_output
    assert "PORTFOLIO PERFORMANCE & ALPHA" in term_output


def test_automated_pipeline_execution(tmp_path, sample_multi_day_dataset):
    """Verifies AutomatedPaperTradingPipeline end-to-end lifecycle."""
    csv_file = tmp_path / "test_market_data.csv"
    sample_multi_day_dataset.to_csv(csv_file, index=False)

    pipeline = AutomatedPaperTradingPipeline(
        capital=500_000.0,
        ledger_path=str(tmp_path / "test_pipeline_ledger.json"),
        reports_dir=str(tmp_path / "reports"),
    )

    res = pipeline.run_daily_pipeline(csv_file=csv_file)

    assert res.total_equity > 0
    assert res.data_source.startswith("Custom CSV")
    assert Path(res.report_path).exists()
    assert res.market_regime is not None
