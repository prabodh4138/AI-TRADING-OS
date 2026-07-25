"""
Market Data Validator
"""

from __future__ import annotations

from datetime import date

from dto.market_data_dto import MarketDataCreateDTO

from validators.base_validator import (
    BaseValidator,
    ValidationError,
)


class MarketDataValidator(BaseValidator):

    def validate(
        self,
        dto: MarketDataCreateDTO,
    ):

        if dto.trading_date > date.today():

            raise ValidationError(
                "Trading date cannot be in the future."
            )

        if dto.high_price < dto.low_price:

            raise ValidationError(
                "High price cannot be lower than low price."
            )

        if dto.close_price > dto.high_price:

            raise ValidationError(
                "Close price cannot exceed high price."
            )

        if dto.close_price < dto.low_price:

            raise ValidationError(
                "Close price cannot be below low price."
            )

        if dto.volume < 0:

            raise ValidationError(
                "Volume cannot be negative."
            )