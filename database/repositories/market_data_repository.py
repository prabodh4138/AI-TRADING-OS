"""
AI Trading Operating System
Market Data Repository
"""

from __future__ import annotations

from datetime import date
from uuid import UUID
from collections.abc import Iterable
import logging

import pandas as pd
from sqlalchemy import desc, distinct, func, select

from database.models.market_data import MarketData
from database.repositories.base_repository import BaseRepository


class MarketDataRepository(BaseRepository[MarketData]):
    """
    Repository for MarketData.

    Contains only market-data-specific queries.
    """

    model = MarketData

    DEFAULT_BATCH_SIZE = 1000

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
            select(func.count())
            .select_from(MarketData)
            .where(
                MarketData.symbol_id == symbol_id
            )
        )

        return self.session.scalar(stmt) or 0

    # ------------------------------------------------------------------
    # Date Range
    # ------------------------------------------------------------------

    def get_latest_trading_date(
        self,
    ) -> date | None:
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

    def get_earliest_trading_date(
        self,
    ) -> date | None:
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
    # ------------------------------------------------------------------
    # Bulk Insert
    # ------------------------------------------------------------------

    def bulk_insert(
        self,
        entities: Iterable[MarketData],
        *,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> int:
        """
        Insert MarketData entities in batches.

        Parameters
        ----------
        entities : Iterable[MarketData]
            MarketData ORM objects.

        batch_size : int
            Number of rows inserted per batch.

        Returns
        -------
        int
            Number of inserted records.
        """

        logger = logging.getLogger(
            self.__class__.__name__
        )

        entity_list = list(entities)

        if not entity_list:
            logger.info(
                "No MarketData entities received for bulk insert."
            )
            return 0

        inserted = 0

        for start in range(
            0,
            len(entity_list),
            batch_size,
        ):

            batch = entity_list[
                start:start + batch_size
            ]

            self.add_many(batch)

            # Flush only.
            # UnitOfWork owns commit()/rollback().
            self.flush()

            inserted += len(batch)

            logger.info(
                "Inserted batch (%d rows).",
                len(batch),
            )

        logger.info(
            "Bulk insert completed (%d rows).",
            inserted,
        )

        return inserted
    # ------------------------------------------------------------------
    # DataFrame Bulk Import
    # ------------------------------------------------------------------

    def bulk_insert_dataframe(
        self,
        dataframe: pd.DataFrame,
        *,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> int:
        """
        Convert a transformed DataFrame into MarketData ORM
        objects and persist them using bulk_insert().

        NOTE
        ----
        This method is kept temporarily for backward compatibility.
        In a future sprint, DataFrame-to-ORM conversion will be moved
        into a dedicated MarketDataMapper service.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Transformed market data.

        batch_size : int
            Number of records inserted per batch.

        Returns
        -------
        int
            Number of inserted rows.
        """

        logger = logging.getLogger(
            self.__class__.__name__
        )

        if dataframe.empty:
            logger.info(
                "Received empty dataframe."
            )
            return 0

        entities: list[MarketData] = []

        for row in dataframe.itertuples(index=False):

            entity = MarketData(
                symbol_id=row.symbol_id,
                trading_date=row.trading_date,
                open_price=row.open,
                high_price=row.high,
                low_price=row.low,
                close_price=row.close,
                last_price=row.last,
                previous_close=row.prevclose,
                total_traded_quantity=row.tottrdqty,
                total_traded_value=row.tottrdval,
            )

            entities.append(entity)

        logger.info(
            "Converted %d dataframe rows into ORM entities.",
            len(entities),
        )

        return self.bulk_insert(
            entities,
            batch_size=batch_size,
        )