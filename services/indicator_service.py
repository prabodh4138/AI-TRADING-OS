"""
AI Trading Operating System
Indicator Service
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
from uuid import UUID

from database.models.indicator_data import IndicatorData
from database.unit_of_work import UnitOfWork

from dto.indicator_dto import IndicatorDTO

from services.base_service import BaseService

from validators.indicator_validator import IndicatorValidator


class IndicatorService(BaseService):
    """
    Business Service for Indicator Data.
    """

    def __init__(self):
        super().__init__()
        self.validator = IndicatorValidator()

    # ==========================================================
    # Create
    # ==========================================================

    def create_indicator(
        self,
        dto: IndicatorDTO,
    ) -> IndicatorData:
        """
        Create a new indicator record.
        """

        indicator = IndicatorData(
            **asdict(dto)
        )

        self.validator.validate(indicator)

        with UnitOfWork() as uow:

            if uow.indicators.exists_for_symbol_and_date(
                dto.symbol_id,
                dto.trading_date,
            ):
                raise ValueError(
                    "Indicator already exists for this symbol and trading date."
                )

            uow.indicators.add(indicator)

            uow.flush()

            return indicator

    # ==========================================================
    # Read
    # ==========================================================

    def get_indicator(
        self,
        indicator_id: UUID,
    ) -> IndicatorData | None:
        """
        Get indicator by primary key.
        """

        with UnitOfWork() as uow:
            return uow.indicators.get_by_id(indicator_id)

    def get_latest(
        self,
        symbol_id: UUID,
    ) -> IndicatorData | None:
        """
        Get latest indicator for a symbol.
        """

        with UnitOfWork() as uow:
            return uow.indicators.get_latest(symbol_id)

    def get_by_symbol(
        self,
        symbol_id: UUID,
    ):
        """
        Get complete indicator history.
        """

        with UnitOfWork() as uow:
            return uow.indicators.get_by_symbol(symbol_id)

    def get_by_symbol_and_date(
        self,
        symbol_id: UUID,
        trading_date: date,
    ) -> IndicatorData | None:
        """
        Get indicator for one trading date.
        """

        with UnitOfWork() as uow:
            return uow.indicators.get_by_symbol_and_date(
                symbol_id,
                trading_date,
            )

    # ==========================================================
    # Statistics
    # ==========================================================

    def count_by_symbol(
        self,
        symbol_id: UUID,
    ) -> int:
        """
        Count indicator rows for a symbol.
        """

        with UnitOfWork() as uow:
            return uow.indicators.count_by_symbol(
                symbol_id
            )

    # ==========================================================
    # Delete
    # ==========================================================

    def delete_indicator(
        self,
        indicator_id: UUID,
    ) -> None:
        """
        Delete a single indicator.
        """

        with UnitOfWork() as uow:

            indicator = uow.indicators.get_by_id(
                indicator_id
            )

            self.require_not_none(
                indicator,
                "Indicator",
            )

            uow.indicators.delete(
                indicator
            )

            uow.flush()

    def delete_by_symbol(
        self,
        symbol_id: UUID,
    ) -> int:
        """
        Delete all indicators for a symbol.
        """

        with UnitOfWork() as uow:

            deleted = uow.indicators.delete_by_symbol(
                symbol_id
            )

            uow.flush()

            return deleted