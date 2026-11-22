"""
AI Trading Operating System
Module: analytics/fundamental_engine.py

Institutional Fundamental Analysis Engine:
- Evaluates corporate valuation, balance sheet health, profitability, and institutional flows.
- Computes four-pillar quantitative score (0-100):
  * Valuation Attractiveness (25 pts)
  * Profitability & Capital Efficiency (25 pts)
  * Solvency & Balance Sheet Health (25 pts)
  * Growth Momentum & Institutional Inflows (25 pts)
- Categorizes stocks into institutional quality tiers.
- Emits specific audit highlights and financial red flags.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from data_engine.fundamental_data import CompanyFundamentals, FundamentalDataProvider


class FundamentalQualityTier(str, Enum):
    INSTITUTIONAL_COMPOUNDER = "INSTITUTIONAL_COMPOUNDER"
    HIGH_GROWTH_MOMENTUM = "HIGH_GROWTH_MOMENTUM"
    DEEP_VALUE_BARGAIN = "DEEP_VALUE_BARGAIN"
    CYCLICAL_TURNAROUND = "CYCLICAL_TURNAROUND"
    SPECULATIVE_RISK = "SPECULATIVE_RISK"
    FINANCIALLY_DISTRESSED = "FINANCIALLY_DISTRESSED"


@dataclass
class FundamentalAnalysisReport:
    symbol: str
    company_name: str
    sector: str
    market_cap_cr: float
    market_cap_category: str
    overall_fundamental_score: float  # 0 to 100
    quality_tier: FundamentalQualityTier
    # Pillar breakdown
    valuation_score: float  # 0 to 25
    profitability_score: float  # 0 to 25
    solvency_score: float  # 0 to 25
    growth_institutional_score: float  # 0 to 25
    # Ratios
    pe_ratio: float
    industry_pe: float
    pb_ratio: float
    peg_ratio: float
    roe_pct: float
    roce_pct: float
    debt_to_equity: float
    fii_dii_holding_pct: float
    fii_dii_trend: str
    promoter_pledge_pct: float
    piotroski_f_score: int
    # Qualitative highlights & warnings
    strengths: List[str]
    red_flags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["quality_tier"] = self.quality_tier.value
        return d


class FundamentalAnalysisEngine:
    """
    Evaluates corporate financial health, returns, and valuation metrics
    for candidate stocks identified by technical/GTF scanners.
    """

    def __init__(self, data_provider: Optional[FundamentalDataProvider] = None) -> None:
        self.provider = data_provider or FundamentalDataProvider()

    def analyze_stock(self, symbol: str) -> FundamentalAnalysisReport:
        f = self.provider.get_fundamentals(symbol)

        # -------------------------------------------------------------
        # Pillar 1: Valuation Score (0 to 25)
        # -------------------------------------------------------------
        val_score = 0.0
        # P/E vs Industry P/E
        if f.pe_ratio > 0 and f.industry_pe > 0:
            pe_discount = (f.industry_pe - f.pe_ratio) / f.industry_pe
            if pe_discount >= 0.20:
                val_score += 10.0
            elif pe_discount >= 0.0:
                val_score += 8.0
            elif pe_discount >= -0.25:
                val_score += 6.0
            elif pe_discount >= -0.50:
                val_score += 4.0
            else:
                val_score += 2.0
        else:
            val_score += 4.0

        # PEG Ratio
        if 0 < f.peg_ratio <= 1.0:
            val_score += 8.0
        elif f.peg_ratio <= 1.5:
            val_score += 6.0
        elif f.peg_ratio <= 2.2:
            val_score += 4.0
        else:
            val_score += 1.0

        # P/B and EV/EBITDA
        if f.pb_ratio <= 3.0:
            val_score += 4.0
        elif f.pb_ratio <= 7.0:
            val_score += 3.0
        else:
            val_score += 1.0

        if f.ev_to_ebitda <= 15.0:
            val_score += 3.0
        elif f.ev_to_ebitda <= 25.0:
            val_score += 2.0
        else:
            val_score += 1.0

        val_score = min(25.0, round(val_score, 1))

        # -------------------------------------------------------------
        # Pillar 2: Profitability & Capital Efficiency (0 to 25)
        # -------------------------------------------------------------
        prof_score = 0.0
        # ROE
        if f.roe_pct >= 25.0:
            prof_score += 10.0
        elif f.roe_pct >= 18.0:
            prof_score += 8.0
        elif f.roe_pct >= 12.0:
            prof_score += 5.0
        elif f.roe_pct >= 8.0:
            prof_score += 3.0
        else:
            prof_score += 1.0

        # ROCE
        if f.roce_pct >= 25.0:
            prof_score += 8.0
        elif f.roce_pct >= 18.0:
            prof_score += 6.0
        elif f.roce_pct >= 12.0:
            prof_score += 4.0
        else:
            prof_score += 2.0

        # Free Cash Flow
        if f.free_cash_flow_cr > 10000.0:
            prof_score += 7.0
        elif f.free_cash_flow_cr > 1000.0:
            prof_score += 5.0
        elif f.free_cash_flow_cr > 0.0:
            prof_score += 3.0
        else:
            prof_score += 1.0

        prof_score = min(25.0, round(prof_score, 1))

        # -------------------------------------------------------------
        # Pillar 3: Solvency & Balance Sheet Health (0 to 25)
        # -------------------------------------------------------------
        solv_score = 0.0
        # Debt to Equity (Industry-Specific Thresholds)
        is_banking_fin = (
            "BANK" in f.sector.upper() or "FINANC" in f.sector.upper() or "NBFC" in f.sector.upper() or
            symbol in {"HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK", "BAJFINANCE", "BAJAJFINSV"}
        )
        is_capital_intensive = (
            any(k in f.sector.upper() for k in ["AUTO", "METAL", "STEEL", "ENERGY", "INFRA", "POWER", "CEMENT"]) or
            symbol in {"TATAMOTORS", "TATASTEEL", "NTPC", "POWERGRID", "LT", "JSWSTEEL", "HINDALCO"}
        )
        if is_banking_fin:
            if f.debt_to_equity <= 2.0:
                solv_score += 10.0
            elif f.debt_to_equity <= 5.0:
                solv_score += 8.0
            elif f.debt_to_equity <= 7.0:
                solv_score += 5.0
            elif f.debt_to_equity <= 9.0:
                solv_score += 2.0
            else:
                solv_score += 0.0
        elif is_capital_intensive:
            if f.debt_to_equity <= 0.40:
                solv_score += 10.0
            elif f.debt_to_equity <= 1.0:
                solv_score += 8.0
            elif f.debt_to_equity <= 1.5:
                solv_score += 5.0
            elif f.debt_to_equity <= 2.2:
                solv_score += 2.0
            else:
                solv_score += 0.0
        else:
            if f.debt_to_equity <= 0.15:
                solv_score += 10.0
            elif f.debt_to_equity <= 0.50:
                solv_score += 8.0
            elif f.debt_to_equity <= 1.0:
                solv_score += 5.0
            elif f.debt_to_equity <= 1.8:
                solv_score += 2.0
            else:
                solv_score += 0.0

        # Interest Coverage
        if f.interest_coverage >= 15.0:
            solv_score += 5.0
        elif f.interest_coverage >= 5.0:
            solv_score += 4.0
        elif f.interest_coverage >= 2.5:
            solv_score += 2.5
        else:
            solv_score += 0.5

        # Piotroski F-Score (0 to 9)
        if f.piotroski_f_score >= 8:
            solv_score += 6.0
        elif f.piotroski_f_score >= 6:
            solv_score += 4.5
        elif f.piotroski_f_score >= 4:
            solv_score += 2.5
        else:
            solv_score += 0.0

        # Promoter Pledge
        if f.promoter_pledge_pct == 0.0:
            solv_score += 4.0
        elif f.promoter_pledge_pct <= 2.0:
            solv_score += 2.5
        elif f.promoter_pledge_pct <= 10.0:
            solv_score += 1.0
        else:
            solv_score += 0.0

        solv_score = min(25.0, round(solv_score, 1))

        # -------------------------------------------------------------
        # Pillar 4: Growth Momentum & Institutional Inflows (0 to 25)
        # -------------------------------------------------------------
        growth_score = 0.0
        # 3Y Sales & Profit Growth
        avg_growth = (f.sales_growth_3y_pct + f.profit_growth_3y_pct) / 2.0
        if avg_growth >= 25.0:
            growth_score += 8.0
        elif avg_growth >= 15.0:
            growth_score += 6.5
        elif avg_growth >= 10.0:
            growth_score += 4.5
        elif avg_growth >= 5.0:
            growth_score += 2.5
        else:
            growth_score += 1.0

        # Quarterly EPS Growth
        if f.quarterly_eps_growth_yoy >= 20.0:
            growth_score += 7.0
        elif f.quarterly_eps_growth_yoy >= 12.0:
            growth_score += 5.5
        elif f.quarterly_eps_growth_yoy >= 5.0:
            growth_score += 3.5
        else:
            growth_score += 1.0

        # Institutional Ownership Level & Trend
        tot_inst = f.fii_holding_pct + f.dii_holding_pct
        if tot_inst >= 40.0:
            growth_score += 5.0
        elif tot_inst >= 20.0:
            growth_score += 3.5
        else:
            growth_score += 2.0

        if f.institutional_trend == "STRONG_ACCUMULATION":
            growth_score += 5.0
        elif f.institutional_trend == "MILD_ACCUMULATION":
            growth_score += 3.5
        elif f.institutional_trend == "NEUTRAL":
            growth_score += 2.0
        else:
            growth_score += 0.0

        growth_score = min(25.0, round(growth_score, 1))

        # Total Fundamental Score (0 to 100)
        total_score = round(val_score + prof_score + solv_score + growth_score, 1)

        # Determine Tier with industry-specific leverage tolerance
        max_comp_de = 6.0 if is_banking_fin else (1.8 if is_capital_intensive else 0.8)
        max_distress_de = 10.0 if is_banking_fin else (2.5 if is_capital_intensive else 1.8)
        if total_score >= 80.0 and f.roe_pct >= 14.0 and f.debt_to_equity <= max_comp_de:
            tier = FundamentalQualityTier.INSTITUTIONAL_COMPOUNDER
        elif f.sales_growth_3y_pct >= 18.0 and f.profit_growth_3y_pct >= 18.0 and total_score >= 70.0:
            tier = FundamentalQualityTier.HIGH_GROWTH_MOMENTUM
        elif f.pe_ratio <= f.industry_pe * 0.90 and total_score >= 65.0:
            tier = FundamentalQualityTier.DEEP_VALUE_BARGAIN
        elif f.profit_growth_3y_pct >= 20.0 and f.debt_to_equity <= (8.0 if is_banking_fin else 2.0):
            tier = FundamentalQualityTier.CYCLICAL_TURNAROUND
        elif total_score < 45.0 or f.debt_to_equity > max_distress_de or f.promoter_pledge_pct > 15.0:
            tier = FundamentalQualityTier.FINANCIALLY_DISTRESSED
        else:
            tier = FundamentalQualityTier.SPECULATIVE_RISK

        # Qualitative Strengths
        strengths: List[str] = []
        if f.roe_pct >= 18.0:
            strengths.append(f"Outstanding return on equity: ROE of {f.roe_pct:.1f}%")
        if is_banking_fin:
            if f.debt_to_equity <= 4.0:
                strengths.append(f"Highly conservative banking capital structure with D/E of {f.debt_to_equity:.2f}x")
        elif f.debt_to_equity <= 0.2:
            strengths.append(f"Virtually debt-free balance sheet with D/E of {f.debt_to_equity:.2f}")
        elif f.debt_to_equity <= 0.8:
            strengths.append(f"Conservative leverage profile (D/E: {f.debt_to_equity:.2f})")

        # Board-governed / institutional ownership recognition
        if f.promoter_holding_pct == 0.0 or f.total_institutional_holding_pct >= 50.0:
            strengths.append(f"Board-governed premier compounder backed by {f.total_institutional_holding_pct:.1f}% institutional ownership (FII+DII)")

        if f.piotroski_f_score >= 8:
            strengths.append(f"Pristine operational financial health (Piotroski F-Score: {f.piotroski_f_score}/9)")
        if f.institutional_trend in {"STRONG_ACCUMULATION", "MILD_ACCUMULATION"}:
            strengths.append(f"Institutional accumulation: FII+DII hold {f.total_institutional_holding_pct:.1f}% with net quarterly inflows")
        if f.peg_ratio > 0 and f.peg_ratio <= 1.2:
            strengths.append(f"Attractive valuation relative to growth (PEG: {f.peg_ratio:.2f})")
        if f.pe_ratio < f.industry_pe:
            strengths.append(f"Trading at discount to industry P/E ({f.pe_ratio:.1f} vs {f.industry_pe:.1f})")

        # Qualitative Red Flags
        red_flags: List[str] = []
        if (not is_banking_fin and f.debt_to_equity > 1.8) or (is_banking_fin and f.debt_to_equity > 8.5):
            red_flags.append(f"Elevated balance sheet leverage: D/E ratio of {f.debt_to_equity:.2f}")
        if f.promoter_pledge_pct > 5.0:
            red_flags.append(f"Promoter pledge risk: {f.promoter_pledge_pct:.1f}% of promoter stake is pledged")
        if f.pe_ratio > 60.0 and f.peg_ratio > 2.5:
            red_flags.append(f"Rich valuation multiple (P/E: {f.pe_ratio:.1f}, PEG: {f.peg_ratio:.2f}) with limited margin of safety")
        if f.institutional_trend == "DISTRIBUTION":
            red_flags.append("Net institutional selling observed in recent quarterly filings")
        if f.quarterly_eps_growth_yoy < 0.0:
            red_flags.append(f"Contracting quarterly profitability (EPS YoY: {f.quarterly_eps_growth_yoy:+.1f}%)")
        if f.interest_coverage < 2.5 and not is_banking_fin and f.debt_to_equity > 1.0:
            red_flags.append(f"Tight debt servicing coverage (Interest Coverage: {f.interest_coverage:.1f}x)")

        if not strengths:
            strengths.append("Standard financial metrics aligned with broad industry averages.")
        if not red_flags:
            red_flags.append("No immediate structural balance sheet red flags or alarming pledges detected.")

        return FundamentalAnalysisReport(
            symbol=symbol,
            company_name=f.company_name,
            sector=f.sector,
            market_cap_cr=f.market_cap_cr,
            market_cap_category=f.market_cap_category,
            overall_fundamental_score=total_score,
            quality_tier=tier,
            valuation_score=val_score,
            profitability_score=prof_score,
            solvency_score=solv_score,
            growth_institutional_score=growth_score,
            pe_ratio=f.pe_ratio,
            industry_pe=f.industry_pe,
            pb_ratio=f.pb_ratio,
            peg_ratio=f.peg_ratio,
            roe_pct=f.roe_pct,
            roce_pct=f.roce_pct,
            debt_to_equity=f.debt_to_equity,
            fii_dii_holding_pct=f.total_institutional_holding_pct,
            fii_dii_trend=f.institutional_trend,
            promoter_pledge_pct=f.promoter_pledge_pct,
            piotroski_f_score=f.piotroski_f_score,
            strengths=strengths,
            red_flags=red_flags,
        )
