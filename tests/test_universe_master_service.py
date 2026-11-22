from datetime import date

import pytest

from database.models.symbol import Symbol
from database.unit_of_work import UnitOfWork
from services.universe_master_service import UniverseMasterService


def _create_symbol(uow: UnitOfWork, code: str) -> Symbol:
    symbol = Symbol(
        symbol_code=code,
        symbol_name=f"Test {code}",
        exchange="NSE",
        instrument_type="EQUITY",
        is_active=True,
    )
    uow.symbols.add(symbol)
    uow.flush()
    return symbol


def _records(
    symbol_code: str,
    *,
    universe_code: str = "TEST500",
    universe_name: str = "Test Universe 500",
    universe_type: str = "INDEX",
    provider: str = "TEST",
    effective_from: date = date(2026, 1, 1),
    effective_to: date | None = None,
) -> list[dict]:
    return [
        {
            "universe_code": universe_code,
            "universe_name": universe_name,
            "universe_type": universe_type,
            "provider": provider,
            "symbol_code": symbol_code,
            "effective_from": effective_from,
            "effective_to": effective_to,
        }
    ]


def test_import_creates_universe_and_membership(db_session):
    service = UniverseMasterService()

    uow = UnitOfWork()
    try:
        symbol = _create_symbol(uow, "TESTIMP1")

        result = service.import_records(
            _records(symbol.symbol_code),
            uow,
        )

        assert result["received"] == 1
        assert result["imported"] == 1
        assert result["skipped"] == 0

        universe = uow.universes.get_by_universe_code("TEST500")

        assert universe is not None

        membership = uow.universes.get_membership(
            universe.universe_id,
            symbol.symbol_id,
            date(2026, 1, 1),
        )

        assert membership is not None
        assert membership.effective_from == date(2026, 1, 1)
        assert membership.effective_to is None
    finally:
        uow.rollback()
        uow.close()


def test_reimport_same_membership_is_idempotent(db_session):
    service = UniverseMasterService()

    uow = UnitOfWork()
    try:
        symbol = _create_symbol(uow, "TESTIMP2")

        first = service.import_records(
            _records(symbol.symbol_code),
            uow,
        )

        second = service.import_records(
            _records(symbol.symbol_code),
            uow,
        )

        assert first["imported"] == 1
        assert first["skipped"] == 0

        assert second["imported"] == 0
        assert second["skipped"] == 1
    finally:
        uow.rollback()
        uow.close()


def test_unknown_symbol_is_rejected(db_session):
    service = UniverseMasterService()

    uow = UnitOfWork()
    try:
        with pytest.raises(
            ValueError,
            match="Unknown symbol_code",
        ):
            service.import_records(
                _records("DOES_NOT_EXIST"),
                uow,
            )
    finally:
        uow.rollback()
        uow.close()


def test_multiple_universe_codes_are_rejected(db_session):
    service = UniverseMasterService()

    uow = UnitOfWork()
    try:
        symbol1 = _create_symbol(uow, "TESTIMP3")
        symbol2 = _create_symbol(uow, "TESTIMP4")

        records = _records(
            symbol1.symbol_code,
            universe_code="TEST500",
        )

        records.append(
            _records(
                symbol2.symbol_code,
                universe_code="NIFTY500",
            )[0]
        )

        with pytest.raises(
            ValueError,
            match="exactly one universe_code",
        ):
            service.import_records(records, uow)
    finally:
        uow.rollback()
        uow.close()


def test_universe_metadata_mismatch_is_rejected(db_session):
    service = UniverseMasterService()

    uow = UnitOfWork()
    try:
        symbol = _create_symbol(uow, "TESTIMP5")

        service.import_records(
            _records(symbol.symbol_code),
            uow,
        )

        with pytest.raises(
            ValueError,
            match="Universe metadata mismatch",
        ):
            service.import_records(
                _records(
                    symbol.symbol_code,
                    universe_name="Different Universe",
                ),
                uow,
            )
    finally:
        uow.rollback()
        uow.close()


def test_historical_membership_is_preserved(db_session):
    service = UniverseMasterService()

    uow = UnitOfWork()
    try:
        symbol = _create_symbol(uow, "TESTIMP6")

        first = service.import_records(
            _records(
                symbol.symbol_code,
                effective_from=date(2026, 1, 1),
                effective_to=date(2026, 6, 30),
            ),
            uow,
        )

        second = service.import_records(
            _records(
                symbol.symbol_code,
                effective_from=date(2026, 7, 1),
                effective_to=None,
            ),
            uow,
        )

        assert first["imported"] == 1
        assert second["imported"] == 1

        memberships = uow.universes.get_symbol_memberships(
            symbol.symbol_id,
            as_of_date=date(2026, 6, 30),
        )

        assert len(memberships) == 1
        assert memberships[0].effective_from == date(2026, 1, 1)

        memberships = uow.universes.get_symbol_memberships(
            symbol.symbol_id,
            as_of_date=date(2026, 7, 1),
        )

        assert len(memberships) == 1
        assert memberships[0].effective_from == date(2026, 7, 1)
    finally:
        uow.rollback()
        uow.close()


def test_invalid_date_range_is_rejected(db_session):
    service = UniverseMasterService()

    uow = UnitOfWork()
    try:
        symbol = _create_symbol(uow, "TESTIMP7")

        with pytest.raises(
            ValueError,
            match="effective_to cannot be earlier",
        ):
            service.import_records(
                _records(
                    symbol.symbol_code,
                    effective_from=date(2026, 7, 1),
                    effective_to=date(2026, 6, 30),
                ),
                uow,
            )
    finally:
        uow.rollback()
        uow.close()


def test_missing_effective_from_is_rejected(db_session):
    service = UniverseMasterService()

    uow = UnitOfWork()
    try:
        symbol = _create_symbol(uow, "TESTIMP8")

        records = _records(symbol.symbol_code)
        records[0]["effective_from"] = None

        with pytest.raises(
            ValueError,
            match="effective_from is required",
        ):
            service.import_records(records, uow)
    finally:
        uow.rollback()
        uow.close()
