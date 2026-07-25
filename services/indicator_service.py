from __future__ import annotations

from datetime import date

from database.models.indicator_data import IndicatorData
from database.repositories.indicator_repository import IndicatorRepository


class IndicatorService:
    """Business service for IndicatorData."""

    def __init__(self, repository: IndicatorRepository):
        self.repository = repository

    def save_indicator(self, indicator: IndicatorData) -> IndicatorData:
        return self.repository.save(indicator)

    def save_indicators(
        self,
        indicators: list[IndicatorData],
    ) -> None:
        self.repository.save_all(indicators)

    def get_history(
        self,
        symbol_id,
    ):
        return self.repository.get_by_symbol(symbol_id)

    def get_indicator(
        self,
        symbol_id,
        trading_date: date,
    ):
        return self.repository.get_by_symbol_and_date(
            symbol_id,
            trading_date,
        )

    def delete_history(
        self,
        symbol_id,
    ) -> None:
        self.repository.delete_by_symbol(symbol_id)