"""
AI Trading Operating System
Universe Repository Tests
"""

from datetime import date

from database.models.symbol import Symbol
from database.models.universe import Universe
from database.models.universe_constituent import UniverseConstituent
from database.repositories.universe_repository import UniverseRepository


def create_symbol(session, symbol_code: str = "TEST_UNIVERSE_SYMBOL") -> Symbol:
    """Create a minimal test symbol."""

    symbol = Symbol(
        symbol_code=symbol_code,
        symbol_name="Test Universe Symbol",
        exchange="NSE",
        instrument_type="EQUITY",
        isin=f"TEST{symbol_code[:8]}",
        lot_size=1,
        tick_size=0.05,
        face_value=10,
        is_fno=False,
        is_active=True,
    )

    session.add(symbol)
    session.flush()

    return symbol


def create_universe(
    session,
    universe_code: str = "TEST_UNIVERSE",
) -> Universe:
    """Create a minimal test universe."""

    universe = Universe(
        universe_code=universe_code,
        universe_name="Test Universe",
        universe_type="TEST",
        provider="AI-TOS",
        description="Repository test universe",
        is_active=True,
    )

    session.add(universe)
    session.flush()

    return universe


def test_get_by_universe_code(db_session):
    universe = create_universe(
        db_session,
        "TEST_GET_UNIVERSE",
    )

    repository = UniverseRepository(db_session)

    result = repository.get_by_universe_code(
        "TEST_GET_UNIVERSE"
    )

    assert result is not None
    assert result.universe_id == universe.universe_id
    assert result.universe_code == "TEST_GET_UNIVERSE"


def test_get_active_universes(db_session):
    active = create_universe(
        db_session,
        "TEST_ACTIVE_UNIVERSE",
    )

    inactive = create_universe(
        db_session,
        "TEST_INACTIVE_UNIVERSE",
    )

    inactive.is_active = False
    db_session.flush()

    repository = UniverseRepository(db_session)

    results = repository.get_active_universes()

    codes = {item.universe_code for item in results}

    assert active.universe_code in codes
    assert inactive.universe_code not in codes


def test_add_and_get_current_constituent(db_session):
    symbol = create_symbol(
        db_session,
        "TEST_CURRENT_SYMBOL",
    )

    universe = create_universe(
        db_session,
        "TEST_CURRENT_UNIVERSE",
    )

    membership = UniverseConstituent(
        universe_id=universe.universe_id,
        symbol_id=symbol.symbol_id,
        effective_from=date(2026, 1, 1),
        effective_to=None,
        is_active=True,
    )

    db_session.add(membership)
    db_session.flush()

    repository = UniverseRepository(db_session)

    results = repository.get_constituents(
        universe.universe_id
    )

    assert len(results) == 1
    assert results[0].symbol_id == symbol.symbol_id


def test_historical_membership_survives_closure(db_session):
    symbol = create_symbol(
        db_session,
        "TEST_HISTORY_SYMBOL",
    )

    universe = create_universe(
        db_session,
        "TEST_HISTORY_UNIVERSE",
    )

    membership = UniverseConstituent(
        universe_id=universe.universe_id,
        symbol_id=symbol.symbol_id,
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 9, 1),
        is_active=False,
    )

    db_session.add(membership)
    db_session.flush()

    repository = UniverseRepository(db_session)

    # Current membership must not be returned.
    assert (
        repository.is_symbol_in_universe(
            universe.universe_id,
            symbol.symbol_id,
        )
        is False
    )

    # Historical membership must still be valid.
    assert (
        repository.is_symbol_in_universe(
            universe.universe_id,
            symbol.symbol_id,
            date(2026, 6, 1),
        )
        is True
    )

    # After the membership ended, it must no longer be valid.
    assert (
        repository.is_symbol_in_universe(
            universe.universe_id,
            symbol.symbol_id,
            date(2026, 9, 2),
        )
        is False
    )


def test_historical_constituent_symbols(db_session):
    symbol = create_symbol(
        db_session,
        "TEST_HIST_SYMBOL",
    )

    universe = create_universe(
        db_session,
        "TEST_HIST_UNIVERSE",
    )

    membership = UniverseConstituent(
        universe_id=universe.universe_id,
        symbol_id=symbol.symbol_id,
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 9, 1),
        is_active=False,
    )

    db_session.add(membership)
    db_session.flush()

    repository = UniverseRepository(db_session)

    results = repository.get_constituent_symbols(
        universe.universe_id,
        as_of_date=date(2026, 6, 1),
    )

    assert len(results) == 1
    assert results[0].symbol_code == "TEST_HIST_SYMBOL"


def test_count_constituents_respects_historical_date(db_session):
    symbol = create_symbol(
        db_session,
        "TEST_COUNT_SYMBOL",
    )

    universe = create_universe(
        db_session,
        "TEST_COUNT_UNIVERSE",
    )

    membership = UniverseConstituent(
        universe_id=universe.universe_id,
        symbol_id=symbol.symbol_id,
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 9, 1),
        is_active=False,
    )

    db_session.add(membership)
    db_session.flush()

    repository = UniverseRepository(db_session)

    assert (
        repository.count_constituents(
            universe.universe_id
        )
        == 0
    )

    assert (
        repository.count_constituents(
            universe.universe_id,
            as_of_date=date(2026, 6, 1),
        )
        == 1
    )

    assert (
        repository.count_constituents(
            universe.universe_id,
            as_of_date=date(2026, 9, 2),
        )
        == 0
    )
