"""
AI Trading Operating System
Symbol Master Model
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING


from database.base_model import BaseModel

if TYPE_CHECKING:
    from .market_data import MarketData
    from .indicator_data import IndicatorData



class Symbol(BaseModel):
    """
    Master table containing all tradable instruments.
    """

    __tablename__ = "symbol"

    symbol_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    symbol_code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
        index=True,
    )

    symbol_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    exchange: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="NSE",
    )

    instrument_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="EQUITY",
    )

    sector: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    industry: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    isin: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
    )

    lot_size: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    tick_size: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.05"),
        nullable=False,
    )

    face_value: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    listing_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    is_fno: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    market_data: Mapped[list["MarketData"]] = relationship(
        back_populates="symbol",
        cascade="all, delete-orphan",
    )
    indicator_data: Mapped[list["IndicatorData"]] = relationship(
        back_populates="symbol",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Symbol(symbol_code='{self.symbol_code}', "
            f"exchange='{self.exchange}')>"
        )