"""
AI Trading Operating System
Module: analytics/demand_supply_zones.py

Pure Institutional Demand & Supply Zone Engine (GTF Methodology):
- Identifies institutional order flow footprints:
  * Demand Zones: DBR (Drop-Base-Rally) and RBR (Rally-Base-Rally)
  * Supply Zones: RBD (Rally-Base-Drop) and DBD (Drop-Base-Drop)
- Precise Zone Boundary Mapping:
  * Proximal Line: Inner boundary (Entry level)
  * Distal Line: Outer boundary (Stop-loss level)
- Odds Enhancer & Quality Scoring (0 to 10):
  1. Strength / Explosiveness of Leg-out (expansion body, volume)
  2. Time at Base (1-3 candles = Institutional accumulator; 4-6 candles = Good)
  3. Freshness (Fresh / Untested vs Tested vs Violated)
  4. Reward-to-Risk ratio to opposing Supply Zone (minimum 2:1, ideally 3:1+)
- Current Market Location Detection:
  * AT_DEMAND_ZONE (Price currently testing proximal line)
  * APPROACHING_DEMAND (Price within 1-2.5% of demand zone)
  * IN_TRANSIT (Price in open space between zones)
  * AT_SUPPLY_ZONE (Price at opposing target zone)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd


class ZoneType(str, Enum):
    DEMAND_DBR = "DEMAND_DBR"  # Drop-Base-Rally (Reversal Demand)
    DEMAND_RBR = "DEMAND_RBR"  # Rally-Base-Rally (Continuation Demand)
    SUPPLY_RBD = "SUPPLY_RBD"  # Rally-Base-Drop (Reversal Supply)
    SUPPLY_DBD = "SUPPLY_DBD"  # Drop-Base-Drop (Continuation Supply)


class ZoneFreshness(str, Enum):
    FRESH = "FRESH"          # Never tested (Highest probability)
    TESTED_1X = "TESTED_1X"  # Tested once, held
    TESTED_2X = "TESTED_2X"  # Tested twice (Depleted)
    VIOLATED = "VIOLATED"    # Broken beyond distal line


class PriceLocation(str, Enum):
    AT_DEMAND_ZONE = "AT_DEMAND_ZONE"              # Current price is inside/touching demand zone
    APPROACHING_DEMAND = "APPROACHING_DEMAND"      # Current price within 0.1% to 2.5% above demand zone
    IN_TRANSIT = "IN_TRANSIT"                      # Price moving between zones
    AT_SUPPLY_ZONE = "AT_SUPPLY_ZONE"              # Price at target supply zone
    APPROACHING_SUPPLY = "APPROACHING_SUPPLY"      # Price near supply zone


@dataclass(frozen=True)
class CandleInfo:
    index: int
    trading_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    candle_range: float
    body_size: float
    body_pct: float
    is_exciting: bool  # Body >= 50% of range (Leg-in / Leg-out candle)
    is_boring: bool    # Body < 50% of range (Base candle)
    is_green: bool
    is_red: bool


@dataclass
class DemandSupplyZone:
    zone_id: str
    symbol: str
    zone_type: ZoneType
    formation_date: date
    proximal_line: float  # Demand: Highest body of base | Supply: Lowest body of base
    distal_line: float    # Demand: Lowest wick of base   | Supply: Highest wick of base
    zone_width: float     # abs(proximal - distal)
    zone_width_pct: float # (zone_width / proximal) * 100
    base_candle_count: int
    leg_out_strength: float # % gain of leg-out
    leg_out_volume_ratio: float
    freshness: ZoneFreshness
    touch_count: int
    odds_enhancer_score: float # 0 to 10 quality score
    opposing_target: Optional[float] = None
    reward_to_risk: float = 2.0
    current_distance_pct: float = 0.0
    location_state: PriceLocation = PriceLocation.IN_TRANSIT
    # GTF Institutional Test Timing & Penetration Depth
    test_dates: List[date] = field(default_factory=list)
    last_tested_date: Optional[date] = None
    deepest_penetration_px: Optional[float] = None
    penetration_pct: Optional[float] = None
    freshness_detail: str = "FRESH (Virgin - 0 Tests)"
    # Institutional-Style Framework v1.0 Attributes (PDF Specification)
    atr_14: float = 1.0
    displacement_ratio: float = 1.0
    bos_type: str = "NO_CLEAR_BREAK"
    has_liquidity_sweep: bool = False
    sweep_desc: str = ""
    is_chop_area: bool = False
    volatility_buffer_px: float = 0.5
    buffered_stop_loss: float = 0.0
    scorecard_100: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["zone_type"] = self.zone_type.value
        d["freshness"] = self.freshness.value
        d["location_state"] = self.location_state.value
        d["formation_date"] = str(self.formation_date)
        d["test_dates"] = [str(td) for td in self.test_dates]
        d["last_tested_date"] = str(self.last_tested_date) if self.last_tested_date else "Never Tested (Fresh)"
        d["deepest_penetration_px"] = self.deepest_penetration_px
        d["penetration_pct"] = self.penetration_pct
        d["freshness_detail"] = self.freshness_detail
        d["atr_14"] = round(self.atr_14, 2)
        d["displacement_ratio"] = round(self.displacement_ratio, 2)
        d["bos_type"] = self.bos_type
        d["has_liquidity_sweep"] = self.has_liquidity_sweep
        d["sweep_desc"] = self.sweep_desc
        d["is_chop_area"] = self.is_chop_area
        d["volatility_buffer_px"] = round(self.volatility_buffer_px, 2)
        d["buffered_stop_loss"] = round(self.buffered_stop_loss, 2)
        d["scorecard_100"] = self.scorecard_100
        return d


class DemandSupplyZoneEngine:
    """
    Institutional Demand & Supply Zone Detector (GTF Methodology).
    """

    def __init__(
        self,
        min_leg_out_body_pct: float = 0.50,
        max_base_candles: int = 6,
        min_base_candles: int = 1,
        min_reward_to_risk: float = 2.0,
        approach_threshold_pct: float = 2.5,
    ) -> None:
        self.min_leg_out_body_pct = min_leg_out_body_pct
        self.max_base_candles = max_base_candles
        self.min_base_candles = min_base_candles
        self.min_reward_to_risk = min_reward_to_risk
        self.approach_threshold_pct = approach_threshold_pct

    def parse_candles(self, df: pd.DataFrame) -> List[CandleInfo]:
        """Classifies each candle into Exciting vs Boring (Base) based on GTF rules."""
        candles = []
        clean = df.sort_values("trading_date").reset_index(drop=True)

        for idx, row in clean.iterrows():
            o = float(row["open"])
            h = float(row["high"])
            l = float(row["low"])
            c = float(row["close"])
            v = int(row.get("volume", 1000))
            t_date = row["trading_date"]
            if isinstance(t_date, str):
                t_date = pd.to_datetime(t_date).date()

            c_range = max(0.01, h - l)
            body = abs(c - o)
            body_pct = body / c_range

            is_exciting = body_pct >= self.min_leg_out_body_pct
            is_boring = not is_exciting
            is_green = c >= o
            is_red = c < o

            candles.append(CandleInfo(
                index=idx,
                trading_date=t_date,
                open=o,
                high=h,
                low=l,
                close=c,
                volume=v,
                candle_range=c_range,
                body_size=body,
                body_pct=round(body_pct, 3),
                is_exciting=is_exciting,
                is_boring=is_boring,
                is_green=is_green,
                is_red=is_red,
            ))

        return candles

    def find_all_zones(
        self,
        df: pd.DataFrame,
        symbol: str = "STOCK",
    ) -> Tuple[List[DemandSupplyZone], List[DemandSupplyZone]]:
        """
        Scans complete price series and identifies all valid Demand and Supply zones.
        Returns: (demand_zones, supply_zones)
        """
        if len(df) < 5:
            return [], []

        candles = self.parse_candles(df)
        n = len(candles)
        demand_zones: List[DemandSupplyZone] = []
        supply_zones: List[DemandSupplyZone] = []

        avg_vol = df["volume"].tail(20).mean() if "volume" in df.columns else 1000.0
        avg_vol = max(1.0, float(avg_vol))

        # Calculate 14-period ATR for volatility-normalized displacement and buffers
        highs = df["high"].values
        lows = df["low"].values
        closes = df["close"].values
        if len(df) >= 2:
            tr = [max(highs[k] - lows[k], abs(highs[k] - closes[k-1]), abs(lows[k] - closes[k-1])) for k in range(1, len(df))]
            atr_14 = float(sum(tr[-14:]) / min(len(tr), 14)) if tr else 1.0
        else:
            atr_14 = 1.0
        atr_14 = max(0.01, atr_14)

        # Scan for Base + Leg-Out structures
        for i in range(1, n - 1):
            # Check for base candles starting at index i
            for base_len in range(self.min_base_candles, self.max_base_candles + 1):
                leg_out_idx = i + base_len
                if leg_out_idx >= n:
                    break

                leg_in_idx = i - 1
                leg_in = candles[leg_in_idx]
                base_candles = candles[i:leg_out_idx]
                leg_out = candles[leg_out_idx]

                # Check if all base candles are boring candles (or tight consolidation)
                if not all(c.is_boring for c in base_candles):
                    # Allow at most 1 slightly larger candle if body < 55%
                    boring_count = sum(1 for c in base_candles if c.is_boring)
                    if boring_count < len(base_candles) - 1:
                        continue

                # Prior structural lookback for BOS and Liquidity Sweep
                prior_slice = candles[max(0, i - 20):i]

                # ---------------------------------------------------------
                # 1. DEMAND ZONE DETECTION (DBR or RBR)
                # ---------------------------------------------------------
                # Leg-out MUST be an Exciting Green candle closing above the base high
                base_highest_high = max(c.high for c in base_candles)
                base_lowest_low = min(c.low for c in base_candles)
                base_highest_body = max(max(c.open, c.close) for c in base_candles)

                if leg_out.is_green and leg_out.is_exciting and leg_out.close > base_highest_high:
                    # Leg-in determines DBR vs RBR
                    z_type = ZoneType.DEMAND_DBR if leg_in.is_red else ZoneType.DEMAND_RBR

                    # Boundaries
                    proximal = round(base_highest_body, 2)
                    distal = round(base_lowest_low, 2)
                    z_width = round(proximal - distal, 2)

                    if z_width > 0:
                        leg_out_gain = round(((leg_out.close - proximal) / proximal) * 100.0, 2)
                        vol_ratio = round(leg_out.volume / avg_vol, 2)

                        # Break of Structure (BOS)
                        prior_highest_high = max(c.high for c in prior_slice) if prior_slice else leg_out.high
                        recent_pivot_high = max(c.high for c in prior_slice[-3:]) if len(prior_slice) >= 3 else prior_highest_high

                        if leg_out.close > prior_highest_high:
                            bos_type = "SWING_BOS"
                        elif leg_out.close > recent_pivot_high:
                            bos_type = "INTERNAL_BOS"
                        else:
                            bos_type = "NO_CLEAR_BREAK"

                        # Liquidity Sweep (Spring / Stop-Hunt)
                        prior_lowest_low = min(c.low for c in prior_slice) if prior_slice else base_lowest_low
                        has_sweep = base_lowest_low < prior_lowest_low
                        sweep_desc = f"Swept prior swing low of Rs. {prior_lowest_low:,.2f}" if has_sweep else "No prior low sweep"

                        # Volatility-Normalized Displacement & Buffer
                        disp_px = leg_out.close - proximal
                        disp_ratio = round(disp_px / atr_14, 2)
                        vol_buffer = round(max(0.3, atr_14 * 0.20), 2)
                        buffered_sl = round(distal - vol_buffer, 2)

                        # Chop / Garbage flag
                        is_chop = (base_len >= 5) or (disp_ratio < 0.9)

                        # Audit subsequent price action for freshness
                        freshness, touches, violated, t_dates, last_t, deep_px, pen_pct, fresh_detail = self._evaluate_freshness(
                            candles[leg_out_idx + 1:],
                            proximal=proximal,
                            distal=distal,
                            is_demand=True,
                        )

                        if not violated:
                            score = self._calculate_odds_enhancer_score(
                                base_len=base_len,
                                leg_out_gain=leg_out_gain,
                                vol_ratio=vol_ratio,
                                freshness=freshness,
                                z_type=z_type,
                            )

                            zid = f"DEMAND_{symbol}_{leg_out.trading_date}_{proximal}"
                            d_zone = DemandSupplyZone(
                                zone_id=zid,
                                symbol=symbol,
                                zone_type=z_type,
                                formation_date=leg_out.trading_date,
                                proximal_line=proximal,
                                distal_line=distal,
                                zone_width=z_width,
                                zone_width_pct=round((z_width / proximal) * 100.0, 2),
                                base_candle_count=base_len,
                                leg_out_strength=leg_out_gain,
                                leg_out_volume_ratio=vol_ratio,
                                freshness=freshness,
                                touch_count=touches,
                                odds_enhancer_score=score,
                                test_dates=t_dates,
                                last_tested_date=last_t,
                                deepest_penetration_px=deep_px,
                                penetration_pct=pen_pct,
                                freshness_detail=fresh_detail,
                                atr_14=atr_14,
                                displacement_ratio=disp_ratio,
                                bos_type=bos_type,
                                has_liquidity_sweep=has_sweep,
                                sweep_desc=sweep_desc,
                                is_chop_area=is_chop,
                                volatility_buffer_px=vol_buffer,
                                buffered_stop_loss=buffered_sl,
                            )
                            demand_zones.append(d_zone)

                # ---------------------------------------------------------
                # 2. SUPPLY ZONE DETECTION (RBD or DBD)
                # ---------------------------------------------------------
                # Leg-out MUST be an Exciting Red candle closing below the base low
                base_lowest_body = min(min(c.open, c.close) for c in base_candles)

                if leg_out.is_red and leg_out.is_exciting and leg_out.close < base_lowest_low:
                    z_type = ZoneType.SUPPLY_RBD if leg_in.is_green else ZoneType.SUPPLY_DBD

                    # Boundaries
                    proximal = round(base_lowest_body, 2)
                    distal = round(base_highest_high, 2)
                    z_width = round(distal - proximal, 2)

                    if z_width > 0:
                        leg_out_drop = round(((proximal - leg_out.close) / proximal) * 100.0, 2)
                        vol_ratio = round(leg_out.volume / avg_vol, 2)

                        # Break of Structure (BOS)
                        prior_lowest_low_sup = min(c.low for c in prior_slice) if prior_slice else leg_out.low
                        recent_pivot_low_sup = min(c.low for c in prior_slice[-3:]) if len(prior_slice) >= 3 else prior_lowest_low_sup

                        if leg_out.close < prior_lowest_low_sup:
                            bos_type = "SWING_BOS"
                        elif leg_out.close < recent_pivot_low_sup:
                            bos_type = "INTERNAL_BOS"
                        else:
                            bos_type = "NO_CLEAR_BREAK"

                        # Liquidity Sweep
                        prior_highest_high_sup = max(c.high for c in prior_slice) if prior_slice else base_highest_high
                        has_sweep = base_highest_high > prior_highest_high_sup
                        sweep_desc = f"Swept prior swing high of Rs. {prior_highest_high_sup:,.2f}" if has_sweep else "No prior high sweep"

                        disp_px = proximal - leg_out.close
                        disp_ratio = round(disp_px / atr_14, 2)
                        vol_buffer = round(max(0.3, atr_14 * 0.20), 2)
                        buffered_sl = round(distal + vol_buffer, 2)
                        is_chop = (base_len >= 5) or (disp_ratio < 0.9)

                        freshness, touches, violated, t_dates, last_t, deep_px, pen_pct, fresh_detail = self._evaluate_freshness(
                            candles[leg_out_idx + 1:],
                            proximal=proximal,
                            distal=distal,
                            is_demand=False,
                        )

                        if not violated:
                            score = self._calculate_odds_enhancer_score(
                                base_len=base_len,
                                leg_out_gain=leg_out_drop,
                                vol_ratio=vol_ratio,
                                freshness=freshness,
                                z_type=z_type,
                            )

                            zid = f"SUPPLY_{symbol}_{leg_out.trading_date}_{proximal}"
                            s_zone = DemandSupplyZone(
                                zone_id=zid,
                                symbol=symbol,
                                zone_type=z_type,
                                formation_date=leg_out.trading_date,
                                proximal_line=proximal,
                                distal_line=distal,
                                zone_width=z_width,
                                zone_width_pct=round((z_width / proximal) * 100.0, 2),
                                base_candle_count=base_len,
                                leg_out_strength=leg_out_drop,
                                leg_out_volume_ratio=vol_ratio,
                                freshness=freshness,
                                touch_count=touches,
                                odds_enhancer_score=score,
                                test_dates=t_dates,
                                last_tested_date=last_t,
                                deepest_penetration_px=deep_px,
                                penetration_pct=pen_pct,
                                freshness_detail=fresh_detail,
                                atr_14=atr_14,
                                displacement_ratio=disp_ratio,
                                bos_type=bos_type,
                                has_liquidity_sweep=has_sweep,
                                sweep_desc=sweep_desc,
                                is_chop_area=is_chop,
                                volatility_buffer_px=vol_buffer,
                                buffered_stop_loss=buffered_sl,
                            )
                            supply_zones.append(s_zone)

        # De-duplicate overlapping zones (keep highest score)
        unique_demand = self._deduplicate_zones(demand_zones, is_demand=True)
        unique_supply = self._deduplicate_zones(supply_zones, is_demand=False)

        # Update current location & R:R based on current price
        latest_candle = candles[-1]
        cur_price = latest_candle.close

        active_demand = self._enrich_demand_zones_with_supply(
            unique_demand, unique_supply, cur_price
        )

        return active_demand, unique_supply

    def _evaluate_freshness(
        self,
        subsequent_candles: List[CandleInfo],
        proximal: float,
        distal: float,
        is_demand: bool,
    ) -> Tuple[ZoneFreshness, int, bool, List[date], Optional[date], Optional[float], Optional[float], str]:
        """Traces price trajectory to determine if zone is fresh, tested, or violated, recording exact test dates and depth."""
        if not subsequent_candles:
            return ZoneFreshness.FRESH, 0, False, [], None, None, 0.0, "FRESH (Virgin - 0 Tests)"

        touches = 0
        violated = False
        violation_date = None
        test_dates: List[date] = []
        in_zone = False
        deepest_extreme = float("inf") if is_demand else float("-inf")

        for c in subsequent_candles:
            if is_demand:
                # If price penetrated below distal line (broken demand)
                if c.close < distal:
                    violated = True
                    violation_date = c.trading_date
                    break
                # If price tested the zone (low <= proximal)
                if c.low <= proximal:
                    deepest_extreme = min(deepest_extreme, c.low)
                    if not in_zone:
                        touches += 1
                        test_dates.append(c.trading_date)
                        in_zone = True
                else:
                    in_zone = False
            else:
                # Supply zone: violated if close > distal
                if c.close > distal:
                    violated = True
                    violation_date = c.trading_date
                    break
                # If price tested the supply zone (high >= proximal)
                if c.high >= proximal:
                    deepest_extreme = max(deepest_extreme, c.high)
                    if not in_zone:
                        touches += 1
                        test_dates.append(c.trading_date)
                        in_zone = True
                else:
                    in_zone = False

        z_w = max(0.01, abs(proximal - distal))
        if is_demand:
            deepest_px = round(deepest_extreme, 2) if deepest_extreme != float("inf") else None
            pen_pct = round(((proximal - deepest_extreme) / z_w) * 100.0, 1) if deepest_px else 0.0
        else:
            deepest_px = round(deepest_extreme, 2) if deepest_extreme != float("-inf") else None
            pen_pct = round(((deepest_extreme - proximal) / z_w) * 100.0, 1) if deepest_px else 0.0

        last_tested = test_dates[-1] if test_dates else None

        if violated:
            return ZoneFreshness.VIOLATED, touches, True, test_dates, last_tested, deepest_px, pen_pct, f"VIOLATED (Breached on {violation_date})"
        if touches == 0:
            return ZoneFreshness.FRESH, 0, False, [], None, None, 0.0, "FRESH (Virgin - 0 Tests)"
        if touches == 1:
            return ZoneFreshness.TESTED_1X, 1, False, test_dates, last_tested, deepest_px, pen_pct, f"TESTED_1X (Date: {test_dates[0]})"
        dates_str = ", ".join(str(d) for d in test_dates[:2])
        return ZoneFreshness.TESTED_2X, touches, False, test_dates, last_tested, deepest_px, pen_pct, f"TESTED_{touches}X (Last: {last_tested})"

    def _calculate_odds_enhancer_score(
        self,
        base_len: int,
        leg_out_gain: float,
        vol_ratio: float,
        freshness: ZoneFreshness,
        z_type: ZoneType,
    ) -> float:
        """
        GTF Odds Enhancer Scoring (0.0 to 10.0 scale):
        - Freshness: Fresh = 3.0, Tested 1x = 1.5, Tested 2x = 0.5
        - Time at base: 1-3 candles = 3.0, 4-6 candles = 1.5
        - Strength of departure: Leg-out gain > 2% = 2.0, > 1% = 1.0
        - Volume expansion: Vol ratio > 1.2 = 2.0, > 1.0 = 1.0
        """
        score = 0.0

        # 1. Freshness (Max 3 pts)
        if freshness == ZoneFreshness.FRESH:
            score += 3.0
        elif freshness == ZoneFreshness.TESTED_1X:
            score += 1.5
        else:
            score += 0.5

        # 2. Time at Base (Max 3 pts)
        if base_len in {1, 2, 3}:
            score += 3.0
        elif base_len <= 6:
            score += 1.5
        else:
            score += 0.5

        # 3. Strength of Leg-out (Max 2 pts)
        if leg_out_gain >= 2.0:
            score += 2.0
        elif leg_out_gain >= 1.0:
            score += 1.2
        else:
            score += 0.5

        # 4. Volume Confirmation (Max 2 pts)
        if vol_ratio >= 1.25:
            score += 2.0
        elif vol_ratio >= 1.0:
            score += 1.0
        else:
            score += 0.5

        return round(min(10.0, score), 1)

    def _deduplicate_zones(
        self,
        zones: List[DemandSupplyZone],
        is_demand: bool,
    ) -> List[DemandSupplyZone]:
        """Retains the most significant zones by clustering nearby proximal lines."""
        if not zones:
            return []

        # Sort by formation date descending (most recent first)
        sorted_zones = sorted(zones, key=lambda z: (z.formation_date, z.odds_enhancer_score), reverse=True)
        unique: List[DemandSupplyZone] = []

        for z in sorted_zones:
            # Check if an existing zone is within 1% of this proximal line
            is_overlap = False
            for u in unique:
                diff_pct = abs(z.proximal_line - u.proximal_line) / u.proximal_line * 100.0
                if diff_pct < 1.0:
                    is_overlap = True
                    break
            if not is_overlap:
                unique.append(z)

        return unique

    def _enrich_demand_zones_with_supply(
        self,
        demand_zones: List[DemandSupplyZone],
        supply_zones: List[DemandSupplyZone],
        current_price: float,
    ) -> List[DemandSupplyZone]:
        """Calculates distance, price location state, and Reward-to-Risk against opposing supply."""
        enriched = []

        # Sort supply zones ascending by proximal line
        valid_supplies = sorted([s for s in supply_zones if s.proximal_line > current_price * 0.99], key=lambda s: s.proximal_line)

        for d in demand_zones:
            # Only consider demand zones below or at current price
            if d.proximal_line > current_price * 1.02:
                continue

            dist_pct = round(((current_price - d.proximal_line) / d.proximal_line) * 100.0, 2)
            d.current_distance_pct = dist_pct

            # Location State
            if abs(dist_pct) <= 0.4:
                d.location_state = PriceLocation.AT_DEMAND_ZONE
            elif 0.4 < dist_pct <= self.approach_threshold_pct:
                d.location_state = PriceLocation.APPROACHING_DEMAND
            else:
                d.location_state = PriceLocation.IN_TRANSIT

            # Nearest opposing supply target
            opp_supply = None
            for s in valid_supplies:
                if s.proximal_line > d.proximal_line:
                    opp_supply = s.proximal_line
                    break

            risk = max(1.0, d.zone_width)
            if opp_supply is not None:
                reward = opp_supply - d.proximal_line
                rr = round(reward / risk, 2)
            else:
                # Default 2.5x zone width target if no clear supply overhead
                opp_supply = round(d.proximal_line + risk * 2.5, 2)
                rr = 2.5

            d.opposing_target = opp_supply
            d.reward_to_risk = max(1.0, rr)
            enriched.append(d)

        # Sort demand zones: closest to current price first, then by score
        enriched.sort(key=lambda z: (abs(z.current_distance_pct), -z.odds_enhancer_score))
        return enriched
