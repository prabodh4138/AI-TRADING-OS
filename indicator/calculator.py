from __future__ import annotations

import talib
import pandas as pd
#from indicator.supertrend import calculate_supertrend


class IndicatorCalculator:
    """Technical Indicator Calculator using TA-Lib."""

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()
        df = df.sort_values("trading_date")

        # Standard OHLCV columns
        open_price = df["open"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        close = df["close"].astype(float)
        volume = df["volume"].astype(float)

        # =========================
        # Moving Averages
        # =========================

        df["sma20"] = talib.SMA(close, timeperiod=20)
        df["sma50"] = talib.SMA(close, timeperiod=50)
        df["sma100"] = talib.SMA(close, timeperiod=100)
        df["sma200"] = talib.SMA(close, timeperiod=200)

        df["ema9"] = talib.EMA(close, timeperiod=9)
        df["ema20"] = talib.EMA(close, timeperiod=20)
        df["ema50"] = talib.EMA(close, timeperiod=50)
        df["ema100"] = talib.EMA(close, timeperiod=100)
        df["ema200"] = talib.EMA(close, timeperiod=200)

        # =========================
        # RSI
        # =========================

        df["rsi14"] = talib.RSI(close, timeperiod=14)

        # =========================
        # MACD
        # =========================

        (
            df["macd"],
            df["macd_signal"],
            df["macd_histogram"],
        ) = talib.MACD(
            close,
            fastperiod=12,
            slowperiod=26,
            signalperiod=9,
        )

        # =========================
        # ATR
        # =========================

        df["atr14"] = talib.ATR(
            high,
            low,
            close,
            timeperiod=14,
        )
                # =========================
        # ADX / +DI / -DI
        # =========================

        df["adx14"] = talib.ADX(
            high,
            low,
            close,
            timeperiod=14,
        )

        df["plus_di"] = talib.PLUS_DI(
            high,
            low,
            close,
            timeperiod=14,
        )

        df["minus_di"] = talib.MINUS_DI(
            high,
            low,
            close,
            timeperiod=14,
        )
                # =========================
        # Bollinger Bands
        # =========================

        (
            df["bb_upper"],
            df["bb_middle"],
            df["bb_lower"],
        ) = talib.BBANDS(
            close,
            timeperiod=20,
            nbdevup=2,
            nbdevdn=2,
            matype=0,
        )
                # =========================
        # OBV
        # =========================

        df["obv"] = talib.OBV(
            close,
            volume,
        )

        # =========================
        # Volume SMA
        # =========================

        df["volume_sma20"] = talib.SMA(
            volume,
            timeperiod=20,
        )

        df["relative_volume"] = (
            volume / df["volume_sma20"]
        )
                # =========================
        # ROC
        # =========================

        df["roc10"] = talib.ROC(
            close,
            timeperiod=10,
        )

        # =========================
        # Momentum
        # =========================

        df["momentum10"] = talib.MOM(
            close,
            timeperiod=10,
        )
                # =========================
        # Stochastic Oscillator
        # =========================

        (
            df["stochastic_k"],
            df["stochastic_d"],
        ) = talib.STOCH(
            high,
            low,
            close,
        )
        
        # =========================
        # SuperTrend
        # =========================

        #df = calculate_supertrend(df)

        return df