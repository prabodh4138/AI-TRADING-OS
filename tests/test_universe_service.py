"""
AI Trading Operating System
Universe Service Tests
"""

from datetime import date
from uuid import uuid4

import pytest

from database.models.symbol import Symbol
from database.unit_of_work import UnitOfWork
from services.universe_service import UniverseService
from validators.base_validator import ValidationError


def _create_test_symbol(symbol_code: str) -> Symbol:
    with UnitOfWork() as uow:
        symbol = Symbol(
            symbol_code=symbol_code,
            exchange="NSE",
            instrument_type="EQUITY",
            symbol_name="AI-TOS Test Company",
            series="EQ",
            tick_size=0.05,
            is_fno=False,
            is_active=True,
        )

        uow.symbols.add(symbol)
        uow.flush()

        symbol_id = symbol.symbol_id

        uow.commit()

    with UnitOfWork() as uow:
        return uow.symbols.get_by_id(symbol_id)


def _cleanup_universe(universe_id):
    with UnitOfWork() as uow:
        universe = uow.universes.get_by_id(universe_id)

        if universe is not None:
            uow.universes.delete(universe)
            uow.flush()

        uow.commit()


def _cleanup_symbol(symbol_id):
    with UnitOfWork() as uow:
        symbol = uow.symbols.get_by_id(symbol_id)

        if symbol is not None:
            uow.symbols.delete(symbol)
            uow.flush()

        uow.commit()


def test_create_universe_duplicate_is_rejected():
    service = UniverseService()

    first = service.create_universe(
        "TEST_SERVICE_UNIVERSE",
        "Test Service Universe",
        "TEST",
        "AI-TOS",
    )

    try:
        with pytest.raises(ValidationError):
            service.create_universe(
                "TEST_SERVICE_UNIVERSE",
                "Duplicate Universe",
                "TEST",
                "AI-TOS",
            )
    finally:
        _cleanup_universe(first.universe_id)


def test_create_universe_blank_code_is_rejected():
    service = UniverseService()

    with pytest.raises(ValidationError):
        service.create_universe(
            "",
            "Invalid Universe",
        )


def test_create_universe_blank_name_is_rejected():
    service = UniverseService()

    with pytest.raises(ValidationError):
        service.create_universe(
            "INVALID_NAME_UNIVERSE",
            "",
        )


def test_invalid_membership_date_range_is_rejected():
    service = UniverseService()

    with pytest.raises(ValidationError):
        service._validate_membership_dates(
            date(2026, 9, 1),
            date(2026, 8, 31),
        )


def test_valid_membership_date_range_is_accepted():
    service = UniverseService()

    service._validate_membership_dates(
        date(2026, 1, 1),
        date(2026, 9, 1),
    )


def test_open_ended_membership_date_is_accepted():
    service = UniverseService()

    service._validate_membership_dates(
        date(2026, 1, 1),
        None,
    )


def test_add_membership_requires_existing_universe():
    service = UniverseService()

    symbol = _create_test_symbol("TEST_MISSING_UNIVERSE_SYMBOL")

    try:
        with pytest.raises(ValueError, match="Universe cannot be None"):
            service.add_membership(
                universe_id=uuid4(),
                symbol_id=symbol.symbol_id,
                effective_from=date(2026, 1, 1),
            )
    finally:
        _cleanup_symbol(symbol.symbol_id)


def test_add_membership_requires_existing_symbol():
    service = UniverseService()

    universe = service.create_universe(
        "TEST_MISSING_SYMBOL_UNIVERSE",
        "Missing Symbol Test",
        "TEST",
        "AI-TOS",
    )

    try:
        with pytest.raises(ValueError, match="Symbol cannot be None"):
            service.add_membership(
                universe_id=universe.universe_id,
                symbol_id=uuid4(),
                effective_from=date(2026, 1, 1),
            )
    finally:
        _cleanup_universe(universe.universe_id)


def test_duplicate_membership_is_rejected():
    service = UniverseService()

    universe = service.create_universe(
        "TEST_DUPLICATE_MEMBERSHIP_UNIVERSE",
        "Duplicate Membership Test",
        "TEST",
        "AI-TOS",
    )

    symbol = _create_test_symbol(
        "TEST_DUP_MEM"
    )

    try:
        service.add_membership(
            universe.universe_id,
            symbol.symbol_id,
            date(2026, 1, 1),
        )

        with pytest.raises(ValidationError):
            service.add_membership(
                universe.universe_id,
                symbol.symbol_id,
                date(2026, 1, 1),
            )

    finally:
        _cleanup_universe(universe.universe_id)
        _cleanup_symbol(symbol.symbol_id)


def test_close_membership_and_preserve_history():
    service = UniverseService()

    universe = service.create_universe(
        "TEST_CLOSE_MEMBERSHIP_UNIVERSE",
        "Close Membership Test",
        "TEST",
        "AI-TOS",
    )

    symbol = _create_test_symbol(
        "TEST_CLOSE_MEMBERSHIP_SYMBOL"
    )

    try:
        service.add_membership(
            universe.universe_id,
            symbol.symbol_id,
            date(2026, 1, 1),
        )

        closed = service.close_membership(
            universe.universe_id,
            symbol.symbol_id,
            date(2026, 9, 1),
        )

        assert closed.effective_to == date(2026, 9, 1)
        assert closed.is_active is False

        assert (
            service.is_symbol_in_universe(
                universe.universe_id,
                symbol.symbol_id,
            )
            is False
        )

        assert (
            service.is_symbol_in_universe(
                universe.universe_id,
                symbol.symbol_id,
                date(2026, 6, 1),
            )
            is True
        )

    finally:
        _cleanup_universe(universe.universe_id)
        _cleanup_symbol(symbol.symbol_id)


def test_close_already_closed_membership_is_rejected():
    service = UniverseService()

    universe = service.create_universe(
        "TEST_ALREADY_CLOSED_UNIVERSE",
        "Already Closed Test",
        "TEST",
        "AI-TOS",
    )

    symbol = _create_test_symbol(
        "TEST_CLOSED"
    )

    try:
        service.add_membership(
            universe.universe_id,
            symbol.symbol_id,
            date(2026, 1, 1),
        )

        service.close_membership(
            universe.universe_id,
            symbol.symbol_id,
            date(2026, 9, 1),
        )

        with pytest.raises(ValueError):
            service.close_membership(
                universe.universe_id,
                symbol.symbol_id,
                date(2026, 10, 1),
            )

    finally:
        _cleanup_universe(universe.universe_id)
        _cleanup_symbol(symbol.symbol_id)






