from decimal import Decimal

import pytest

from database.models.symbol import Symbol
from database.repositories.symbol_repository import SymbolRepository


@pytest.fixture
def repository(db_session):
    return SymbolRepository(db_session)


def test_get_by_symbol_code(repository):
    symbol = Symbol(
        symbol_code="TEST001",
        symbol_name="Test Company",
        exchange="NSE",
        instrument_type="EQUITY",
        isin="INETEST001",
        lot_size=1,
        tick_size=Decimal("0.05"),
        face_value=Decimal("10.00"),
    )

    repository.add(symbol)
    repository.flush()

    result = repository.get_by_symbol_code("TEST001")

    assert result is not None
    assert result.symbol_code == "TEST001"


def test_get_by_exchange(repository):
    repository.add(
        Symbol(
            symbol_code="TESTNSE",
            symbol_name="NSE Company",
            exchange="NSE",
            instrument_type="EQUITY",
            isin="INETESTNSE",
            lot_size=1,
            tick_size=Decimal("0.05"),
            face_value=Decimal("10.00"),
        )
    )
    repository.flush()

    results = repository.get_by_exchange("NSE")

    assert any(symbol.symbol_code == "TESTNSE" for symbol in results)


def test_get_symbol_id_map(repository):
    symbol = Symbol(
        symbol_code="TESTMAP",
        symbol_name="Map Company",
        exchange="NSE",
        instrument_type="EQUITY",
        isin="INETESTMAP",
        lot_size=1,
        tick_size=Decimal("0.05"),
        face_value=Decimal("10.00"),
    )

    repository.add(symbol)
    repository.flush()

    result = repository.get_symbol_id_map(["TESTMAP"])

    assert "TESTMAP" in result
    assert result["TESTMAP"] == symbol.symbol_id


def test_bulk_upsert_inserts_new_symbols(repository):
    records = [
        {
            "symbol_code": "TESTNEW1",
            "symbol_name": "New Company 1",
            "exchange": "NSE",
            "instrument_type": "EQUITY",
            "sector": None,
            "industry": None,
            "isin": "INETESTNEW1",
            "lot_size": 1,
            "tick_size": Decimal("0.05"),
            "face_value": Decimal("10.00"),
            "listing_date": None,
            "is_fno": False,
        },
        {
            "symbol_code": "TESTNEW2",
            "symbol_name": "New Company 2",
            "exchange": "NSE",
            "instrument_type": "EQUITY",
            "sector": None,
            "industry": None,
            "isin": "INETESTNEW2",
            "lot_size": 1,
            "tick_size": Decimal("0.05"),
            "face_value": Decimal("5.00"),
            "listing_date": None,
            "is_fno": False,
        },
    ]

    result = repository.bulk_upsert(records)

    assert result["received"] == 2
    assert result["affected"] == 2

    first = repository.get_by_symbol_code("TESTNEW1")
    second = repository.get_by_symbol_code("TESTNEW2")

    assert first is not None
    assert second is not None
    assert first.symbol_name == "New Company 1"
    assert second.symbol_name == "New Company 2"


def test_bulk_upsert_updates_existing_symbol(repository):
    existing = Symbol(
        symbol_code="TESTUPDATE",
        symbol_name="Original Company Name",
        exchange="NSE",
        instrument_type="EQUITY",
        sector="Original Sector",
        industry="Original Industry",
        isin="INETESTUPDATE1",
        lot_size=1,
        tick_size=Decimal("0.05"),
        face_value=Decimal("10.00"),
        listing_date=None,
        is_fno=False,
    )

    repository.add(existing)
    repository.flush()

    original_id = existing.symbol_id

    records = [
        {
            "symbol_code": "TESTUPDATE",
            "symbol_name": "Updated Company Name",
            "exchange": "NSE",
            "instrument_type": "EQUITY",
            "sector": "Updated Sector",
            "industry": "Updated Industry",
            "isin": "INETESTUPDATE1",
            "lot_size": 1,
            "tick_size": Decimal("0.10"),
            "face_value": Decimal("5.00"),
            "listing_date": None,
            "is_fno": True,
        }
    ]

    result = repository.bulk_upsert(records)

    assert result["received"] == 1
    assert result["affected"] == 1

    updated = repository.get_by_symbol_code("TESTUPDATE")

    assert updated is not None
    assert updated.symbol_id == original_id

    # NSE-owned fields update.
    assert updated.symbol_name == "Updated Company Name"
    assert updated.exchange == "NSE"
    assert updated.instrument_type == "EQUITY"
    assert updated.isin == "INETESTUPDATE1"
    assert updated.lot_size == 1
    assert updated.tick_size == Decimal("0.10")
    assert updated.face_value == Decimal("5.00")

    # Enrichment fields are preserved.
    assert updated.sector == "Original Sector"
    assert updated.industry == "Original Industry"
    assert updated.is_fno is False


