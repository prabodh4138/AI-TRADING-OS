"""
AI Trading Operating System
Indicator Repository
"""

from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import delete, desc, select

from database.models.indicator_data import IndicatorData
from database.repositories.base_repository import BaseRepository


class IndicatorRepository(BaseRepository[IndicatorData]):
    """
    Repository for IndicatorData.

    Only indicator-specific queries should exist here.
    Generic CRUD functionality is inherited from BaseRepository.
    """

    model = IndicatorData

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_by_symbol(
        self,
        symbol_id: UUID,
    ) -> Sequence[IndicatorData]:
        """
        Return all indicator records for a symbol.
        """

        stmt = (
            select(IndicatorData)
            .where(
                IndicatorData.symbol_id == symbol_id
            )
            .order_by(
                IndicatorData.trading_date
            )
        )

        return self.session.scalars(stmt).all()

    def get_latest(
        self,
        symbol_id: UUID,
    ) -> IndicatorData | None:
        """
        Return latest indicator record for a symbol.
        """

        stmt = (
            select(IndicatorData)
            .where(
                IndicatorData.symbol_id == symbol_id
            )
            .order_by(
                desc(IndicatorData.trading_date)
            )
            .limit(1)
        )

        return self.session.scalar(stmt)

    def get_by_symbol_and_date(
        self,
        symbol_id: UUID,
        trading_date,
    ) -> IndicatorData | None:
        """
        Return indicator record for a symbol on a specific trading date.
        """

        stmt = (
            select(IndicatorData)
            .where(
                IndicatorData.symbol_id == symbol_id,
                IndicatorData.trading_date == trading_date,
            )
        )

        return self.session.scalar(stmt)

    def delete_by_symbol(
        self,
        symbol_id: UUID,
    ) -> int:
        """
        Delete all indicator records for a symbol.

        Returns:
            Number of deleted rows.
        """

        stmt = (
            delete(IndicatorData)
            .where(
                IndicatorData.symbol_id == symbol_id
            )
        )

        result = self.session.execute(stmt)

        return result.rowcount or 0

    def exists_for_symbol_and_date(
        self,
        symbol_id: UUID,
        trading_date,
    ) -> bool:
        """
        Check whether an indicator record already exists.
        """

        stmt = (
            select(IndicatorData.indicator_data_id)
            .where(
                IndicatorData.symbol_id == symbol_id,
                IndicatorData.trading_date == trading_date,
            )
            .limit(1)
        )

        return self.session.scalar(stmt) is not None

    def count_by_symbol(
        self,
        symbol_id: UUID,
    ) -> int:
        """
        Return total indicator records for a symbol.
        """

        stmt = (
            select(IndicatorData)
            .where(
                IndicatorData.symbol_id == symbol_id
            )
        )

        return len(self.session.scalars(stmt).all())