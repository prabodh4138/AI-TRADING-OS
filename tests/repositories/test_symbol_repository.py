"""
AI Trading Operating System
Repository Layer Tests
Symbol Repository
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
    return SymbolRepository(db_session)


@pytest.fixture
def sample_symbols(repository):
    symbols = [
        Symbol(
            symbol_code="RELIANCE",
            symbol_name="Reliance Industries",
            exchange="NSE",
            instrument_type="EQUITY",
            sector="Oil & Gas",
            industry="Refinery",
            tick_size=Decimal("0.05"),
            lot_size=1,
            is_fno=True,
        ),
        Symbol(
            symbol_code="TCS",
            symbol_name="Tata Consultancy Services",
            exchange="NSE",
            instrument_type="EQUITY",
            sector="IT",
            industry="Software",
            tick_size=Decimal("0.05"),
            lot_size=1,
            is_fno=True,
        ),
        Symbol(
            symbol_code="HDFCBANK",
            symbol_name="HDFC Bank",
            exchange="NSE",
            instrument_type="EQUITY",
            sector="Banking",
            industry="Private Bank",
            tick_size=Decimal("0.05"),
            lot_size=1,
            is_fno=True,
        ),
    ]

    repository.add_many(symbols)
    repository.flush()

    return symbols


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_get_by_symbol_code(
    repository,
    sample_symbols,
):
    symbol = repository.get_by_symbol_code("RELIANCE")

    assert symbol is not None
    assert symbol.symbol_code == "RELIANCE"


def test_get_by_symbol_code_not_found(
    repository,
):
    symbol = repository.get_by_symbol_code("UNKNOWN")

    assert symbol is None


def test_exists_by_symbol_code_true(
    repository,
    sample_symbols,
):
    assert repository.exists_by_symbol_code("RELIANCE") is True


def test_exists_by_symbol_code_false(
    repository,
):
    assert repository.exists_by_symbol_code("UNKNOWN") is False


def test_get_all_symbol_codes(
    repository,
    sample_symbols,
):
    codes = repository.get_all_symbol_codes()

    assert "RELIANCE" in codes
    assert "TCS" in codes
    assert "HDFCBANK" in codes


def test_get_active_symbols(
    repository,
    sample_symbols,
):
    rows = repository.get_active_symbols()

    assert len(rows) >= 3


def test_get_by_exchange(
    repository,
    sample_symbols,
):
    rows = repository.get_by_exchange("NSE")

    assert len(rows) >= 3

    for row in rows:
        assert row.exchange == "NSE"


def test_count_by_exchange(
    repository,
    sample_symbols,
):
    count = repository.count_by_exchange("NSE")

    assert count >= 3


def test_search_by_symbol_code(
    repository,
    sample_symbols,
):
    rows = repository.search("REL")

    assert len(rows) == 1
    assert rows[0].symbol_code == "RELIANCE"


def test_search_by_symbol_name(
    repository,
    sample_symbols,
):
    rows = repository.search("Consultancy")

    assert len(rows) == 1
    assert rows[0].symbol_code == "TCS"


def test_search_not_found(
    repository,
):
    rows = repository.search("XYZXYZXYZ")

    assert rows == []