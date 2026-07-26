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
    Converts transformed pandas DataFrames into
    MarketData ORM entities.

    This class belongs to the ETL layer and is
    responsible only for object mapping.

    It performs no database operations.
    """

    def __init__(self) -> None:
        """
        Initialize mapper.
        """

        self.logger = logging.getLogger(
            self.__class__.__name__
        )
    def dataframe_to_entities(
        self,
        dataframe: pd.DataFrame,
    ) -> list[MarketData]:
        """
        Convert a transformed pandas DataFrame into a list
        of MarketData ORM entities.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Validated and transformed market data.

        Returns
        -------
        list[MarketData]
            ORM entities ready for persistence.
        """

        if dataframe.empty:
            self.logger.info(
                "Received empty dataframe."
            )
            return []

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

        self.logger.info(
            "Converted %d dataframe rows into ORM entities.",
            len(entities),
        )

        return entities