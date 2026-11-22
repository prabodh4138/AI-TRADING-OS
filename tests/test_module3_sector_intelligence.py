"""
Unit tests for Module 3: Sector Intelligence and Rotation (Section 3).
"""

import pandas as pd
import pytest

from analytics.sector_intelligence import (
    SectorIntelligenceEngine,
    SectorMetrics,
)
from data_engine.contracts import SectorMappingResolver


@pytest.fixture
def sample_universe_data():
    # Construct a sample multi-sector DataFrame
    rows = [
        # IT stocks (strong outperformance)
        {"symbol": "TCS", "trading_date": "2026-09-25", "close": 4200.0, "prevclose": 4100.0, "ret_20d": 8.0, "ret_60d": 10.0},
        {"symbol": "INFY", "trading_date": "2026-09-25", "close": 1900.0, "prevclose": 1850.0, "ret_20d": 7.0, "ret_60d": 9.0},
        {"symbol": "WIPRO", "trading_date": "2026-09-25", "close": 550.0, "prevclose": 540.0, "ret_20d": 6.0, "ret_60d": 7.0},
        # Energy stocks (negative returns)
        {"symbol": "RELIANCE", "trading_date": "2026-09-25", "close": 2900.0, "prevclose": 2920.0, "ret_20d": -3.0, "ret_60d": -1.0},
        {"symbol": "ONGC", "trading_date": "2026-09-25", "close": 280.0, "prevclose": 285.0, "ret_20d": -4.0, "ret_60d": -2.0},
    ]
    return pd.DataFrame(rows)


def test_sector_metrics_calculation(sample_universe_data):
    """Verify sector aggregation, relative strength, and ranking."""
    engine = SectorIntelligenceEngine()
    # Benchmark return = 2.0%
    sectors = engine.calculate_sector_metrics(
        sample_universe_data,
        benchmark_ret_20d=2.0,
        benchmark_ret_60d=4.0,
    )

    assert len(sectors) >= 2
    # IT should rank #1 because median ret_20d is ~7% vs Energy ~-3.5%
    top = sectors[0]
    assert top.sector_id == "IT"
    assert top.relative_strength_20d > 0
    assert top.momentum_rank == 1
    assert top.rotation_status in {"LEADING", "WEAKENING"}


def test_sector_leaderboard_builder(sample_universe_data):
    """Verify leaderboard segments sectors correctly into Leaders and Laggards."""
    engine = SectorIntelligenceEngine()
    sectors = engine.calculate_sector_metrics(
        sample_universe_data,
        benchmark_ret_20d=2.0,
        benchmark_ret_60d=4.0,
    )
    leaderboard = engine.build_leaderboard(sectors)

    # IT should be among leaders or improving
    leader_or_improving = [s.sector_id for s in leaderboard.leaders + leaderboard.improving]
    assert "IT" in leader_or_improving

    # Energy should be among laggards or weakening
    laggard_or_weakening = [s.sector_id for s in leaderboard.laggards + leaderboard.weakening]
    assert "ENERGY" in laggard_or_weakening


def test_stock_vs_sector_strength(sample_universe_data):
    """Verify stock vs sector strength calculation."""
    engine = SectorIntelligenceEngine()
    sectors = engine.calculate_sector_metrics(
        sample_universe_data,
        benchmark_ret_20d=2.0,
        benchmark_ret_60d=4.0,
    )
    sec_lookup = {s.sector_id: s for s in sectors}

    # TCS has ret_20d = 12.0%, IT median is 7.0% -> +5.0% outperformer
    res = engine.calculate_stock_vs_sector_strength("TCS", stock_ret_20d=12.0, sector_metrics_lookup=sec_lookup)
    assert res.symbol == "TCS"
    assert res.stock_vs_sector_strength > 0
    assert res.classification == "SECTOR_OUTPERFORMER"
    assert res.is_sector_leader is True

    # Underperforming IT stock with ret_20d = 2.0% -> -5.0%
    res_under = engine.calculate_stock_vs_sector_strength("WIPRO", stock_ret_20d=2.0, sector_metrics_lookup=sec_lookup)
    assert res_under.stock_vs_sector_strength < 0
    assert res_under.classification == "SECTOR_UNDERPERFORMER"


def test_sector_concentration_guardrail():
    """Verify sector concentration limits prevent overexposure."""
    current_allocations = {"IT": 18.0, "FIN_SERVICE": 10.0}

    # Propose 5% more IT -> total 23% > 20% limit -> should reject
    ok, msg = SectorIntelligenceEngine.check_sector_concentration_guardrail(
        sector_id="IT",
        current_sector_allocations_pct=current_allocations,
        proposed_trade_pct=5.0,
        max_sector_limit_pct=20.0,
    )
    assert ok is False
    assert "Sector concentration breach" in msg

    # Propose 5% more FIN_SERVICE -> total 15% <= 20% limit -> should pass
    ok_fin, msg_fin = SectorIntelligenceEngine.check_sector_concentration_guardrail(
        sector_id="FIN_SERVICE",
        current_sector_allocations_pct=current_allocations,
        proposed_trade_pct=5.0,
        max_sector_limit_pct=20.0,
    )
    assert ok_fin is True
