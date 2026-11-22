"""
AI Trading Operating System
Module 2: Market-Index Intelligence Layer (Section 2)

Computes:
- Multi-horizon trend state, MA structures, momentum, and breakout context.
- Realised volatility, range expansion/contraction (ATR ratio), gap behaviour, and volatility regime.
- Market breadth engine: Advance/Decline ratio, % constituents above 20/50/200 DMA, new highs/lows.
- Relative strength and intermarket leadership confirmation (e.g. NIFTY 50 vs Bank Nifty).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass(frozen=True, slots=True)
class TrendState:
    ret_5d: float
    ret_20d: float
    ret_50d: float
    ma_alignment: str  # "BULLISH_STACK", "BEARISH_STACK", "MIXED"
    trend_persistence: float  # 0.0 to 1.0 (% positive bars in 20d)
    rsi14: float
    is_20d_breakout: bool
    trend_label: str  # "STRONG_BULLISH", "MODERATE_BULLISH", "NEUTRAL", "BEARISH", "STRONG_BEARISH"


@dataclass(frozen=True, slots=True)
class VolatilityState:
    realised_vol_20d_ann: float  # Annualized %
    atr14: float
    atr_ratio: float  # ATR14 / SMA(ATR14, 20)
    gap_pct: float
    volatility_regime: str  # "LOW", "NORMAL", "HIGH", "EXTREME_STRESS"


@dataclass(frozen=True, slots=True)
class MarketBreadthState:
    advances: int
    declines: int
    unchanged: int
    ad_ratio: float
    pct_above_20dma: float
    pct_above_50dma: float
    pct_above_200dma: float
    new_20d_highs: int
    new_20d_lows: int
    breadth_regime: str  # "HEALTHY_EXPANSION", "SELECTIVE_RALLY", "NEUTRAL", "DETERIORATING", "SEVERE_WEAKNESS"


@dataclass(frozen=True, slots=True)
class IndexIntelligenceSnapshot:
    index_code: str
    trading_date: date
    close: float
    trend: TrendState
    volatility: VolatilityState
    relative_strength_vs_benchmark: float = 0.0
    confirmation_status: str = "CONFIRMED"


class IndexIntelligenceEngine:
    """
    Computes Section 2 market-index intelligence and market breadth context.
    """

    @staticmethod
    def calculate_trend_state(df: pd.DataFrame) -> TrendState:
        """
        Analyzes multi-horizon returns, moving average structure,
        trend persistence, and momentum.
        """
        if df.empty or len(df) < 5:
            return TrendState(
                ret_5d=0.0,
                ret_20d=0.0,
                ret_50d=0.0,
                ma_alignment="MIXED",
                trend_persistence=0.5,
                rsi14=50.0,
                is_20d_breakout=False,
                trend_label="NEUTRAL",
            )

        x = df.copy().sort_values("trading_date").reset_index(drop=True)
        c = pd.to_numeric(x["close"], errors="coerce")
        n = len(c)

        ret_5d = float((c.iloc[-1] / c.iloc[-5] - 1) * 100) if n >= 5 else 0.0
        ret_20d = float((c.iloc[-1] / c.iloc[-20] - 1) * 100) if n >= 20 else ret_5d
        ret_50d = float((c.iloc[-1] / c.iloc[-50] - 1) * 100) if n >= 50 else ret_20d

        # Trend persistence: % of positive daily returns over last 20 days
        diffs = c.diff().tail(20).dropna()
        pos_days = (diffs > 0).sum()
        persistence = float(pos_days / len(diffs)) if len(diffs) > 0 else 0.5

        # Moving averages
        ema20 = c.ewm(span=20, adjust=False).mean().iloc[-1]
        ema50 = c.ewm(span=50, adjust=False).mean().iloc[-1]
        ema200 = c.ewm(span=200, adjust=False).mean().iloc[-1] if n >= 50 else ema50
        latest_c = c.iloc[-1]

        if latest_c > ema20 > ema50 > ema200:
            ma_alignment = "BULLISH_STACK"
        elif latest_c < ema20 < ema50 < ema200:
            ma_alignment = "BEARISH_STACK"
        else:
            ma_alignment = "MIXED"

        # RSI(14)
        delta = c.diff()
        gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
        rs = gain.iloc[-1] / (loss.iloc[-1] + 1e-9)
        rsi14 = float(100 - (100 / (1 + rs)))

        # 20d High Breakout
        high20 = x["high"].tail(20).max() if "high" in x.columns else c.tail(20).max()
        is_breakout = bool(latest_c >= high20 * 0.998)

        # Composite Trend Label
        if ma_alignment == "BULLISH_STACK" and ret_20d > 2.0 and rsi14 > 55:
            trend_label = "STRONG_BULLISH"
        elif latest_c > ema50 and ret_20d > 0:
            trend_label = "MODERATE_BULLISH"
        elif ma_alignment == "BEARISH_STACK" and ret_20d < -2.0 and rsi14 < 45:
            trend_label = "STRONG_BEARISH"
        elif latest_c < ema50 and ret_20d < 0:
            trend_label = "BEARISH"
        else:
            trend_label = "NEUTRAL"

        return TrendState(
            ret_5d=round(ret_5d, 2),
            ret_20d=round(ret_20d, 2),
            ret_50d=round(ret_50d, 2),
            ma_alignment=ma_alignment,
            trend_persistence=round(persistence, 2),
            rsi14=round(rsi14, 2),
            is_20d_breakout=is_breakout,
            trend_label=trend_label,
        )

    @staticmethod
    def calculate_volatility_state(df: pd.DataFrame) -> VolatilityState:
        """
        Calculates realised volatility, ATR expansion/contraction ratio,
        and gap behaviour.
        """
        if df.empty or len(df) < 5:
            return VolatilityState(
                realised_vol_20d_ann=15.0,
                atr14=10.0,
                atr_ratio=1.0,
                gap_pct=0.0,
                volatility_regime="NORMAL",
            )

        x = df.copy().sort_values("trading_date").reset_index(drop=True)
        c = pd.to_numeric(x["close"], errors="coerce")
        h = pd.to_numeric(x["high"], errors="coerce") if "high" in x.columns else c
        l = pd.to_numeric(x["low"], errors="coerce") if "low" in x.columns else c
        o = pd.to_numeric(x["open"], errors="coerce") if "open" in x.columns else c

        # Realised vol: 20-day annualized
        log_ret = np.log(c / c.shift(1)).dropna().tail(20)
        daily_std = float(log_ret.std()) if len(log_ret) > 1 else 0.01
        realised_vol_ann = float(daily_std * np.sqrt(252) * 100)

        # ATR 14
        prev_c = c.shift(1)
        tr = pd.concat([(h - l), (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
        atr14_series = tr.ewm(alpha=1/14, adjust=False).mean()
        latest_atr = float(atr14_series.iloc[-1])

        # ATR ratio vs 20-day average ATR
        atr_sma20 = float(atr14_series.tail(20).mean()) if len(atr14_series) >= 20 else latest_atr
        atr_ratio = float(latest_atr / (atr_sma20 + 1e-9))

        # Gap %
        if len(c) >= 2:
            gap_pct = float((o.iloc[-1] - c.iloc[-2]) / c.iloc[-2] * 100)
        else:
            gap_pct = 0.0

        # Volatility regime
        if realised_vol_ann > 28.0 or atr_ratio > 1.4:
            vol_regime = "EXTREME_STRESS"
        elif realised_vol_ann > 20.0 or atr_ratio > 1.2:
            vol_regime = "HIGH"
        elif realised_vol_ann < 12.0 and atr_ratio < 0.85:
            vol_regime = "LOW"
        else:
            vol_regime = "NORMAL"

        return VolatilityState(
            realised_vol_20d_ann=round(realised_vol_ann, 2),
            atr14=round(latest_atr, 2),
            atr_ratio=round(atr_ratio, 2),
            gap_pct=round(gap_pct, 2),
            volatility_regime=vol_regime,
        )

    @staticmethod
    def calculate_market_breadth(universe_df: pd.DataFrame) -> MarketBreadthState:
        """
        Calculates broad market participation across constituent symbols.
        Supports single-day or multi-day universe frames.
        """
        if universe_df.empty or "symbol" not in universe_df.columns:
            return MarketBreadthState(
                advances=0,
                declines=0,
                unchanged=0,
                ad_ratio=1.0,
                pct_above_20dma=50.0,
                pct_above_50dma=50.0,
                pct_above_200dma=50.0,
                new_20d_highs=0,
                new_20d_lows=0,
                breadth_regime="NEUTRAL",
            )

        # If data contains multiple dates, evaluate the latest trading date
        latest_dt = universe_df["trading_date"].max() if "trading_date" in universe_df.columns else None
        current_data = universe_df[universe_df["trading_date"] == latest_dt] if latest_dt else universe_df

        advances = 0
        declines = 0
        unchanged = 0

        # Calculate advance / decline
        if "prevclose" in current_data.columns:
            diff = current_data["close"] - current_data["prevclose"]
            advances = int((diff > 0).sum())
            declines = int((diff < 0).sum())
            unchanged = int((diff == 0).sum())
        elif "open" in current_data.columns:
            diff = current_data["close"] - current_data["open"]
            advances = int((diff > 0).sum())
            declines = int((diff < 0).sum())
            unchanged = int((diff == 0).sum())
        else:
            advances = len(current_data) // 2
            declines = len(current_data) - advances

        total = max(1, advances + declines + unchanged)
        ad_ratio = float(advances / max(1, declines))

        # Check moving averages participation if history exists
        pct_above_20dma = 50.0
        pct_above_50dma = 50.0
        pct_above_200dma = 50.0
        new_highs = 0
        new_lows = 0

        # If multi-day history per symbol is present:
        if len(universe_df["trading_date"].unique()) >= 20 if "trading_date" in universe_df.columns else False:
            above_20 = 0
            above_50 = 0
            above_200 = 0
            count = 0
            for sym, g in universe_df.groupby("symbol"):
                if len(g) < 20:
                    continue
                count += 1
                g_sorted = g.sort_values("trading_date")
                c = g_sorted["close"]
                last_c = c.iloc[-1]
                if last_c > c.tail(20).mean():
                    above_20 += 1
                if len(g) >= 50 and last_c > c.tail(50).mean():
                    above_50 += 1
                if len(g) >= 200 and last_c > c.tail(200).mean():
                    above_200 += 1
                if last_c >= g_sorted["high"].tail(20).max() * 0.998:
                    new_highs += 1
                if last_c <= g_sorted["low"].tail(20).min() * 1.002:
                    new_lows += 1

            if count > 0:
                pct_above_20dma = float(above_20 / count * 100)
                pct_above_50dma = float(above_50 / max(1, count) * 100)
                pct_above_200dma = float(above_200 / max(1, count) * 100)
        else:
            # Derived estimate from advance percentage if single cross-section
            adv_pct = (advances / total) * 100
            pct_above_20dma = adv_pct
            pct_above_50dma = adv_pct * 0.95
            pct_above_200dma = adv_pct * 0.90

        # Breadth regime assessment
        if pct_above_20dma >= 65.0 and ad_ratio >= 1.5:
            breadth_regime = "HEALTHY_EXPANSION"
        elif pct_above_20dma >= 50.0 and ad_ratio < 1.0:
            breadth_regime = "SELECTIVE_RALLY"  # Heavyweights up, but breadth narrow
        elif pct_above_20dma <= 35.0 and ad_ratio <= 0.6:
            breadth_regime = "SEVERE_WEAKNESS"
        elif pct_above_20dma < 45.0:
            breadth_regime = "DETERIORATING"
        else:
            breadth_regime = "NEUTRAL"

        return MarketBreadthState(
            advances=advances,
            declines=declines,
            unchanged=unchanged,
            ad_ratio=round(ad_ratio, 2),
            pct_above_20dma=round(pct_above_20dma, 1),
            pct_above_50dma=round(pct_above_50dma, 1),
            pct_above_200dma=round(pct_above_200dma, 1),
            new_20d_highs=new_highs,
            new_20d_lows=new_lows,
            breadth_regime=breadth_regime,
        )

    @staticmethod
    def evaluate_intermarket_leadership(
        benchmark_snap: IndexIntelligenceSnapshot,
        sector_or_banking_snap: IndexIntelligenceSnapshot,
    ) -> str:
        """
        Assesses whether banking / sector index confirms or diverges from broad market.
        """
        b_trend = benchmark_snap.trend.trend_label
        s_trend = sector_or_banking_snap.trend.trend_label

        if "BULLISH" in b_trend and "BULLISH" in s_trend:
            return "CONFIRMED_BULLISH"
        elif "BEARISH" in b_trend and "BEARISH" in s_trend:
            return "CONFIRMED_BEARISH"
        elif "BULLISH" in b_trend and "BEARISH" in s_trend:
            return "DIVERGING_BEARISH"  # Benchmark is up, but key sector/bank is lagging
        elif "BEARISH" in b_trend and "BULLISH" in s_trend:
            return "DIVERGING_BULLISH"  # Benchmark is down, but key sector/bank is leading
        return "NEUTRAL"
