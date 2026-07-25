from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.indicator_data import IndicatorData


class IndicatorRepository:
    """Repository for IndicatorData."""

    def __init__(self, session: Session):
        self.session = session

    def save(self, indicator: IndicatorData) -> IndicatorData:
        self.session.add(indicator)
        self.session.flush()
        return indicator

    def save_all(self, indicators: list[IndicatorData]) -> None:
        self.session.add_all(indicators)
        self.session.flush()

    def get_by_symbol(
        self,
        symbol_id,
    ) -> Sequence[IndicatorData]:
        stmt = (
            select(IndicatorData)
            .where(IndicatorData.symbol_id == symbol_id)
            .order_by(IndicatorData.trading_date)
        )
        return self.session.scalars(stmt).all()

    def get_by_symbol_and_date(
        self,
        symbol_id,
        trading_date,
    ) -> IndicatorData | None:
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
        symbol_id,
    ) -> None:
        rows = self.get_by_symbol(symbol_id)
        for row in rows:
            self.session.delete(row)