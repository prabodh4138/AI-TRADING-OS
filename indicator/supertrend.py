from __future__ import annotations

import numpy as np
import pandas as pd
import talib


def calculate_supertrend(
    df: pd.DataFrame,
    period: int = 10,
    multiplier: float = 3.0,
) -> pd.DataFrame:

    df = df.copy()

    high = df["high"].astype(float)
    low = df["low"].astype(float)
    close = df["close"].astype(float)

    atr = talib.ATR(
        high,
        low,
        close,
        timeperiod=period,
    )

    hl2 = (high + low) / 2

    basic_upper = hl2 + multiplier * atr
    basic_lower = hl2 - multiplier * atr

    final_upper = basic_upper.copy()
    final_lower = basic_lower.copy()

    supertrend = np.full(len(df), np.nan)
    direction = np.full(len(df), 1)

    # -----------------------------
    # Final Bands
    # -----------------------------
    for i in range(1, len(df)):

        if (
            basic_upper.iloc[i] < final_upper.iloc[i - 1]
            or close.iloc[i - 1] > final_upper.iloc[i - 1]
        ):
            final_upper.iloc[i] = basic_upper.iloc[i]
        else:
            final_upper.iloc[i] = final_upper.iloc[i - 1]

        if (
            basic_lower.iloc[i] > final_lower.iloc[i - 1]
            or close.iloc[i - 1] < final_lower.iloc[i - 1]
        ):
            final_lower.iloc[i] = basic_lower.iloc[i]
        else:
            final_lower.iloc[i] = final_lower.iloc[i - 1]

    # -----------------------------
    # Initialize first valid value
    # -----------------------------
    start = period

    if start >= len(df):
        df["supertrend"] = supertrend
        df["supertrend_direction"] = direction
        return df

    if close.iloc[start] <= final_upper.iloc[start]:
        supertrend[start] = final_upper.iloc[start]
        direction[start] = -1
    else:
        supertrend[start] = final_lower.iloc[start]
        direction[start] = 1

    # -----------------------------
    # Remaining candles
    # -----------------------------
    for i in range(start + 1, len(df)):

        if supertrend[i - 1] == final_upper.iloc[i - 1]:

            if close.iloc[i] <= final_upper.iloc[i]:
                supertrend[i] = final_upper.iloc[i]
                direction[i] = -1
            else:
                supertrend[i] = final_lower.iloc[i]
                direction[i] = 1

        else:

            if close.iloc[i] >= final_lower.iloc[i]:
                supertrend[i] = final_lower.iloc[i]
                direction[i] = 1
            else:
                supertrend[i] = final_upper.iloc[i]
                direction[i] = -1

    df["supertrend"] = supertrend
    df["supertrend_direction"] = direction

    return df