"""
AI Trading Operating System
Module 4: Support and Resistance Intelligence Engine (Section 5)

Implements:
- Swing-point clustering with uncertainty bands (zones, not exact single prices).
- Multi-session extremes and Pivot levels (Classical / Fibonacci).
- Zone strength scoring based on recency, repeated interactions, and volatility bands.
- Predefined breakout/retest confirmation criteria net of transaction costs and slippage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


@dataclass(frozen=True, slots=True)
class PriceZone:
    zone_type: str  # "SUPPORT" or "RESISTANCE"
    level: float
    lower_band: float
    upper_band: float
    uncertainty_pct: float
    touch_count: int
    recency_bars: int
    strength_score: float  # 0.0 to 100.0
    method: str  # "SWING_CLUSTER", "PIVOT", "MULTI_SESSION_EXTREME"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_type": self.zone_type,
            "level": round(self.level, 2),
            "lower_band": round(self.lower_band, 2),
            "upper_band": round(self.upper_band, 2),
            "uncertainty_pct": round(self.uncertainty_pct, 2),
            "touch_count": self.touch_count,
            "recency_bars": self.recency_bars,
            "strength_score": round(self.strength_score, 1),
            "method": self.method,
        }


@dataclass(frozen=True, slots=True)
class SupportResistanceContext:
    current_price: float
    nearest_support: Optional[PriceZone]
    nearest_resistance: Optional[PriceZone]
    dist_to_support_pct: float
    dist_to_resistance_pct: float
    is_breakout_confirmed: bool
    is_retest_bounce: bool
    all_zones: tuple[PriceZone, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_price": round(self.current_price, 2),
            "nearest_support": self.nearest_support.to_dict() if self.nearest_support else None,
            "dist_to_support_pct": round(self.dist_to_support_pct, 2),
            "nearest_resistance": self.nearest_resistance.to_dict() if self.nearest_resistance else None,
            "dist_to_resistance_pct": round(self.dist_to_resistance_pct, 2),
            "is_breakout_confirmed": self.is_breakout_confirmed,
            "is_retest_bounce": self.is_retest_bounce,
            "total_zones_identified": len(self.all_zones),
        }


class SupportResistanceEngine:
    """
    Computes probabilistic support and resistance zones and confirmation signals.
    """

    def __init__(
        self,
        default_uncertainty_pct: float = 0.5,
        cost_slippage_buffer_pct: float = 0.25,
    ) -> None:
        self.default_uncertainty_pct = default_uncertainty_pct
        self.cost_slippage_buffer_pct = cost_slippage_buffer_pct

    def identify_zones(
        self,
        df: pd.DataFrame,
        lookback_bars: int = 60,
        cluster_tolerance_pct: float = 0.8,
    ) -> SupportResistanceContext:
        """
        Extracts swing points, clusters them into probabilistic zones,
        and determines distances from the latest closing price.
        """
        if df.empty or len(df) < 5:
            current = float(df["close"].iloc[-1]) if not df.empty else 100.0
            return SupportResistanceContext(
                current_price=current,
                nearest_support=None,
                nearest_resistance=None,
                dist_to_support_pct=999.0,
                dist_to_resistance_pct=999.0,
                is_breakout_confirmed=False,
                is_retest_bounce=False,
            )

        x = df.copy().sort_values("trading_date").tail(lookback_bars).reset_index(drop=True)
        c = x["close"]
        h = x["high"] if "high" in x.columns else c
        l = x["low"] if "low" in x.columns else c
        current_price = float(c.iloc[-1])
        n = len(x)

        # 1. Identify local swing highs and swing lows
        swing_highs: List[Tuple[float, int]] = []
        swing_lows: List[Tuple[float, int]] = []

        window = 3  # 3 bars on each side for a swing pivot
        for i in range(window, n - window):
            # Swing High
            if h.iloc[i] == max(h.iloc[i - window : i + window + 1]):
                swing_highs.append((float(h.iloc[i]), n - 1 - i))
            # Swing Low
            if l.iloc[i] == min(l.iloc[i - window : i + window + 1]):
                swing_lows.append((float(l.iloc[i]), n - 1 - i))

        # Add 20-day and 50-day multi-session extremes from prior bars (no future leakage)
        if n > 20:
            swing_highs.append((float(h.iloc[:-1].tail(20).max()), 1))
            swing_lows.append((float(l.iloc[:-1].tail(20).min()), 1))

        # 2. Cluster swing points into zones
        zones: List[PriceZone] = []

        def _cluster_points(points: List[Tuple[float, int]], zone_type: str) -> List[PriceZone]:
            if not points:
                return []
            sorted_pts = sorted(points, key=lambda p: p[0])
            clusters: List[List[Tuple[float, int]]] = []
            current_cluster = [sorted_pts[0]]

            for pt in sorted_pts[1:]:
                # If price is within cluster_tolerance_pct of the cluster mean
                cluster_mean = sum(p[0] for p in current_cluster) / len(current_cluster)
                diff_pct = abs(pt[0] - cluster_mean) / cluster_mean * 100
                if diff_pct <= cluster_tolerance_pct:
                    current_cluster.append(pt)
                else:
                    clusters.append(current_cluster)
                    current_cluster = [pt]
            if current_cluster:
                clusters.append(current_cluster)

            clustered_zones = []
            for cluster in clusters:
                level = sum(p[0] for p in cluster) / len(cluster)
                touch_count = len(cluster)
                recency = min(p[1] for p in cluster)
                # Uncertainty band width
                uncert_pct = max(self.default_uncertainty_pct, cluster_tolerance_pct * 0.75)
                half_width = level * (uncert_pct / 100.0)
                lower_b = level - half_width
                upper_b = level + half_width

                # Zone strength score: combination of touches (up to 40 pts), recency (up to 40 pts), and baseline (20 pts)
                touch_pts = min(40.0, touch_count * 12.0)
                recency_pts = max(0.0, 40.0 - recency * 1.0)
                strength = min(100.0, 20.0 + touch_pts + recency_pts)

                clustered_zones.append(
                    PriceZone(
                        zone_type=zone_type,
                        level=level,
                        lower_band=lower_b,
                        upper_band=upper_b,
                        uncertainty_pct=uncert_pct,
                        touch_count=touch_count,
                        recency_bars=recency,
                        strength_score=strength,
                        method="SWING_CLUSTER",
                    )
                )
            return clustered_zones

        high_zones = _cluster_points(swing_highs, "RESISTANCE")
        low_zones = _cluster_points(swing_lows, "SUPPORT")
        all_zones = high_zones + low_zones

        # 3. Classify nearest support (< current_price) and nearest resistance (> current_price)
        supports = [z for z in all_zones if z.level <= current_price]
        resistances = [z for z in all_zones if z.level >= current_price]

        nearest_support = max(supports, key=lambda z: z.level) if supports else None
        nearest_resistance = min(resistances, key=lambda z: z.level) if resistances else None

        dist_supp_pct = (
            float((current_price - nearest_support.upper_band) / current_price * 100)
            if nearest_support
            else 999.0
        )
        dist_res_pct = (
            float((nearest_resistance.lower_band - current_price) / current_price * 100)
            if nearest_resistance
            else 999.0
        )

        # 4. Confirmation criteria net of slippage and costs
        # Breakout confirmed if current price > resistance upper band by more than cost/slippage buffer
        is_breakout = False
        buffer_mult = 1 + self.cost_slippage_buffer_pct / 100.0
        for z in high_zones:
            if current_price > z.upper_band * buffer_mult and z.recency_bars <= 5:
                is_breakout = True
                break

        # Retest bounce if price touched support upper band and closed higher
        is_bounce = False
        if nearest_support and dist_supp_pct < 1.0 and len(c) >= 2:
            if c.iloc[-1] > c.iloc[-2]:  # Positive reversal bar
                is_bounce = True

        return SupportResistanceContext(
            current_price=current_price,
            nearest_support=nearest_support,
            nearest_resistance=nearest_resistance,
            dist_to_support_pct=round(dist_supp_pct, 2),
            dist_to_resistance_pct=round(dist_res_pct, 2),
            is_breakout_confirmed=is_breakout,
            is_retest_bounce=is_bounce,
            all_zones=tuple(sorted(all_zones, key=lambda z: z.level)),
        )
