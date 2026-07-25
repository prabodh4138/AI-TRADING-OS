"""
AI Trading Operating System
Market Data Repository
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import desc, distinct, select

from database.models.market_data import MarketData
from database.repositories.base_repository import BaseRepository


class MarketDataRepository(BaseRepository[MarketData]):
    """
    Repository for MarketData.
    Contains only market-data-specific queries.
    """

    model = MarketData

    # ------------------------------------------------------------------
    # Latest Price
    # ------------------------------------------------------------------

    def get_latest_price(
        self,
        symbol_id: UUID,
    ) -> MarketData | None:
        """
        Return latest available market data for a symbol.
        """

        stmt = (
            select(MarketData)
            .where(
                MarketData.symbol_id == symbol_id
            )
            .order_by(
                desc(MarketData.trading_date)
            )
            .limit(1)
        )

        return self.session.scalar(stmt)

    # ------------------------------------------------------------------
    # Price History
    # ------------------------------------------------------------------

    def get_price_history(
        self,
        symbol_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[MarketData]:
        """
        Return market data between two dates.
        """

        stmt = (
            select(MarketData)
            .where(
                MarketData.symbol_id == symbol_id,
                MarketData.trading_date >= start_date,
                MarketData.trading_date <= end_date,
            )
            .order_by(
                MarketData.trading_date
            )
        )

        return self.session.scalars(stmt).all()

    def get_price_history_by_symbol(
        self,
        symbol_id: UUID,
    ) -> list[MarketData]:
        """
        Return complete historical market data for a symbol.
        """

        stmt = (
            select(MarketData)
            .where(
                MarketData.symbol_id == symbol_id
            )
            .order_by(
                MarketData.trading_date
            )
        )

        return self.session.scalars(stmt).all()

    # ------------------------------------------------------------------
    # Trading Date Queries
    # ------------------------------------------------------------------

    def get_by_symbol_and_date(
        self,
        symbol_id: UUID,
        trading_date: date,
    ) -> MarketData | None:
        """
        Return market data for a symbol on a specific trading date.
        """

        stmt = (
            select(MarketData)
            .where(
                MarketData.symbol_id == symbol_id,
                MarketData.trading_date == trading_date,
            )
        )

        return self.session.scalar(stmt)

    def exists_for_symbol_and_date(
        self,
        symbol_id: UUID,
        trading_date: date,
    ) -> bool:
        """
        Check whether market data exists.
        """

        stmt = (
            select(MarketData.market_data_id)
            .where(
                MarketData.symbol_id == symbol_id,
                MarketData.trading_date == trading_date,
            )
            .limit(1)
        )

        return self.session.scalar(stmt) is not None

    # ------------------------------------------------------------------
    # Symbol Queries
    # ------------------------------------------------------------------

    def get_all_symbol_ids(self) -> list[UUID]:
        """
        Return all distinct symbol IDs having market data.
        """

        stmt = (
            select(
                distinct(MarketData.symbol_id)
            )
            .order_by(
                MarketData.symbol_id
            )
        )

        return list(
            self.session.scalars(stmt).all()
        )

    def count_by_symbol(
        self,
        symbol_id: UUID,
    ) -> int:
        """
        Return number of records for one symbol.
        """

        stmt = (
            select(MarketData)
            .where(
                MarketData.symbol_id == symbol_id
            )
        )

        return len(
            self.session.scalars(stmt).all()
        )

    # ------------------------------------------------------------------
    # Date Range
    # ------------------------------------------------------------------

    def get_latest_trading_date(self) -> date | None:
        """
        Return latest trading date in database.
        """

        stmt = (
            select(MarketData.trading_date)
            .order_by(
                desc(MarketData.trading_date)
            )
            .limit(1)
        )

        return self.session.scalar(stmt)

    def get_earliest_trading_date(self) -> date | None:
        """
        Return earliest trading date in database.
        """

        stmt = (
            select(MarketData.trading_date)
            .order_by(
                MarketData.trading_date
            )
            .limit(1)
        )

        return self.session.scalar(stmt)