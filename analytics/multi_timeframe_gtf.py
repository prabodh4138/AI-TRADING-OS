"""
AI Trading Operating System
Module: analytics/multi_timeframe_gtf.py

Multi-Timeframe Institutional GTF Analysis Engine:
- Resamples daily market data into:
  * Monthly (M)
  * Quarterly (Q)
  * Half-Yearly (HY)
  * Yearly (Y)
- Evaluates Trend, Momentum, and Institutional Footprints across all 4 macro horizons.
- Location on the Curve Analysis:
  * Determines exact position between higher-timeframe Demand and Supply zones:
    VERY_LOW (0-25%), LOW (25-40%), EQUILIBRIUM (40-60%), HIGH (60-80%), VERY_HIGH (80-100%)
- Multi-Timeframe Alignment Grading:
  * GRADE A+ : Flawless confluence across Yearly, Half-Yearly, Quarterly, Monthly + Low on Curve
  * GRADE A  : Strong Quarterly & Monthly institutional support + Low/Equilibrium on Curve
  * GRADE B  : Selective pullback setup
  * GRADE C  : Conflicted / Unaligned
  * AVOID    : High on Curve / Testing Macro Supply (Retail Trap)
- Market Condition Confluence:
  * Integrates NIFTY 50 & Bank Nifty multi-timeframe posture to dynamically adjust trade permissibility.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from analytics.demand_supply_zones import (
    DemandSupplyZone,
    DemandSupplyZoneEngine,
    PriceLocation,
    ZoneFreshness,
    ZoneType,
)


class TimeframeTrend(str, Enum):
    STRONG_BULLISH = "STRONG_BULLISH"
    BULLISH = "BULLISH"
    NEUTRAL_RANGE = "NEUTRAL_RANGE"
    BEARISH = "BEARISH"
    STRONG_BEARISH = "STRONG_BEARISH"


class CurveLocation(str, Enum):
    VERY_LOW = "VERY_LOW"      # 0% to 25% (Wholesale Accumulation - Prime Buy)
    LOW = "LOW"                # 25% to 40% (Favorable Buy Zone)
    EQUILIBRIUM = "EQUILIBRIUM"# 40% to 60% (Fair Value / Caution)
    HIGH = "HIGH"              # 60% to 80% (Expensive / Do Not Buy)
    VERY_HIGH = "VERY_HIGH"    # 80% to 100% (Institutional Distribution / Extreme Danger)


class AlignmentGrade(str, Enum):
    GRADE_A_PLUS = "GRADE_A_PLUS"  # Flawless Institutional Confluence (Y, HY, Q, M Bullish + Low Curve)
    GRADE_A = "GRADE_A"            # Strong HTF Support (Q & M Bullish + Low/Mid Curve)
    GRADE_B = "GRADE_B"            # Selective Pullback
    GRADE_C = "GRADE_C"            # Misaligned / Choppy
    AVOID_TRAP = "AVOID_TRAP"      # High on Curve / Macro Supply Trap


@dataclass
class TimeframeState:
    timeframe_name: str       # "Monthly", "Quarterly", "Half-Yearly", "Yearly"
    bar_count: int
    latest_close: float
    timeframe_return_pct: float
    trend_state: TimeframeTrend
    is_bullish: bool
    is_at_demand: bool
    nearest_demand_level: Optional[float] = None
    nearest_supply_level: Optional[float] = None


@dataclass
class StockMultiTimeframeAlignment:
    symbol: str
    current_price: float
    as_of_date: date
    # Timeframe States
    yearly: TimeframeState
    half_yearly: TimeframeState
    quarterly: TimeframeState
    monthly: TimeframeState
    # Curve Analysis
    curve_location_pct: float
    curve_state: CurveLocation
    htf_demand_zone: Optional[float]
    htf_supply_zone: Optional[float]
    # Daily Execution
    has_daily_demand: bool
    daily_zone_type: Optional[str]
    daily_proximal_entry: float
    daily_distal_stop: float
    daily_target_supply: float
    reward_to_risk: float
    # Confluence
    alignment_grade: AlignmentGrade
    alignment_score: float # 0 to 100
    is_best_aligned_for_trading: bool
    confluence_rationale: List[str]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["as_of_date"] = str(self.as_of_date)
        d["curve_state"] = self.curve_state.value
        d["alignment_grade"] = self.alignment_grade.value
        return d


@dataclass
class MacroMarketPosture:
    benchmark_symbol: str
    as_of_date: date
    yearly_trend: str
    quarterly_trend: str
    monthly_trend: str
    market_curve_location: str
    overall_posture: str  # "AGGRESSIVE_BULLISH", "MODERATE_BULLISH", "DEFENSIVE_CHOPPY", "BEARISH_DISTRIBUTION"
    sizing_recommendation: float # 1.0x, 0.75x, 0.50x, 0.0x
    summary_notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MultiTimeframeGTFEngine:
    """
    Computes institutional Multi-Timeframe Confluence across
    Monthly, Quarterly, Half-Yearly, and Yearly horizons.
    """

    def __init__(self) -> None:
        self.zone_engine = DemandSupplyZoneEngine()

    def resample_timeframes(
        self,
        daily_df: pd.DataFrame,
    ) -> Dict[str, pd.DataFrame]:
        """
        Resamples clean daily OHLCV bars into Monthly, Quarterly, Half-Yearly, and Yearly bars.
        """
        df = daily_df.copy()
        df["trading_date"] = pd.to_datetime(df["trading_date"])
        df = df.set_index("trading_date").sort_index()

        def _agg_resample(rule: str) -> pd.DataFrame:
            res = df.resample(rule).agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }).dropna()
            return res.reset_index()

        return {
            "Daily": daily_df.sort_values("trading_date").reset_index(drop=True),
            "Monthly": _agg_resample("MS"),
            "Quarterly": _agg_resample("QS"),
            "Half-Yearly": _agg_resample("6MS"),
            "Yearly": _agg_resample("YS"),
        }

    def evaluate_timeframe_state(
        self,
        tf_df: pd.DataFrame,
        tf_name: str,
    ) -> TimeframeState:
        """Evaluates trend, return, and demand/supply zone presence on a resampled timeframe."""
        if tf_df.empty:
            return TimeframeState(
                timeframe_name=tf_name,
                bar_count=0,
                latest_close=0.0,
                timeframe_return_pct=0.0,
                trend_state=TimeframeTrend.NEUTRAL_RANGE,
                is_bullish=False,
                is_at_demand=False,
            )

        n = len(tf_df)
        latest_bar = tf_df.iloc[-1]
        c = float(latest_bar["close"])
        o = float(latest_bar["open"])

        # Timeframe return
        ret = round(((c / o) - 1.0) * 100.0, 2)
        if n > 1:
            prev_c = float(tf_df.iloc[-2]["close"])
            ret = round(((c / prev_c) - 1.0) * 100.0, 2)

        # Trend identification
        if n >= 3:
            recent_closes = tf_df["close"].tail(3).values
            if recent_closes[2] > recent_closes[1] > recent_closes[0] and c >= o:
                trend = TimeframeTrend.STRONG_BULLISH
                is_bull = True
            elif c >= o or (recent_closes[2] > recent_closes[1]):
                trend = TimeframeTrend.BULLISH
                is_bull = True
            elif recent_closes[2] < recent_closes[1] < recent_closes[0] and c < o:
                trend = TimeframeTrend.STRONG_BEARISH
                is_bull = False
            elif c < o:
                trend = TimeframeTrend.BEARISH
                is_bull = False
            else:
                trend = TimeframeTrend.NEUTRAL_RANGE
                is_bull = False
        else:
            trend = TimeframeTrend.BULLISH if c >= o else TimeframeTrend.BEARISH
            is_bull = (c >= o)

        # Zone detection on this timeframe
        demand_zones, supply_zones = self.zone_engine.find_all_zones(tf_df, symbol=tf_name)
        is_at_d = any(z.location_state == PriceLocation.AT_DEMAND_ZONE for z in demand_zones)

        nearest_d = demand_zones[0].proximal_line if demand_zones else None
        nearest_s = supply_zones[0].proximal_line if supply_zones else None

        return TimeframeState(
            timeframe_name=tf_name,
            bar_count=n,
            latest_close=round(c, 2),
            timeframe_return_pct=ret,
            trend_state=trend,
            is_bullish=is_bull,
            is_at_demand=is_at_d,
            nearest_demand_level=nearest_d,
            nearest_supply_level=nearest_s,
        )

    def calculate_curve_location(
        self,
        current_price: float,
        monthly_state: TimeframeState,
        quarterly_state: TimeframeState,
        daily_df: pd.DataFrame,
    ) -> Tuple[float, CurveLocation, Optional[float], Optional[float]]:
        """
        Determines the institutional Location on the Curve (Wholesale vs Retail price).
        Formula: (Current Price - HTF Demand) / (HTF Supply - HTF Demand) * 100
        """
        htf_demand = quarterly_state.nearest_demand_level or monthly_state.nearest_demand_level
        htf_supply = quarterly_state.nearest_supply_level or monthly_state.nearest_supply_level

        # Fallback to multi-month swing extremes if zones not yet tagged
        if htf_demand is None or htf_demand >= current_price:
            htf_demand = float(daily_df["low"].tail(120).min()) if len(daily_df) >= 60 else float(daily_df["low"].min())
        if htf_supply is None or htf_supply <= current_price:
            htf_supply = float(daily_df["high"].tail(120).max()) if len(daily_df) >= 60 else float(daily_df["high"].max())

        span = max(1.0, htf_supply - htf_demand)
        raw_pct = ((current_price - htf_demand) / span) * 100.0
        curve_pct = round(np.clip(raw_pct, 0.0, 100.0), 1)

        if curve_pct <= 25.0:
            c_loc = CurveLocation.VERY_LOW
        elif curve_pct <= 40.0:
            c_loc = CurveLocation.LOW
        elif curve_pct <= 60.0:
            c_loc = CurveLocation.EQUILIBRIUM
        elif curve_pct <= 80.0:
            c_loc = CurveLocation.HIGH
        else:
            c_loc = CurveLocation.VERY_HIGH

        return curve_pct, c_loc, round(htf_demand, 2), round(htf_supply, 2)

    def evaluate_stock_alignment(
        self,
        daily_df: pd.DataFrame,
        symbol: str,
        as_of_date: Optional[date] = None,
    ) -> StockMultiTimeframeAlignment:
        """
        Performs full institutional multi-timeframe analysis on a single stock.
        Evaluates Yearly, Half-Yearly, Quarterly, Monthly, and Daily confluence.
        """
        clean = daily_df.sort_values("trading_date").reset_index(drop=True)
        cur_price = float(clean.iloc[-1]["close"])
        eff_date = as_of_date or pd.to_datetime(clean.iloc[-1]["trading_date"]).date()

        # 1. Resample to all 4 macro timeframes
        tf_dict = self.resample_timeframes(clean)

        # 2. Evaluate state for each horizon
        y_state = self.evaluate_timeframe_state(tf_dict["Yearly"], "Yearly")
        hy_state = self.evaluate_timeframe_state(tf_dict["Half-Yearly"], "Half-Yearly")
        q_state = self.evaluate_timeframe_state(tf_dict["Quarterly"], "Quarterly")
        m_state = self.evaluate_timeframe_state(tf_dict["Monthly"], "Monthly")

        # 3. Curve Analysis
        curve_pct, curve_state, htf_d, htf_s = self.calculate_curve_location(
            cur_price, m_state, q_state, clean
        )

        # 4. Daily Execution Zone
        daily_demand, daily_supply = self.zone_engine.find_all_zones(clean, symbol=symbol)
        has_daily_d = len(daily_demand) > 0
        best_daily = daily_demand[0] if has_daily_d else None

        proximal = best_daily.proximal_line if best_daily else round(cur_price * 0.98, 2)
        distal = best_daily.distal_line if best_daily else round(cur_price * 0.96, 2)
        target = best_daily.opposing_target if best_daily else round(cur_price * 1.05, 2)
        rr = best_daily.reward_to_risk if best_daily else 2.0
        z_type = best_daily.zone_type.value.replace("DEMAND_", "") if best_daily else None

        # 5. Confluence Scoring & Grading
        score = 0.0
        rationale: List[str] = []

        # Timeframe points (Max 55 pts)
        if y_state.is_bullish:
            score += 15.0
            rationale.append("Yearly trend is structurally Bullish (+15)")
        if hy_state.is_bullish:
            score += 10.0
            rationale.append("Half-Yearly momentum is positive (+10)")
        if q_state.is_bullish:
            score += 15.0
            rationale.append("Quarterly institutional order flow is Bullish (+15)")
        if m_state.is_bullish:
            score += 15.0
            rationale.append("Monthly intermediate trend is Bullish (+15)")

        # Curve points (Max 25 pts)
        if curve_state == CurveLocation.VERY_LOW:
            score += 25.0
            rationale.append(f"Wholesale price: VERY LOW on Curve ({curve_pct}%) (+25)")
        elif curve_state == CurveLocation.LOW:
            score += 18.0
            rationale.append(f"Wholesale price: LOW on Curve ({curve_pct}%) (+18)")
        elif curve_state == CurveLocation.EQUILIBRIUM:
            score += 8.0
            rationale.append(f"Equilibrium on Curve ({curve_pct}%) (+8)")
        else:
            score -= 15.0
            rationale.append(f"WARNING: High on Curve ({curve_pct}%) - Expensive retail price (-15)")

        # Daily Zone points (Max 20 pts)
        if best_daily and best_daily.freshness == ZoneFreshness.FRESH:
            score += 20.0
            rationale.append(f"Fresh Daily {z_type} Demand Zone active (+20)")
        elif best_daily:
            score += 10.0
            rationale.append(f"Tested Daily {z_type} Demand Zone active (+10)")

        score = round(np.clip(score, 0.0, 100.0), 1)

        # Assign Institutional Alignment Grade
        if (
            score >= 80.0 and
            y_state.is_bullish and
            q_state.is_bullish and
            curve_state in {CurveLocation.VERY_LOW, CurveLocation.LOW} and
            best_daily is not None
        ):
            grade = AlignmentGrade.GRADE_A_PLUS
            is_best = True
        elif score >= 65.0 and curve_state in {CurveLocation.VERY_LOW, CurveLocation.LOW, CurveLocation.EQUILIBRIUM}:
            grade = AlignmentGrade.GRADE_A
            is_best = True
        elif curve_state in {CurveLocation.HIGH, CurveLocation.VERY_HIGH}:
            grade = AlignmentGrade.AVOID_TRAP
            is_best = False
            rationale.append("AVOID: Stock is near macro supply ceiling")
        elif score >= 45.0:
            grade = AlignmentGrade.GRADE_B
            is_best = False
        else:
            grade = AlignmentGrade.GRADE_C
            is_best = False

        return StockMultiTimeframeAlignment(
            symbol=symbol,
            current_price=cur_price,
            as_of_date=eff_date,
            yearly=y_state,
            half_yearly=hy_state,
            quarterly=q_state,
            monthly=m_state,
            curve_location_pct=curve_pct,
            curve_state=curve_state,
            htf_demand_zone=htf_d,
            htf_supply_zone=htf_s,
            has_daily_demand=has_daily_d,
            daily_zone_type=z_type,
            daily_proximal_entry=proximal,
            daily_distal_stop=distal,
            daily_target_supply=target,
            reward_to_risk=rr,
            alignment_grade=grade,
            alignment_score=score,
            is_best_aligned_for_trading=is_best,
            confluence_rationale=rationale,
        )

    def evaluate_macro_market_condition(
        self,
        daily_df: pd.DataFrame,
        benchmark_symbol: str = "NIFTY 50",
    ) -> MacroMarketPosture:
        """
        Analyzes the broader market condition (NIFTY 50) across all 4 macro timeframes
        to provide overall posture and capital sizing guidelines.
        """
        bench_df = daily_df[daily_df["symbol"].str.upper() == benchmark_symbol.upper()]
        if bench_df.empty or len(bench_df) < 15:
            # Composite fallback
            bench_df = (
                daily_df.groupby("trading_date", as_index=False)
                .agg({"open": "mean", "high": "max", "low": "min", "close": "mean", "volume": "sum"})
            )

        align = self.evaluate_stock_alignment(bench_df, symbol=benchmark_symbol)

        y_str = align.yearly.trend_state.value
        q_str = align.quarterly.trend_state.value
        m_str = align.monthly.trend_state.value
        curve_str = align.curve_state.value

        notes = []
        if align.yearly.is_bullish and align.quarterly.is_bullish:
            if align.curve_state in {CurveLocation.VERY_LOW, CurveLocation.LOW}:
                posture = "AGGRESSIVE_BULLISH"
                mult = 1.0
                notes.append("Market is in Secular Bullish Alignment and LOW on macro curve. Optimal buying window.")
            else:
                posture = "MODERATE_BULLISH"
                mult = 0.75
                notes.append(f"Market trend is Bullish but at {curve_str} curve location. Favor only Grade A+ setups.")
        elif align.monthly.is_bullish:
            posture = "DEFENSIVE_CHOPPY"
            mult = 0.50
            notes.append("Macro timeframes mixed. Reduce trade size and demand tight wholesale entries.")
        else:
            posture = "BEARISH_DISTRIBUTION"
            mult = 0.0
            notes.append("Market is under macro institutional distribution. Halt new long entries.")

        return MacroMarketPosture(
            benchmark_symbol=benchmark_symbol,
            as_of_date=align.as_of_date,
            yearly_trend=y_str,
            quarterly_trend=q_str,
            monthly_trend=m_str,
            market_curve_location=curve_str,
            overall_posture=posture,
            sizing_recommendation=mult,
            summary_notes=notes,
        )
