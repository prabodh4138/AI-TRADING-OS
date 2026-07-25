"""
AI Trading Operating System
Market Data Model

Stores End-of-Day (EOD) market data for all tradable instruments.
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.symbol import Symbol   

from sqlalchemy import (
    BigInteger,
    Date,
    ForeignKey,
    Index,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base_model import BaseModel


class MarketData(BaseModel):
    """
    Daily End-of-Day (EOD) market data.

    One record represents one symbol on one trading day.
    """

    __tablename__ = "market_data"

    __table_args__ = (
        UniqueConstraint(
            "symbol_id",
            "trading_date",
            name="uq_market_data_symbol_date",
        ),
        Index(
            "ix_market_data_symbol_date",
            "symbol_id",
            "trading_date",
        ),
    )

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------

    market_data_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ------------------------------------------------------------------
    # Foreign Key
    # ------------------------------------------------------------------

    symbol_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "symbol.symbol_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Trading Information
    # ------------------------------------------------------------------

    trading_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # OHLC Prices
    # ------------------------------------------------------------------

    open_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    high_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    low_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    close_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
    )

    adjusted_close: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Volume Information
    # ------------------------------------------------------------------

    volume: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    delivery_volume: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    delivery_percent: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    trade_count: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Market Statistics
    # ------------------------------------------------------------------

    turnover: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4),
        nullable=True,
    )

    vwap: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    symbol: Mapped["Symbol"] = relationship(
        back_populates="market_data",
    )

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<MarketData("
            f"symbol_id={self.symbol_id}, "
            f"date={self.trading_date}, "
            f"close={self.close_price})>"
        )