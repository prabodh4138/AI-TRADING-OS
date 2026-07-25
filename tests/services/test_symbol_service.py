"""
AI Trading Operating System
Symbol Service Tests
"""

from uuid import uuid4

import pytest

from dto.symbol_dto import SymbolCreateDTO
from services.symbol_service import SymbolService
from validators.base_validator import ValidationError


@pytest.fixture
def service():
    return SymbolService()


def create_dto(symbol_code: str | None = None) -> SymbolCreateDTO:
    """
    Creates a unique DTO every time to avoid
    UNIQUE constraint violations in PostgreSQL.
    """

    uid = uuid4().hex[:12].upper()

    if symbol_code is None:
        symbol_code = f"TEST_{uid}"

    return SymbolCreateDTO(
        symbol_code=symbol_code,
        symbol_name=f"Company {uid}",
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


def test_create_symbol(service):

    dto = create_dto()

    symbol = service.create_symbol(dto)

    assert symbol is not None
    assert symbol.symbol_code == dto.symbol_code


def test_duplicate_symbol(service):

    dto = create_dto()

    service.create_symbol(dto)

    with pytest.raises(ValidationError):
        service.create_symbol(dto)


def test_get_symbol(service):

    dto = create_dto()

    symbol = service.create_symbol(dto)

    result = service.get_symbol(symbol.symbol_id)

    assert result is not None
    assert result.symbol_id == symbol.symbol_id


def test_get_by_symbol_code(service):

    dto = create_dto()

    service.create_symbol(dto)

    result = service.get_by_symbol_code(dto.symbol_code)

    assert result is not None
    assert result.symbol_code == dto.symbol_code


def test_activate_deactivate(service):

    dto = create_dto()

    symbol = service.create_symbol(dto)

    service.deactivate_symbol(symbol.symbol_id)

    result = service.get_symbol(symbol.symbol_id)

    assert result.is_active is False

    service.activate_symbol(symbol.symbol_id)

    result = service.get_symbol(symbol.symbol_id)

    assert result.is_active is True


def test_delete_symbol(service):

    dto = create_dto()

    symbol = service.create_symbol(dto)

    service.delete_symbol(symbol.symbol_id)

    result = service.get_symbol(symbol.symbol_id)

    assert result is None


def test_search(service):

    dto = create_dto()

    service.create_symbol(dto)

    result = service.search(dto.symbol_code[:8])

    assert len(result) >= 1