"""
AI Trading Operating System
Module 7: Unified Intelligence Scanner and Section 9 Scan Output Engine.

Orchestrates:
1. Data availability contract validation.
2. Market-Index intelligence (NIFTY 50, Bank Nifty, S/R zones).
3. Sector intelligence and rotation leaderboard/laggards.
4. Stock-level forecasting with stock-vs-sector relative strength.
5. Opportunity candidate ranking.
6. Independent Risk Gate (Trade Plan generation & explicit rejection auditing).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from ai.hierarchical_engine import (
    HierarchicalDecisionEngine,
    IndexSectorContextScore,
    MarketRegimeClassification,
    RankedCandidate,
    RejectedCandidate,
    StockForecast,
    TradePlan,
)
from analytics.index_intelligence import (
    IndexIntelligenceEngine,
    IndexIntelligenceSnapshot,
    MarketBreadthState,
)
from analytics.sector_intelligence import (
    SectorIntelligenceEngine,
    SectorLeaderboard,
    SectorMetrics,
)
from analytics.support_resistance import (
    SupportResistanceContext,
    SupportResistanceEngine,
)
from data_engine.contracts import (
    DataAvailabilityContract,
    DataContractValidator,
    SectorMappingResolver,
)


@dataclass(frozen=True)
class ScanReport:
    as_of_date: date
    contract: DataAvailabilityContract
    regime: MarketRegimeClassification
    nifty50_snap: IndexIntelligenceSnapshot
    nifty50_sr: SupportResistanceContext
    banknifty_snap: Optional[IndexIntelligenceSnapshot]
    banknifty_sr: Optional[SupportResistanceContext]
    breadth: MarketBreadthState
    leaderboard: SectorLeaderboard
    all_sectors: tuple[SectorMetrics, ...]
    ranked_candidates: tuple[RankedCandidate, ...]
    trade_plans: tuple[TradePlan, ...]
    rejected_candidates: tuple[RejectedCandidate, ...]

    def to_summary_dict(self) -> Dict[str, Any]:
        return {
            "as_of_date": str(self.as_of_date),
            "market_regime": self.regime.regime,
            "regime_confidence": self.regime.confidence_score,
            "regime_uncertainty": self.regime.uncertainty_score,
            "breadth_ad_ratio": self.breadth.ad_ratio,
            "breadth_regime": self.breadth.breadth_regime,
            "total_candidates_screened": len(self.ranked_candidates) + len(self.rejected_candidates),
            "approved_trade_plans": len(self.trade_plans),
            "rejected_candidates": len(self.rejected_candidates),
        }

    def format_section_9_output(self) -> str:
        """
        Formats scan results into the exact 6-part specification mandated by Section 9.
        """
        sep = "=" * 80
        subsep = "-" * 80
        out: List[str] = []

        out.append(sep)
        out.append(f"  AI TRADING OPERATING SYSTEM (AI-TOS) -- QUANTITATIVE SCAN REPORT")
        out.append(f"  As of: {self.as_of_date} | Safe Decision Status: {'SAFE' if self.contract.is_safe_for_decision else 'DEGRADED/STALE'}")
        out.append(sep)

        # ------------------------------------------------------------------
        # Section 9.1: Overall market regime and confidence/uncertainty
        # ------------------------------------------------------------------
        out.append("\n[1] OVERALL MARKET REGIME & CONFIDENCE/UNCERTAINTY STATUS")
        out.append(subsep)
        out.append(f"  Regime State      : {self.regime.regime}")
        out.append(f"  Confidence Score  : {self.regime.confidence_score:.1f}%")
        out.append(f"  Uncertainty Score : {self.regime.uncertainty_score:.1f}%")
        out.append(f"  Sizing Multiplier : {self.regime.regime_multiplier:.2f}x")
        out.append("  Primary Drivers   :")
        for d in self.regime.primary_drivers:
            out.append(f"    * {d}")

        # ------------------------------------------------------------------
        # Section 9.2: NIFTY 50 and Bank Nifty trend, vol, and S/R zones
        # ------------------------------------------------------------------
        out.append("\n[2] NIFTY 50 & BANK NIFTY TREND, VOLATILITY & S/R ZONES")
        out.append(subsep)
        out.append(f"  NIFTY 50 Close    : {self.nifty50_snap.close:,.2f}")
        out.append(f"  NIFTY 50 Trend    : {self.nifty50_snap.trend.trend_label} (20d: {self.nifty50_snap.trend.ret_20d:+.2f}%, RSI: {self.nifty50_snap.trend.rsi14:.1f})")
        out.append(f"  NIFTY 50 Vol      : {self.nifty50_snap.volatility.volatility_regime} (Realised Vol: {self.nifty50_snap.volatility.realised_vol_20d_ann:.1f}%)")
        if self.nifty50_sr.nearest_support:
            s = self.nifty50_sr.nearest_support
            out.append(f"  NIFTY 50 Support  : Zone [{s.lower_band:,.2f} - {s.upper_band:,.2f}] (Dist: {self.nifty50_sr.dist_to_support_pct:.1f}%, Strength: {s.strength_score:.0f}/100)")
        if self.nifty50_sr.nearest_resistance:
            r = self.nifty50_sr.nearest_resistance
            out.append(f"  NIFTY 50 Resist.  : Zone [{r.lower_band:,.2f} - {r.upper_band:,.2f}] (Dist: {self.nifty50_sr.dist_to_resistance_pct:.1f}%, Strength: {r.strength_score:.0f}/100)")

        if self.banknifty_snap:
            out.append(f"  BANK NIFTY Close  : {self.banknifty_snap.close:,.2f}")
            out.append(f"  BANK NIFTY Trend  : {self.banknifty_snap.trend.trend_label} (20d: {self.banknifty_snap.trend.ret_20d:+.2f}%)")
            out.append(f"  Leadership State  : {self.banknifty_snap.confirmation_status}")

        # ------------------------------------------------------------------
        # Section 9.3: Sector leaderboard & laggard list with breadth
        # ------------------------------------------------------------------
        out.append("\n[3] SECTOR LEADERBOARD & LAGGARDS (ROTATION & BREADTH CONTEXT)")
        out.append(subsep)
        out.append(f"  {'Rank':<5} {'Sector':<30} {'Status':<12} {'20d RS':<10} {'Adv%':<8} {'Quality':<14} {'Ceiling':<8}")
        for s in self.all_sectors:
            out.append(
                f"  #{s.momentum_rank:<4} {s.sector_name[:28]:<30} {s.rotation_status:<12} {s.relative_strength_20d:+6.2f}%   {s.breadth_pct_advancing:5.1f}%   {s.participation_quality:<14} {s.max_exposure_pct:.0f}%"
            )

        # ------------------------------------------------------------------
        # Section 9.4 & 9.5: Approved Candidates, Sector Strength & Trade Plans
        # ------------------------------------------------------------------
        out.append("\n[4 & 5] NIFTY 500 CANDIDATES & INDEPENDENT RISK-GATED TRADE PLANS")
        out.append(subsep)
        if not self.trade_plans:
            out.append("  No candidates approved by Risk Gate under current market regime and liquidity constraints.")
        else:
            cand_map = {c.symbol: c for c in self.ranked_candidates}
            for plan in self.trade_plans:
                cand = cand_map.get(plan.symbol)
                fc = cand.forecast if cand else None
                sec_str = f"{fc.stock_vs_sector_strength:+.1f}% vs {fc.sector_name}" if fc else "N/A"
                out.append(f"\n  Candidate: {plan.symbol} | Action: {plan.action} | Outcome: {plan.risk_gate_outcome}")
                out.append(f"    Sector Strength : {sec_str}")
                out.append(f"    Horizon/Uncert  : 20-day horizon | Uncertainty: {fc.uncertainty_pct if fc else 20.0:.1f}%")
                out.append(f"    Trade Execution : Entry @ {plan.entry_trigger:.2f} | Stop: {plan.stop_loss:.2f} | Target: {plan.target_zone:.2f} (R:R {plan.reward_to_risk:.2f})")
                out.append(f"    Position Sizing : {plan.position_size_shares} shares (Value: Rs. {plan.position_value:,.2f} | Risk: Rs. {plan.risk_amount:,.2f})")
                if fc and fc.rationale:
                    out.append(f"    Rationale       : {'; '.join(fc.rationale)}")

        # ------------------------------------------------------------------
        # Section 9.6: Rejected candidates and explicit reasons
        # ------------------------------------------------------------------
        out.append("\n[6] REJECTED CANDIDATES & EXPLICIT AUDIT REASONS")
        out.append(subsep)
        if not self.rejected_candidates:
            out.append("  No rejected candidates.")
        else:
            out.append(f"  Total Excluded Candidates: {len(self.rejected_candidates)}")
            # Show top rejections
            for r in self.rejected_candidates[:12]:
                out.append(f"  * {r.symbol:<12} [{r.rejection_category}]: {r.reason}")
            if len(self.rejected_candidates) > 12:
                out.append(f"    ... and {len(self.rejected_candidates) - 12} additional excluded instruments.")

        out.append(sep)
        out.append("  RELIABILITY GUARDRAILS (Section 10): Signals are probabilistic decision inputs;")
        out.append("  no outcome is guaranteed. Risk must be strictly controlled at portfolio level.")
        out.append(sep)

        return "\n".join(out)


class Scanner:
    """
    Enterprise quantitative scanner implementing Sections 1 through 10.
    """

    def __init__(
        self,
        capital: float = 1_000_000.0,
        risk_per_trade_pct: float = 1.0,
        max_positions: int = 20,
        max_sector_exposure_pct: float = 20.0,
        min_candidate_score: float = 65.0,
    ) -> None:
        self.decision_engine = HierarchicalDecisionEngine(
            capital=capital,
            risk_per_trade_pct=risk_per_trade_pct,
            max_positions=max_positions,
            max_sector_exposure_pct=max_sector_exposure_pct,
            min_candidate_score=min_candidate_score,
        )

    def scan(
        self,
        data: pd.DataFrame,
        top_n: int = 50,
        reference_date: Optional[date] = None,
    ) -> ScanReport:
        """
        Executes end-to-end multi-layer quantitative scan over input market data.
        """
        # Step 1: Validate data contract
        contract = DataContractValidator.create_contract(data, reference_date=reference_date)

        if data.empty or "symbol" not in data.columns:
            empty_snap = IndexIntelligenceSnapshot(
                "NIFTY 50", date.today(), 0.0,
                self.decision_engine.index_engine.calculate_trend_state(pd.DataFrame()),
                self.decision_engine.index_engine.calculate_volatility_state(pd.DataFrame()),
            )
            empty_sr = SupportResistanceContext(0.0, None, None, 999.0, 999.0, False, False)
            empty_breadth = MarketBreadthState(0, 0, 0, 1.0, 50.0, 50.0, 50.0, 0, 0, "NEUTRAL")
            empty_regime = MarketRegimeClassification("RANGE_BOUND", 50.0, 50.0, ("Empty data",), 0.5)
            empty_lb = SectorLeaderboard((), (), (), ())
            return ScanReport(
                as_of_date=date.today(),
                contract=contract,
                regime=empty_regime,
                nifty50_snap=empty_snap,
                nifty50_sr=empty_sr,
                banknifty_snap=None,
                banknifty_sr=None,
                breadth=empty_breadth,
                leaderboard=empty_lb,
                all_sectors=(),
                ranked_candidates=(),
                trade_plans=(),
                rejected_candidates=(),
            )

        as_of_date = contract.as_of_date

        # Step 2: Extract or Synthesize Index Data (NIFTY 50 & Bank Nifty)
        nifty_df = data[data["symbol"].isin({"NIFTY 50", "^NSEI", "NIFTY"})]
        if nifty_df.empty or len(nifty_df) < 5:
            # Synthesize composite Nifty 50 from constituents if index ticker not in feed
            nifty_df = (
                data.groupby("trading_date", as_index=False)
                .agg({
                    "open": "mean",
                    "high": "max",
                    "low": "min",
                    "close": "mean",
                    "volume": "sum",
                })
                .sort_values("trading_date")
            )

        nifty_trend = self.decision_engine.index_engine.calculate_trend_state(nifty_df)
        nifty_vol = self.decision_engine.index_engine.calculate_volatility_state(nifty_df)
        nifty_close = float(nifty_df["close"].iloc[-1])
        nifty_snap = IndexIntelligenceSnapshot(
            index_code="NIFTY 50",
            trading_date=as_of_date,
            close=nifty_close,
            trend=nifty_trend,
            volatility=nifty_vol,
        )
        nifty_sr = self.decision_engine.sr_engine.identify_zones(nifty_df)

        # Bank Nifty
        bank_df = data[data["symbol"].isin({"NIFTY BANK", "BANKNIFTY"})]
        bank_snap = None
        bank_sr = None
        if not bank_df.empty and len(bank_df) >= 5:
            b_trend = self.decision_engine.index_engine.calculate_trend_state(bank_df)
            b_vol = self.decision_engine.index_engine.calculate_volatility_state(bank_df)
            b_close = float(bank_df["close"].iloc[-1])
            bank_snap = IndexIntelligenceSnapshot(
                index_code="NIFTY BANK",
                trading_date=as_of_date,
                close=b_close,
                trend=b_trend,
                volatility=b_vol,
                confirmation_status=self.decision_engine.index_engine.evaluate_intermarket_leadership(nifty_snap, bank_snap or nifty_snap),
            )
            bank_sr = self.decision_engine.sr_engine.identify_zones(bank_df)

        # Step 3: Compute Market Breadth
        breadth = self.decision_engine.index_engine.calculate_market_breadth(data)

        # Step 4: Layer A Market Regime
        regime = self.decision_engine.classify_market_regime(nifty_snap, breadth)

        # Step 5: Layer B Sector Intelligence
        sector_metrics = self.decision_engine.sector_engine.calculate_sector_metrics(
            universe_df=data,
            benchmark_ret_20d=nifty_trend.ret_20d,
            benchmark_ret_60d=nifty_trend.ret_50d,
        )
        leaderboard = self.decision_engine.sector_engine.build_leaderboard(sector_metrics)
        sec_lookup = {s.sector_id: s for s in sector_metrics}

        context_score = self.decision_engine.evaluate_context(
            nifty_snap=nifty_snap,
            bank_snap=bank_snap or nifty_snap,
            sectors=sector_metrics,
            breadth=breadth,
        )

        # Step 6: Layer C Stock-level Forecasting & S/R Zones across Constituents
        scored_candidates: List[Tuple[RankedCandidate, SupportResistanceContext, pd.DataFrame]] = []
        rejected_candidates: List[RejectedCandidate] = []

        # Group data by stock symbol
        for symbol, stock_group in data.groupby("symbol", sort=False):
            sym = str(symbol).strip().upper()
            if sym in {"NIFTY 50", "NIFTY BANK", "^NSEI", "NIFTY"}:
                continue

            # Check history requirement
            if len(stock_group) < 20:
                rejected_candidates.append(
                    RejectedCandidate(
                        symbol=sym,
                        rejection_category="STALE_DATA",
                        reason=f"Insufficient historical bars ({len(stock_group)} bars < 20 required)",
                        raw_score=0.0,
                    )
                )
                continue

            try:
                forecast, sr_ctx = self.decision_engine.forecast_stock(
                    symbol=sym,
                    stock_df=stock_group,
                    context=context_score,
                    sector_lookup=sec_lookup,
                )

                # Composite score blending forecast quality, macro score, and uncertainty
                macro_boost = (context_score.macro_score - 50.0) * 0.2
                uncert_discount = forecast.uncertainty_pct * 0.25
                comp_score = max(0.0, min(100.0, forecast.predicted_opportunity_score + macro_boost - uncert_discount))

                latest_row = stock_group.iloc[-1]
                close_p = float(latest_row["close"])
                turnover_lacs = float(latest_row.get("turnover", 100.0))

                cand = RankedCandidate(
                    rank=0,
                    symbol=sym,
                    forecast=forecast,
                    composite_score=round(comp_score, 1),
                    close_price=close_p,
                    liquidity_score=turnover_lacs,
                    is_qualified=comp_score >= self.decision_engine.min_candidate_score,
                )
                scored_candidates.append((cand, sr_ctx, stock_group))

            except Exception as ex:
                rejected_candidates.append(
                    RejectedCandidate(
                        symbol=sym,
                        rejection_category="WEAK_EVIDENCE",
                        reason=f"Calculation exception: {str(ex)}",
                        raw_score=0.0,
                    )
                )

        # Step 7: Layer D Candidate Ranking
        scored_candidates.sort(key=lambda item: item[0].composite_score, reverse=True)
        ranked_candidates: List[RankedCandidate] = []
        for rank_idx, (cand, sr_ctx, group) in enumerate(scored_candidates[:top_n]):
            ranked_cand = RankedCandidate(
                rank=rank_idx + 1,
                symbol=cand.symbol,
                forecast=cand.forecast,
                composite_score=cand.composite_score,
                close_price=cand.close_price,
                liquidity_score=cand.liquidity_score,
                is_qualified=cand.is_qualified,
            )
            ranked_candidates.append(ranked_cand)

        # Step 8: Layer E Risk Gate & Trade Plan Generation
        approved_trade_plans: List[TradePlan] = []
        current_sector_allocs: Dict[str, float] = {}

        for cand in ranked_candidates:
            # Find matching sr_ctx and stock_df
            match = next((item for item in scored_candidates if item[0].symbol == cand.symbol), None)
            if not match:
                continue
            _, sr_ctx, stock_df = match

            trade_plan, rejection = self.decision_engine.evaluate_risk_gate_and_plan(
                candidate=cand,
                sr_ctx=sr_ctx,
                stock_df=stock_df,
                regime=regime,
                current_sector_allocations=current_sector_allocs,
                existing_position_count=len(approved_trade_plans),
            )

            if trade_plan:
                approved_trade_plans.append(trade_plan)
                sec_id = cand.forecast.sector_id
                plan_weight = (trade_plan.position_value / self.decision_engine.capital) * 100.0
                current_sector_allocs[sec_id] = current_sector_allocs.get(sec_id, 0.0) + plan_weight
            elif rejection:
                rejected_candidates.append(rejection)

        return ScanReport(
            as_of_date=as_of_date,
            contract=contract,
            regime=regime,
            nifty50_snap=nifty_snap,
            nifty50_sr=nifty_sr,
            banknifty_snap=bank_snap,
            banknifty_sr=bank_sr,
            breadth=breadth,
            leaderboard=leaderboard,
            all_sectors=tuple(sector_metrics),
            ranked_candidates=tuple(ranked_candidates),
            trade_plans=tuple(approved_trade_plans),
            rejected_candidates=tuple(rejected_candidates),
        )
