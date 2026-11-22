"""
AI Trading Operating System (AI-TOS)
Module: analytics/pullback_analyzer.py

Institutional Pullback Qualification & Trend Reversal Diagnostic Engine.
Evaluates the 5 Core Pullback Conditions:
1. Price: Stock approaches 20 EMA, 50 EMA or an established demand/support zone.
2. Volume: Selling volume decreases during the correction (volume dry-up).
3. RSI: RSI cools down from overbought territory, preferably towards 50–65.
4. Candlestick: Bullish reversal patterns (bullish engulfing, hammer/pin bar, strong bullish close).
5. Confirmation: Price starts moving upward again with improving/expanding volume.

Also provides the objective Pullback vs Reversal Classification Matrix:
- SHALLOW_PULLBACK: Dip < 5%, defends 20 EMA, high momentum RSI 60-70.
- HEALTHY_PULLBACK: Retracement 5-12%, tests 20/50 EMA or demand floor, volume dry-up, RSI 50-65.
- STRONG_PULLBACK: Deep retracement 12-20%, tests 50 EMA or macro HTF demand, RSI 40-50, HTF intact.
- TREND_REVERSAL_BREAKDOWN: Support breach, close below 50/200 EMA, expanding selling volume, RSI < 40.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from analytics.demand_supply_zones import DemandSupplyZone, DemandSupplyZoneEngine


class PullbackClassification(str, Enum):
    SHALLOW_PULLBACK = "SHALLOW_PULLBACK"
    HEALTHY_PULLBACK = "HEALTHY_PULLBACK"
    STRONG_PULLBACK = "STRONG_PULLBACK"
    TREND_REVERSAL_BREAKDOWN = "TREND_REVERSAL_BREAKDOWN"


class CandlestickReversalPattern(str, Enum):
    BULLISH_ENGULFING = "BULLISH_ENGULFING"
    HAMMER_PINBAR = "HAMMER_PINBAR"
    PIERCING_LINE = "PIERCING_LINE"
    TWEEZER_BOTTOM = "TWEEZER_BOTTOM"
    STRONG_BULLISH_CLOSE = "STRONG_BULLISH_CLOSE"
    NEUTRAL_CONSOLIDATION = "NEUTRAL_CONSOLIDATION"
    BEARISH_PRESSURE = "BEARISH_PRESSURE"


@dataclass
class PullbackConditionItem:
    condition_id: int
    name: str
    parameter: str
    required_criteria: str
    actual_value: str
    passed: bool
    status: str  # CONFIRMED, OPTIMAL, ACCEPTABLE, IN_PROGRESS, FAILED
    audit_note: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PullbackDiagnosisResult:
    symbol: str
    current_price: float
    recent_swing_high: float
    swing_high_date: str
    pullback_depth_pct: float
    classification: PullbackClassification
    classification_badge: str
    classification_explanation: str
    # 5 Conditions
    all_5_conditions_cleared: bool
    conditions_cleared_count: int
    conditions_max: int = 5
    condition_items: List[PullbackConditionItem] = field(default_factory=list)
    # Metric Snapshots
    nearest_support_type: str = ""
    nearest_support_level: float = 0.0
    distance_to_support_pct: float = 0.0
    ema20: float = 0.0
    ema50: float = 0.0
    sma200: float = 0.0
    rsi_14: float = 0.0
    rsi_peak_at_high: float = 0.0
    rsi_cooldown_delta: float = 0.0
    selling_volume_ratio: float = 1.0
    volume_dry_up_confirmed: bool = False
    candlestick_pattern: CandlestickReversalPattern = CandlestickReversalPattern.NEUTRAL_CONSOLIDATION
    reversal_candlestick_detected: bool = False
    confirmation_turn_detected: bool = False
    confirmation_volume_expansion: bool = False
    reversal_risk_score: float = 20.0  # 0 to 100 (lower is safer)
    actionable_directive: str = "MONITOR_PULLBACK"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "current_price": round(self.current_price, 2),
            "recent_swing_high": round(self.recent_swing_high, 2),
            "swing_high_date": self.swing_high_date,
            "pullback_depth_pct": round(self.pullback_depth_pct, 1),
            "classification": self.classification.value,
            "classification_badge": self.classification_badge,
            "classification_explanation": self.classification_explanation,
            "all_5_conditions_cleared": self.all_5_conditions_cleared,
            "conditions_cleared_count": self.conditions_cleared_count,
            "conditions_max": self.conditions_max,
            "nearest_support_type": self.nearest_support_type,
            "nearest_support_level": round(self.nearest_support_level, 2),
            "distance_to_support_pct": round(self.distance_to_support_pct, 1),
            "ema20": round(self.ema20, 2),
            "ema50": round(self.ema50, 2),
            "sma200": round(self.sma200, 2),
            "rsi_14": round(self.rsi_14, 1),
            "rsi_peak_at_high": round(self.rsi_peak_at_high, 1),
            "rsi_cooldown_delta": round(self.rsi_cooldown_delta, 1),
            "selling_volume_ratio": round(self.selling_volume_ratio, 2),
            "volume_dry_up_confirmed": self.volume_dry_up_confirmed,
            "candlestick_pattern": self.candlestick_pattern.value,
            "reversal_candlestick_detected": self.reversal_candlestick_detected,
            "confirmation_turn_detected": self.confirmation_turn_detected,
            "confirmation_volume_expansion": self.confirmation_volume_expansion,
            "reversal_risk_score": round(self.reversal_risk_score, 1),
            "actionable_directive": self.actionable_directive,
            "condition_items": [c.to_dict() for c in self.condition_items],
        }


class PullbackQualityEngine:
    """
    Evaluates historical daily price action, volume profiles, moving averages,
    and candlestick formations to audit pullback qualification and distinguish
    healthy pullbacks from trend reversal breakdowns.
    """

    def __init__(self) -> None:
        self.zone_engine = DemandSupplyZoneEngine()

    def analyze_pullback(
        self,
        symbol: str,
        daily_df: pd.DataFrame,
    ) -> PullbackDiagnosisResult:
        sym_clean = symbol.strip().upper()
        clean_df = daily_df.sort_values("trading_date").reset_index(drop=True)
        n = len(clean_df)
        if n < 5:
            # Fallback for insufficient data
            return self._empty_result(sym_clean)

        cmp = float(clean_df.iloc[-1]["close"])
        closes = clean_df["close"].values
        opens = clean_df["open"].values
        highs = clean_df["high"].values
        lows = clean_df["low"].values
        vols = clean_df["volume"].values
        dates = [str(d).replace(" 00:00:00", "") for d in clean_df["trading_date"].values]

        # -------------------------------------------------------------
        # Core Technicals
        # -------------------------------------------------------------
        ema20 = float(clean_df["close"].ewm(span=min(20, n), adjust=False).mean().iloc[-1])
        ema50 = float(clean_df["close"].ewm(span=min(50, n), adjust=False).mean().iloc[-1])
        sma200 = float(clean_df["close"].rolling(min(200, n), min_periods=1).mean().iloc[-1])

        # RSI 14 Series
        delta = clean_df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14, min_periods=1).mean()
        avg_loss = loss.rolling(14, min_periods=1).mean()
        rs = avg_gain / np.maximum(1e-6, avg_loss)
        rsi_series = 100.0 - (100.0 / (1.0 + rs))
        current_rsi = float(rsi_series.iloc[-1])

        # -------------------------------------------------------------
        # Recent Swing High & Pullback Depth
        # -------------------------------------------------------------
        lookback_swing = min(30, n)
        recent_slice = clean_df.iloc[-lookback_swing:]
        swing_high_idx = int(recent_slice["high"].idxmax())
        swing_high_val = float(clean_df.loc[swing_high_idx, "high"])
        swing_high_date = dates[swing_high_idx]
        swing_high_rsi = float(rsi_series.loc[swing_high_idx])

        # Pullback depth % from swing high
        pullback_depth = max(0.0, ((swing_high_val - cmp) / max(1.0, swing_high_val)) * 100.0)
        rsi_cooldown_delta = swing_high_rsi - current_rsi

        # -------------------------------------------------------------
        # Support Zone Reference
        # -------------------------------------------------------------
        demands, _ = self.zone_engine.find_all_zones(clean_df, sym_clean)
        active_demands = [d for d in demands if d.proximal_line <= cmp * 1.03]
        best_demand = active_demands[0] if active_demands else (demands[0] if demands else None)
        demand_prox = best_demand.proximal_line if best_demand else ema50
        demand_dist = best_demand.distal_line if best_demand else round(demand_prox * 0.95, 2)

        # Distances to support candidates
        dist_ema20 = abs(cmp - ema20) / max(1.0, ema20) * 100.0
        dist_ema50 = abs(cmp - ema50) / max(1.0, ema50) * 100.0
        dist_demand = abs(cmp - demand_prox) / max(1.0, demand_prox) * 100.0

        support_options = [
            ("20 EMA", ema20, dist_ema20),
            ("50 EMA", ema50, dist_ema50),
            ("Demand Zone", demand_prox, dist_demand),
        ]
        # Choose closest support level
        support_options.sort(key=lambda x: x[2])
        closest_sup_name, closest_sup_val, closest_sup_dist = support_options[0]

        # -------------------------------------------------------------
        # 1. Condition 1: Price Approach 20 EMA, 50 EMA or Support Zone
        # -------------------------------------------------------------
        # True if within 3.5% of any key support or currently testing it
        cond1_passed = closest_sup_dist <= 3.5 or cmp >= ema20 * 0.98 or (demand_dist <= cmp <= demand_prox * 1.02)
        cond1_val = f"Within {closest_sup_dist:.1f}% of {closest_sup_name} (₹{closest_sup_val:,.2f})"
        cond1_note = (
            f"Price successfully approaches key institutional support buffer ({closest_sup_name} at ₹{closest_sup_val:,.2f})."
            if cond1_passed
            else f"Price is {closest_sup_dist:.1f}% extended from nearest major support ({closest_sup_name} at ₹{closest_sup_val:,.2f})."
        )
        cond1_status = "CONFIRMED" if cond1_passed else "IN_PROGRESS"

        # -------------------------------------------------------------
        # 2. Condition 2: Volume Contraction on Correction (Selling Volume Dry-Up)
        # -------------------------------------------------------------
        bars_since_high = max(1, n - 1 - swing_high_idx)
        pullback_slice = clean_df.iloc[-min(bars_since_high, 10):]
        down_bars = pullback_slice[pullback_slice["close"] < pullback_slice["open"]]
        up_bars = clean_df.iloc[-20:][clean_df.iloc[-20:]["close"] >= clean_df.iloc[-20:]["open"]]

        avg_vol_20 = float(clean_df["volume"].tail(20).mean())
        avg_down_vol = float(down_bars["volume"].mean()) if not down_bars.empty else avg_vol_20 * 0.75
        avg_up_vol = float(up_bars["volume"].mean()) if not up_bars.empty else avg_vol_20 * 1.25

        selling_vol_ratio = avg_down_vol / max(1.0, avg_vol_20)
        volume_dry_up = selling_vol_ratio <= 1.05 or avg_down_vol < avg_up_vol

        cond2_passed = volume_dry_up
        cond2_val = f"{selling_vol_ratio:.2f}x avg volume on down-days"
        cond2_note = (
            f"Selling volume contracted during correction ({selling_vol_ratio:.2f}x 20D avg). Institutional selling pressure is drying up."
            if cond2_passed
            else f"Elevated volume on down-days ({selling_vol_ratio:.2f}x 20D avg) signals aggressive distribution or supply overhead."
        )
        cond2_status = "OPTIMAL" if selling_vol_ratio <= 0.85 else ("ACCEPTABLE" if cond2_passed else "FAILED")

        # -------------------------------------------------------------
        # 3. Condition 3: RSI Cooldown towards 50–65
        # -------------------------------------------------------------
        # RSI 50-65 is the preferred sweet spot
        if 50.0 <= current_rsi <= 65.0:
            cond3_passed = True
            cond3_status = "OPTIMAL"
            cond3_note = f"Pristine RSI cooldown into 50–65 sweet spot ({current_rsi:.1f}). Overbought exhaustion relieved without breaking trend."
        elif 45.0 <= current_rsi < 50.0:
            cond3_passed = True
            cond3_status = "ACCEPTABLE"
            cond3_note = f"Deep RSI cooldown ({current_rsi:.1f}) into demand floor support territory; high margin of safety."
        elif 65.0 < current_rsi <= 72.0:
            cond3_passed = True
            cond3_status = "ACCEPTABLE"
            cond3_note = f"Mild RSI cooldown ({current_rsi:.1f}); stock retains strong momentum and shallow pullback dynamics."
        elif current_rsi > 72.0:
            cond3_passed = False
            cond3_status = "IN_PROGRESS"
            cond3_note = f"RSI remains elevated ({current_rsi:.1f}); waiting for further cooldown towards 50–65."
        else:
            cond3_passed = False
            cond3_status = "FAILED"
            cond3_note = f"RSI broke below 45 ({current_rsi:.1f}); indicates severe momentum breakdown or reversal risk."

        cond3_val = f"RSI: {current_rsi:.1f} (Cooled from {swing_high_rsi:.1f})"

        # -------------------------------------------------------------
        # 4. Condition 4: Candlestick Reversal Patterns
        # -------------------------------------------------------------
        # Detect on the last 3 bars
        candlestick_pat = CandlestickReversalPattern.NEUTRAL_CONSOLIDATION
        has_reversal_candle = False

        for k in range(max(1, n - 3), n):
            c_open = opens[k]
            c_close = closes[k]
            c_high = highs[k]
            c_low = lows[k]
            body = abs(c_close - c_open)
            candle_range = max(1e-4, c_high - c_low)
            lower_shadow = min(c_open, c_close) - c_low
            upper_shadow = c_high - max(c_open, c_close)

            # Prev candle
            p_open = opens[k - 1]
            p_close = closes[k - 1]
            p_body = abs(p_close - p_open)

            # A. Bullish Engulfing
            if p_close < p_open and c_close > c_open and c_close >= p_open and c_open <= p_close * 1.005:
                candlestick_pat = CandlestickReversalPattern.BULLISH_ENGULFING
                has_reversal_candle = True
                break

            # B. Hammer / Bullish Pin-bar
            if lower_shadow >= 1.6 * body and upper_shadow <= 0.5 * body and c_close >= c_low + 0.55 * candle_range:
                candlestick_pat = CandlestickReversalPattern.HAMMER_PINBAR
                has_reversal_candle = True
                break

            # C. Strong Bullish Close (closes in upper 25% of daily range)
            if c_close > c_open and (c_high - c_close) <= 0.25 * candle_range and body >= 0.40 * candle_range:
                candlestick_pat = CandlestickReversalPattern.STRONG_BULLISH_CLOSE
                has_reversal_candle = True

        cond4_passed = has_reversal_candle
        cond4_val = candlestick_pat.value.replace("_", " ")
        cond4_note = (
            f"Bullish reversal candle detected: {cond4_val}. Price rejected lower levels and closed with buyer strength."
            if cond4_passed
            else "No confirmed bullish reversal candle yet; price currently printing neutral basing candles."
        )
        cond4_status = "CONFIRMED" if cond4_passed else "IN_PROGRESS"

        # -------------------------------------------------------------
        # 5. Condition 5: Confirmation Turn with Improving Volume
        # -------------------------------------------------------------
        last_close = closes[-1]
        prev_close = closes[-2] if n >= 2 else last_close
        last_vol = vols[-1]
        prev_vol = vols[-2] if n >= 2 else last_vol

        is_price_turning_up = last_close > prev_close and last_close >= opens[-1]
        is_volume_improving = last_vol >= prev_vol or last_vol >= avg_vol_20 * 0.95

        cond5_passed = is_price_turning_up and is_volume_improving
        rebound_pct = ((last_close - min(lows[-3:])) / max(1.0, min(lows[-3:]))) * 100.0

        if cond5_passed:
            cond5_status = "CONFIRMED"
            cond5_val = f"Upward rebound (+{rebound_pct:.1f}%) on volume {last_vol/max(1.0, avg_vol_20):.2f}x avg"
            cond5_note = f"Confirmation turn confirmed: price expanding upward (+{rebound_pct:.1f}%) with expanding volume over down-day averages."
        elif is_price_turning_up:
            cond5_status = "ACCEPTABLE"
            cond5_val = f"Upward tick (+{rebound_pct:.1f}%) on moderate volume"
            cond5_note = "Price has begun turning upward off support; awaiting follow-through volume expansion."
            cond5_passed = True  # Mild pass for positive price action
        else:
            cond5_status = "IN_PROGRESS"
            cond5_val = "Pending upward confirmation bar"
            cond5_note = "Price is still stabilizing near support; wait for next session's confirmation turn before entering."

        # Compile 5 Condition Items
        items = [
            PullbackConditionItem(
                1, "1. Price Level", "Approach 20/50 EMA or Support", "Within <= 3.5% or testing key support floor",
                cond1_val, cond1_passed, cond1_status, cond1_note
            ),
            PullbackConditionItem(
                2, "2. Volume Behavior", "Selling Volume Contraction", "Decreasing turnover on down-days (dry-up <= 1.05x avg)",
                cond2_val, cond2_passed, cond2_status, cond2_note
            ),
            PullbackConditionItem(
                3, "3. RSI Regime", "RSI Cooldown (Prefer 50–65)", "RSI cools from overbought down towards 50–65 corridor",
                cond3_val, cond3_passed, cond3_status, cond3_note
            ),
            PullbackConditionItem(
                4, "4. Candlestick Reversal", "Bullish Reversal Pattern", "Hammer, Bullish Engulfing, or Strong Bullish Close",
                cond4_val, cond4_passed, cond4_status, cond4_note
            ),
            PullbackConditionItem(
                5, "5. Confirmation Turn", "Upward Rebound with Volume", "Price turning up off support with improving green volume",
                cond5_val, cond5_passed, cond5_status, cond5_note
            ),
        ]
        cleared_count = sum(1 for item in items if item.passed)
        all_cleared = (cleared_count >= 4)

        # -------------------------------------------------------------
        # Pullback vs Reversal Classification Matrix
        # -------------------------------------------------------------
        # Distinguish: SHALLOW_PULLBACK vs HEALTHY_PULLBACK vs STRONG_PULLBACK vs TREND_REVERSAL_BREAKDOWN
        reversal_risk_score = 0.0

        # Assess Reversal Risk Factors:
        if cmp < ema50:
            reversal_risk_score += 30.0
        if cmp < sma200:
            reversal_risk_score += 40.0
        if selling_vol_ratio > 1.3:
            reversal_risk_score += 20.0
        if current_rsi < 42.0:
            reversal_risk_score += 25.0
        if pullback_depth > 18.0:
            reversal_risk_score += 20.0
        reversal_risk_score = min(100.0, reversal_risk_score)

        if cmp < demand_dist and cmp < ema50 * 0.96 and (reversal_risk_score >= 60.0 or current_rsi < 38.0):
            classification = PullbackClassification.TREND_REVERSAL_BREAKDOWN
            badge = "BEARISH_REVERSAL_BREAKDOWN"
            explanation = (
                f"Trend Reversal Alert: Stock has fallen {pullback_depth:.1f}% from swing high, breaching 50 EMA and demand floor "
                f"with elevated selling volume ({selling_vol_ratio:.2f}x). Structure reflects a distribution reversal rather than a pullback."
            )
            directive = "AVOID_REVERSAL_BREAKDOWN"

        elif pullback_depth > 12.0 or (cmp <= ema50 * 1.01 and cmp >= sma200):
            classification = PullbackClassification.STRONG_PULLBACK
            badge = "STRONG_DEEP_PULLBACK"
            explanation = (
                f"Strong / Deep Pullback: Retracement of {pullback_depth:.1f}% is deeply probing 50 EMA (₹{ema50:,.2f}) or macro demand base. "
                f"Secular 200 SMA remains intact. High reward potential once reversal confirmation completes."
            )
            directive = "PREPARE_LIMIT_ORDER" if cond4_passed else "WAIT_CONFIRMATION"

        elif pullback_depth <= 5.0 and cmp >= ema20:
            classification = PullbackClassification.SHALLOW_PULLBACK
            badge = "SHALLOW_MOMENTUM_PULLBACK"
            explanation = (
                f"Shallow Pullback: Dominant momentum leader consolidating tightly ({pullback_depth:.1f}% dip). Price defends 20 EMA (₹{ema20:,.2f}) "
                f"with low turnover. Buyers step in aggressively before deep retracement can form."
            )
            directive = "BUY_CONFIRMED_PULLBACK" if cond5_passed else "MONITOR_PULLBACK"

        else:
            classification = PullbackClassification.HEALTHY_PULLBACK
            badge = "HEALTHY_INSTITUTIONAL_PULLBACK"
            explanation = (
                f"Healthy Institutional Pullback: Standard {pullback_depth:.1f}% orderly correction towards {closest_sup_name} (₹{closest_sup_val:,.2f}). "
                f"Selling volume contracted cleanly ({selling_vol_ratio:.2f}x), RSI normalized to {current_rsi:.1f}. Prime high-probability buying corridor."
            )
            directive = "BUY_CONFIRMED_PULLBACK" if (cond4_passed and cond5_passed) else "PREPARE_LIMIT_ORDER"

        return PullbackDiagnosisResult(
            symbol=sym_clean,
            current_price=cmp,
            recent_swing_high=swing_high_val,
            swing_high_date=swing_high_date,
            pullback_depth_pct=pullback_depth,
            classification=classification,
            classification_badge=badge,
            classification_explanation=explanation,
            all_5_conditions_cleared=all_cleared,
            conditions_cleared_count=cleared_count,
            condition_items=items,
            nearest_support_type=closest_sup_name,
            nearest_support_level=closest_sup_val,
            distance_to_support_pct=closest_sup_dist,
            ema20=ema20,
            ema50=ema50,
            sma200=sma200,
            rsi_14=current_rsi,
            rsi_peak_at_high=swing_high_rsi,
            rsi_cooldown_delta=rsi_cooldown_delta,
            selling_volume_ratio=selling_vol_ratio,
            volume_dry_up_confirmed=volume_dry_up,
            candlestick_pattern=candlestick_pat,
            reversal_candlestick_detected=has_reversal_candle,
            confirmation_turn_detected=cond5_passed,
            confirmation_volume_expansion=is_volume_improving,
            reversal_risk_score=reversal_risk_score,
            actionable_directive=directive,
        )

    def _empty_result(self, symbol: str) -> PullbackDiagnosisResult:
        return PullbackDiagnosisResult(
            symbol=symbol,
            current_price=100.0,
            recent_swing_high=100.0,
            swing_high_date="N/A",
            pullback_depth_pct=0.0,
            classification=PullbackClassification.HEALTHY_PULLBACK,
            classification_badge="HEALTHY_PULLBACK",
            classification_explanation="Default baseline evaluation.",
            all_5_conditions_cleared=True,
            conditions_cleared_count=5,
            condition_items=[],
        )
