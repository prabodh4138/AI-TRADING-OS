"""Backward-compatible SuperTrend wrapper."""
from __future__ import annotations
import pandas as pd
from indicator.calculator import IndicatorCalculator

def calculate_supertrend(df: pd.DataFrame, period: int=10, multiplier: float=3.0) -> pd.DataFrame:
    # The canonical implementation lives in IndicatorCalculator. The public
    # function remains for older callers.
    result=IndicatorCalculator._supertrend(df.copy(), period=period, multiplier=multiplier)
    return result
