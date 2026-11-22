from __future__ import annotations

from database.repositories.indicator_repository import IndicatorRepository
from dto.indicator_dto import IndicatorDTO
from database.models.indicator_data import IndicatorData


class IndicatorSaver:
    """Saves calculated indicators to the database."""

    def __init__(self, repository: IndicatorRepository):
        self.repository = repository

    def save(self, indicators: list[IndicatorDTO]) -> None:
        records = []

        for dto in indicators:
            records.append(
                IndicatorData(
                    symbol_id=dto.symbol_id,
                    trading_date=dto.trading_date,
                    sma20=dto.sma20,
                    sma50=dto.sma50,
                    sma100=dto.sma100,
                    sma200=dto.sma200,
                    ema9=dto.ema9,
                    ema20=dto.ema20,
                    ema50=dto.ema50,
                    ema100=dto.ema100,
                    ema200=dto.ema200,
                    rsi14=dto.rsi14,
                    macd=dto.macd,
                    macd_signal=dto.macd_signal,
                    macd_histogram=dto.macd_histogram,
                    atr14=dto.atr14,
                    bb_upper=dto.bb_upper,
                    bb_middle=dto.bb_middle,
                    bb_lower=dto.bb_lower,
                    adx14=dto.adx14,
                    plus_di=dto.plus_di,
                    minus_di=dto.minus_di,
                    supertrend=dto.supertrend,
                    supertrend_direction=dto.supertrend_direction,
                    obv=dto.obv,
                    volume_sma20=dto.volume_sma20,
                    relative_volume=dto.relative_volume,
                    roc10=dto.roc10,
                    momentum10=dto.momentum10,
                    stochastic_k=dto.stochastic_k,
                    stochastic_d=dto.stochastic_d,
                    trend_score=dto.trend_score,
                    momentum_score=dto.momentum_score,
                )
            )

        self.repository.save_all(records)