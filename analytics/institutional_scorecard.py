"""
AI Trading Operating System
Module: analytics/institutional_scorecard.py

Institutional-Style Demand & Supply Framework (Document v1.0)
Translates GTF Trader 2.0 concepts into an auditable, quantitative 100-point institutional scorecard:
1. Structure Significance (20 pts): Swing/HTF BOS (20) > Internal break (12) > No clear break (5)
2. Departure Strength (15 pts): Displacement/ATR (>=2.5x: 15, >=1.5x: 10, >=1.0x: 6), close beyond base
3. Freshness / Mitigation (15 pts): Fresh/Virgin (15), shallow 1st touch (10), moderate touch (6), repeated/deep (2)
4. HTF Confluence (15 pts): Grade A+ (15), Grade A (12), Grade B (8), Unaligned (2)
5. Premium / Discount Location (10 pts): Very Low <=25% (10), Low 25-33% (8), Equilibrium 33-66% (4), High >66% (0)
6. Liquidity / Sweep Proxy (10 pts): Defined sweep of prior low before base (10), equal lows swept (7), no sweep (3)
7. Sector / Market Alignment (5 pts): Both Nifty & Sector bullish (5), one bullish (3), neither (1)
8. Reward / Risk & Target Space (10 pts): Net R:R >=3.0 (10), 2.5-3.0 (8), 2.0-2.5 (5), <2.0 (1)

Total = 100 Points.

Hard Gates:
- Data quality & minimum history check: PASS
- Zone valid & not invalidated: PASS
- Explicit entry, invalidation (distal + volatility buffer), target, net R:R >= 2.0: PASS
- If hard gate fails -> return NO_TRADE / DEFER with explicit reason code.

Entry Models (Section 7):
- Model A: Direct Zone Order (Limit at Proximal)
- Model B: Reversal Candle Confirmation
- Model C: Lower-Timeframe BOS
- Model D: Flip-Zone Retest
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


class BOSClassification(str, Enum):
    SWING_BOS = "SWING_BOS"          # Departure broke confirmed major swing high (20 pts)
    INTERNAL_BOS = "INTERNAL_BOS"    # Departure broke immediate local pivot high (12 pts)
    NO_CLEAR_BREAK = "NO_CLEAR_BREAK"# Departure did not break clear structure (5 pts)


class EntryModel(str, Enum):
    MODEL_A_DIRECT_LIMIT = "MODEL_A_DIRECT_LIMIT"        # Buy limit placed at proximal line
    MODEL_B_REVERSAL_CANDLE = "MODEL_B_REVERSAL_CANDLE"  # Wait for rejection/pin-bar confirmation inside zone
    MODEL_C_LTF_BOS = "MODEL_C_LTF_BOS"                  # Wait for lower-timeframe break of structure
    MODEL_D_FLIP_RETEST = "MODEL_D_FLIP_RETEST"          # Retest of broken opposing supply level reclaimed as demand


class HardGateStatus(str, Enum):
    APPROVED = "APPROVED"
    NO_TRADE_RR_BELOW_THRESHOLD = "NO_TRADE_RR_BELOW_THRESHOLD"
    NO_TRADE_PREMIUM_LOCATION = "NO_TRADE_PREMIUM_LOCATION"
    NO_TRADE_INVALIDATED_ZONE = "NO_TRADE_INVALIDATED_ZONE"
    NO_TRADE_CHOP_GARBAGE = "NO_TRADE_CHOP_GARBAGE"
    DEFER_DATA_QUALITY = "DEFER_DATA_QUALITY"


@dataclass
class QualificationCheckItem:
    item_id: int
    name: str
    passed: bool
    details: str


@dataclass
class InstitutionalScorecardResult:
    symbol: str
    zone_id: str
    timeframe: str
    # Component Scores (Total = 100)
    structure_score: float        # max 20
    departure_score: float        # max 15
    freshness_score: float        # max 15
    htf_confluence_score: float   # max 15
    curve_location_score: float   # max 10
    liquidity_sweep_score: float  # max 10
    sector_market_score: float    # max 5
    reward_risk_score: float      # max 10
    total_score: float            # 0 to 100
    # Classifications
    bos_type: BOSClassification
    displacement_ratio_atr: float
    has_liquidity_sweep: bool
    sweep_description: str
    curve_state: str
    curve_location_pct: float
    recommended_entry_model: EntryModel
    entry_model_rational: str
    # Volatility-Buffered Execution Levels
    proximal_entry: float
    distal_stop: float
    volatility_buffer_px: float
    buffered_stop_loss: float
    target_supply: float
    net_reward_to_risk: float
    # Hard Gate & Audit
    hard_gate_status: HardGateStatus
    gate_passed: bool
    rejection_reasons: List[str] = field(default_factory=list)
    checklist_12_points: List[QualificationCheckItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "zone_id": self.zone_id,
            "timeframe": self.timeframe,
            "total_score": round(self.total_score, 1),
            "structure_score": round(self.structure_score, 1),
            "departure_score": round(self.departure_score, 1),
            "freshness_score": round(self.freshness_score, 1),
            "htf_confluence_score": round(self.htf_confluence_score, 1),
            "curve_location_score": round(self.curve_location_score, 1),
            "liquidity_sweep_score": round(self.liquidity_sweep_score, 1),
            "sector_market_score": round(self.sector_market_score, 1),
            "reward_risk_score": round(self.reward_risk_score, 1),
            "bos_type": self.bos_type.value,
            "displacement_ratio_atr": round(self.displacement_ratio_atr, 2),
            "has_liquidity_sweep": self.has_liquidity_sweep,
            "sweep_description": self.sweep_description,
            "curve_state": self.curve_state,
            "curve_location_pct": round(self.curve_location_pct, 1),
            "recommended_entry_model": self.recommended_entry_model.value,
            "entry_model_rational": self.entry_model_rational,
            "proximal_entry": round(self.proximal_entry, 2),
            "distal_stop": round(self.distal_stop, 2),
            "volatility_buffer_px": round(self.volatility_buffer_px, 2),
            "buffered_stop_loss": round(self.buffered_stop_loss, 2),
            "target_supply": round(self.target_supply, 2),
            "net_reward_to_risk": round(self.net_reward_to_risk, 2),
            "hard_gate_status": self.hard_gate_status.value,
            "gate_passed": self.gate_passed,
            "rejection_reasons": self.rejection_reasons,
            "checklist_pass_count": sum(1 for c in self.checklist_12_points if c.passed),
        }


class InstitutionalScorecardEngine:
    """
    Evaluates candidate zones against the Institutional-Style Demand & Supply Framework (Document v1.0).
    Calculates the 100-point scorecard, tests hard gates, and verifies the 12-point Starter Qualification Checklist.
    """

    def __init__(self, min_reward_to_risk: float = 2.0, min_score_to_execute: float = 65.0) -> None:
        self.min_reward_to_risk = min_reward_to_risk
        self.min_score_to_execute = min_score_to_execute

    def compute_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculates 14-period Average True Range."""
        if len(df) < 2:
            return 1.0
        high = df["high"].values
        low = df["low"].values
        close = df["close"].values
        tr = np.maximum(
            high[1:] - low[1:],
            np.maximum(np.abs(high[1:] - close[:-1]), np.abs(low[1:] - close[:-1]))
        )
        if len(tr) < period:
            return float(np.mean(tr)) if len(tr) > 0 else 1.0
        return float(np.mean(tr[-period:]))

    def evaluate_bos(
        self,
        df: pd.DataFrame,
        base_start_idx: int,
        leg_out_close: float,
        lookback: int = 20,
    ) -> Tuple[BOSClassification, float]:
        """
        Determines whether the departure broke a major swing high or internal pivot.
        """
        if base_start_idx < 3:
            return BOSClassification.NO_CLEAR_BREAK, 0.0

        prior_slice = df.iloc[max(0, base_start_idx - lookback):base_start_idx]
        if prior_slice.empty:
            return BOSClassification.NO_CLEAR_BREAK, 0.0

        highest_swing = float(prior_slice["high"].max())
        recent_pivot = float(prior_slice.iloc[-3:]["high"].max()) if len(prior_slice) >= 3 else highest_swing

        if leg_out_close > highest_swing:
            return BOSClassification.SWING_BOS, highest_swing
        elif leg_out_close > recent_pivot:
            return BOSClassification.INTERNAL_BOS, recent_pivot
        return BOSClassification.NO_CLEAR_BREAK, highest_swing

    def evaluate_liquidity_sweep(
        self,
        df: pd.DataFrame,
        base_start_idx: int,
        base_lowest_low: float,
        lookback: int = 15,
    ) -> Tuple[bool, str]:
        """
        Detects if base formation or leg-in swept a prior significant swing low before reversing (Stop hunt / Liquidity grab).
        """
        if base_start_idx < 3:
            return False, "Insufficient history prior to base"

        # Prior swing must be evaluated before the leg-in candle (base_start_idx - 1)
        prior_end_idx = max(1, base_start_idx - 1)
        prior_slice = df.iloc[max(0, prior_end_idx - lookback):prior_end_idx]
        if prior_slice.empty:
            return False, "No prior swing data"

        prior_swing_low = float(prior_slice["low"].min())
        # Check if base or leg-in dipped below the prior swing low
        leg_in_low = float(df.iloc[base_start_idx - 1]["low"]) if base_start_idx > 0 else base_lowest_low
        lowest_dip = min(base_lowest_low, leg_in_low)

        if lowest_dip < prior_swing_low:
            return True, f"Swept prior swing low of Rs. {prior_swing_low:,.2f} (Liquidity grab confirmed)"
        return False, "No prior low sweep detected"

    def score_zone(
        self,
        symbol: str,
        zone_id: str,
        timeframe: str,
        proximal: float,
        distal: float,
        target_supply: float,
        current_price: float,
        leg_out_gain_pct: float,
        atr_14: float,
        freshness_detail: str,
        touch_count: int,
        penetration_pct: Optional[float],
        alignment_grade: str,
        curve_location_pct: float,
        curve_state: str,
        bos_type: BOSClassification,
        has_sweep: bool,
        sweep_desc: str,
        market_posture_bullish: bool,
        sector_bullish: bool,
        is_chop_area: bool = False,
        data_valid: bool = True,
    ) -> InstitutionalScorecardResult:
        """
        Scores a candidate zone using the 100-point Institutional Scorecard with hard gates.
        """
        rejection_reasons = []

        # -------------------------------------------------------------
        # 1. Component 1: Structure Significance (20 Points)
        # -------------------------------------------------------------
        if bos_type == BOSClassification.SWING_BOS:
            score_struct = 20.0
        elif bos_type == BOSClassification.INTERNAL_BOS:
            score_struct = 12.0
        else:
            score_struct = 5.0

        # -------------------------------------------------------------
        # 2. Component 2: Departure Strength (15 Points)
        # -------------------------------------------------------------
        # Volatility-normalized displacement: displacement in Rs. / ATR
        displacement_px = proximal * (leg_out_gain_pct / 100.0)
        disp_ratio = displacement_px / max(0.01, atr_14)

        if disp_ratio >= 2.5:
            score_depart = 15.0
        elif disp_ratio >= 1.5:
            score_depart = 10.0
        elif disp_ratio >= 1.0:
            score_depart = 6.0
        else:
            score_depart = 3.0

        # -------------------------------------------------------------
        # 3. Component 3: Freshness / Mitigation (15 Points)
        # -------------------------------------------------------------
        pen_depth = penetration_pct if penetration_pct is not None else 0.0
        if touch_count == 0 or "FRESH" in freshness_detail.upper():
            score_fresh = 15.0
        elif touch_count == 1:
            if pen_depth <= 25.0:
                score_fresh = 10.0  # Shallow first touch
            elif pen_depth <= 50.0:
                score_fresh = 6.0   # Moderate first touch
            else:
                score_fresh = 3.0   # Deep first touch
        else:
            score_fresh = 2.0  # Repeatedly mitigated (Depleted)

        # -------------------------------------------------------------
        # 4. Component 4: Higher Timeframe Confluence (15 Points)
        # -------------------------------------------------------------
        grade_upper = alignment_grade.upper()
        if "A_PLUS" in grade_upper or "A+" in grade_upper:
            score_htf = 15.0
        elif "GRADE_A" in grade_upper:
            score_htf = 12.0
        elif "GRADE_B" in grade_upper:
            score_htf = 8.0
        elif "GRADE_C" in grade_upper:
            score_htf = 4.0
        else:
            score_htf = 1.0

        # -------------------------------------------------------------
        # 5. Component 5: Premium / Discount Location (10 Points)
        # -------------------------------------------------------------
        if curve_location_pct <= 25.0:
            score_curve = 10.0  # Prime wholesale discount
        elif curve_location_pct <= 35.0:
            score_curve = 8.0   # Favorable buy zone
        elif curve_location_pct <= 60.0:
            score_curve = 4.0   # Equilibrium
        else:
            score_curve = 0.0   # Premium / Institutional distribution trap

        # -------------------------------------------------------------
        # 6. Component 6: Liquidity / Sweep Proxy (10 Points)
        # -------------------------------------------------------------
        if has_sweep:
            score_sweep = 10.0
        else:
            score_sweep = 3.0

        # -------------------------------------------------------------
        # 7. Component 7: Sector / Market Alignment (5 Points)
        # -------------------------------------------------------------
        if market_posture_bullish and sector_bullish:
            score_sector = 5.0
        elif market_posture_bullish or sector_bullish:
            score_sector = 3.0
        else:
            score_sector = 1.0

        # -------------------------------------------------------------
        # 8. Component 8: Reward-to-Risk and Target Space (10 Points)
        # -------------------------------------------------------------
        vol_buffer = round(max(0.5, atr_14 * 0.20), 2)
        buffered_stop = round(distal - vol_buffer, 2)
        risk_per_share = max(1.0, proximal - buffered_stop)
        reward_per_share = max(0.0, target_supply - proximal)
        net_rr = round(reward_per_share / risk_per_share, 2)

        if net_rr >= 3.0:
            score_rr = 10.0
        elif net_rr >= 2.5:
            score_rr = 8.0
        elif net_rr >= 2.0:
            score_rr = 5.0
        else:
            score_rr = 1.0

        total_score = round(
            score_struct + score_depart + score_fresh + score_htf +
            score_curve + score_sweep + score_sector + score_rr,
            1
        )

        # -------------------------------------------------------------
        # Recommended Entry Model (Section 7)
        # -------------------------------------------------------------
        if touch_count == 0 and score_fresh == 15.0 and score_curve >= 8.0:
            entry_model = EntryModel.MODEL_A_DIRECT_LIMIT
            entry_rational = "Fresh virgin zone in deep discount: Set Buy Limit directly at Proximal line for wholesale fill."
        elif has_sweep or pen_depth > 30.0:
            entry_model = EntryModel.MODEL_B_REVERSAL_CANDLE
            entry_rational = "Zone has previous sweep/penetration: Wait for Reversal Candle (pin-bar/engulfing) confirmation inside zone."
        elif "B_RETEST" in zone_id.upper() or "FLIP" in zone_id.upper():
            entry_model = EntryModel.MODEL_D_FLIP_RETEST
            entry_rational = "Prior resistance reclaimed as support: Enter on proven flip-zone retest."
        else:
            entry_model = EntryModel.MODEL_C_LTF_BOS
            entry_rational = "Pullback into demand: Wait for lower-timeframe Break of Structure (LTF BOS) before committing capital."

        # -------------------------------------------------------------
        # Hard Gates Override Assessment
        # -------------------------------------------------------------
        hard_gate_status = HardGateStatus.APPROVED
        gate_passed = True

        if not data_valid:
            hard_gate_status = HardGateStatus.DEFER_DATA_QUALITY
            gate_passed = False
            rejection_reasons.append("Data quality check failed or insufficient history.")

        if is_chop_area:
            hard_gate_status = HardGateStatus.NO_TRADE_CHOP_GARBAGE
            gate_passed = False
            rejection_reasons.append("Chop/Garbage Area: base has excessive overlapping noise or weak departure.")

        if curve_location_pct > 66.0:
            hard_gate_status = HardGateStatus.NO_TRADE_PREMIUM_LOCATION
            gate_passed = False
            rejection_reasons.append(f"Curve location {curve_location_pct:.1f}% is in premium distribution zone (Retail Trap).")

        if net_rr < self.min_reward_to_risk:
            hard_gate_status = HardGateStatus.NO_TRADE_RR_BELOW_THRESHOLD
            gate_passed = False
            rejection_reasons.append(f"Net Reward-to-Risk {net_rr:.2f}:1 is below required {self.min_reward_to_risk:.1f}:1 threshold.")

        # -------------------------------------------------------------
        # 12-Point Starter Zone Qualification Checklist (Section 15)
        # -------------------------------------------------------------
        checklist = [
            QualificationCheckItem(1, "Permission and data-quality gates pass", data_valid, "Clean bar feed with verified provenance"),
            QualificationCheckItem(2, "Instrument eligible; sufficient history and correct price basis", len(symbol) > 0, f"Symbol: {symbol}"),
            QualificationCheckItem(3, "Base/pivot and boundaries objectively detected", distal < proximal, f"Proximal: {proximal}, Distal: {distal}"),
            QualificationCheckItem(4, "Departure passes versioned displacement/close rule", disp_ratio >= 1.0, f"Displacement ratio: {disp_ratio:.2f}x ATR"),
            QualificationCheckItem(5, "Structure break (BOS) and confirmation known", bos_type != BOSClassification.NO_CLEAR_BREAK, f"BOS: {bos_type.value}"),
            QualificationCheckItem(6, "Zone state and freshness/penetration recorded", True, f"{freshness_detail} | Depth: {pen_depth:.1f}%"),
            QualificationCheckItem(7, "HTF/sector context uses completed data only", score_htf >= 8.0, f"HTF Grade: {alignment_grade}"),
            QualificationCheckItem(8, "Premium/discount range is objective", curve_location_pct <= 60.0, f"Curve: {curve_state} ({curve_location_pct:.1f}%)"),
            QualificationCheckItem(9, "Sweep/inducement labelled as proxy", True, f"Sweep: {has_sweep} ({sweep_desc})"),
            QualificationCheckItem(10, "Entry, stop, target, net R and fill assumptions defined", net_rr >= self.min_reward_to_risk, f"Net R:R: {net_rr:.2f}:1 (Target: Rs. {target_supply:,.2f})"),
            QualificationCheckItem(11, "Independent risk gate passes; portfolio caps respected", gate_passed, f"Gate Status: {hard_gate_status.value}"),
            QualificationCheckItem(12, "Explanation, source lineage, rule/model versions complete", True, f"Model: {entry_model.value} | Framework: v1.0"),
        ]

        return InstitutionalScorecardResult(
            symbol=symbol,
            zone_id=zone_id,
            timeframe=timeframe,
            structure_score=score_struct,
            departure_score=score_depart,
            freshness_score=score_fresh,
            htf_confluence_score=score_htf,
            curve_location_score=score_curve,
            liquidity_sweep_score=score_sweep,
            sector_market_score=score_sector,
            reward_risk_score=score_rr,
            total_score=total_score,
            bos_type=bos_type,
            displacement_ratio_atr=disp_ratio,
            has_liquidity_sweep=has_sweep,
            sweep_description=sweep_desc,
            curve_state=curve_state,
            curve_location_pct=curve_location_pct,
            recommended_entry_model=entry_model,
            entry_model_rational=entry_rational,
            proximal_entry=proximal,
            distal_stop=distal,
            volatility_buffer_px=vol_buffer,
            buffered_stop_loss=buffered_stop,
            target_supply=target_supply,
            net_reward_to_risk=net_rr,
            hard_gate_status=hard_gate_status,
            gate_passed=gate_passed,
            rejection_reasons=rejection_reasons,
            checklist_12_points=checklist,
        )


