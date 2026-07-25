"""
AI Trading Operating System
Market Data DTO
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(slots=True)
class MarketDataCreateDTO:
    symbol_id: UUID
    trading_date: date

    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal

    adjusted_close: Decimal | None = None

    volume: int = 0
    delivery_volume: int | None = None
    delivery_percent: Decimal | None = None

    turnover: Decimal | None = None
    vwap: Decimal | None = None
    trade_count: int | None = None