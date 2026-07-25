"""
Market Data Service
"""

from database.models.market_data import MarketData
from database.unit_of_work import UnitOfWork

from dto.market_data_dto import MarketDataCreateDTO

from validators.market_data_validator import (
    MarketDataValidator,
)


class MarketDataService:

    def __init__(self):

        self.validator = MarketDataValidator()

    def create_market_data(
        self,
        dto: MarketDataCreateDTO,
    ):

        self.validator.validate(dto)

        with UnitOfWork() as uow:

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

            return data