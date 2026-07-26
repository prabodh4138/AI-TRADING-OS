"""
AI Trading Operating System
Indicator Service Tests
"""

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from dto.symbol_dto import SymbolCreateDTO
from dto.indicator_dto import IndicatorDTO

from services.symbol_service import SymbolService
from services.indicator_service import IndicatorService


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------

@pytest.fixture
def symbol_service():
    return SymbolService()


@pytest.fixture
def indicator_service():
    return IndicatorService()


@pytest.fixture
def symbol(symbol_service):

    uid = uuid4().hex[:10].upper()

    dto = SymbolCreateDTO(
        symbol_code=f"IND_{uid}",
        symbol_name=f"Indicator Test {uid}",
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


# ---------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------

def create_indicator_dto(symbol_id):

    return IndicatorDTO(
        symbol_id=symbol_id,
        trading_date=date.today(),

        sma20=Decimal("100"),
        sma50=Decimal("101"),
        sma100=Decimal("102"),
        sma200=Decimal("103"),

        ema9=Decimal("100"),
        ema20=Decimal("101"),
        ema50=Decimal("102"),
        ema100=Decimal("103"),
        ema200=Decimal("104"),

        rsi14=Decimal("55"),

        macd=Decimal("1.25"),
        macd_signal=Decimal("1.10"),
        macd_histogram=Decimal("0.15"),

        atr14=Decimal("3.50"),

        bb_upper=Decimal("110"),
        bb_middle=Decimal("105"),
        bb_lower=Decimal("100"),

        adx14=Decimal("25"),
        plus_di=Decimal("28"),
        minus_di=Decimal("18"),

        obv=Decimal("100000"),
        volume_sma20=Decimal("120000"),
        relative_volume=Decimal("1.15"),

        roc10=Decimal("5"),
        momentum10=Decimal("7"),

        stochastic_k=Decimal("82"),
        stochastic_d=Decimal("79"),

        trend_score=Decimal("8.5"),
        momentum_score=Decimal("7.8"),
    )


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

def test_create_indicator(
    indicator_service,
    symbol,
):

    dto = create_indicator_dto(symbol.symbol_id)

    indicator = indicator_service.create_indicator(dto)

    assert indicator is not None
    assert indicator.symbol_id == symbol.symbol_id


def test_duplicate_indicator(
    indicator_service,
    symbol,
):

    dto = create_indicator_dto(symbol.symbol_id)

    indicator_service.create_indicator(dto)

    with pytest.raises(ValueError):
        indicator_service.create_indicator(dto)


def test_get_indicator(
    indicator_service,
    symbol,
):

    dto = create_indicator_dto(symbol.symbol_id)

    indicator = indicator_service.create_indicator(dto)

    result = indicator_service.get_indicator(
        indicator.indicator_data_id
    )

    assert result is not None
    assert result.indicator_data_id == indicator.indicator_data_id


def test_get_latest(
    indicator_service,
    symbol,
):

    dto = create_indicator_dto(symbol.symbol_id)

    indicator_service.create_indicator(dto)

    latest = indicator_service.get_latest(
        symbol.symbol_id
    )

    assert latest is not None
    assert latest.symbol_id == symbol.symbol_id


def test_get_by_symbol(
    indicator_service,
    symbol,
):

    dto = create_indicator_dto(symbol.symbol_id)

    indicator_service.create_indicator(dto)

    result = indicator_service.get_by_symbol(
        symbol.symbol_id
    )

    assert len(result) >= 1


def test_get_by_symbol_and_date(
    indicator_service,
    symbol,
):

    dto = create_indicator_dto(symbol.symbol_id)

    indicator_service.create_indicator(dto)

    result = indicator_service.get_by_symbol_and_date(
        symbol.symbol_id,
        dto.trading_date,
    )

    assert result is not None


def test_count_by_symbol(
    indicator_service,
    symbol,
):

    dto = create_indicator_dto(symbol.symbol_id)

    indicator_service.create_indicator(dto)

    count = indicator_service.count_by_symbol(
        symbol.symbol_id
    )

    assert count >= 1


def test_delete_indicator(
    indicator_service,
    symbol,
):

    dto = create_indicator_dto(symbol.symbol_id)

    indicator = indicator_service.create_indicator(dto)

    indicator_service.delete_indicator(
        indicator.indicator_data_id
    )

    deleted = indicator_service.get_indicator(
        indicator.indicator_data_id
    )

    assert deleted is None


def test_delete_by_symbol(
    indicator_service,
    symbol,
):

    dto = create_indicator_dto(symbol.symbol_id)

    indicator_service.create_indicator(dto)

    deleted = indicator_service.delete_by_symbol(
        symbol.symbol_id
    )

    assert deleted >= 1