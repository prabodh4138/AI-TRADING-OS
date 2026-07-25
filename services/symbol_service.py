"""
AI Trading Operating System
Symbol Service

Business Service for Symbol Management
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from database.models.symbol import Symbol
from database.unit_of_work import UnitOfWork

from dto.symbol_dto import SymbolCreateDTO

from services.base_service import BaseService

from validators.symbol_validator import SymbolValidator
from validators.base_validator import ValidationError


class SymbolService(BaseService):
    """
    Business Service for Symbol operations.
    """

    def __init__(self) -> None:
        super().__init__()
        self.validator = SymbolValidator()

    # ---------------------------------------------------------
    # Create Symbol
    # ---------------------------------------------------------

    def create_symbol(
        self,
        dto: SymbolCreateDTO,
    ) -> Symbol:

        self.validator.validate(dto)

        with UnitOfWork() as uow:

            existing = uow.symbols.get_by_symbol_code(
                dto.symbol_code
            )

            if existing:
                raise ValidationError(
                    f"Symbol '{dto.symbol_code}' already exists."
                )

            symbol = Symbol(
                symbol_code=dto.symbol_code,
                symbol_name=dto.symbol_name,
                exchange=dto.exchange,
                instrument_type=dto.instrument_type,
                sector=dto.sector,
                industry=dto.industry,
                isin=dto.isin,
                lot_size=dto.lot_size,
                tick_size=dto.tick_size,
                face_value=dto.face_value,
                listing_date=dto.listing_date,
                is_fno=dto.is_fno,
            )

            uow.symbols.add(symbol)

            uow.flush()

            return symbol

    # ---------------------------------------------------------
    # Read
    # ---------------------------------------------------------

    def get_symbol(
        self,
        symbol_id: UUID,
    ) -> Optional[Symbol]:

        with UnitOfWork() as uow:
            return uow.symbols.get_by_id(symbol_id)

    def get_by_symbol_code(
        self,
        symbol_code: str,
    ) -> Optional[Symbol]:

        with UnitOfWork() as uow:
            return uow.symbols.get_by_symbol_code(symbol_code)

    def get_all_symbols(self):

        with UnitOfWork() as uow:
            return uow.symbols.get_all()

    def get_active_symbols(self):

        with UnitOfWork() as uow:
            return uow.symbols.get_active_symbols()

    def search(
        self,
        keyword: str,
    ):

        with UnitOfWork() as uow:
            return uow.symbols.search(keyword)

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    def activate_symbol(
        self,
        symbol_id: UUID,
    ) -> None:

        with UnitOfWork() as uow:

            symbol = uow.symbols.get_by_id(symbol_id)

            self.require_not_none(symbol, "Symbol")

            symbol.is_active = True

            uow.flush()

    def deactivate_symbol(
        self,
        symbol_id: UUID,
    ) -> None:

        with UnitOfWork() as uow:

            symbol = uow.symbols.get_by_id(symbol_id)

            self.require_not_none(symbol, "Symbol")

            symbol.is_active = False

            uow.flush()

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete_symbol(
        self,
        symbol_id: UUID,
    ) -> None:

        with UnitOfWork() as uow:

            symbol = uow.symbols.get_by_id(symbol_id)

            self.require_not_none(symbol, "Symbol")

            uow.symbols.delete(symbol)

            uow.flush()