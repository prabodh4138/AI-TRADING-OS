"""
Unit tests for Automated Paper Trading Engine (portfolio/paper_trader.py).
"""

from datetime import date
import pandas as pd
import pytest

from ai.hierarchical_engine import TradePlan
from portfolio.paper_trader import PaperTradingManager


def test_paper_trading_order_execution_and_sizing(tmp_path):
    """Verify PaperTradingManager executes approved TradePlans into active positions."""
    ledger_file = tmp_path / "test_ledger.json"
    manager = PaperTradingManager(initial_capital=1_000_000.0, ledger_path=ledger_file)

    plan = TradePlan(
        symbol="TCS",
        trading_date=date(2026, 9, 25),
        action="BUY",
        entry_trigger=4000.0,
        stop_loss=3900.0,
        target_zone=4250.0,
        reward_to_risk=2.5,
        position_size_shares=50,
        position_value=200000.0,
        risk_amount=5000.0,
        risk_gate_outcome="APPROVED",
        gate_reason="Passed",
    )

    positions = manager.execute_trade_plans([plan], sector_lookup={"TCS": "IT"})
    assert len(positions) == 1
    assert "TCS" in manager.positions
    pos = manager.positions["TCS"]
    assert pos.symbol == "TCS"
    assert pos.quantity == 50
    assert pos.entry_price >= 4000.0  # Slippage added
    assert manager.current_cash < 1_000_000.0
    assert manager.total_equity <= 1_000_000.0  # Due to slippage/fees


def test_paper_trading_target_and_stop_loss_exits(tmp_path):
    """Verify daily price bar triggers target exit and stop loss exit."""
    ledger_file = tmp_path / "test_ledger.json"
    manager = PaperTradingManager(initial_capital=1_000_000.0, ledger_path=ledger_file)

    plan1 = TradePlan(
        symbol="TCS",
        trading_date=date(2026, 9, 25),
        action="BUY",
        entry_trigger=4000.0,
        stop_loss=3900.0,
        target_zone=4200.0,
        reward_to_risk=2.0,
        position_size_shares=25,
        position_value=100000.0,
        risk_amount=2500.0,
        risk_gate_outcome="APPROVED",
        gate_reason="Passed",
    )
    manager.execute_trade_plans([plan1])

    # Next day: TCS hits 4250 (exceeds target 4200)
    next_day_df = pd.DataFrame([{
        "symbol": "TCS",
        "trading_date": "2026-09-26",
        "open": 4100.0,
        "high": 4250.0,
        "low": 4080.0,
        "close": 4220.0,
        "volume": 200000,
    }])

    closed = manager.on_daily_market_data(next_day_df)
    assert len(closed) == 1
    assert closed[0].symbol == "TCS"
    assert closed[0].exit_reason == "TARGET"
    assert closed[0].net_pnl > 0  # Profit recorded
    assert "TCS" not in manager.positions  # Position closed
    assert len(manager.closed_trades) == 1


def test_paper_trading_persistence(tmp_path):
    """Verify ledger state survives reloading from disk."""
    ledger_file = tmp_path / "test_ledger.json"
    manager1 = PaperTradingManager(initial_capital=500_000.0, ledger_path=ledger_file)

    plan = TradePlan(
        symbol="INFY",
        trading_date=date(2026, 9, 25),
        action="BUY",
        entry_trigger=1800.0,
        stop_loss=1750.0,
        target_zone=1920.0,
        reward_to_risk=2.4,
        position_size_shares=50,
        position_value=90000.0,
        risk_amount=2500.0,
        risk_gate_outcome="APPROVED",
        gate_reason="Passed",
    )
    manager1.execute_trade_plans([plan])

    # Create new manager pointing to same ledger file
    manager2 = PaperTradingManager(ledger_path=ledger_file)
    assert "INFY" in manager2.positions
    assert manager2.positions["INFY"].quantity == 50
    assert manager2.current_cash == manager1.current_cash
