"""
AI Trading Operating System
Module: scanner/gtf_scanner.py

Institutional GTF Demand & Supply Zone Trade Scanner with Multi-Timeframe Alignment:
- Timeframe Confluence across:
  * Yearly (Y)       : Macro secular trend
  * Half-Yearly (HY) : Multi-quarter momentum
  * Quarterly (Q)    : Institutional trend & Location on the Curve
  * Monthly (M)      : Intermediate trend & dominant zones
  * Daily (D)        : Precision execution at fresh DBR / RBR zones
- Location on the Curve:
  * VERY_LOW (0-25%), LOW (25-40%), EQUILIBRIUM (40-60%), HIGH (60-80%), VERY_HIGH (80-100%)
- Alignment Grading:
  * GRADE A+ : Flawless Multi-Timeframe Confluence (Best Aligned for Trading)
  * GRADE A  : Strong HTF Confluence
  * GRADE B  : Selective Pullback
  * AVOID    : High on Curve / Retail Trap
- Broader Market Condition (NIFTY 50 & Bank Nifty) Confluence:
  * Dynamic sizing multiplier and market regime guidance
- Dedicated Machine Learning Integration:
  * Calibrated Win Probability P(Holds & Reaches >= 2R) + Shannon Entropy Uncertainty
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from ai.demand_supply_ml import DemandMLPrediction, MLDemandSupplyPredictor
from analytics.demand_supply_zones import (
    DemandSupplyZone,
    DemandSupplyZoneEngine,
    PriceLocation,
    ZoneFreshness,
    ZoneType,
)
from analytics.institutional_scorecard import (
    BOSClassification,
    EntryModel,
    HardGateStatus,
    InstitutionalScorecardEngine,
    InstitutionalScorecardResult,
    calculate_fundamental_quality_score,
    calculate_positional_entry_score,
)
from analytics.multi_timeframe_gtf import (
    AlignmentGrade,
    CurveLocation,
    MacroMarketPosture,
    MultiTimeframeGTFEngine,
    StockMultiTimeframeAlignment,
)
from analytics.stock_thesis_engine import StockThesis, StockThesisEngine
from data_engine.fundamental_data import FundamentalDataProvider


@dataclass
class GTFTradeCandidate:
    symbol: str
    zone_type: str
    location_state: str
    current_price: float
    proximal_line: float
    distal_line: float
    target_supply: float
    zone_width: float
    risk_pct: float
    reward_to_risk: float
    odds_enhancer_score: float
    ml_success_probability: float
    ml_uncertainty_score: float
    conviction_tier: str
    composite_rank_score: float
    # Multi-Timeframe Confluence
    yearly_trend: str
    half_yearly_trend: str
    quarterly_trend: str
    monthly_trend: str
    curve_location_pct: float
    curve_state: str
    alignment_grade: str
    is_best_aligned: bool
    is_actionable: bool
    setup_notes: str
    # GTF Institutional Test Date & Freshness History
    formation_date: str = ""
    freshness: str = "FRESH"
    touch_count: int = 0
    last_tested_date: str = "Never Tested (Fresh)"
    tested_dates: List[str] = field(default_factory=list)
    freshness_detail: str = "FRESH (Virgin - 0 Tests)"
    deepest_penetration_px: Optional[float] = None
    penetration_pct: Optional[float] = None
    # 360-Degree Fundamental & News Intelligence
    fundamental_tier: str = "AVERAGE"
    fundamental_score: float = 50.0
    news_sentiment_badge: str = "NEUTRAL"
    conviction_score_360: float = 50.0
    why_to_buy_summary: str = ""
    why_to_hold_summary: str = ""
    why_not_to_buy_summary: str = ""
    # Institutional 100-Point Framework & Entry Model (PDF v1.0)
    scorecard_100: Optional[Dict[str, Any]] = None
    institutional_score_100: float = 70.0
    recommended_entry_model: str = "MODEL_A_DIRECT_LIMIT"
    entry_model_rational: str = ""
    bos_type: str = "NO_CLEAR_BREAK"
    displacement_ratio_atr: float = 1.0
    has_liquidity_sweep: bool = False
    sweep_description: str = ""
    buffered_stop_loss: float = 0.0
    hard_gate_status: str = "APPROVED"
    gate_passed: bool = True
    checklist_12_points: List[Dict[str, Any]] = field(default_factory=list)
    # Dual Output Architecture: Fundamental Quality vs Positional Entry Suitability
    fundamental_quality_score: float = 75.0
    fundamental_health_verdict: str = "FINANCIALLY_HEALTHY"
    positional_entry_score: float = 75.0
    positional_suitability_verdict: str = "PRIME_BUY_SUITABLE"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.setdefault("formation_date", getattr(self, "formation_date", ""))
        d.setdefault("freshness", getattr(self, "freshness", "FRESH"))
        d.setdefault("touch_count", getattr(self, "touch_count", 0))
        d.setdefault("last_tested_date", getattr(self, "last_tested_date", "Never Tested (Fresh)"))
        d.setdefault("tested_dates", getattr(self, "tested_dates", []))
        d.setdefault("freshness_detail", getattr(self, "freshness_detail", "FRESH (Virgin - 0 Tests)"))
        d.setdefault("deepest_penetration_px", getattr(self, "deepest_penetration_px", None))
        d.setdefault("penetration_pct", getattr(self, "penetration_pct", None))
        d.setdefault("fundamental_tier", getattr(self, "fundamental_tier", "AVERAGE"))
        d.setdefault("fundamental_score", getattr(self, "fundamental_score", 50.0))
        d.setdefault("news_sentiment_badge", getattr(self, "news_sentiment_badge", "NEUTRAL"))
        d.setdefault("conviction_score_360", getattr(self, "conviction_score_360", 50.0))
        d.setdefault("why_to_buy_summary", getattr(self, "why_to_buy_summary", ""))
        d.setdefault("why_to_hold_summary", getattr(self, "why_to_hold_summary", ""))
        d.setdefault("why_not_to_buy_summary", getattr(self, "why_not_to_buy_summary", ""))
        d.setdefault("scorecard_100", getattr(self, "scorecard_100", None))
        d.setdefault("institutional_score_100", getattr(self, "institutional_score_100", 70.0))
        d.setdefault("recommended_entry_model", getattr(self, "recommended_entry_model", "MODEL_A_DIRECT_LIMIT"))
        d.setdefault("entry_model_rational", getattr(self, "entry_model_rational", ""))
        d.setdefault("bos_type", getattr(self, "bos_type", "NO_CLEAR_BREAK"))
        d.setdefault("displacement_ratio_atr", getattr(self, "displacement_ratio_atr", 1.0))
        d.setdefault("has_liquidity_sweep", getattr(self, "has_liquidity_sweep", False))
        d.setdefault("sweep_description", getattr(self, "sweep_description", ""))
        d.setdefault("buffered_stop_loss", getattr(self, "buffered_stop_loss", 0.0))
        d.setdefault("hard_gate_status", getattr(self, "hard_gate_status", "APPROVED"))
        d.setdefault("gate_passed", getattr(self, "gate_passed", True))
        d.setdefault("checklist_12_points", getattr(self, "checklist_12_points", []))
        d.setdefault("fundamental_quality_score", getattr(self, "fundamental_quality_score", 75.0))
        d.setdefault("fundamental_health_verdict", getattr(self, "fundamental_health_verdict", "FINANCIALLY_HEALTHY"))
        d.setdefault("positional_entry_score", getattr(self, "positional_entry_score", 75.0))
        d.setdefault("positional_suitability_verdict", getattr(self, "positional_suitability_verdict", "PRIME_BUY_SUITABLE"))
        return d


@dataclass
class GTFScanResult:
    as_of_date: date
    market_posture: MacroMarketPosture
    total_symbols_scanned: int
    total_demand_zones_found: int
    fresh_demand_zones_count: int
    at_demand_count: int
    approaching_demand_count: int
    best_aligned_candidates: List[GTFTradeCandidate]
    actionable_candidates: List[GTFTradeCandidate]
    watchlist_candidates: List[GTFTradeCandidate]
    avoid_trap_candidates: List[GTFTradeCandidate]
    top_stock_theses: Optional[List[StockThesis]] = None

    def format_terminal_report(self) -> str:
        sep = "=" * 90
        subsep = "-" * 90
        lines: List[str] = []

        lines.append(sep)
        lines.append("  GTF INSTITUTIONAL MULTI-TIMEFRAME DEMAND & SUPPLY SCANNER -- QUANTITATIVE REPORT")
        lines.append(f"  As of: {self.as_of_date} | Horizons: Yearly -> Half-Yearly -> Quarterly -> Monthly -> Daily")
        lines.append(sep)

        # -------------------------------------------------------------
        # Part 1: Macro Market Condition (NIFTY 50 Confluence)
        # -------------------------------------------------------------
        mp = self.market_posture
        lines.append("\n[1] BROADER MARKET CONDITION & MACRO HORIZONS (NIFTY 50 CONFLUENCE)")
        lines.append(subsep)
        lines.append(f"  Benchmark Symbol      : {mp.benchmark_symbol}")
        lines.append(f"  Overall Market Posture: {mp.overall_posture} (Recommended Sizing: {mp.sizing_recommendation:.2f}x)")
        lines.append(f"  Yearly Trend (Y)      : {mp.yearly_trend}")
        lines.append(f"  Quarterly Trend (Q)   : {mp.quarterly_trend} | Market Curve Location: {mp.market_curve_location}")
        lines.append(f"  Monthly Trend (M)     : {mp.monthly_trend}")
        for note in mp.summary_notes:
            lines.append(f"  * Guideline: {note}")

        lines.append(f"\n  Universe Stats: {self.total_symbols_scanned} stocks screened | {self.total_demand_zones_found} zones ({self.fresh_demand_zones_count} Fresh) | {self.at_demand_count} AT Demand")
        lines.append(subsep)

        # -------------------------------------------------------------
        # Part 2: Best Aligned Stocks (Grade A+ & Grade A Confluence)
        # -------------------------------------------------------------
        lines.append("\n[2] TOP INSTITUTIONAL ALIGNED STOCKS (GRADE A+ / GRADE A CONFLUENCE)")
        lines.append("    Mandate: All-timeframe bullish alignment + Low on Curve + Fresh Demand Zone")
        lines.append(subsep)

        top_picks = self.best_aligned_candidates
        if top_picks:
            lines.append(
                f"  {'#':<3} {'Symbol':<10} {'Grade':<9} {'Y':<5} {'HY':<5} {'Q':<5} {'M':<5} "
                f"{'Curve%':<7} {'Price':<8} {'Proximal':<9} {'Distal':<8} {'Target':<8} {'R:R':<5} {'ML Prob':<8}"
            )
            for idx, c in enumerate(top_picks[:15], 1):
                p_str = f"{c.ml_success_probability:.1f}%"
                c_str = f"{c.curve_location_pct:.1f}%"
                y_short = "BULL" if "BULL" in c.yearly_trend else "BEAR"
                hy_short = "BULL" if "BULL" in c.half_yearly_trend else "BEAR"
                q_short = "BULL" if "BULL" in c.quarterly_trend else "BEAR"
                m_short = "BULL" if "BULL" in c.monthly_trend else "BEAR"

                lines.append(
                    f"  #{idx:<2} {c.symbol:<10} {c.alignment_grade:<9} {y_short:<5} {hy_short:<5} {q_short:<5} {m_short:<5} "
                    f"{c_str:<7} {c.current_price:<8.2f} {c.proximal_line:<9.2f} {c.distal_line:<8.2f} {c.target_supply:<8.2f} {c.reward_to_risk:<5.1f} {p_str:<8}"
                )
        else:
            lines.append("  No symbols currently achieving Grade A+/A multi-timeframe alignment in lower curve.")

        # -------------------------------------------------------------
        # Part 3: Actionable Trade Setups (At Demand Zone / Pullback)
        # -------------------------------------------------------------
        lines.append("\n[3] HIGH-CONVICTION ACTIONABLE SETUPS (AT DEMAND ZONE)")
        lines.append(subsep)
        if self.actionable_candidates:
            lines.append(
                f"  {'#':<3} {'Symbol':<10} {'Pattern':<8} {'Price':<9} {'Proximal':<9} "
                f"{'Distal':<8} {'Target':<8} {'R:R':<5} {'Odds':<6} {'ML Prob':<8} {'Tier':<10} {'State'}"
            )
            for idx, c in enumerate(self.actionable_candidates[:10], 1):
                p_str = f"{c.ml_success_probability:.1f}%"
                odds_str = f"{c.odds_enhancer_score:.1f}/10"
                lines.append(
                    f"  #{idx:<2} {c.symbol:<10} {c.zone_type:<8} {c.current_price:<9.2f} {c.proximal_line:<9.2f} "
                    f"{c.distal_line:<8.2f} {c.target_supply:<8.2f} {c.reward_to_risk:<5.1f} {odds_str:<6} {p_str:<8} {c.conviction_tier:<10} {c.location_state}"
                )
        else:
            lines.append("  No stocks currently testing fresh demand zones with ML prob >= 60% and R:R >= 2.0.")

        # -------------------------------------------------------------
        # Part 4: 360-DEGREE Institutional Conviction & Actionable Notes
        # -------------------------------------------------------------
        if self.top_stock_theses:
            lines.append("\n[4] 360-DEGREE INSTITUTIONAL CONVICTION & VALUABLE ACTIONABLE NOTES (TOP CANDIDATES)")
            lines.append("    Confluence: Technical GTF (35%) + ML Win Prob (25%) + Fundamentals (25%) + News (15%)")
            lines.append(subsep)
            for t in self.top_stock_theses[:3]:
                lines.append(f"  >>> {t.symbol} ({t.company_name}) -- Verdict: {t.executive_verdict} (Conviction: {t.conviction_score_360:.1f}/100)")
                lines.append(f"      P/E: {t.pe_ratio:.1f}x (Ind: {t.industry_pe:.1f}x) | ROE: {t.roe_pct:.1f}% | D/E: {t.debt_to_equity:.2f} | F-Score: {t.piotroski_f_score}/9 | News: {t.news_sentiment_badge}")
                lines.append("      [+] WHY TO BUY:")
                for b_note in t.why_to_buy[:3]:
                    lines.append(f"         * {b_note}")
                lines.append("      [=] WHY TO HOLD:")
                for h_note in t.why_to_hold[:2]:
                    lines.append(f"         * {h_note}")
                lines.append("      [!] WHY NOT TO BUY / RED FLAGS:")
                for r_note in t.why_not_to_buy[:2]:
                    lines.append(f"         * {r_note}")
                lines.append("")

        # -------------------------------------------------------------
        # Part 5: Watchlist: Approaching Demand Zones
        # -------------------------------------------------------------
        lines.append("\n[5] WATCHLIST: STOCKS APPROACHING FRESH DEMAND ZONES (PENDING PULLBACK)")
        lines.append(subsep)
        if self.watchlist_candidates:
            lines.append(
                f"  {'#':<3} {'Symbol':<10} {'Pattern':<8} {'Price':<9} {'Proximal':<9} "
                f"{'Distal':<8} {'Target':<8} {'R:R':<5} {'Curve Location':<15} {'Distance'}"
            )
            for idx, c in enumerate(self.watchlist_candidates[:8], 1):
                dist_str = f"+{((c.current_price - c.proximal_line)/c.proximal_line)*100.0:.2f}%"
                curve_info = f"{c.curve_state} ({c.curve_location_pct:.1f}%)"
                lines.append(
                    f"  #{idx:<2} {c.symbol:<10} {c.zone_type:<8} {c.current_price:<9.2f} {c.proximal_line:<9.2f} "
                    f"{c.distal_line:<8.2f} {c.target_supply:<8.2f} {c.reward_to_risk:<5.1f} {curve_info:<15} {dist_str}"
                )

        # -------------------------------------------------------------
        # Part 6: Institutional Distribution / Avoid List
        # -------------------------------------------------------------
        if self.avoid_trap_candidates:
            lines.append("\n[6] INSTITUTIONAL SUPPLY WARNING LIST (HIGH ON CURVE - DO NOT BUY)")
            lines.append(subsep)
            for c in self.avoid_trap_candidates[:5]:
                lines.append(f"  * {c.symbol:<10} Price: Rs. {c.current_price:,.2f} | Curve: {c.curve_state} ({c.curve_location_pct:.1f}%) | Warning: Testing Macro Supply ceiling")

        lines.append(subsep)
        lines.append("  GTF INSTITUTIONAL EXECUTION MANDATE:")
        lines.append("  * Grade A+ Confluence: Full trade size allowed (Yearly+Quarterly Bullish + Low Curve).")
        lines.append("  * Wholesale Entry    : Buy Limit placed strictly at Proximal Line.")
        lines.append("  * Invalidation Level : Distal Stop Loss placed safely 0.3% below lowest base wick.")
        lines.append("  * Asymmetric Target  : Opposing Supply Zone Proximal Line (Minimum 2:1 R:R).")
        lines.append(sep)
        return "\n".join(lines)


class GTFTradeScanner:
    """
    Dedicated Scanner executing the GTF Pure Demand & Supply Zone Concept
    with full Multi-Timeframe Alignment (Monthly, Quarterly, Half-Yearly, Yearly).
    """

    def __init__(
        self,
        min_odds_score: float = 6.0,
        min_reward_to_risk: float = 2.0,
        min_ml_probability: float = 0.58,
    ) -> None:
        self.zone_engine = DemandSupplyZoneEngine(min_reward_to_risk=min_reward_to_risk)
        self.mtf_engine = MultiTimeframeGTFEngine()
        self.ml_predictor = MLDemandSupplyPredictor()
        self.thesis_engine = StockThesisEngine()
        self.fundamental_provider = FundamentalDataProvider()
        self.inst_scorecard = InstitutionalScorecardEngine(min_reward_to_risk=min_reward_to_risk)
        self.min_odds_score = min_odds_score
        self.min_reward_to_risk = min_reward_to_risk
        self.min_ml_probability = min_ml_probability

    def scan_universe(
        self,
        data: pd.DataFrame,
        as_of_date: Optional[date] = None,
        benchmark_symbol: str = "NIFTY 50",
    ) -> GTFScanResult:
        """
        Scans market universe for institutional Demand & Supply zones with multi-timeframe alignment.
        """
        if data.empty or "symbol" not in data.columns:
            empty_posture = MacroMarketPosture(
                benchmark_symbol=benchmark_symbol,
                as_of_date=date.today(),
                yearly_trend="NEUTRAL",
                quarterly_trend="NEUTRAL",
                monthly_trend="NEUTRAL",
                market_curve_location="EQUILIBRIUM",
                overall_posture="NEUTRAL",
                sizing_recommendation=0.5,
                summary_notes=["No data available"],
            )
            return GTFScanResult(
                as_of_date=date.today(),
                market_posture=empty_posture,
                total_symbols_scanned=0,
                total_demand_zones_found=0,
                fresh_demand_zones_count=0,
                at_demand_count=0,
                approaching_demand_count=0,
                best_aligned_candidates=[],
                actionable_candidates=[],
                watchlist_candidates=[],
                avoid_trap_candidates=[],
                top_stock_theses=[],
            )

        df = data.copy()
        df["trading_date"] = pd.to_datetime(df["trading_date"]).dt.date
        eff_date = as_of_date or df["trading_date"].max()
        visible_df = df[df["trading_date"] <= eff_date]

        # 1. Macro Market Condition (NIFTY 50 Confluence)
        market_posture = self.mtf_engine.evaluate_macro_market_condition(
            visible_df, benchmark_symbol=benchmark_symbol
        )

        symbols = visible_df["symbol"].unique()
        all_candidates: List[GTFTradeCandidate] = []
        theses_by_sym: Dict[str, StockThesis] = {}
        total_demand_count = 0
        fresh_count = 0
        at_demand_cnt = 0
        approaching_cnt = 0

        for sym in symbols:
            # Skip benchmark from stock scan
            if sym.upper() in {"NIFTY 50", "BANK NIFTY", "^NSEI"}:
                continue

            sym_df = visible_df[visible_df["symbol"] == sym].sort_values("trading_date")
            if len(sym_df) < 5:
                continue

            cur_price = float(sym_df.iloc[-1]["close"])

            # Precompute indicators (RSI 14) and fundamental quality
            delta = sym_df["close"].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(14, min_periods=1).mean().iloc[-1]
            avg_loss = loss.rolling(14, min_periods=1).mean().iloc[-1]
            rs = avg_gain / max(1e-6, avg_loss)
            rsi_14 = float(100 - (100 / (1 + rs)))

            f_data = self.fundamental_provider.get_fundamentals(sym)
            fund_qual_score, fund_health_verdict, fund_rationale = calculate_fundamental_quality_score(f_data)

            # 2. Multi-Timeframe Alignment Evaluation (Y, HY, Q, M)
            align: StockMultiTimeframeAlignment = self.mtf_engine.evaluate_stock_alignment(
                sym_df, symbol=sym, as_of_date=eff_date
            )

            # 3. 360-Degree Stock Thesis & Fundamentals (Fast in-memory during bulk scan)
            thesis = self.thesis_engine.generate_stock_thesis(sym, sym_df, live_news=False)
            theses_by_sym[sym] = thesis

            # 4. Detect Daily Demand & Supply Zones
            demand_zones, supply_zones = self.zone_engine.find_all_zones(sym_df, symbol=sym)
            total_demand_count += len(demand_zones)

            # If no demand zone found, synthesize baseline from MTF alignment
            if not demand_zones:
                if align.is_best_aligned_for_trading:
                    pos_score, pos_verdict, pos_rationale = calculate_positional_entry_score(
                        current_price=cur_price,
                        proximal_line=align.daily_proximal_entry,
                        distal_line=align.daily_distal_stop,
                        buffered_stop_loss=align.daily_distal_stop,
                        target_supply=align.daily_target_supply,
                        curve_location_pct=align.curve_location_pct,
                        alignment_grade=align.alignment_grade.value,
                        rsi_14=rsi_14,
                        touch_count=0,
                        reward_to_risk=align.reward_to_risk,
                    )
                    cand = GTFTradeCandidate(
                        symbol=sym,
                        zone_type="MTF_TREND",
                        location_state=PriceLocation.IN_TRANSIT.value,
                        current_price=cur_price,
                        proximal_line=align.daily_proximal_entry,
                        distal_line=align.daily_distal_stop,
                        target_supply=align.daily_target_supply,
                        zone_width=round(align.daily_proximal_entry - align.daily_distal_stop, 2),
                        risk_pct=round(((align.daily_proximal_entry - align.daily_distal_stop) / align.daily_proximal_entry) * 100.0, 2),
                        reward_to_risk=align.reward_to_risk,
                        odds_enhancer_score=round(align.alignment_score / 10.0, 1),
                        ml_success_probability=round(align.alignment_score, 1),
                        ml_uncertainty_score=20.0,
                        conviction_tier="HIGH" if align.alignment_grade == AlignmentGrade.GRADE_A_PLUS else "MODERATE",
                        composite_rank_score=align.alignment_score,
                        yearly_trend=align.yearly.trend_state.value,
                        half_yearly_trend=align.half_yearly.trend_state.value,
                        quarterly_trend=align.quarterly.trend_state.value,
                        monthly_trend=align.monthly.trend_state.value,
                        curve_location_pct=align.curve_location_pct,
                        curve_state=align.curve_state.value,
                        alignment_grade=align.alignment_grade.value,
                        is_best_aligned=True,
                        is_actionable=False,
                        setup_notes="MTF Confluence without active daily base",
                        formation_date=str(eff_date),
                        freshness="FRESH",
                        touch_count=0,
                        last_tested_date="Never Tested (Fresh)",
                        tested_dates=[],
                        freshness_detail="FRESH (Secular MTF Trend - 0 Tests)",
                        deepest_penetration_px=None,
                        penetration_pct=0.0,
                        fundamental_tier=thesis.fundamental_tier,
                        fundamental_score=round(thesis.fundamental_quality_score * 4.0, 1),
                        news_sentiment_badge=thesis.news_sentiment_badge,
                        conviction_score_360=thesis.conviction_score_360,
                        why_to_buy_summary=" | ".join(thesis.why_to_buy[:2]),
                        why_to_hold_summary=" | ".join(thesis.why_to_hold[:2]),
                        why_not_to_buy_summary=" | ".join(thesis.why_not_to_buy[:2]),
                        fundamental_quality_score=fund_qual_score,
                        fundamental_health_verdict=fund_health_verdict,
                        positional_entry_score=pos_score,
                        positional_suitability_verdict=pos_verdict,
                    )
                    all_candidates.append(cand)
                continue

            for d_zone in demand_zones:
                if d_zone.freshness == ZoneFreshness.FRESH:
                    fresh_count += 1

                if d_zone.location_state == PriceLocation.AT_DEMAND_ZONE:
                    at_demand_cnt += 1
                elif d_zone.location_state == PriceLocation.APPROACHING_DEMAND:
                    approaching_cnt += 1

                # 4. Predict via dedicated ML Model
                ml_pred: DemandMLPrediction = self.ml_predictor.predict_zone(d_zone)

                # Composite score: 40% MTF Alignment + 30% Odds Enhancer + 30% ML probability
                comp_score = (
                    (align.alignment_score * 0.40) +
                    (d_zone.odds_enhancer_score * 10.0 * 0.30) +
                    (ml_pred.success_probability * 100.0 * 0.30)
                )

                # 5. Evaluate Institutional-Style 100-Point Scorecard (Document v1.0)
                market_bullish = market_posture.overall_posture in {"STRONG_BULLISH", "BULLISH", "SELECTIVE_BUY"}
                bos_val = getattr(d_zone, "bos_type", "NO_CLEAR_BREAK")
                try:
                    bos_enum = BOSClassification(bos_val)
                except Exception:
                    bos_enum = BOSClassification.NO_CLEAR_BREAK

                scorecard_res = self.inst_scorecard.score_zone(
                    symbol=sym,
                    zone_id=d_zone.zone_id,
                    timeframe="Daily",
                    proximal=d_zone.proximal_line,
                    distal=d_zone.distal_line,
                    target_supply=ml_pred.target_price,
                    current_price=cur_price,
                    leg_out_gain_pct=d_zone.leg_out_strength,
                    atr_14=getattr(d_zone, "atr_14", 1.0),
                    freshness_detail=getattr(d_zone, "freshness_detail", d_zone.freshness.value),
                    touch_count=d_zone.touch_count,
                    penetration_pct=getattr(d_zone, "penetration_pct", None),
                    alignment_grade=align.alignment_grade.value,
                    curve_location_pct=align.curve_location_pct,
                    curve_state=align.curve_state.value,
                    bos_type=bos_enum,
                    has_sweep=getattr(d_zone, "has_liquidity_sweep", False),
                    sweep_desc=getattr(d_zone, "sweep_desc", ""),
                    market_posture_bullish=market_bullish,
                    sector_bullish=True,
                    is_chop_area=getattr(d_zone, "is_chop_area", False),
                    data_valid=True,
                )

                # Hard Gates Override (Section 4 & 8):
                # Setup must pass all data readiness, valid zone, positive net R:R, and risk policy checks.
                is_act = (
                    d_zone.location_state in {PriceLocation.AT_DEMAND_ZONE, PriceLocation.APPROACHING_DEMAND} and
                    scorecard_res.gate_passed and
                    scorecard_res.total_score >= 60.0 and
                    ml_pred.success_probability >= self.min_ml_probability and
                    d_zone.reward_to_risk >= self.min_reward_to_risk and
                    market_posture.sizing_recommendation > 0.0
                )

                # Compute Positional Entry Score & Suitability Verdict
                pos_score, pos_verdict, pos_rationale = calculate_positional_entry_score(
                    current_price=cur_price,
                    proximal_line=d_zone.proximal_line,
                    distal_line=d_zone.distal_line,
                    buffered_stop_loss=scorecard_res.buffered_stop_loss,
                    target_supply=ml_pred.target_price,
                    curve_location_pct=align.curve_location_pct,
                    alignment_grade=align.alignment_grade.value,
                    rsi_14=rsi_14,
                    touch_count=d_zone.touch_count,
                    reward_to_risk=d_zone.reward_to_risk,
                )

                cand = GTFTradeCandidate(
                    symbol=sym,
                    zone_type=d_zone.zone_type.value.replace("DEMAND_", ""),
                    location_state=d_zone.location_state.value,
                    current_price=cur_price,
                    proximal_line=d_zone.proximal_line,
                    distal_line=d_zone.distal_line,
                    target_supply=ml_pred.target_price,
                    zone_width=d_zone.zone_width,
                    risk_pct=d_zone.zone_width_pct,
                    reward_to_risk=d_zone.reward_to_risk,
                    odds_enhancer_score=d_zone.odds_enhancer_score,
                    ml_success_probability=round(ml_pred.success_probability * 100.0, 1),
                    ml_uncertainty_score=round(ml_pred.uncertainty_score * 100.0, 1),
                    conviction_tier=ml_pred.conviction_tier,
                    composite_rank_score=round(comp_score, 1),
                    yearly_trend=align.yearly.trend_state.value,
                    half_yearly_trend=align.half_yearly.trend_state.value,
                    quarterly_trend=align.quarterly.trend_state.value,
                    monthly_trend=align.monthly.trend_state.value,
                    curve_location_pct=align.curve_location_pct,
                    curve_state=align.curve_state.value,
                    alignment_grade=align.alignment_grade.value,
                    is_best_aligned=align.is_best_aligned_for_trading,
                    is_actionable=is_act,
                    setup_notes=" | ".join(align.confluence_rationale[:2]),
                    formation_date=str(d_zone.formation_date),
                    freshness=d_zone.freshness.value,
                    touch_count=d_zone.touch_count,
                    last_tested_date=str(d_zone.last_tested_date) if getattr(d_zone, "last_tested_date", None) else "Never Tested (Fresh)",
                    tested_dates=[str(d) for d in getattr(d_zone, "test_dates", [])],
                    freshness_detail=getattr(d_zone, "freshness_detail", d_zone.freshness.value),
                    deepest_penetration_px=getattr(d_zone, "deepest_penetration_px", None),
                    penetration_pct=getattr(d_zone, "penetration_pct", None),
                    fundamental_tier=thesis.fundamental_tier,
                    fundamental_score=round(thesis.fundamental_quality_score * 4.0, 1),
                    news_sentiment_badge=thesis.news_sentiment_badge,
                    conviction_score_360=thesis.conviction_score_360,
                    why_to_buy_summary=" | ".join(thesis.why_to_buy[:2]),
                    why_to_hold_summary=" | ".join(thesis.why_to_hold[:2]),
                    why_not_to_buy_summary=" | ".join(thesis.why_not_to_buy[:2]),
                    scorecard_100=scorecard_res.to_dict(),
                    institutional_score_100=scorecard_res.total_score,
                    recommended_entry_model=scorecard_res.recommended_entry_model.value,
                    entry_model_rational=scorecard_res.entry_model_rational,
                    bos_type=scorecard_res.bos_type.value,
                    displacement_ratio_atr=scorecard_res.displacement_ratio_atr,
                    has_liquidity_sweep=scorecard_res.has_liquidity_sweep,
                    sweep_description=scorecard_res.sweep_description,
                    buffered_stop_loss=scorecard_res.buffered_stop_loss,
                    hard_gate_status=scorecard_res.hard_gate_status.value,
                    gate_passed=scorecard_res.gate_passed,
                    checklist_12_points=[asdict(c) for c in scorecard_res.checklist_12_points],
                    fundamental_quality_score=fund_qual_score,
                    fundamental_health_verdict=fund_health_verdict,
                    positional_entry_score=pos_score,
                    positional_suitability_verdict=pos_verdict,
                )
                all_candidates.append(cand)

        # Categorize
        all_candidates.sort(key=lambda c: (c.is_actionable, c.is_best_aligned, c.institutional_score_100, c.composite_rank_score), reverse=True)

        best_aligned = [c for c in all_candidates if c.is_best_aligned]
        actionable = [c for c in all_candidates if c.is_actionable]
        watchlist = [
            c for c in all_candidates
            if not c.is_actionable and c.location_state == PriceLocation.APPROACHING_DEMAND.value
        ]
        avoid_list = [
            c for c in all_candidates
            if c.alignment_grade == AlignmentGrade.AVOID_TRAP.value or c.curve_state in {CurveLocation.HIGH.value, CurveLocation.VERY_HIGH.value}
        ]

        top_picks_for_theses = actionable if actionable else (best_aligned if best_aligned else watchlist)
        seen_syms = set()
        top_theses: List[StockThesis] = []
        for c in top_picks_for_theses:
            if c.symbol not in seen_syms and c.symbol in theses_by_sym:
                seen_syms.add(c.symbol)
                top_theses.append(theses_by_sym[c.symbol])
                if len(top_theses) >= 3:
                    break

        return GTFScanResult(
            as_of_date=eff_date,
            market_posture=market_posture,
            total_symbols_scanned=len(symbols),
            total_demand_zones_found=total_demand_count,
            fresh_demand_zones_count=fresh_count,
            at_demand_count=at_demand_cnt,
            approaching_demand_count=approaching_cnt,
            best_aligned_candidates=best_aligned,
            actionable_candidates=actionable,
            watchlist_candidates=watchlist,
            avoid_trap_candidates=avoid_list,
            top_stock_theses=top_theses,
        )