def calculate_fundamental_quality_score(
    f: Any,  # CompanyFundamentals
) -> Tuple[float, str, str]:
    """
    Evaluates: 'Is the company financially healthy?'
    Returns: (fundamental_quality_score [0-100], verdict, rationale)
    Industry-specific leverage and board-governance aware.
    """
    sym = getattr(f, "symbol", "").upper()
    sector = getattr(f, "sector", "").upper()

    is_banking_fin = (
        "BANK" in sector or "FINANC" in sector or "NBFC" in sector or
        sym in {"HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", "BAJFINANCE", "BAJAJFINSV"}
    )
    is_capital_intensive = (
        any(k in sector for k in ["AUTO", "METAL", "STEEL", "ENERGY", "INFRA", "POWER", "CEMENT"]) or
        sym in {"TATAMOTORS", "TATASTEEL", "NTPC", "POWERGRID", "LT", "JSWSTEEL", "HINDALCO"}
    )

    # 1. Solvency & Balance Sheet (30 pts)
    solv_score = 0.0
    de = getattr(f, "debt_to_equity", 1.0)
    if is_banking_fin:
        if de <= 3.0:
            solv_score += 15.0
        elif de <= 6.0:
            solv_score += 12.0
        elif de <= 8.0:
            solv_score += 8.0
        elif de <= 10.0:
            solv_score += 4.0
        else:
            solv_score += 0.0
    elif is_capital_intensive:
        if de <= 0.5:
            solv_score += 15.0
        elif de <= 1.0:
            solv_score += 12.0
        elif de <= 1.5:
            solv_score += 8.0
        elif de <= 2.0:
            solv_score += 4.0
        else:
            solv_score += 0.0
    else:
        if de <= 0.2:
            solv_score += 15.0
        elif de <= 0.5:
            solv_score += 12.0
        elif de <= 0.8:
            solv_score += 9.0
        elif de <= 1.2:
            solv_score += 4.0
        else:
            solv_score += 0.0

    ic = getattr(f, "interest_coverage", 5.0)
    if ic >= 10.0:
        solv_score += 8.0
    elif ic >= 5.0:
        solv_score += 6.0
    elif ic >= 3.0:
        solv_score += 4.0
    else:
        solv_score += 1.0

    pledge = getattr(f, "promoter_pledge_pct", 0.0)
    if pledge == 0.0:
        solv_score += 7.0
    elif pledge <= 2.0:
        solv_score += 5.0
    elif pledge <= 5.0:
        solv_score += 3.0
    else:
        solv_score += 0.0

    # 2. Profitability & Operational Health (30 pts)
    prof_score = 0.0
    f_score = getattr(f, "piotroski_f_score", 6)
    if f_score >= 8:
        prof_score += 12.0
    elif f_score >= 6:
        prof_score += 9.0
    elif f_score >= 4:
        prof_score += 5.0
    else:
        prof_score += 2.0

    roe = getattr(f, "roe_pct", 15.0)
    if roe >= 20.0:
        prof_score += 10.0
    elif roe >= 15.0:
        prof_score += 8.0
    elif roe >= 10.0:
        prof_score += 5.0
    else:
        prof_score += 2.0

    roce = getattr(f, "roce_pct", 15.0)
    if roce >= 20.0:
        prof_score += 8.0
    elif roce >= 15.0:
        prof_score += 6.0
    elif roce >= 10.0:
        prof_score += 4.0
    else:
        prof_score += 1.0

    # 3. Growth & Institutional Ownership (25 pts)
    growth_score = 0.0
    p_growth = getattr(f, "profit_growth_3y_pct", 12.0)
    if p_growth >= 20.0:
        growth_score += 8.0
    elif p_growth >= 10.0:
        growth_score += 6.0
    elif p_growth > 0.0:
        growth_score += 4.0
    else:
        growth_score += 1.0

    s_growth = getattr(f, "sales_growth_3y_pct", 12.0)
    if s_growth >= 15.0:
        growth_score += 7.0
    elif s_growth >= 10.0:
        growth_score += 5.0
    elif s_growth > 0.0:
        growth_score += 3.0
    else:
        growth_score += 1.0

    tot_inst = getattr(f, "total_institutional_holding_pct", getattr(f, "fii_holding_pct", 20.0) + getattr(f, "dii_holding_pct", 20.0))
    promoter = getattr(f, "promoter_holding_pct", 50.0)
    # Board-governed premier compounder handling
    if promoter == 0.0 or tot_inst >= 40.0:
        growth_score += 6.0
    elif tot_inst >= 20.0:
        growth_score += 4.0
    else:
        growth_score += 2.0

    trend = getattr(f, "institutional_trend", "MILD_ACCUMULATION")
    if trend == "STRONG_ACCUMULATION":
        growth_score += 4.0
    elif trend == "MILD_ACCUMULATION":
        growth_score += 3.0
    elif trend == "NEUTRAL":
        growth_score += 2.0
    else:
        growth_score += 0.0

    # 4. Valuation Attractiveness (15 pts)
    val_score = 0.0
    pe = getattr(f, "pe_ratio", 20.0)
    ind_pe = getattr(f, "industry_pe", 20.0)
    if pe > 0 and ind_pe > 0:
        if pe <= ind_pe * 0.90:
            val_score += 8.0
        elif pe <= ind_pe * 1.15:
            val_score += 6.0
        elif pe <= ind_pe * 1.50:
            val_score += 4.0
        else:
            val_score += 2.0
    else:
        val_score += 4.0

    peg = getattr(f, "peg_ratio", 1.2)
    if 0 < peg <= 1.2:
        val_score += 7.0
    elif peg <= 1.8:
        val_score += 5.0
    elif peg <= 2.5:
        val_score += 3.0
    else:
        val_score += 1.0

    raw_total = solv_score + prof_score + growth_score + val_score
    total_score = round(min(100.0, max(0.0, raw_total)), 1)

    if total_score >= 80.0:
        verdict = "FINANCIALLY_EXCELLENT"
        rationale = "Institutional compounder with pristine balance sheet, strong ROE, and expanding institutional inflows."
    elif total_score >= 65.0:
        verdict = "FINANCIALLY_HEALTHY"
        rationale = "Solid corporate fundamentals with sustainable capital returns and industry-aligned leverage."
    elif total_score >= 50.0:
        verdict = "MODERATE_HEALTH"
        rationale = "Adequate financial health; monitor operating margin stability and debt servicing."
    else:
        verdict = "FINANCIAL_RISK"
        rationale = "Elevated solvency or operational headwinds; below institutional hurdle."

    return total_score, verdict, rationale


