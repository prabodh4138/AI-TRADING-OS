"""
AI Trading Operating System
Repository Layer Tests
Indicator Repository
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from database.models.indicator_data import IndicatorData
from database.models.symbol import Symbol
from database.repositories.indicator_repository import (
    IndicatorRepository,
)


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def repository(db_session):
    return IndicatorRepository(db_session)


@pytest.fixture
def sample_indicator_data(repository):
    symbol = Symbol(
        symbol_code="RELIANCE",
        symbol_name="Reliance Industries",
        exchange="NSE",
        instrument_type="EQUITY",
        tick_size=Decimal("0.05"),
        lot_size=1,
        is_fno=True,
    )

    repository.session.add(symbol)
    repository.session.flush()

    rows = [
        IndicatorData(
            symbol_id=symbol.symbol_id,
            trading_date=date(2025, 1, 1),
            sma20=Decimal("100"),
            sma50=Decimal("98"),
            ema20=Decimal("101"),
            ema50=Decimal("99"),
            rsi14=Decimal("55"),
            macd=Decimal("1.20"),
            macd_signal=Decimal("1.00"),
            macd_histogram=Decimal("0.20"),
            atr14=Decimal("2.50"),
            bb_upper=Decimal("110"),
            bb_middle=Decimal("105"),
            bb_lower=Decimal("100"),
            adx14=Decimal("24"),
            plus_di=Decimal("28"),
            minus_di=Decimal("18"),
            obv=Decimal("100000"),
            volume_sma20=Decimal("120000"),
            relative_volume=Decimal("1.10"),
            roc10=Decimal("3.20"),
            momentum10=Decimal("8.50"),
            stochastic_k=Decimal("72"),
            stochastic_d=Decimal("68"),
            trend_score=Decimal("80"),
            momentum_score=Decimal("76"),
        ),
        IndicatorData(
            symbol_id=symbol.symbol_id,
            trading_date=date(2025, 1, 2),
            sma20=Decimal("101"),
            sma50=Decimal("99"),
            ema20=Decimal("102"),
            ema50=Decimal("100"),
            rsi14=Decimal("60"),
            macd=Decimal("1.50"),
            macd_signal=Decimal("1.20"),
            macd_histogram=Decimal("0.30"),
            atr14=Decimal("2.70"),
            bb_upper=Decimal("112"),
            bb_middle=Decimal("107"),
            bb_lower=Decimal("102"),
            adx14=Decimal("26"),
            plus_di=Decimal("30"),
            minus_di=Decimal("17"),
            obv=Decimal("110000"),
            volume_sma20=Decimal("125000"),
            relative_volume=Decimal("1.20"),
            roc10=Decimal("3.80"),
            momentum10=Decimal("9.40"),
            stochastic_k=Decimal("75"),
            stochastic_d=Decimal("71"),
            trend_score=Decimal("84"),
            momentum_score=Decimal("79"),
        ),
    ]

    repository.add_many(rows)
    repository.flush()

    return symbol, rows


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_get_by_symbol(
    repository,
    sample_indicator_data,
):
    symbol, _ = sample_indicator_data

    rows = repository.get_by_symbol(symbol.symbol_id)

    assert len(rows) == 2


def test_get_latest(
    repository,
    sample_indicator_data,
):
    symbol, _ = sample_indicator_data

    row = repository.get_latest(symbol.symbol_id)

    assert row is not None
    assert row.trading_date == date(2025, 1, 2)


def test_get_by_symbol_and_date(
    repository,
    sample_indicator_data,
):
    symbol, _ = sample_indicator_data

    row = repository.get_by_symbol_and_date(
        symbol.symbol_id,
        date(2025, 1, 1),
    )

    assert row is not None
    assert row.rsi14 == Decimal("55")


def test_exists_for_symbol_and_date(
    repository,
    sample_indicator_data,
):
    symbol, _ = sample_indicator_data

    assert repository.exists_for_symbol_and_date(
        symbol.symbol_id,
        date(2025, 1, 2),
    ) is True


def test_exists_for_symbol_and_date_false(
    repository,
    sample_indicator_data,
):
    symbol, _ = sample_indicator_data

    assert repository.exists_for_symbol_and_date(
        symbol.symbol_id,
        date(2025, 1, 10),
    ) is False


def test_count_by_symbol(
    repository,
    sample_indicator_data,
):
    symbol, _ = sample_indicator_data

    assert repository.count_by_symbol(symbol.symbol_id) == 2


def test_delete_by_symbol(
    repository,
    sample_indicator_data,
):
    symbol, _ = sample_indicator_data

    deleted = repository.delete_by_symbol(symbol.symbol_id)

    repository.flush()

    assert deleted == 2
    assert repository.count_by_symbol(symbol.symbol_id) == 0