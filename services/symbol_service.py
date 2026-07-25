"""
Symbol Service
"""

from dto.symbol_dto import SymbolCreateDTO
from database.models.symbol import Symbol
from database.unit_of_work import UnitOfWork
from validators.symbol_validator import SymbolValidator
from validators.base_validator import ValidationError


class SymbolService:

    def __init__(self):

        self.validator = SymbolValidator()

    def create_symbol(self, dto: SymbolCreateDTO):

        # Validate DTO
        self.validator.validate(dto)

        with UnitOfWork() as uow:

            existing = uow.symbols.get_by_symbol_code(dto.symbol_code)

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

            return symbol