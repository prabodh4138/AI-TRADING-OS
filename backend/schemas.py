"""
AI Trading Operating System (AI-TOS)
Backend Pydantic Schemas for High-Speed API and WebSocket Streaming.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MarketStatusResponse(BaseModel):
    as_of_date: str
    latest_trading_date: str = ""
    earliest_trading_date: str = ""
    total_bars: int
    active_symbols: int
    data_health_score: float = 100.0
    health_status: str = "PRISTINE_HEALTH"
    market_posture: str
    sizing_recommendation: float
    yearly_trend: str
    quarterly_trend: str
    monthly_trend: str
    dual_source_verified: bool = True
    discrepancy_count: int = 0
    summary_notes: List[str] = Field(default_factory=list)


class CandleBar(BaseModel):
    time: str  # YYYY-MM-DD
    open: float
    high: float
    low: float
    close: float
    volume: int
    change_pct: float = 0.0
    ema20: Optional[float] = None
    ema50: Optional[float] = None
    sma200: Optional[float] = None


class ChartZoneOverlay(BaseModel):
    zone_id: str
    zone_type: str
    proximal_line: float
    distal_line: float
    buffered_stop_loss: float
    target_supply: float
    formation_date: str
    freshness: str
    color: str = "rgba(16, 185, 129, 0.25)"  # green for demand


class CandleHistoryResponse(BaseModel):
    symbol: str
    timeframe: str = "1D"
    current_price: float
    current_change_pct: float = 0.0
    high_52w: float = 0.0
    low_52w: float = 0.0
    bars: List[CandleBar]
    zones: List[ChartZoneOverlay] = Field(default_factory=list)


class ZoneCandidateDTO(BaseModel):
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
    conviction_tier: str
    yearly_trend: str
    half_yearly_trend: str = "BULLISH"
    quarterly_trend: str
    monthly_trend: str
    curve_location_pct: float
    curve_state: str
    alignment_grade: str
    is_best_aligned: bool
    is_actionable: bool
    formation_date: str
    freshness: str
    touch_count: int
    last_tested_date: str
    tested_dates: List[str] = Field(default_factory=list)
    freshness_detail: str
    penetration_pct: Optional[float] = None
    institutional_score_100: float
    recommended_entry_model: str
    entry_model_rational: str
    bos_type: str
    displacement_ratio_atr: float
    has_liquidity_sweep: bool
    sweep_description: str
    buffered_stop_loss: float
    hard_gate_status: str
    gate_passed: bool
    scorecard_100: Optional[Dict[str, Any]] = None
    checklist_12_points: Optional[List[Dict[str, Any]]] = None
    fundamental_tier: str = "AVERAGE"
    fundamental_score: float = 50.0
    news_sentiment_badge: str = "NEUTRAL"
    conviction_score_360: float = 50.0
    why_to_buy_summary: str = ""
    why_to_hold_summary: str = ""
    why_not_to_buy_summary: str = ""
    # Dual Output Architecture: Fundamental Quality vs Positional Entry Suitability
    fundamental_quality_score: float = 75.0
    fundamental_health_verdict: str = "FINANCIALLY_HEALTHY"
    positional_entry_score: float = 75.0
    positional_suitability_verdict: str = "PRIME_BUY_SUITABLE"
    # Pullback vs Reversal Classification & 5-Condition Audit
    pullback_classification: str = "HEALTHY_PULLBACK"
    pullback_conditions_passed: int = 5


class ZoneScanResponse(BaseModel):
    as_of_date: str
    total_symbols_scanned: int
    total_demand_zones_found: int
    fresh_demand_zones_count: int
    at_demand_count: int
    approaching_demand_count: int
    actionable_candidates: List[ZoneCandidateDTO]
    watchlist_candidates: List[ZoneCandidateDTO]
    best_aligned_candidates: List[ZoneCandidateDTO]
    avoid_trap_candidates: List[ZoneCandidateDTO]


class MTFZoneRecordDTO(BaseModel):
    zone_id: str
    symbol: str
    timeframe: str
    timeframe_horizon_rank: int
    pattern_type: str
    formation_date: str
    proximal_line: float
    distal_line: float
    current_market_price: float
    zone_width_pct: float
    proximity_pct: float
    proximity_status: str
    freshness_detail: str
    touch_count: int
    last_tested_date: str
    tested_dates: List[str] = Field(default_factory=list)
    penetration_pct: Optional[float] = None
    reward_to_risk: float
    odds_enhancer_score: float
    ml_bounce_probability: float
    institutional_footprint_score: float
    holding_horizon: str
    actionable_directive: str
    is_nested_in_htf: bool
    nested_parent_timeframe: Optional[str] = None
    nested_parent_proximal: Optional[float] = None


class MTFMatrixResponse(BaseModel):
    symbol: str
    current_price: float
    macro_curve_location_pct: float
    macro_curve_status: str
    composite_alignment_conviction: str
    deep_understanding_summary: str
    all_active_zones: List[MTFZoneRecordDTO]
    nested_super_zones: List[MTFZoneRecordDTO]


class TacticalChecklistItemDTO(BaseModel):
    id: int
    question: str
    status: str
    passed: bool
    metric: str
    explanation: str


class PullbackConditionItemDTO(BaseModel):
    condition_id: int
    name: str
    parameter: str
    required_criteria: str
    actual_value: str
    passed: bool
    status: str
    audit_note: str


class PullbackDiagnosisDTO(BaseModel):
    symbol: str
    current_price: float
    recent_swing_high: float
    swing_high_date: str
    pullback_depth_pct: float
    classification: str  # SHALLOW_PULLBACK, HEALTHY_PULLBACK, STRONG_PULLBACK, TREND_REVERSAL_BREAKDOWN
    classification_badge: str
    classification_explanation: str
    all_5_conditions_cleared: bool
    conditions_cleared_count: int
    conditions_max: int = 5
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
    candlestick_pattern: str = "NEUTRAL"
    reversal_candlestick_detected: bool = False
    confirmation_turn_detected: bool = False
    confirmation_volume_expansion: bool = False
    reversal_risk_score: float = 20.0
    actionable_directive: str = "MONITOR_PULLBACK"
    condition_items: List[PullbackConditionItemDTO] = Field(default_factory=list)


class StockThesisDTO(BaseModel):
    symbol: str
    company_name: str
    industry: str
    current_price: float
    as_of_date: str
    fundamental_tier: str
    fundamental_quality_score: float
    piotroski_f_score: int
    pe_ratio: float
    industry_pe: float
    valuation_status: str
    roe_pct: float
    roce_pct: float
    debt_to_equity: float
    fcf_yield_pct: float
    promoter_holding_pct: float
    news_sentiment_badge: str
    news_sentiment_score: float
    top_news_catalyst: str
    conviction_score_360: float
    executive_verdict: str
    why_to_buy: List[str]
    why_to_hold: List[str]
    why_not_to_buy: List[str]
    # 5-Pillar Institutional Deep Intelligence
    weekly_trend_verdict: str = "GENUINELY_BULLISH"
    weekly_trend_detail: str = ""
    daily_support_level: float = 0.0
    daily_support_activity: str = "STRONG_BUYING_ABSORPTION"
    daily_support_detail: str = ""
    volume_demand_behavior: str = "BUYERS_ENTERING_AGGRESSIVELY"
    volume_demand_detail: str = ""
    quarterly_sales_growth_pct: float = 0.0
    quarterly_profit_growth_pct: float = 0.0
    valuation_support_verdict: str = "GROWTH_SUPPORTS_VALUATION"
    valuation_support_detail: str = ""
    fii_holding_pct: float = 0.0
    fii_holding_change_qoq: float = 0.0
    dii_holding_pct: float = 0.0
    dii_holding_change_qoq: float = 0.0
    total_institutional_holding_pct: float = 0.0
    institutional_holding_trend: str = "STRONG_ACCUMULATION"
    institutional_holding_detail: str = ""
    # 12-Question Tactical Trade Thesis
    tactical_readiness_score: int = 12
    tactical_readiness_max: int = 12
    tactical_thesis_items: List[TacticalChecklistItemDTO] = Field(default_factory=list)
    # Pullback Quality & Reversal Diagnosis
    pullback_diagnosis: Optional[PullbackDiagnosisDTO] = None


class PositionDTO(BaseModel):
    position_id: str
    symbol: str
    sector_id: str
    entry_date: str
    entry_price: float
    quantity: int
    current_price: float
    stop_loss: float
    target: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    days_held: int
    initial_stop_loss: float


class ClosedTradeDTO(BaseModel):
    trade_id: str
    symbol: str
    sector_id: str
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    quantity: int
    net_pnl: float
    pnl_pct: float
    exit_reason: str
    slippage_and_fees: float


class PortfolioSummaryDTO(BaseModel):
    total_equity: float
    current_cash: float
    open_positions_count: int
    total_closed_trades: int
    win_rate_pct: float
    total_return_pct: float
    positions: List[PositionDTO] = Field(default_factory=list)
    recent_closed_trades: List[ClosedTradeDTO] = Field(default_factory=list)


class ExecuteTradeRequest(BaseModel):
    symbol: str
    action: str = "BUY"
    entry_trigger: float
    stop_loss: float
    target_zone: float
    position_size_shares: Optional[int] = None
    gate_reason: Optional[str] = "Manual Institutional Execution via FastAPI"


class ResetPortfolioRequest(BaseModel):
    capital: float = 1_000_000.0


class AutoTradeResultDTO(BaseModel):
    success: bool
    message: str
    new_positions_opened: int
    positions_closed: int
    stops_updated: int
    open_positions: List[PositionDTO] = Field(default_factory=list)
    execution_details: List[str] = Field(default_factory=list)


class AutoTradeStatusDTO(BaseModel):
    enabled: bool
    max_positions: int
    risk_per_trade_pct: float
    min_cash_reserve_pct: float
    last_run_timestamp: Optional[str] = None
    active_rules: List[str] = Field(default_factory=list)


class WatchlistRecommendationDTO(BaseModel):
    symbol: str
    cmp: float
    zone_type: str
    proximal_line: float
    distal_line: float
    buffered_stop_loss: float
    target_supply: float
    distance_to_demand_pct: float
    reward_to_risk: float
    institutional_score: float
    alignment_grade: str
    curve_state: str
    piotroski_f_score: int
    fundamental_tier: str
    formation_date: str = ""
    freshness_detail: str
    catalyst_summary: str
    action_recommendation: str
    # Multi-Timeframe Trend Harmony (All 6 Horizons)
    yearly_trend: str = "BULLISH"
    half_yearly_trend: str = "BULLISH"
    quarterly_trend: str = "BULLISH"
    monthly_trend: str = "BULLISH"
    weekly_trend: str = "BULLISH"
    daily_trend: str = "BULLISH"
    # Dynamic Institutional Trade Prediction Blueprint
    prediction_signal: str = "BUY_AT_DEMAND_LIMIT"
    predicted_entry_price: float = 0.0
    predicted_stop_loss: float = 0.0
    predicted_target_price: float = 0.0
    projected_upside_pct: float = 0.0
    projected_risk_pct: float = 0.0
    prediction_rationale: str = ""
    # 5-Pillar Snapshot Fields
    support_demand_floor: float = 0.0
    volume_behavior: str = "ACCUMULATION_ON_DIPS"
    quarterly_growth_summary: str = ""
    fii_dii_trend: str = "FII+DII ACCUMULATING"
    # Dual Output Architecture: Fundamental Quality vs Positional Entry Suitability
    fundamental_quality_score: float = 75.0
    fundamental_health_verdict: str = "FINANCIALLY_HEALTHY"
    positional_entry_score: float = 75.0
    positional_suitability_verdict: str = "PRIME_BUY_SUITABLE"
    # Pullback vs Reversal Classification & 5-Condition Audit
    pullback_classification: str = "HEALTHY_PULLBACK"
    pullback_conditions_passed: int = 5


class DualSourceCheckDTO(BaseModel):
    symbol: str
    nse_close: float
    yahoo_close: float
    drift_pct: float
    status: str  # MATCHED_VERIFIED, ACCEPTABLE_SPREAD, FLAGGED_ANOMALY
    notes: str


class MarketSyncResponse(BaseModel):
    success: bool
    message: str
    latest_trading_date: str
    total_bars_synced: int
    symbols_synced: int
    data_health_score: float
    verification_checks: List[DualSourceCheckDTO] = Field(default_factory=list)


class GenericApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class MasterChecklistItemDTO(BaseModel):
    sl_no: int
    category: str
    parameter: str
    preferred_criteria: str
    actual_value: str
    passed: bool
    audit_note: str


class CategorySummaryDTO(BaseModel):
    category: str
    total_items: int
    passed_items: int
    pass_rate_pct: float
    grade: str


class Master123ResponseDTO(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    total_score_123: int
    max_score_123: int
    composite_pass_rate_pct: float
    institutional_tier: str
    hard_gate_cleared: bool
    key_strengths: List[str] = Field(default_factory=list)
    key_red_flags: List[str] = Field(default_factory=list)
    category_summaries: List[CategorySummaryDTO] = Field(default_factory=list)
    all_123_items: List[MasterChecklistItemDTO] = Field(default_factory=list)
