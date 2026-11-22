"""
AI Trading Operating System
Market Data Service

Business Service for Market Data Management
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

import pandas as pd

from database.models.market_data import MarketData
from database.unit_of_work import UnitOfWork
from dto.market_data_dto import MarketDataCreateDTO
from services.base_service import BaseService
from services.market_data_mapper import MarketDataMapper
from validators.base_validator import ValidationError
from validators.market_data_validator import MarketDataValidator


class MarketDataService(BaseService):
    """
    Business Service for Market Data.
    """

    def __init__(self) -> None:
        super().__init__()
        self.validator = MarketDataValidator()
        self.mapper = MarketDataMapper()

    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------

    def create_market_data(
        self,
        dto: MarketDataCreateDTO,
    ) -> MarketData:

        self.validator.validate(dto)

        with UnitOfWork() as uow:

            if uow.market_data.exists_for_symbol_and_date(
                dto.symbol_id,
                dto.trading_date,
            ):
                raise ValidationError(
                    "Market data already exists for this symbol and trading date."
                )

            data = MarketData(
                symbol_id=dto.symbol_id,
                trading_date=dto.trading_date,
                open_price=dto.open_price,
                high_price=dto.high_price,
                low_price=dto.low_price,
                close_price=dto.close_price,
                adjusted_close=dto.adjusted_close,
                volume=dto.volume,
                delivery_volume=dto.delivery_volume,
                delivery_percent=dto.delivery_percent,
                turnover=dto.turnover,
                vwap=dto.vwap,
                trade_count=dto.trade_count,
            )

            uow.market_data.add(data)

            uow.flush()

            return data

    # ---------------------------------------------------------
    # Import
    # ---------------------------------------------------------

    def import_market_data(
        self,
        dataframe: pd.DataFrame,
        *,
        batch_size: int = 1000,
        universe_code: str | None = None,
    ) -> int:
        """
        Import transformed market data into the database.

        When universe_code is supplied, only symbols belonging to
        the current active membership of that universe are imported.
        """

        if dataframe.empty:
            return 0

        dataframe = dataframe.copy()

        # ---------------------------------------------
        # Optional Universe Filter
        # ---------------------------------------------

        if universe_code:

            with UnitOfWork() as uow:

                universe = uow.universes.get_by_universe_code(
                    universe_code
                )

                if universe is None:
                    raise ValidationError(
                        f"Unknown universe: {universe_code}"
                    )

                universe_symbols = (
                    uow.universes.get_constituent_symbols(
                        universe.universe_id,
                        active_only=True,
                    )
                )

                universe_symbol_codes = {
                    symbol.symbol_code
                    for symbol in universe_symbols
                }

            dataframe = dataframe[
                dataframe["symbol"]
                .astype(str)
                .str.strip()
                .isin(universe_symbol_codes)
            ].copy()

            if dataframe.empty:
                return 0

        # ---------------------------------------------
        # Resolve Symbol IDs
        # ---------------------------------------------

        with UnitOfWork() as uow:

            symbol_codes = (
                dataframe["symbol"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
                .tolist()
            )

            symbol_map = uow.symbols.get_symbol_id_map(
                symbol_codes
            )

        dataframe["symbol_id"] = (
            dataframe["symbol"]
            .map(symbol_map)
        )

        # ---------------------------------------------
        # Validate unresolved symbols
        # ---------------------------------------------

        unresolved = dataframe[
            dataframe["symbol_id"].isna()
        ]

        if not unresolved.empty:

            missing = (
                unresolved["symbol"]
                .drop_duplicates()
                .tolist()
            )

            raise ValidationError(
                "Unknown symbol(s): "
                + ", ".join(missing)
            )

        # ---------------------------------------------
        # Convert to ORM entities
        # ---------------------------------------------

        entities = self.mapper.dataframe_to_entities(
            dataframe
        )

        if not entities:
            return 0

        # ---------------------------------------------
        # Bulk Insert
        # ---------------------------------------------

        with UnitOfWork() as uow:

            inserted = uow.market_data.bulk_insert(
                entities,
                batch_size=batch_size,
            )

            return inserted

    # ---------------------------------------------------------
    # Read
    # ---------------------------------------------------------

    def get_market_data(
        self,
        market_data_id: UUID,
    ) -> MarketData | None:

        with UnitOfWork() as uow:
            return uow.market_data.get_by_id(
                market_data_id
            )

    def get_latest_price(
        self,
        symbol_id: UUID,
    ) -> MarketData | None:

        with UnitOfWork() as uow:
            return uow.market_data.get_latest_price(
                symbol_id
            )

    def get_by_symbol_and_date(
        self,
        symbol_id: UUID,
        trading_date: date,
    ) -> MarketData | None:

        with UnitOfWork() as uow:
            return uow.market_data.get_by_symbol_and_date(
                symbol_id,
                trading_date,
            )

    def get_price_history(
        self,
        symbol_id: UUID,
        start_date: date,
        end_date: date,
    ) -> list[MarketData]:

        with UnitOfWork() as uow:
            return uow.market_data.get_price_history(
                symbol_id,
                start_date,
                end_date,
            )

    def get_complete_history(
        self,
        symbol_id: UUID,
    ) -> list[MarketData]:

        with UnitOfWork() as uow:
            return uow.market_data.get_price_history_by_symbol(
                symbol_id
            )

    # ---------------------------------------------------------
    # Information
    # ---------------------------------------------------------

    def count_by_symbol(
        self,
        symbol_id: UUID,
    ) -> int:

        with UnitOfWork() as uow:
            return uow.market_data.count_by_symbol(
                symbol_id
            )

    def get_latest_trading_date(self):

        with UnitOfWork() as uow:
            return uow.market_data.get_latest_trading_date()

    def get_earliest_trading_date(self):

        with UnitOfWork() as uow:
            return uow.market_data.get_earliest_trading_date()

    def get_all_symbol_ids(self):

        with UnitOfWork() as uow:
            return uow.market_data.get_all_symbol_ids()

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete_market_data(
        self,
        market_data_id: UUID,
    ) -> None:

        with UnitOfWork() as uow:

            data = uow.market_data.get_by_id(
                market_data_id
            )

            self.require_not_none(
                data,
                "Market Data",
            )

            uow.market_data.delete(data)

            uow.flush()
