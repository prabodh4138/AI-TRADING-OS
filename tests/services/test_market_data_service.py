"""
AI Trading Operating System
Market Data Service Tests
"""

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from dto.market_data_dto import MarketDataCreateDTO
from dto.symbol_dto import SymbolCreateDTO

from services.market_data_service import MarketDataService
from services.symbol_service import SymbolService

from validators.base_validator import ValidationError


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------

@pytest.fixture
def symbol_service():
    return SymbolService()


@pytest.fixture
def market_service():
    return MarketDataService()


@pytest.fixture
def symbol(symbol_service):
    uid = uuid4().hex[:10].upper()

    dto = SymbolCreateDTO(
        symbol_code=f"MD_{uid}",
        symbol_name=f"Market Test {uid}",
        exchange="NSE",
        instrument_type="EQUITY",
        sector="IT",
        industry="Software",
        isin=f"INE{uid}",
        lot_size=1,
        tick_size=0.05,
        face_value=10,
        listing_date=None,
        is_fno=False,
    )

    return symbol_service.create_symbol(dto)


# ----------------------------------------------------------------------
# Helper
# ----------------------------------------------------------------------

def create_market_dto(symbol_id, trading_date=None):

    if trading_date is None:
        trading_date = date.today()

    return MarketDataCreateDTO(
        symbol_id=symbol_id,
        trading_date=trading_date,

        open_price=Decimal("100"),
        high_price=Decimal("110"),
        low_price=Decimal("95"),
        close_price=Decimal("105"),

        adjusted_close=Decimal("105"),

        volume=100000,

        delivery_volume=50000,
        delivery_percent=Decimal("50.00"),

        turnover=Decimal("1000000"),
        vwap=Decimal("102.50"),

        trade_count=1000,
    )


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def test_create_market_data(
    market_service,
    symbol,
):

    dto = create_market_dto(symbol.symbol_id)

    data = market_service.create_market_data(dto)

    assert data is not None
    assert data.symbol_id == symbol.symbol_id


def test_duplicate_market_data(
    market_service,
    symbol,
):

    dto = create_market_dto(symbol.symbol_id)

    market_service.create_market_data(dto)

    with pytest.raises(ValidationError):
        market_service.create_market_data(dto)


def test_get_market_data(
    market_service,
    symbol,
):

    dto = create_market_dto(symbol.symbol_id)

    data = market_service.create_market_data(dto)

    fetched = market_service.get_market_data(
        data.market_data_id
    )

    assert fetched is not None
    assert fetched.market_data_id == data.market_data_id


def test_get_latest_price(
    market_service,
    symbol,
):

    dto = create_market_dto(symbol.symbol_id)

    market_service.create_market_data(dto)

    latest = market_service.get_latest_price(
        symbol.symbol_id
    )

    assert latest is not None
    assert latest.symbol_id == symbol.symbol_id


def test_get_by_symbol_and_date(
    market_service,
    symbol,
):

    dto = create_market_dto(symbol.symbol_id)

    market_service.create_market_data(dto)

    result = market_service.get_by_symbol_and_date(
        symbol.symbol_id,
        dto.trading_date,
    )

    assert result is not None


def test_price_history(
    market_service,
    symbol,
):

    for i in range(3):

        dto = create_market_dto(
            symbol.symbol_id,
            date.today() - timedelta(days=i),
        )

        market_service.create_market_data(dto)

    history = market_service.get_price_history(
        symbol.symbol_id,
        date.today() - timedelta(days=10),
        date.today(),
    )

    assert len(history) >= 3


def test_count_by_symbol(
    market_service,
    symbol,
):

    dto = create_market_dto(symbol.symbol_id)

    market_service.create_market_data(dto)

    count = market_service.count_by_symbol(
        symbol.symbol_id
    )

    assert count >= 1


def test_delete_market_data(
    market_service,
    symbol,
):

    dto = create_market_dto(symbol.symbol_id)

    data = market_service.create_market_data(dto)

    market_service.delete_market_data(
        data.market_data_id
    )

    deleted = market_service.get_market_data(
        data.market_data_id
    )

    assert deleted is None