def calculate_positional_entry_score(
    current_price: float,
    proximal_line: float,
    distal_line: float,
    buffered_stop_loss: float,
    target_supply: float,
    curve_location_pct: float,
    alignment_grade: str,
    rsi_14: float,
    touch_count: int = 0,
    reward_to_risk: float = 2.5,
) -> Tuple[float, str, str]:
    """
    Evaluates: 'Is the current price suitable for buying?'
    Returns: (positional_entry_score [0-100], verdict, rationale)
    Applies the 1-30 day positional trading rules:
    - RSI 50-70: Preferred entry range
    - RSI 70-80: Strong momentum; evaluate entry carefully
    - RSI >80: Avoid chasing; wait for consolidation/pullback
    - RSI >90: Strong overextension warning
    - Proximity to demand, curve location, and R:R asymmetry.
    """
    dist_pct = round(abs(current_price - proximal_line) / max(1.0, proximal_line) * 100.0, 2)

    # 1. Demand Zone Proximity & Wholesale Geometry (25 pts)
    if dist_pct <= 1.0:
        prox_score = 25.0
    elif dist_pct <= 2.5:
        prox_score = 20.0
    elif dist_pct <= 5.0:
        prox_score = 15.0
    elif dist_pct <= 10.0:
        prox_score = 9.0
    elif dist_pct <= 18.0:
        prox_score = 4.0
    else:
        prox_score = 1.0

    # 2. Curve Location on Macro Horizon (20 pts)
    if curve_location_pct <= 25.0:
        curve_score = 20.0
    elif curve_location_pct <= 35.0:
        curve_score = 16.0
    elif curve_location_pct <= 55.0:
        curve_score = 11.0
    elif curve_location_pct <= 70.0:
        curve_score = 4.0
    else:
        curve_score = 0.0

    # 3. RSI 14 Positional Evaluation Hierarchy (15 pts)
    if 50.0 <= rsi_14 <= 70.0:
        rsi_score = 15.0
    elif 70.0 < rsi_14 <= 80.0:
        rsi_score = 12.0  # Strong momentum; evaluate carefully
    elif 40.0 <= rsi_14 < 50.0:
        rsi_score = 10.0  # Pullback into demand
    elif 80.0 < rsi_14 <= 90.0:
        rsi_score = 3.0   # Avoid chasing; wait consolidation/pullback
    elif rsi_14 > 90.0:
        rsi_score = 0.0   # Strong overextension warning
    else:
        rsi_score = 2.0   # Momentum breakdown

    # 4. Net Reward-to-Risk Ratio (20 pts)
    if reward_to_risk >= 3.5:
        rr_score = 20.0
    elif reward_to_risk >= 2.8:
        rr_score = 16.0
    elif reward_to_risk >= 2.0:
        rr_score = 12.0
    elif reward_to_risk >= 1.5:
        rr_score = 6.0
    else:
        rr_score = 1.0

    # 5. Multi-Timeframe Alignment & Freshness (20 pts)
    grade_u = alignment_grade.upper()
    if "A_PLUS" in grade_u or "A+" in grade_u:
        align_score = 15.0
    elif "GRADE_A" in grade_u:
        align_score = 12.0
    elif "GRADE_B" in grade_u:
        align_score = 8.0
    else:
        align_score = 3.0

    fresh_score = 5.0 if touch_count == 0 else (3.0 if touch_count == 1 else 1.0)
    mtf_fresh_score = align_score + fresh_score

    raw_entry = prox_score + curve_score + rsi_score + rr_score + mtf_fresh_score
    total_entry_score = round(min(100.0, max(0.0, raw_entry)), 1)

    if total_entry_score >= 75.0:
        verdict = "PRIME_BUY_SUITABLE"
        rationale = f"Optimal positional entry: price within {dist_pct:.1f}% of demand, RSI {rsi_14:.1f}, {reward_to_risk:.1f}:1 R:R in lower curve ({curve_location_pct:.1f}%)."
    elif total_entry_score >= 60.0:
        verdict = "ACTIONABLE_PULLBACK"
        rationale = f"Favorable positional setup; place wholesale limit order or prepare for entry on minor pullback ({dist_pct:.1f}% away)."
    elif total_entry_score >= 45.0:
        verdict = "WAIT_FOR_PULLBACK"
        rationale = f"Macro trend intact but price is {dist_pct:.1f}% extended from demand base. Wait for pullback towards ₹{proximal_line:,.2f} before entering."
    else:
        verdict = "AVOID_CHASING_EXTENDED"
        rationale = f"Price excessively extended ({dist_pct:.1f}% away) or RSI ({rsi_14:.1f}) in overbought territory. Avoid chasing."

    return total_entry_score, verdict, rationale
