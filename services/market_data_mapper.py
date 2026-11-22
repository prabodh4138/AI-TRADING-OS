"""
AI Trading Operating System
Market Data Mapper
"""

from __future__ import annotations

import logging

import pandas as pd

from database.models.market_data import MarketData


class MarketDataMapper:
    """
    Convert canonical market-data DataFrames into
    MarketData ORM entities.

    This class performs object mapping only.
    It does not validate business rules or access
    the database.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def dataframe_to_entities(
        self,
        dataframe: pd.DataFrame,
    ) -> list[MarketData]:
        """
        Convert canonical market-data rows into ORM entities.

        Expected canonical columns:

        symbol_id
        trading_date
        open
        high
        low
        close
        volume

        Optional:

        adjusted_close
        delivery_volume
        delivery_percent
        turnover
        vwap
        trade_count
        """

        if dataframe.empty:
            self.logger.info("Received empty dataframe.")
            return []

        required_columns = {
            "symbol_id",
            "trading_date",
            "open",
            "high",
            "low",
            "close",
            "volume",
        }

        missing_columns = sorted(
            required_columns.difference(dataframe.columns)
        )

        if missing_columns:
            raise ValueError(
                "Missing required market-data column(s): "
                + ", ".join(missing_columns)
            )

        entities: list[MarketData] = []

        for row in dataframe.itertuples(index=False):
            entity = MarketData(
                symbol_id=row.symbol_id,
                trading_date=row.trading_date,
                open_price=row.open,
                high_price=row.high,
                low_price=row.low,
                close_price=row.close,
                adjusted_close=getattr(
                    row,
                    "adjusted_close",
                    None,
                ),
                volume=row.volume,
                delivery_volume=getattr(
                    row,
                    "delivery_volume",
                    None,
                ),
                delivery_percent=getattr(
                    row,
                    "delivery_percent",
                    None,
                ),
                trade_count=getattr(
                    row,
                    "trade_count",
                    None,
                ),
                turnover=getattr(
                    row,
                    "turnover",
                    None,
                ),
                vwap=getattr(
                    row,
                    "vwap",
                    None,
                ),
            )

            entities.append(entity)

        self.logger.info(
            "Converted %d dataframe rows into ORM entities.",
            len(entities),
        )

        return entities
