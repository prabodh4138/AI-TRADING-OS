"""Indicator orchestration and DTO generation."""
from __future__ import annotations
from decimal import Decimal
from uuid import UUID
import pandas as pd
from dto.indicator_dto import IndicatorDTO
from indicator.calculator import IndicatorCalculator

class IndicatorEngine:
    def __init__(self, calculator: IndicatorCalculator | None = None): self.calculator=calculator or IndicatorCalculator()
    def calculate_frame(self, data: pd.DataFrame) -> pd.DataFrame: return self.calculator.calculate(data)
    def calculate(self, data: pd.DataFrame, symbol_id: UUID) -> list[IndicatorDTO]:
        x=self.calculate_frame(data); rows=[]
        fields=("sma20","sma50","sma100","sma200","ema9","ema20","ema50","ema100","ema200","rsi14","macd","macd_signal","macd_histogram","atr14","bb_upper","bb_middle","bb_lower","adx14","plus_di","minus_di","obv","volume_sma20","relative_volume","roc10","momentum10","stochastic_k","stochastic_d","trend_score","momentum_score")
        for row in x.itertuples(index=False):
            kwargs={f:(Decimal(str(getattr(row,f))) if pd.notna(getattr(row,f)) else None) for f in fields}; rows.append(IndicatorDTO(symbol_id=symbol_id,trading_date=row.trading_date,**kwargs))
        return rows
