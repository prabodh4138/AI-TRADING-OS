"""
AI Trading Operating System
Module 5: Hierarchical Forecasting and Decision Engine (Section 4 & 9)

Implements the multi-layer hierarchical decision flow:
- Layer A — Market regime: classify broad-market conditions with confidence & uncertainty.
- Layer B — Index and sector context: score NIFTY 50, Bank Nifty, sectors, and breadth.
- Layer C — Stock-level forecasting: point-in-time technicals + market/sector context.
- Layer D — Candidate ranking: ranked by validated quality, liquidity, net opportunity, uncertainty.
- Layer E — Risk gate & trade plan: independently approve, resize, reject, or defer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from analytics.index_intelligence import (
    IndexIntelligenceEngine,
    IndexIntelligenceSnapshot,
    MarketBreadthState,
)
from analytics.sector_intelligence import (
    SectorIntelligenceEngine,
    SectorMetrics,
)
from analytics.support_resistance import (
    PriceZone,
    SupportResistanceContext,
    SupportResistanceEngine,
)
from data_engine.contracts import DataAvailabilityContract, SectorMappingResolver
from indicator.calculator import IndicatorCalculator
from ai.ml_models import MLMarketRegimeClassifier, MLStockOpportunityForecaster


@dataclass(frozen=True, slots=True)
class MarketRegimeClassification:
    regime: str  # "TRENDING_BULLISH", "TRENDING_BEARISH", "RANGE_BOUND", "HIGH_VOLATILITY", "STRESSED"
    confidence_score: float  # 0.0 to 100.0
    uncertainty_score: float  # 0.0 to 100.0
    primary_drivers: tuple[str, ...]
    regime_multiplier: float  # Sizing multiplier: 1.0 down to 0.0


@dataclass(frozen=True, slots=True)
class IndexSectorContextScore:
    nifty50_trend: str
    banknifty_trend: str
    intermarket_confirmation: str
    leading_sectors: tuple[str, ...]
    lagging_sectors: tuple[str, ...]
    breadth_regime: str
    macro_score: float  # 0.0 to 100.0


@dataclass(frozen=True, slots=True)
class StockForecast:
    symbol: str
    trading_date: date
    sector_id: str
    sector_name: str
    stock_vs_sector_strength: float
    forecast_horizon_days: int
    predicted_opportunity_score: float  # 0.0 to 100.0
    forecast_direction: str  # "BULLISH", "NEUTRAL", "BEARISH"
    uncertainty_pct: float
    rationale: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RankedCandidate:
    rank: int
    symbol: str
    forecast: StockForecast
    composite_score: float
    close_price: float
    liquidity_score: float
    is_qualified: bool


@dataclass(frozen=True, slots=True)
class TradePlan:
    symbol: str
    trading_date: date
    action: str  # "BUY", "DEFER", "REJECT"
    entry_trigger: float
    stop_loss: float
    target_zone: float
    reward_to_risk: float
    position_size_shares: int
    position_value: float
    risk_amount: float
    risk_gate_outcome: str  # "APPROVED", "RESIZED", "REJECTED_RISK", "REJECTED_SECTOR_LIMIT", "REJECTED_LIQUIDITY"
    gate_reason: str


@dataclass(frozen=True, slots=True)
class RejectedCandidate:
    symbol: str
    rejection_category: str  # "STALE_DATA", "WEAK_EVIDENCE", "POOR_LIQUIDITY", "CORRELATED_EXPOSURE", "BEARISH_REGIME"
    reason: str
    raw_score: float


class HierarchicalDecisionEngine:
    """
    Executes the 5-layer hierarchical forecasting and decision flow.
    """

    def __init__(
        self,
        capital: float = 1_000_000.0,
        risk_per_trade_pct: float = 1.0,
        max_positions: int = 20,
        max_sector_exposure_pct: float = 20.0,
        min_candidate_score: float = 65.0,
        min_reward_to_risk: float = 1.8,
        min_turnover_lacs: float = 25.0,
    ) -> None:
        self.capital = capital
        self.risk_per_trade_pct = risk_per_trade_pct
        self.max_positions = max_positions
        self.max_sector_exposure_pct = max_sector_exposure_pct
        self.min_candidate_score = min_candidate_score
        self.min_reward_to_risk = min_reward_to_risk
        self.min_turnover_lacs = min_turnover_lacs

        self.resolver = SectorMappingResolver()
        self.index_engine = IndexIntelligenceEngine()
        self.sector_engine = SectorIntelligenceEngine(self.resolver)
        self.sr_engine = SupportResistanceEngine()
        self.calculator = IndicatorCalculator()
        self.ml_regime = MLMarketRegimeClassifier()
        self.ml_stock = MLStockOpportunityForecaster()

    def classify_market_regime(
        self,
        nifty_snapshot: IndexIntelligenceSnapshot,
        breadth: MarketBreadthState,
    ) -> MarketRegimeClassification:
        """
        Layer A — Market Regime Classifier.
        Combines broad index trend, volatility regime, and market breadth.
        """
        drivers: List[str] = []
        conf = 70.0
        uncert = 30.0

        nifty_trend = nifty_snapshot.trend.trend_label
        vol_regime = nifty_snapshot.volatility.volatility_regime
        ad_ratio = breadth.ad_ratio

        # Feature extraction for ML Regime Classifier
        ml_features = {
            "ret_5d": nifty_snapshot.trend.ret_5d,
            "ret_20d": nifty_snapshot.trend.ret_20d,
            "ret_50d": nifty_snapshot.trend.ret_50d,
            "realised_vol_20d": nifty_snapshot.volatility.realised_vol_20d_ann,
            "atr_ratio": nifty_snapshot.volatility.atr_ratio,
            "rsi14": nifty_snapshot.trend.rsi14,
            "ad_ratio": breadth.ad_ratio,
            "pct_above_20dma": breadth.pct_above_20dma,
        }
        ml_pred = self.ml_regime.predict_regime(ml_features)

        drivers.append(f"NIFTY 50 Trend is {nifty_trend} (RSI: {nifty_snapshot.trend.rsi14})")
        drivers.append(f"Volatility regime is {vol_regime} (Realized: {nifty_snapshot.volatility.realised_vol_20d_ann}%)")
        drivers.append(f"Market Breadth AD Ratio: {ad_ratio:.2f} ({breadth.breadth_regime})")
        drivers.append(f"ML Classifier Prediction: {ml_pred.predicted_regime} ({ml_pred.confidence:.1f}% confidence, {ml_pred.uncertainty:.1f}% entropy uncertainty)")

        if vol_regime == "EXTREME_STRESS":
            regime = "STRESSED"
            conf = 85.0
            uncert = 55.0
            mult = 0.0
        elif "BEARISH" in nifty_trend and ad_ratio < 0.8:
            regime = "TRENDING_BEARISH"
            conf = 80.0
            uncert = 25.0
            mult = 0.0
        elif "BULLISH" in nifty_trend and ad_ratio >= 1.2:
            regime = "TRENDING_BULLISH"
            conf = 82.0
            uncert = 20.0
            mult = 1.0
        elif vol_regime == "HIGH":
            regime = "HIGH_VOLATILITY"
            conf = 75.0
            uncert = 40.0
            mult = 0.4
        else:
            regime = ml_pred.predicted_regime if ml_pred.predicted_regime != "STRESSED" else "RANGE_BOUND"
            conf = round((conf * 0.5) + (ml_pred.confidence * 0.5), 1)
            uncert = round((uncert * 0.5) + (ml_pred.uncertainty * 0.5), 1)
            mult = 0.6 if regime == "RANGE_BOUND" else 1.0 if regime == "TRENDING_BULLISH" else 0.4

        return MarketRegimeClassification(
            regime=regime,
            confidence_score=conf,
            uncertainty_score=uncert,
            primary_drivers=tuple(drivers),
            regime_multiplier=mult,
        )

    def evaluate_context(
        self,
        nifty_snap: IndexIntelligenceSnapshot,
        bank_snap: IndexIntelligenceSnapshot,
        sectors: List[SectorMetrics],
        breadth: MarketBreadthState,
    ) -> IndexSectorContextScore:
        """
        Layer B — Index and Sector Context.
        """
        intermarket = self.index_engine.evaluate_intermarket_leadership(nifty_snap, bank_snap)
        leaders = tuple(s.sector_name for s in sectors if s.rotation_status == "LEADING")[:3]
        laggards = tuple(s.sector_name for s in sectors if s.rotation_status == "LAGGING")[:3]

        macro = 50.0
        if "BULLISH" in nifty_snap.trend.trend_label:
            macro += 20.0
        elif "BEARISH" in nifty_snap.trend.trend_label:
            macro -= 20.0

        if intermarket == "CONFIRMED_BULLISH":
            macro += 15.0
        elif intermarket == "DIVERGING_BEARISH":
            macro -= 15.0

        if breadth.ad_ratio > 1.3:
            macro += 15.0
        elif breadth.ad_ratio < 0.7:
            macro -= 15.0

        macro = max(0.0, min(100.0, macro))

        return IndexSectorContextScore(
            nifty50_trend=nifty_snap.trend.trend_label,
            banknifty_trend=bank_snap.trend.trend_label,
            intermarket_confirmation=intermarket,
            leading_sectors=leaders,
            lagging_sectors=laggards,
            breadth_regime=breadth.breadth_regime,
            macro_score=round(macro, 1),
        )

    def forecast_stock(
        self,
        symbol: str,
        stock_df: pd.DataFrame,
        context: IndexSectorContextScore,
        sector_lookup: Dict[str, SectorMetrics],
    ) -> Tuple[StockForecast, SupportResistanceContext]:
        """
        Layer C — Stock-level Forecasting using technicals, S/R zones, and sector strength.
        """
        reasons: List[str] = []
        score = 0.0

        # Run indicator calculation
        ind_df = self.calculator.calculate(stock_df)
        last_row = ind_df.iloc[-1]
        c = float(last_row["close"])
        t_date = last_row["trading_date"]

        # 1. Trend & Moving Averages
        if c > last_row.get("ema20", c):
            score += 15.0
            reasons.append("Price above EMA20")
        if last_row.get("ema20", 0) > last_row.get("ema50", float("inf")):
            score += 15.0
            reasons.append("EMA20 > EMA50 bullish structure")
        if last_row.get("supertrend_direction", -1) > 0:
            score += 10.0
            reasons.append("SuperTrend is positive")

        # 2. Momentum & Volume
        rsi = float(last_row.get("rsi14", 50.0))
        if 50.0 <= rsi <= 68.0:
            score += 10.0
            reasons.append(f"RSI({rsi:.1f}) in optimal bullish expansion zone")
        if last_row.get("macd_histogram", 0.0) > 0:
            score += 5.0
            reasons.append("MACD histogram expanding")
        if last_row.get("relative_volume", 0.0) >= 1.0:
            score += 10.0
            reasons.append("Volume confirms price action (rel_vol >= 1.0)")

        # 3. Sector Relative Strength (Layer B Confluence)
        ret_20d = float((c / ind_df["close"].iloc[-20] - 1) * 100) if len(ind_df) >= 20 else 0.0
        stock_sec = self.sector_engine.calculate_stock_vs_sector_strength(
            symbol, stock_ret_20d=ret_20d, sector_metrics_lookup=sector_lookup
        )
        if stock_sec.classification == "SECTOR_OUTPERFORMER":
            score += 20.0
            reasons.append(f"Outperforming sector ({stock_sec.sector_name}) by +{stock_sec.stock_vs_sector_strength:.1f}%")
        elif stock_sec.classification == "IN_LINE":
            score += 10.0
            reasons.append(f"In-line with sector ({stock_sec.sector_name})")
        else:
            reasons.append(f"Underperforming sector ({stock_sec.sector_name}) by {stock_sec.stock_vs_sector_strength:.1f}%")

        # 4. S/R Confluence (Section 5)
        sr_ctx = self.sr_engine.identify_zones(stock_df)
        if sr_ctx.is_breakout_confirmed:
            score += 15.0
            reasons.append("Confirmed breakout above resistance zone net of slippage")
        elif sr_ctx.is_retest_bounce:
            score += 10.0
            reasons.append("Retest bounce from verified support zone")

        # 5. Machine Learning Stock Opportunity Forecast (Section 4 & 6)
        ema20_val = float(last_row.get("ema20", c))
        ema50_val = float(last_row.get("ema50", c))
        ml_features = {
            "price_vs_ema20_pct": ((c - ema20_val) / (ema20_val + 1e-6)) * 100.0,
            "ema20_vs_ema50_pct": ((ema20_val - ema50_val) / (ema50_val + 1e-6)) * 100.0,
            "rsi14": rsi,
            "adx14": float(last_row.get("adx14", 25.0)),
            "macd_hist_norm": float(last_row.get("macd_histogram", 0.0) / (c * 0.01 + 1e-6)),
            "supertrend_dir": float(last_row.get("supertrend_direction", 1)),
            "stock_vs_sector_strength": stock_sec.stock_vs_sector_strength,
            "relative_volume": float(last_row.get("relative_volume", 1.0)),
            "dist_to_resistance_pct": sr_ctx.dist_to_resistance_pct if sr_ctx.dist_to_resistance_pct < 100 else 10.0,
        }
        ml_fc = self.ml_stock.forecast_stock(symbol, ml_features)
        reasons.append(f"ML Outperformance Probability: {ml_fc.opportunity_probability*100:.1f}%")

        # Blend ML opportunity score (40% weight) with technical/sector score (60% weight)
        blended_score = (score * 0.6) + (ml_fc.expected_alpha_score * 0.4)

        # Model uncertainty blended with ATR volatility
        atr = float(last_row.get("atr14", c * 0.02))
        vol_pct = (atr / c) * 100
        uncertainty = round((min(45.0, max(12.0, vol_pct * 4.0)) * 0.5) + (ml_fc.model_uncertainty * 0.5), 1)

        direction = "BULLISH" if blended_score >= 60.0 else "NEUTRAL" if blended_score >= 40.0 else "BEARISH"

        forecast = StockForecast(
            symbol=symbol,
            trading_date=t_date,
            sector_id=stock_sec.sector_id,
            sector_name=stock_sec.sector_name,
            stock_vs_sector_strength=stock_sec.stock_vs_sector_strength,
            forecast_horizon_days=20,
            predicted_opportunity_score=round(blended_score, 1),
            forecast_direction=direction,
            uncertainty_pct=uncertainty,
            rationale=tuple(reasons),
        )

        return forecast, sr_ctx

    def evaluate_risk_gate_and_plan(
        self,
        candidate: RankedCandidate,
        sr_ctx: SupportResistanceContext,
        stock_df: pd.DataFrame,
        regime: MarketRegimeClassification,
        current_sector_allocations: Dict[str, float],
        existing_position_count: int = 0,
    ) -> Tuple[Optional[TradePlan], Optional[RejectedCandidate]]:
        """
        Layer E — Independent Risk Gate and Trade Plan generation.
        """
        symbol = candidate.symbol
        last_row = stock_df.iloc[-1]
        c = candidate.close_price

        # Check Gate 1: Regime filter
        if regime.regime in {"STRESSED", "TRENDING_BEARISH"}:
            return None, RejectedCandidate(
                symbol=symbol,
                rejection_category="BEARISH_REGIME",
                reason=f"Risk gate active: new long entries halted in {regime.regime} regime",
                raw_score=candidate.composite_score,
            )

        # Check Gate 2: Liquidity filter
        turnover = float(last_row.get("turnover", 100.0))
        if turnover < self.min_turnover_lacs:
            return None, RejectedCandidate(
                symbol=symbol,
                rejection_category="POOR_LIQUIDITY",
                reason=f"Turnover {turnover:.1f} Lacs below required {self.min_turnover_lacs:.1f} Lacs threshold",
                raw_score=candidate.composite_score,
            )

        # Check Gate 3: Score threshold
        if candidate.composite_score < self.min_candidate_score:
            return None, RejectedCandidate(
                symbol=symbol,
                rejection_category="WEAK_EVIDENCE",
                reason=f"Composite score {candidate.composite_score:.1f} below minimum {self.min_candidate_score:.1f}",
                raw_score=candidate.composite_score,
            )

        # Calculate Stop-Loss and Target Zones using S/R zones & ATR
        atr = float(last_row.get("atr14", c * 0.02) or c * 0.02)

        # If support zone exists near price, anchor stop just below support lower band
        if sr_ctx.nearest_support and sr_ctx.nearest_support.level < c:
            stop = round(sr_ctx.nearest_support.lower_band * 0.995, 2)
        else:
            stop = round(c - 2.0 * atr, 2)

        # Ensure stop is below entry
        if stop >= c:
            stop = round(c - 2.0 * atr, 2)

        risk_per_share = c - stop
        if risk_per_share <= 0:
            risk_per_share = c * 0.03
            stop = round(c - risk_per_share, 2)

        # Target zone: min 2x risk, or resistance zone
        min_target = round(c + risk_per_share * self.min_reward_to_risk, 2)
        if sr_ctx.nearest_resistance and sr_ctx.nearest_resistance.level > min_target:
            target = round(sr_ctx.nearest_resistance.lower_band, 2)
        else:
            target = min_target

        rr_ratio = round((target - c) / risk_per_share, 2)
        if rr_ratio < self.min_reward_to_risk:
            target = round(c + risk_per_share * self.min_reward_to_risk, 2)
            rr_ratio = self.min_reward_to_risk

        # Check Gate 4: Position count
        if existing_position_count >= self.max_positions:
            return None, RejectedCandidate(
                symbol=symbol,
                rejection_category="CORRELATED_EXPOSURE",
                reason=f"Max portfolio positions limit reached ({self.max_positions})",
                raw_score=candidate.composite_score,
            )

        # Position Sizing using capital, risk per trade, and regime multiplier
        base_risk_amount = self.capital * (self.risk_per_trade_pct / 100.0)
        adjusted_risk_amount = base_risk_amount * regime.regime_multiplier

        qty = int(adjusted_risk_amount // risk_per_share)
        if qty < 1:
            return None, RejectedCandidate(
                symbol=symbol,
                rejection_category="WEAK_EVIDENCE",
                reason="Insufficient risk budget for minimum 1 share sizing",
                raw_score=candidate.composite_score,
            )

        pos_value = round(qty * c, 2)
        proposed_weight_pct = (pos_value / self.capital) * 100.0

        # Check Gate 5: Sector Concentration Limits
        sec_id = candidate.forecast.sector_id
        ok_sector, sec_reason = self.sector_engine.check_sector_concentration_guardrail(
            sector_id=sec_id,
            current_sector_allocations_pct=current_sector_allocations,
            proposed_trade_pct=proposed_weight_pct,
            max_sector_limit_pct=self.max_sector_exposure_pct,
        )

        outcome = "APPROVED"
        gate_msg = "Passed independent risk gate"
        if not ok_sector:
            # Try resizing to fit remaining sector room
            current_alloc = current_sector_allocations.get(sec_id, 0.0)
            avail_pct = max(0.0, self.max_sector_exposure_pct - current_alloc)
            if avail_pct >= 2.0:  # Allow resizing if at least 2% room remains
                resized_val = self.capital * (avail_pct / 100.0)
                qty = int(resized_val // c)
                if qty >= 1:
                    pos_value = round(qty * c, 2)
                    outcome = "RESIZED"
                    gate_msg = f"Position resized to fit {self.max_sector_exposure_pct}% sector ceiling"
                else:
                    return None, RejectedCandidate(
                        symbol=symbol,
                        rejection_category="CORRELATED_EXPOSURE",
                        reason=sec_reason,
                        raw_score=candidate.composite_score,
                    )
            else:
                return None, RejectedCandidate(
                    symbol=symbol,
                    rejection_category="CORRELATED_EXPOSURE",
                    reason=sec_reason,
                    raw_score=candidate.composite_score,
                )

        trade_plan = TradePlan(
            symbol=symbol,
            trading_date=candidate.forecast.trading_date,
            action="BUY",
            entry_trigger=round(c, 2),
            stop_loss=round(stop, 2),
            target_zone=round(target, 2),
            reward_to_risk=rr_ratio,
            position_size_shares=qty,
            position_value=pos_value,
            risk_amount=round(qty * risk_per_share, 2),
            risk_gate_outcome=outcome,
            gate_reason=gate_msg,
        )

        return trade_plan, None
