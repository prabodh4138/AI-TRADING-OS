"""
AI Trading Operating System
Market Data Repository
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import desc, select

from database.models.market_data import MarketData
from database.repositories.base_repository import BaseRepository
from sqlalchemy import distinct


class MarketDataRepository(BaseRepository[MarketData]):

    model = MarketData

    def get_latest_price(self, symbol_id):
        stmt = (
            select(MarketData)
            .where(MarketData.symbol_id == symbol_id)
            .order_by(desc(MarketData.trading_date))
            .limit(1)
        )
        return self.session.scalar(stmt)

        def get_price_history(
        self,
        symbol_id,
        start_date: date,
        end_date: date,
    ):
         stmt = (
            select(MarketData)
            .where(
                MarketData.symbol_id == symbol_id,
                MarketData.trading_date >= start_date,
                MarketData.trading_date <= end_date,
            )
            .order_by(MarketData.trading_date)
        )

        return self.session.scalars(stmt).all()

    def get_all_symbol_ids(self) -> list[int]:
        """
        Return all distinct symbol IDs that have market data.
        """

        stmt = (
            select(distinct(MarketData.symbol_id))
            .order_by(MarketData.symbol_id)
        )

        return list(self.session.scalars(stmt).all())

    def get_price_history_by_symbol(
        self,
        symbol_id: int,
    ):
        """
        Return complete OHLCV history for one symbol.
        """

        stmt = (
            select(MarketData)
            .where(
                MarketData.symbol_id == symbol_id
            )
            .order_by(MarketData.trading_date)
        )

        return self.session.scalars(stmt).all()