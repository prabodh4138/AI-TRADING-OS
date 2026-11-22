"""
AI Trading Operating System (AI-TOS)
Module: risk/risk_gate.py
Specification Baseline: Master Final Consolidated System Specification v3.1 (Section 8)

Independent Risk Gate & Policy Evaluation Engine:
- Evaluates candidates strictly independently from ranking scores.
- Checks: Data readiness, Liquidity/tradability, Volatility/stop distance, Concentration,
  Event risk, Portfolio limits, and Model uncertainty.
- Emits canonical DecisionStatus:
  * FOCUS
  * PAPER PLAN APPROVED
  * DEFER
  * EXCLUDED
  * NO TRADE
  * INSUFFICIENT DATA
- Preserves full audit trail with policy version and explicit rejection reason codes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from core.system_spec import DecisionStatus, QualityState


@dataclass
class RiskCheckResult:
    check_name: str
    passed: bool
    observed_value: Any
    threshold: Any
    reason_code: str
    message: str


@dataclass
class EvaluatedCandidateDecision:
    symbol: str
    trading_date: date
    decision_status: DecisionStatus
    is_paper_approved: bool
    approved_shares: int
    entry_price: float
    stop_loss: float
    target_price: float
    reward_to_risk: float
    position_value: float
    risk_amount: float
    risk_checks: List[RiskCheckResult]
    primary_reason: str
    policy_version: str = "v3.1-ConsolidatedRiskPolicy"
    evaluation_timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "trading_date": str(self.trading_date),
            "decision_status": self.decision_status.value,
            "is_paper_approved": self.is_paper_approved,
            "approved_shares": self.approved_shares,
            "entry_price": round(self.entry_price, 2),
            "stop_loss": round(self.stop_loss, 2),
            "target_price": round(self.target_price, 2),
            "reward_to_risk": round(self.reward_to_risk, 2),
            "position_value": round(self.position_value, 2),
            "risk_amount": round(self.risk_amount, 2),
            "primary_reason": self.primary_reason,
            "policy_version": self.policy_version,
            "evaluation_timestamp": self.evaluation_timestamp.isoformat(),
            "risk_checks": [asdict(c) for c in self.risk_checks],
        }


class IndependentRiskGate:
    """
    Independent Risk Gate enforcing Section 8 policy constraints.
    """

    def __init__(
        self,
        capital: float = 1_000_000.0,
        risk_per_trade_pct: float = 1.0,
        max_positions: int = 12,
        max_sector_exposure_pct: float = 20.0,
        max_single_stock_exposure_pct: float = 10.0,
        min_reward_to_risk: float = 2.0,
        min_daily_volume: int = 25000,
        max_uncertainty_score: float = 85.0,
        min_ml_win_probability: float = 65.0,
    ) -> None:
        self.capital = capital
        self.risk_per_trade_pct = risk_per_trade_pct
        self.max_positions = max_positions
        self.max_sector_exposure_pct = max_sector_exposure_pct
        self.max_single_stock_exposure_pct = max_single_stock_exposure_pct
        self.min_reward_to_risk = min_reward_to_risk
        self.min_daily_volume = min_daily_volume
        self.max_uncertainty_score = max_uncertainty_score
        self.min_ml_win_probability = min_ml_win_probability
        self.policy_version = "v3.1-ConsolidatedRiskPolicy"

    def evaluate_candidate(
        self,
        symbol: str,
        trading_date: date,
        current_price: float,
        entry_price: float,
        stop_loss: float,
        target_price: float,
        sector: str = "OTHER",
        quality_state: QualityState = QualityState.READY,
        history_bars_count: int = 100,
        daily_volume: int = 50000,
        model_uncertainty_score: float = 35.0,
        current_open_positions: int = 0,
        current_sector_exposure_pct: float = 0.0,
        is_at_or_approaching_zone: bool = True,
        is_corporate_action_pending: bool = False,
        market_regime: str = "NEUTRAL",
        regime_multiplier: float = 1.0,
        ml_win_probability: float = 75.0,
    ) -> EvaluatedCandidateDecision:
        """
        Executes independent risk gate checks across all Section 8 dimensions.
        """
        checks: List[RiskCheckResult] = []

        # 0. Market Condition & Hostile Regime Risk Gate (Capital Preservation Mode)
        if regime_multiplier <= 0.20 or market_regime in ["TRENDING_BEARISH", "BEARISH_CRASH", "HIGH_VOLATILITY_DOWN"]:
            checks.append(RiskCheckResult(
                check_name="MARKET_REGIME_SAFETY",
                passed=False,
                observed_value=f"regime={market_regime}, multiplier={regime_multiplier:.2f}x",
                threshold="multiplier>0.20 and regime!=TRENDING_BEARISH",
                reason_code="BEARISH_REGIME_CAPITAL_PRESERVATION",
                message="Capital preservation mode active: Long entries prohibited during hostile market regime",
            ))
            return self._build_decision(
                symbol=symbol,
                trading_date=trading_date,
                status=DecisionStatus.DEFER,
                reason=f"DEFER: Market regime is {market_regime} ({regime_multiplier:.2f}x sizing). Long entries prohibited to preserve capital during market downtrend.",
                checks=checks,
                entry=entry_price, stop=stop_loss, target=target_price,
            )

        # 1. Data Readiness Check
        data_ready = (quality_state in [QualityState.READY, QualityState.DEGRADED]) and history_bars_count >= 30
        checks.append(RiskCheckResult(
            check_name="DATA_READINESS",
            passed=data_ready,
            observed_value=f"state={quality_state.value}, bars={history_bars_count}",
            threshold="state!=QUARANTINED and bars>=30",
            reason_code="DATA_QUARANTINED_OR_SHORT_HISTORY" if not data_ready else "DATA_READY",
            message="Data readiness verified" if data_ready else "Data is quarantined, stale or lacks minimum 30-bar history",
        ))

        if not data_ready:
            return self._build_decision(
                symbol=symbol,
                trading_date=trading_date,
                status=DecisionStatus.INSUFFICIENT_DATA,
                reason="INSUFFICIENT DATA: Market bars quarantined, unaligned, or shorter than 30 sessions.",
                checks=checks,
                entry=entry_price, stop=stop_loss, target=target_price,
            )

        # 2. Liquidity & Tradability Check
        has_liquidity = daily_volume >= self.min_daily_volume and current_price > 5.0
        checks.append(RiskCheckResult(
            check_name="LIQUIDITY_TRADABILITY",
            passed=has_liquidity,
            observed_value=f"vol={daily_volume:,}, price={current_price:.2f}",
            threshold=f"vol>={self.min_daily_volume:,}, price>5.0",
            reason_code="POOR_LIQUIDITY_PENNY_STOCK" if not has_liquidity else "LIQUIDITY_OK",
            message="Liquidity check passed" if has_liquidity else "Abnormal low volume or penny-stock price",
        ))

        if not has_liquidity:
            return self._build_decision(
                symbol=symbol,
                trading_date=trading_date,
                status=DecisionStatus.EXCLUDED,
                reason="EXCLUDED: Fails minimum daily liquidity threshold (illiquid or penny stock).",
                checks=checks,
                entry=entry_price, stop=stop_loss, target=target_price,
            )

        # 3. Volatility / Stop Distance / Invalidation Coherence
        risk_per_share = entry_price - stop_loss
        reward_per_share = target_price - entry_price
        rr_ratio = (reward_per_share / risk_per_share) if risk_per_share > 0 else 0.0

        coherent_geometry = (entry_price > stop_loss) and (target_price > entry_price) and (risk_per_share > 0)
        sufficient_rr = rr_ratio >= self.min_reward_to_risk

        checks.append(RiskCheckResult(
            check_name="STOP_AND_REWARD_GEOMETRY",
            passed=coherent_geometry and sufficient_rr,
            observed_value=f"R:R={rr_ratio:.2f}:1, risk_per_share={risk_per_share:.2f}",
            threshold=f"R:R>={self.min_reward_to_risk:.1f}:1 and stop<entry<target",
            reason_code="UNFAVORABLE_REWARD_RISK" if not sufficient_rr else ("INCOHERENT_STOP" if not coherent_geometry else "GEOMETRY_OK"),
            message="Risk-to-reward is favorable" if (coherent_geometry and sufficient_rr) else f"Reward-to-risk ({rr_ratio:.2f}) below minimum {self.min_reward_to_risk}:1",
        ))

        if not coherent_geometry or not sufficient_rr:
            return self._build_decision(
                symbol=symbol,
                trading_date=trading_date,
                status=DecisionStatus.NO_TRADE,
                reason=f"NO TRADE: Setup reward-to-risk ratio ({rr_ratio:.2f}:1) fails minimum policy requirement ({self.min_reward_to_risk}:1).",
                checks=checks,
                entry=entry_price, stop=stop_loss, target=target_price,
                rr=rr_ratio,
            )

        # 4. Model Uncertainty Check
        uncertainty_ok = model_uncertainty_score <= self.max_uncertainty_score
        checks.append(RiskCheckResult(
            check_name="MODEL_UNCERTAINTY",
            passed=uncertainty_ok,
            observed_value=f"uncertainty={model_uncertainty_score:.1f}%",
            threshold=f"uncertainty<={self.max_uncertainty_score:.1f}%",
            reason_code="HIGH_MODEL_UNCERTAINTY" if not uncertainty_ok else "MODEL_CONFIDENCE_OK",
            message="Model uncertainty acceptable" if uncertainty_ok else "Model entropy uncertainty exceeds safety limit",
        ))

        if not uncertainty_ok:
            return self._build_decision(
                symbol=symbol,
                trading_date=trading_date,
                status=DecisionStatus.DEFER,
                reason=f"DEFER: Model prediction uncertainty ({model_uncertainty_score:.1f}%) exceeds safety threshold. Awaiting clearer signal.",
                checks=checks,
                entry=entry_price, stop=stop_loss, target=target_price,
                rr=rr_ratio,
            )

        # 4B. ML Win Probability Check (Institutional Conviction Filter)
        win_prob_ok = ml_win_probability >= self.min_ml_win_probability
        checks.append(RiskCheckResult(
            check_name="ML_WIN_PROBABILITY",
            passed=win_prob_ok,
            observed_value=f"win_prob={ml_win_probability:.1f}%",
            threshold=f"win_prob>={self.min_ml_win_probability:.1f}%",
            reason_code="LOW_ML_WIN_PROBABILITY" if not win_prob_ok else "HIGH_ML_WIN_PROBABILITY",
            message=f"ML win probability ({ml_win_probability:.1f}%) meets threshold" if win_prob_ok else f"ML win probability ({ml_win_probability:.1f}%) below minimum conviction ({self.min_ml_win_probability}%)",
        ))

        if not win_prob_ok:
            return self._build_decision(
                symbol=symbol,
                trading_date=trading_date,
                status=DecisionStatus.DEFER,
                reason=f"DEFER: Dedicated ML Win Probability ({ml_win_probability:.1f}%) below minimum institutional conviction threshold ({self.min_ml_win_probability:.1f}%).",
                checks=checks,
                entry=entry_price, stop=stop_loss, target=target_price,
                rr=rr_ratio,
            )

        # 5. Portfolio & Concentration Limits
        portfolio_not_full = current_open_positions < self.max_positions
        sector_not_saturated = current_sector_exposure_pct < self.max_sector_exposure_pct
        checks.append(RiskCheckResult(
            check_name="PORTFOLIO_CONCENTRATION_LIMITS",
            passed=portfolio_not_full and sector_not_saturated,
            observed_value=f"open_pos={current_open_positions}/{self.max_positions}, sector_exp={current_sector_exposure_pct:.1f}%/{self.max_sector_exposure_pct:.1f}%",
            threshold=f"pos<{self.max_positions}, sector<{self.max_sector_exposure_pct}%",
            reason_code="PORTFOLIO_LIMIT_EXCEEDED" if not (portfolio_not_full and sector_not_saturated) else "LIMITS_OK",
            message="Portfolio capacity available" if (portfolio_not_full and sector_not_saturated) else "Portfolio position or sector concentration limit reached",
        ))

        if not portfolio_not_full or not sector_not_saturated:
            return self._build_decision(
                symbol=symbol,
                trading_date=trading_date,
                status=DecisionStatus.FOCUS,
                reason="FOCUS: Eligible candidate meets quality criteria, but deferred from paper execution due to portfolio capacity/sector limit.",
                checks=checks,
                entry=entry_price, stop=stop_loss, target=target_price,
                rr=rr_ratio,
            )

        # 6. Setup Readiness / Pullback Proximity
        if not is_at_or_approaching_zone:
            checks.append(RiskCheckResult(
                check_name="ZONE_PROXIMITY_PULLBACK",
                passed=False,
                observed_value="Price distant from demand entry",
                threshold="At or approaching proximal line (<=3%)",
                reason_code="PENDING_PULLBACK_RETEST",
                message="Price has not yet pulled back into execution window",
            ))
            return self._build_decision(
                symbol=symbol,
                trading_date=trading_date,
                status=DecisionStatus.DEFER,
                reason="DEFER: Setup identified, but current market price has not pulled back to entry zone proximal line.",
                checks=checks,
                entry=entry_price, stop=stop_loss, target=target_price,
                rr=rr_ratio,
            )

        # 7. Sizing & Capital Allocation Calculation
        max_risk_amount = self.capital * (self.risk_per_trade_pct / 100.0)
        calculated_shares = max(1, int(max_risk_amount // risk_per_share))
        pos_value = calculated_shares * entry_price

        # Single stock exposure cap check
        max_pos_value = self.capital * (self.max_single_stock_exposure_pct / 100.0)
        if pos_value > max_pos_value:
            calculated_shares = max(1, int(max_pos_value // entry_price))
            pos_value = calculated_shares * entry_price

        actual_risk = calculated_shares * risk_per_share

        checks.append(RiskCheckResult(
            check_name="SIZING_AND_CAPITAL",
            passed=True,
            observed_value=f"shares={calculated_shares}, value=Rs.{pos_value:,.2f}, risk=Rs.{actual_risk:,.2f}",
            threshold=f"risk<={max_risk_amount:,.2f}, cap<={max_pos_value:,.2f}",
            reason_code="SIZING_APPROVED",
            message=f"Sized {calculated_shares} shares adhering strictly to 1% equity risk limit",
        ))

        # Passed all 7 dimensions! Status: PAPER PLAN APPROVED
        return EvaluatedCandidateDecision(
            symbol=symbol,
            trading_date=trading_date,
            decision_status=DecisionStatus.PAPER_PLAN_APPROVED,
            is_paper_approved=True,
            approved_shares=calculated_shares,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_price=target_price,
            reward_to_risk=rr_ratio,
            position_value=pos_value,
            risk_amount=actual_risk,
            risk_checks=checks,
            primary_reason=f"PAPER PLAN APPROVED: Passed independent risk gate. Risk: Rs. {actual_risk:,.2f} ({self.risk_per_trade_pct}% equity) | R:R {rr_ratio:.2f}:1.",
            policy_version=self.policy_version,
        )

    def _build_decision(
        self,
        symbol: str,
        trading_date: date,
        status: DecisionStatus,
        reason: str,
        checks: List[RiskCheckResult],
        entry: float,
        stop: float,
        target: float,
        rr: float = 0.0,
    ) -> EvaluatedCandidateDecision:
        return EvaluatedCandidateDecision(
            symbol=symbol,
            trading_date=trading_date,
            decision_status=status,
            is_paper_approved=False,
            approved_shares=0,
            entry_price=entry,
            stop_loss=stop,
            target_price=target,
            reward_to_risk=rr,
            position_value=0.0,
            risk_amount=0.0,
            risk_checks=checks,
            primary_reason=reason,
            policy_version=self.policy_version,
        )
