"""
AI Trading Operating System
Repository Layer Tests
Market Data Repository
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from database.models.market_data import MarketData
from database.models.symbol import Symbol
from database.repositories.market_data_repository import (
    MarketDataRepository,
)


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def repository(db_session):
    return MarketDataRepository(db_session)


@pytest.fixture
def sample_market_data(repository):
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
        MarketData(
            symbol_id=symbol.symbol_id,
            trading_date=date(2025, 1, 1),
            open_price=Decimal("100"),
            high_price=Decimal("110"),
            low_price=Decimal("95"),
            close_price=Decimal("108"),
            adjusted_close=Decimal("108"),
            volume=1000,
        ),
        MarketData(
            symbol_id=symbol.symbol_id,
            trading_date=date(2025, 1, 2),
            open_price=Decimal("108"),
            high_price=Decimal("115"),
            low_price=Decimal("105"),
            close_price=Decimal("112"),
            adjusted_close=Decimal("112"),
            volume=1200,
        ),
        MarketData(
            symbol_id=symbol.symbol_id,
            trading_date=date(2025, 1, 3),
            open_price=Decimal("112"),
            high_price=Decimal("118"),
            low_price=Decimal("110"),
            close_price=Decimal("117"),
            adjusted_close=Decimal("117"),
            volume=1400,
        ),
    ]

    repository.add_many(rows)
    repository.flush()

    return symbol, rows


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_get_latest_price(
    repository,
    sample_market_data,
):
    symbol, _ = sample_market_data

    row = repository.get_latest_price(symbol.symbol_id)

    assert row is not None
    assert row.trading_date == date(2025, 1, 3)


def test_get_price_history(
    repository,
    sample_market_data,
):
    symbol, _ = sample_market_data

    rows = repository.get_price_history(
        symbol.symbol_id,
        date(2025, 1, 1),
        date(2025, 1, 3),
    )

    assert len(rows) == 3


def test_get_price_history_by_symbol(
    repository,
    sample_market_data,
):
    symbol, _ = sample_market_data

    rows = repository.get_price_history_by_symbol(
        symbol.symbol_id
    )

    assert len(rows) == 3


def test_get_by_symbol_and_date(
    repository,
    sample_market_data,
):
    symbol, _ = sample_market_data

    row = repository.get_by_symbol_and_date(
        symbol.symbol_id,
        date(2025, 1, 2),
    )

    assert row is not None
    assert row.close_price == Decimal("112")


def test_exists_for_symbol_and_date(
    repository,
    sample_market_data,
):
    symbol, _ = sample_market_data

    assert repository.exists_for_symbol_and_date(
        symbol.symbol_id,
        date(2025, 1, 2),
    )


def test_count_by_symbol(
    repository,
    sample_market_data,
):
    symbol, _ = sample_market_data

    assert repository.count_by_symbol(symbol.symbol_id) == 3


def test_get_latest_trading_date(
    repository,
    sample_market_data,
):
    latest = repository.get_latest_trading_date()

    assert latest == date(2025, 1, 3)


def test_get_earliest_trading_date(
    repository,
    sample_market_data,
):
    earliest = repository.get_earliest_trading_date()

    assert earliest == date(2025, 1, 1)


def test_get_all_symbol_ids(
    repository,
    sample_market_data,
):
    symbol, _ = sample_market_data

    ids = repository.get_all_symbol_ids()

    assert symbol.symbol_id in ids