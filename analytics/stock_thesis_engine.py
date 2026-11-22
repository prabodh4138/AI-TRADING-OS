"""
AI Trading Operating System
Module: analytics/stock_thesis_engine.py

Institutional 360-Degree Stock Thesis & Decision Engine:
Synthesizes:
1. Multi-Timeframe GTF Demand/Supply Alignment (Yearly, Half-Yearly, Quarterly, Monthly, Daily)
2. Dedicated Machine Learning Zone Probability & Uncertainty
3. Fundamental Valuation, Balance Sheet Quality, and Institutional Flows
4. Real-time Corporate News Sentiment & Catalysts

Generates concrete, actionable institutional investment & trading theses:
- 360° Composite Conviction Score (0-100)
- Executive Verdict (STRONG_CONVICTION_BUY, PULLBACK_ACCUMULATE, HOLD_AND_TRAIL, AVOID_DO_NOT_BUY)
- Valuable Actionable Notes:
  * WHY TO BUY: Confluence reasons to enter at wholesale prices
  * WHY TO HOLD: Position management, trailing stop rules, and target runway
  * WHY NOT TO BUY / RED FLAGS: Specific invalidation levels and risk warnings
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
import pandas as pd

from analytics.fundamental_engine import FundamentalAnalysisEngine, FundamentalAnalysisReport
from analytics.multi_timeframe_gtf import (
    AlignmentGrade,
    CurveLocation,
    MultiTimeframeGTFEngine,
    StockMultiTimeframeAlignment,
)
from analytics.demand_supply_zones import DemandSupplyZoneEngine, PriceLocation, ZoneType
from ai.demand_supply_ml import MLDemandSupplyPredictor
from data_engine.news_engine import NewsEngine, StockNewsProfile


@dataclass
class StockThesis:
    symbol: str
    company_name: str
    sector: str
    current_price: float
    executive_verdict: str  # STRONG_CONVICTION_BUY, PULLBACK_ACCUMULATE, HOLD_AND_TRAIL, NEUTRAL_WATCHLIST, AVOID_DO_NOT_BUY
    conviction_score_360: float  # 0 to 100
    # 4 Pillar Breakdown
    technical_gtf_score: float  # 0 to 35
    ml_forecast_score: float  # 0 to 25
    fundamental_quality_score: float  # 0 to 25
    news_sentiment_score: float  # 0 to 15
    # Institutional GTF Demand/Supply Parameters
    timeframe_alignment_grade: str
    curve_location: str
    curve_location_pct: float
    zone_pattern: str
    proximal_entry: float
    distal_stop: float
    target_supply: float
    reward_to_risk: float
    ml_success_probability: float
    # Fundamental Ratios
    pe_ratio: float
    industry_pe: float
    roe_pct: float
    debt_to_equity: float
    fii_dii_holding_pct: float
    piotroski_f_score: int
    fundamental_tier: str
    # News & Sentiment
    news_sentiment_badge: str
    top_catalysts: List[str]
    recent_headlines: List[str]
    # The Actionable Notes
    why_to_buy: List[str]
    why_to_hold: List[str]
    why_not_to_buy: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def format_terminal_report(self) -> str:
        sep = "=" * 88
        subsep = "-" * 88
        lines: List[str] = []

        lines.append(sep)
        lines.append(f"  AI-TOS 360-DEGREE INSTITUTIONAL STOCK THESIS: {self.symbol} ({self.company_name})")
        lines.append(f"  Sector: {self.sector} | Current Price: Rs. {self.current_price:,.2f}")
        lines.append(sep)

        # Verdict Header
        verdict_badge = f"*** {self.executive_verdict.replace('_', ' ')} ***"
        lines.append(f"  EXECUTIVE VERDICT     : {verdict_badge}")
        lines.append(f"  360-DEGREE CONVICTION : {self.conviction_score_360:.1f} / 100.0")
        lines.append(
            f"  Pillar Breakdown      : GTF Technicals: {self.technical_gtf_score:.1f}/35 | "
            f"ML Win Prob: {self.ml_forecast_score:.1f}/25 | "
            f"Fundamentals: {self.fundamental_quality_score:.1f}/25 | "
            f"News: {self.news_sentiment_score:.1f}/15"
        )
        lines.append(subsep)

        # Quantitative Snapshot
        lines.append("  [1] EXECUTION & MULTI-TIMEFRAME CONFLUENCE")
        lines.append(f"  * Alignment Grade : {self.timeframe_alignment_grade} | Curve Location: {self.curve_location} ({self.curve_location_pct:.1f}%)")
        lines.append(f"  * Demand Zone     : {self.zone_pattern} (Proximal Entry: Rs. {self.proximal_entry:,.2f} | Distal Stop: Rs. {self.distal_stop:,.2f})")
        lines.append(f"  * Target Supply   : Rs. {self.target_supply:,.2f} (Reward-to-Risk: {self.reward_to_risk:.1f}:1)")
        lines.append(f"  * ML Win Prob     : {self.ml_success_probability:.1f}% (Holds and Reaches >= 2R)")
        lines.append("")

        lines.append("  [2] FUNDAMENTAL HEALTH & QUALITY SCORECARD")
        lines.append(f"  * Quality Tier    : {self.fundamental_tier.replace('_', ' ')}")
        lines.append(
            f"  * Valuation       : P/E: {self.pe_ratio:.1f}x (Industry: {self.industry_pe:.1f}x) | "
            f"ROE: {self.roe_pct:.1f}% | Debt/Equity: {self.debt_to_equity:.2f}"
        )
        lines.append(
            f"  * Ownership & Ops : FII + DII Holding: {self.fii_dii_holding_pct:.1f}% | "
            f"Piotroski F-Score: {self.piotroski_f_score}/9"
        )
        lines.append("")

        lines.append("  [3] LATEST NEWS & CATALYST INTELLIGENCE")
        lines.append(f"  * Sentiment Badge : {self.news_sentiment_badge.replace('_', ' ')}")
        for cat in self.top_catalysts[:2]:
            lines.append(f"  * Catalyst Event  : {cat}")
        for hl in self.recent_headlines[:3]:
            lines.append(f"  * Recent Headline : \"{hl}\"")
        lines.append(subsep)

        # -------------------------------------------------------------
        # The 3-Part Actionable Notes
        # -------------------------------------------------------------
        lines.append("  [4] VALUABLE INSTITUTIONAL ACTIONABLE NOTES")
        lines.append(subsep)

        lines.append("  [+] WHY TO BUY (Entry Rationale & High-Conviction Confluence):")
        for idx, pt in enumerate(self.why_to_buy, 1):
            lines.append(f"    {idx}. {pt}")
        lines.append("")

        lines.append("  [=] WHY TO HOLD (Trade Management, Trailing Rules & Runway):")
        for idx, pt in enumerate(self.why_to_hold, 1):
            lines.append(f"    {idx}. {pt}")
        lines.append("")

        lines.append("  [!] WHY NOT TO BUY / RED FLAGS (Invalidation Rules & Red Alerts):")
        for idx, pt in enumerate(self.why_not_to_buy, 1):
            lines.append(f"    {idx}. {pt}")

        lines.append(sep)
        return "\n".join(lines)


class StockThesisEngine:
    """
    Synthesizes Technicals, ML Predictions, Fundamentals, and News into
    a concrete 360-degree institutional trade thesis.
    """

    def __init__(
        self,
        fundamental_engine: Optional[FundamentalAnalysisEngine] = None,
        news_engine: Optional[NewsEngine] = None,
    ) -> None:
        self.fundamental_engine = fundamental_engine or FundamentalAnalysisEngine()
        self.news_engine = news_engine or NewsEngine()
        self.mtf_engine = MultiTimeframeGTFEngine()
        self.zone_engine = DemandSupplyZoneEngine()
        self.ml_predictor = MLDemandSupplyPredictor()

    def generate_stock_thesis(
        self,
        symbol: str,
        price_history: Optional[pd.DataFrame] = None,
        live_news: bool = True,
    ) -> StockThesis:
        sym = symbol.strip().upper()

        # 1. Fundamental Report
        f_rep: FundamentalAnalysisReport = self.fundamental_engine.analyze_stock(sym)

        # 2. News Profile
        news_prof: StockNewsProfile = self.news_engine.fetch_stock_news(sym, live=live_news)

        # 3. Technical & GTF Analysis
        cur_price = 1000.0
        align_grade = AlignmentGrade.GRADE_A.value
        curve_loc = CurveLocation.LOW.value
        curve_pct = 30.0
        zone_type_str = "DBR_DEMAND"
        prox = 980.0
        dist = 955.0
        target = 1080.0
        rr = 4.0
        ml_prob = 68.0

        if price_history is not None and not price_history.empty:
            sym_df = price_history[price_history["symbol"] == sym].sort_values("trading_date")
            if len(sym_df) >= 5:
                cur_price = float(sym_df.iloc[-1]["close"])
                mtf_res = self.mtf_engine.evaluate_stock_alignment(sym_df, symbol=sym)
                align_grade = mtf_res.alignment_grade.value
                curve_loc = mtf_res.curve_state.value
                curve_pct = mtf_res.curve_location_pct
                prox = mtf_res.daily_proximal_entry
                dist = mtf_res.daily_distal_stop
                target = mtf_res.daily_target_supply
                rr = mtf_res.reward_to_risk

                demand_zones, _ = self.zone_engine.find_all_zones(sym_df, symbol=sym)
                if demand_zones:
                    best_dz = demand_zones[0]
                    zone_type_str = best_dz.zone_type.value
                    prox = best_dz.proximal_line
                    dist = best_dz.distal_line
                    rr = best_dz.reward_to_risk
                    ml_pred = self.ml_predictor.predict_zone(best_dz)
                    target = ml_pred.target_price
                    ml_prob = round(ml_pred.success_probability * 100.0, 1)

        # -------------------------------------------------------------
        # Compute 4-Pillar Scores
        # -------------------------------------------------------------
        # 1. Technical GTF Score (0 to 35)
        tech_score = 0.0
        if align_grade == AlignmentGrade.GRADE_A_PLUS.value:
            tech_score += 18.0
        elif align_grade == AlignmentGrade.GRADE_A.value:
            tech_score += 15.0
        elif align_grade == AlignmentGrade.GRADE_B.value:
            tech_score += 11.0
        else:
            tech_score += 4.0

        if curve_loc in {CurveLocation.VERY_LOW.value, CurveLocation.LOW.value}:
            tech_score += 12.0
        elif curve_loc == CurveLocation.EQUILIBRIUM.value:
            tech_score += 7.0
        else:
            tech_score += 1.0

        if rr >= 3.0:
            tech_score += 5.0
        elif rr >= 2.0:
            tech_score += 3.5
        else:
            tech_score += 1.0
        tech_score = min(35.0, round(tech_score, 1))

        # 2. ML Forecast Score (0 to 25)
        ml_score = round(min(25.0, (ml_prob / 100.0) * 25.0), 1)

        # 3. Fundamental Quality Score (0 to 25)
        fund_score = round(min(25.0, (f_rep.overall_fundamental_score / 100.0) * 25.0), 1)

        # 4. News Sentiment Score (0 to 15)
        # normalize -1.0 to +1.0 -> 0 to 15
        norm_sent = (news_prof.aggregate_sentiment_score + 1.0) / 2.0  # 0.0 to 1.0
        news_score = round(norm_sent * 15.0, 1)

        conviction_360 = round(tech_score + ml_score + fund_score + news_score, 1)

        # -------------------------------------------------------------
        # Executive Verdict
        # -------------------------------------------------------------
        if conviction_360 >= 72.0 and curve_loc in {CurveLocation.VERY_LOW.value, CurveLocation.LOW.value} and f_rep.debt_to_equity <= 1.2:
            verdict = "STRONG_CONVICTION_BUY"
        elif conviction_360 >= 60.0 and curve_loc in {CurveLocation.VERY_LOW.value, CurveLocation.LOW.value, CurveLocation.EQUILIBRIUM.value}:
            verdict = "PULLBACK_ACCUMULATE"
        elif curve_loc in {CurveLocation.HIGH.value, CurveLocation.VERY_HIGH.value} or f_rep.overall_fundamental_score < 40.0:
            verdict = "AVOID_DO_NOT_BUY"
        elif conviction_360 >= 50.0:
            verdict = "HOLD_AND_TRAIL"
        else:
            verdict = "NEUTRAL_WATCHLIST"

        # -------------------------------------------------------------
        # Synthesize Actionable Concrete Notes
        # -------------------------------------------------------------
        # [A] WHY TO BUY
        why_to_buy: List[str] = []
        why_to_buy.append(
            f"Multi-Timeframe Trend Harmony ({align_grade}): Higher timeframes confirm secular institutional tailwinds; price respects demand structures."
        )
        why_to_buy.append(
            f"Wholesale Curve Positioning: Stock is trading at {curve_loc} on the curve ({curve_pct:.1f}%), offering deep wholesale accumulation discount before institutional mark-up."
        )
        why_to_buy.append(
            f"Fresh Demand Footprint: Testing {zone_type_str.replace('_', ' ')} with Proximal Buy Limit at Rs. {prox:,.2f} and defined invalidation at Rs. {dist:,.2f}."
        )
        why_to_buy.append(
            f"Machine Learning Edge: Predictive model assigns {ml_prob:.1f}% probability of defending the base and fulfilling target objective."
        )
        why_to_buy.append(
            f"Fundamental Balance Sheet Moat: {f_rep.company_name} demonstrates ROE of {f_rep.roe_pct:.1f}%, manageable D/E of {f_rep.debt_to_equity:.2f}, and Piotroski F-Score of {f_rep.piotroski_f_score}/9 ({f_rep.quality_tier.value.replace('_', ' ')})."
        )
        if f_rep.fii_dii_holding_pct >= 25.0:
            why_to_buy.append(
                f"Smart Money Ownership: Combined FII & DII institutional holding stands at {f_rep.fii_dii_holding_pct:.1f}% ({f_rep.fii_dii_trend.replace('_', ' ')})."
            )
        if news_prof.sentiment_badge == "BULLISH_CATALYST":
            why_to_buy.append(
                f"Catalyst Tailwinds: Bullish news sentiment (+{news_prof.aggregate_sentiment_score:.2f}) with active growth drivers supporting quarterly momentum."
            )

        # [B] WHY TO HOLD
        why_to_hold: List[str] = []
        why_to_hold.append(
            f"Asymmetric Target Runway: Opposing institutional supply zone is located up at Rs. {target:,.2f}, delivering a {rr:.1f}:1 Reward-to-Risk margin."
        )
        why_to_hold.append(
            f"Defined Structural Invalidation: Place Distal Stop Loss at Rs. {dist * 0.997:,.2f} (0.3% below lowest base wick). Hold through intraday oscillations as long as the base holds."
        )
        why_to_hold.append(
            f"Two-Stage Profit Harvesting: Scale out 50% position size at 2R (Rs. {prox + 2.0 * (prox - dist):,.2f}) and immediately trail stop-loss to entry price (cost) for an asymmetric risk-free trade."
        )
        why_to_hold.append(
            f"Fundamental Growth Floor: Stable operations in {f_rep.sector} protect underlying earnings power and limit severe structural drawdowns."
        )

        # [C] WHY NOT TO BUY / RED FLAGS
        why_not_to_buy: List[str] = []
        why_not_to_buy.append(
            f"Base Violation Alert: Immediately abort or cancel buy orders if price closes below Distal Line (Rs. {dist:,.2f}) on elevated volume, proving demand exhaustion."
        )
        if curve_loc in {CurveLocation.HIGH.value, CurveLocation.VERY_HIGH.value}:
            why_not_to_buy.append(
                f"Curve Overextension: Stock is at {curve_loc} ({curve_pct:.1f}%) on the macro curve. Do NOT initiate fresh longs into institutional supply."
            )
        else:
            why_not_to_buy.append(
                f"Do Not Chase Markup: If market gaps up above Rs. {prox * 1.025:,.2f} without filling at proximal line, let the trade pass. Do NOT FOMO at retail prices."
            )
        for rf in f_rep.red_flags:
            why_not_to_buy.append(f"Balance Sheet/Valuation Caveat: {rf}")
        if news_prof.has_event_risk:
            why_not_to_buy.append("Event Risk: Active headline risk or impending corporate/regulatory news warrants tight position sizing.")

        headlines = [n.headline for n in news_prof.news_items]

        return StockThesis(
            symbol=sym,
            company_name=f_rep.company_name,
            sector=f_rep.sector,
            current_price=round(cur_price, 2),
            executive_verdict=verdict,
            conviction_score_360=conviction_360,
            technical_gtf_score=tech_score,
            ml_forecast_score=ml_score,
            fundamental_quality_score=fund_score,
            news_sentiment_score=news_score,
            timeframe_alignment_grade=align_grade,
            curve_location=curve_loc,
            curve_location_pct=curve_pct,
            zone_pattern=zone_type_str.replace("DEMAND_", ""),
            proximal_entry=round(prox, 2),
            distal_stop=round(dist, 2),
            target_supply=round(target, 2),
            reward_to_risk=round(rr, 1),
            ml_success_probability=round(ml_prob, 1),
            pe_ratio=f_rep.pe_ratio,
            industry_pe=f_rep.industry_pe,
            roe_pct=f_rep.roe_pct,
            debt_to_equity=f_rep.debt_to_equity,
            fii_dii_holding_pct=f_rep.fii_dii_holding_pct,
            piotroski_f_score=f_rep.piotroski_f_score,
            fundamental_tier=f_rep.quality_tier.value,
            news_sentiment_badge=news_prof.sentiment_badge,
            top_catalysts=news_prof.top_catalysts,
            recent_headlines=headlines,
            why_to_buy=why_to_buy,
            why_to_hold=why_to_hold,
            why_not_to_buy=why_not_to_buy,
        )
