from __future__ import annotations

from database.models.indicator_data import IndicatorData


class IndicatorValidator:
    """Validation rules for indicator data."""

    @staticmethod
    def validate(indicator: IndicatorData) -> None:
        if indicator.symbol_id is None:
            raise ValueError("symbol_id is required.")

        if indicator.trading_date is None:
            raise ValueError("trading_date is required.")