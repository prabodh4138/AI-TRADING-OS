"""
AI Trading Operating System
Repository Layer Tests
Base Repository
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from database.models.symbol import Symbol
from database.repositories.symbol_repository import SymbolRepository


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def repository(db_session):
    """
    SymbolRepository is used to test BaseRepository methods.
    """
    return SymbolRepository(db_session)


@pytest.fixture
def sample_symbol():
    """
    Sample Symbol entity.
    """
    return Symbol(
        symbol_code="TEST001",
        symbol_name="Test Company",
        exchange="NSE",
        instrument_type="EQUITY",
        sector="TEST",
        industry="TEST",
        tick_size=Decimal("0.05"),
        lot_size=1,
        is_fno=False,
    )


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_add_entity(
    repository,
    sample_symbol,
):
    repository.add(sample_symbol)
    repository.flush()

    assert sample_symbol.symbol_id is not None


def test_get_by_id(
    repository,
    sample_symbol,
):
    repository.add(sample_symbol)
    repository.flush()

    result = repository.get_by_id(sample_symbol.symbol_id)

    assert result is not None
    assert result.symbol_code == "TEST001"


def test_exists_true(
    repository,
    sample_symbol,
):
    repository.add(sample_symbol)
    repository.flush()

    assert repository.exists(sample_symbol.symbol_id) is True


def test_exists_false(
    repository,
):
    import uuid

    assert repository.exists(uuid.uuid4()) is False


def test_get_all(
    repository,
):
    repository.add(
        Symbol(
            symbol_code="AAA",
            symbol_name="AAA",
            exchange="NSE",
            instrument_type="EQUITY",
            tick_size=Decimal("0.05"),
            lot_size=1,
            is_fno=False,
        )
    )

    repository.add(
        Symbol(
            symbol_code="BBB",
            symbol_name="BBB",
            exchange="NSE",
            instrument_type="EQUITY",
            tick_size=Decimal("0.05"),
            lot_size=1,
            is_fno=False,
        )
    )

    repository.flush()

    rows = repository.get_all()

    assert len(rows) >= 2


def test_count(
    repository,
):
    before = repository.count()

    repository.add(
        Symbol(
            symbol_code="COUNT001",
            symbol_name="COUNT001",
            exchange="NSE",
            instrument_type="EQUITY",
            tick_size=Decimal("0.05"),
            lot_size=1,
            is_fno=False,
        )
    )

    repository.flush()

    after = repository.count()

    assert after == before + 1


def test_add_many(
    repository,
):
    symbols = [
        Symbol(
            symbol_code="M001",
            symbol_name="M001",
            exchange="NSE",
            instrument_type="EQUITY",
            tick_size=Decimal("0.05"),
            lot_size=1,
            is_fno=False,
        ),
        Symbol(
            symbol_code="M002",
            symbol_name="M002",
            exchange="NSE",
            instrument_type="EQUITY",
            tick_size=Decimal("0.05"),
            lot_size=1,
            is_fno=False,
        ),
    ]

    repository.add_many(symbols)
    repository.flush()

    assert repository.count() >= 2


def test_delete(
    repository,
    sample_symbol,
):
    repository.add(sample_symbol)
    repository.flush()

    repository.delete(sample_symbol)
    repository.flush()

    assert repository.exists(sample_symbol.symbol_id) is False


def test_delete_many(
    repository,
):
    rows = [
        Symbol(
            symbol_code="DEL001",
            symbol_name="DEL001",
            exchange="NSE",
            instrument_type="EQUITY",
            tick_size=Decimal("0.05"),
            lot_size=1,
            is_fno=False,
        ),
        Symbol(
            symbol_code="DEL002",
            symbol_name="DEL002",
            exchange="NSE",
            instrument_type="EQUITY",
            tick_size=Decimal("0.05"),
            lot_size=1,
            is_fno=False,
        ),
    ]

    repository.add_many(rows)
    repository.flush()

    repository.delete_many(rows)
    repository.flush()

    for row in rows:
        assert repository.exists(row.symbol_id) is False


def test_refresh(
    repository,
    sample_symbol,
):
    repository.add(sample_symbol)
    repository.flush()

    repository.refresh(sample_symbol)

    assert sample_symbol.symbol_code == "TEST001"