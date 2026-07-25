"""
Symbol Validator
"""

from __future__ import annotations

from dto.symbol_dto import SymbolCreateDTO

from validators.base_validator import (
    BaseValidator,
    ValidationError,
)


class SymbolValidator(BaseValidator):

    def validate(self, dto: SymbolCreateDTO):

        if not dto.symbol_code.strip():
            raise ValidationError(
                "Symbol Code cannot be empty."
            )

        if dto.symbol_code != dto.symbol_code.upper():
            raise ValidationError(
                "Symbol Code must be uppercase."
            )

        if dto.lot_size <= 0:
            raise ValidationError(
                "Lot Size must be greater than zero."
            )

        if dto.tick_size <= 0:
            raise ValidationError(
                "Tick Size must be positive."
            )

        if dto.face_value <= 0:
            raise ValidationError(
                "Face Value must be positive."
            )