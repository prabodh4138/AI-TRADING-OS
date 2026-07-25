from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(slots=True)
class IndicatorDTO:
    symbol_id: UUID
    trading_date: date

    sma20: Decimal | None = None
    sma50: Decimal | None = None
    sma100: Decimal | None = None
    sma200: Decimal | None = None

    ema9: Decimal | None = None
    ema20: Decimal | None = None
    ema50: Decimal | None = None
    ema100: Decimal | None = None
    ema200: Decimal | None = None

    rsi14: Decimal | None = None

    macd: Decimal | None = None
    macd_signal: Decimal | None = None
    macd_histogram: Decimal | None = None

    atr14: Decimal | None = None

    bb_upper: Decimal | None = None
    bb_middle: Decimal | None = None
    bb_lower: Decimal | None = None

    adx14: Decimal | None = None
    plus_di: Decimal | None = None
    minus_di: Decimal | None = None

    supertrend: Decimal | None = None
    supertrend_direction: int | None = None

    obv: Decimal | None = None
    volume_sma20: Decimal | None = None
    relative_volume: Decimal | None = None

    roc10: Decimal | None = None
    momentum10: Decimal | None = None

    stochastic_k: Decimal | None = None
    stochastic_d: Decimal | None = None

    trend_score: Decimal | None = None
    momentum_score: Decimal | None = None