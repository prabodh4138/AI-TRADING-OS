"""
AI Trading Operating System
Indicator Data Model
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base_model import BaseModel


class IndicatorData(BaseModel):
    """
    Stores calculated indicator values for each symbol and trading date.
    """

    __tablename__ = "indicator_data"

    __table_args__ = (
        UniqueConstraint(
            "symbol_id",
            "trading_date",
            name="uq_indicator_symbol_date",
        ),
    )

    # Primary Key
    indicator_data_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign Key
    symbol_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("symbol.symbol_id"),
        nullable=False,
        index=True,
    )

    trading_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    # =========================
    # Simple Moving Average
    # =========================
    sma20: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    sma50: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    sma100: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    sma200: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))

    # =========================
    # Exponential Moving Average
    # =========================
    ema9: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    ema20: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    ema50: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    ema100: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    ema200: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))

    # =========================
    # RSI
    # =========================
    rsi14: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))

    # =========================
    # MACD
    # =========================
    macd: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    macd_signal: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    macd_histogram: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))

    # =========================
    # ATR
    # =========================
    atr14: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))

    # =========================
    # Bollinger Bands
    # =========================
    bb_upper: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    bb_middle: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    bb_lower: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))

    # =========================
    # ADX
    # =========================
    adx14: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    plus_di: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    minus_di: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))

    # =========================
    # SuperTrend
    # =========================
    supertrend: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    supertrend_direction: Mapped[int | None] = mapped_column(Integer)

    # =========================
    # Volume
    # =========================
    obv: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    volume_sma20: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    relative_volume: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))

    # =========================
    # Momentum
    # =========================
    roc10: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    momentum10: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))

    # =========================
    # Stochastic
    # =========================
    stochastic_k: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    stochastic_d: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))

    # =========================
    # Composite Scores
    # =========================
    trend_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    momentum_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))

    # Relationship
    symbol = relationship(
        "Symbol",
        back_populates="indicator_data",
    )

    def __repr__(self) -> str:
        return (
            f"<IndicatorData(symbol_id={self.symbol_id}, "
            f"trading_date={self.trading_date})>"
        )