def test_bulk_upsert_does_not_delete_missing_symbols(repository):
    existing = Symbol(
        symbol_code="TESTKEEP",
        symbol_name="Keep Company",
        exchange="NSE",
        instrument_type="EQUITY",
        isin="INETESTKEEP",
        lot_size=1,
        tick_size=Decimal("0.05"),
        face_value=Decimal("10.00"),
    )

    repository.add(existing)
    repository.flush()

    repository.bulk_upsert(
        [
            {
                "symbol_code": "TESTOTHER",
                "symbol_name": "Other Company",
                "exchange": "NSE",
                "instrument_type": "EQUITY",
                "sector": None,
                "industry": None,
                "isin": "INETESTOTHER",
                "lot_size": 1,
                "tick_size": Decimal("0.05"),
                "face_value": Decimal("10.00"),
                "listing_date": None,
                "is_fno": False,
            }
        ]
    )

    kept = repository.get_by_symbol_code("TESTKEEP")

    assert kept is not None
    assert kept.symbol_name == "Keep Company"


def test_bulk_upsert_empty_records(repository):
    result = repository.bulk_upsert([])

    assert result["received"] == 0
    assert result["affected"] == 0


def test_get_active_symbols(repository):
    repository.add(
        Symbol(
            symbol_code="TESTACTIVE",
            symbol_name="Active Company",
            exchange="NSE",
            instrument_type="EQUITY",
            isin="INETESTACTIVE",
            lot_size=1,
            tick_size=Decimal("0.05"),
            face_value=Decimal("10.00"),
        )
    )
    repository.flush()

    results = repository.get_active_symbols()

    assert any(symbol.symbol_code == "TESTACTIVE" for symbol in results)


def test_search_by_symbol_code(repository):
    repository.add(
        Symbol(
            symbol_code="SEARCHABC",
            symbol_name="Search Company",
            exchange="NSE",
            instrument_type="EQUITY",
            isin="INESEARCHABC",
            lot_size=1,
            tick_size=Decimal("0.05"),
            face_value=Decimal("10.00"),
        )
    )
    repository.flush()

    results = repository.search("SEARCHABC")

    assert any(symbol.symbol_code == "SEARCHABC" for symbol in results)


def test_search_by_symbol_name(repository):
    repository.add(
        Symbol(
            symbol_code="SEARCHNAME",
            symbol_name="Unique Search Company",
            exchange="NSE",
            instrument_type="EQUITY",
            isin="INESEARCHNAME",
            lot_size=1,
            tick_size=Decimal("0.05"),
            face_value=Decimal("10.00"),
        )
    )
    repository.flush()

    results = repository.search("Unique Search Company")

    assert any(symbol.symbol_code == "SEARCHNAME" for symbol in results)


def test_exists_by_symbol_code(repository):
    repository.add(
        Symbol(
            symbol_code="TESTEXISTS",
            symbol_name="Exists Company",
            exchange="NSE",
            instrument_type="EQUITY",
            isin="INETESTEXISTS",
            lot_size=1,
            tick_size=Decimal("0.05"),
            face_value=Decimal("10.00"),
        )
    )
    repository.flush()

    assert repository.exists_by_symbol_code("TESTEXISTS") is True
    assert repository.exists_by_symbol_code("DOESNOTEXIST") is False


def test_get_all_symbol_codes(repository):
    repository.add(
        Symbol(
            symbol_code="TESTCODE1",
            symbol_name="Company 1",
            exchange="NSE",
            instrument_type="EQUITY",
            isin="INETESTCODE1",
            lot_size=1,
            tick_size=Decimal("0.05"),
            face_value=Decimal("10.00"),
        )
    )
    repository.add(
        Symbol(
            symbol_code="TESTCODE2",
            symbol_name="Company 2",
            exchange="NSE",
            instrument_type="EQUITY",
            isin="INETESTCODE2",
            lot_size=1,
            tick_size=Decimal("0.05"),
            face_value=Decimal("10.00"),
        )
    )
    repository.flush()

    codes = repository.get_all_symbol_codes()

    assert "TESTCODE1" in codes
    assert "TESTCODE2" in codes


def test_count_by_exchange(repository):
    repository.add(
        Symbol(
            symbol_code="TESTCOUNT",
            symbol_name="Count Company",
            exchange="NSE",
            instrument_type="EQUITY",
            isin="INETESTCOUNT",
            lot_size=1,
            tick_size=Decimal("0.05"),
            face_value=Decimal("10.00"),
        )
    )
    repository.flush()

    assert repository.count_by_exchange("NSE") >= 1
