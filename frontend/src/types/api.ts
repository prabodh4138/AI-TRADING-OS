export interface MarketStatus {
  as_of_date: string;
  latest_trading_date?: string;
  earliest_trading_date?: string;
  total_bars: number;
  active_symbols: number;
  data_health_score: number;
  health_status: string;
  market_posture: string;
  sizing_recommendation: number;
  yearly_trend: string;
  quarterly_trend: string;
  monthly_trend: string;
  dual_source_verified?: boolean;
  discrepancy_count?: number;
  summary_notes: string[];
}

export interface CandleBar {
  time: string; // YYYY-MM-DD
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  change_pct?: number;
  ema20?: number | null;
  ema50?: number | null;
  sma200?: number | null;
}

export interface ChartZoneOverlay {
  zone_id: string;
  zone_type: string;
  proximal_line: number;
  distal_line: number;
  buffered_stop_loss: number;
  target_supply: number;
  formation_date: string;
  freshness: string;
  color: string;
}

export interface CandleHistoryResponse {
  symbol: string;
  timeframe: string;
  current_price: number;
  current_change_pct: number;
  high_52w: number;
  low_52w: number;
  bars: CandleBar[];
  zones: ChartZoneOverlay[];
}

export interface ZoneCandidate {
  symbol: string;
  zone_type: string;
  location_state: string;
  current_price: number;
  proximal_line: number;
  distal_line: number;
  target_supply: number;
  zone_width: number;
  risk_pct: number;
  reward_to_risk: number;
  odds_enhancer_score: number;
  ml_success_probability: number;
  conviction_tier: string;
  yearly_trend: string;
  half_yearly_trend: string;
  quarterly_trend: string;
  monthly_trend: string;
  curve_location_pct: number;
  curve_state: string;
  alignment_grade: string;
  is_best_aligned: boolean;
  is_actionable: boolean;
  formation_date: string;
  freshness: string;
  touch_count: number;
  last_tested_date: string;
  tested_dates: string[];
  freshness_detail: string;
  penetration_pct?: number | null;
  institutional_score_100: number;
  recommended_entry_model: string;
  entry_model_rational: string;
  bos_type: string;
  displacement_ratio_atr: number;
  has_liquidity_sweep: boolean;
  sweep_description: string;
  buffered_stop_loss: number;
  hard_gate_status: string;
  gate_passed: boolean;
  scorecard_100?: Record<string, any>;
  checklist_12_points?: Array<{ item: string; passed: boolean; note: string }>;
  fundamental_tier?: string;
  fundamental_score?: number;
  news_sentiment_badge?: string;
  conviction_score_360?: number;
  why_to_buy_summary?: string;
  why_to_hold_summary?: string;
  why_not_to_buy_summary?: string;
  // Dual Output Architecture
  fundamental_quality_score?: number;
  fundamental_health_verdict?: string;
  positional_entry_score?: number;
  positional_suitability_verdict?: string;
  // Pullback vs Reversal Classification & 5 Conditions
  pullback_classification?: string;
  pullback_conditions_passed?: number;
}

export interface ZoneScanResponse {
  as_of_date: string;
  total_symbols_scanned: number;
  total_demand_zones_found: number;
  fresh_demand_zones_count: number;
  at_demand_count: number;
  approaching_demand_count: number;
  actionable_candidates: ZoneCandidate[];
  watchlist_candidates: ZoneCandidate[];
  best_aligned_candidates: ZoneCandidate[];
  avoid_trap_candidates: ZoneCandidate[];
}

export interface WatchlistRecommendation {
  symbol: string;
  cmp: number;
  zone_type: string;
  proximal_line: number;
  distal_line: number;
  buffered_stop_loss: number;
  target_supply: number;
  distance_to_demand_pct: number;
  reward_to_risk: number;
  institutional_score: number;
  alignment_grade: string;
  curve_state: string;
  piotroski_f_score: number;
  fundamental_tier: string;
  formation_date?: string;
  freshness_detail: string;
  catalyst_summary: string;
  action_recommendation: string;
  // Multi-Timeframe Trend Harmony (All 6 Horizons)
  yearly_trend?: string;
  half_yearly_trend?: string;
  quarterly_trend?: string;
  monthly_trend?: string;
  weekly_trend?: string;
  daily_trend?: string;
  // Dynamic Institutional Trade Prediction Blueprint
  prediction_signal?: string;
  predicted_entry_price?: number;
  predicted_stop_loss?: number;
  predicted_target_price?: number;
  projected_upside_pct?: number;
  projected_risk_pct?: number;
  prediction_rationale?: string;
  // 5-Pillar Snapshot Fields
  support_demand_floor?: number;
  volume_behavior?: string;
  quarterly_growth_summary?: string;
  fii_dii_trend?: string;
  // Dual Output Architecture
  fundamental_quality_score?: number;
  fundamental_health_verdict?: string;
  positional_entry_score?: number;
  positional_suitability_verdict?: string;
  // Pullback vs Reversal Classification & 5 Conditions
  pullback_classification?: string;
  pullback_conditions_passed?: number;
}

export interface MTFZoneRecord {
  zone_id: string;
  symbol: string;
  timeframe: string;
  timeframe_horizon_rank: number;
  pattern_type: string;
  formation_date: string;
  proximal_line: number;
  distal_line: number;
  current_market_price: number;
  zone_width_pct: number;
  proximity_pct: number;
  proximity_status: string;
  freshness_detail: string;
  touch_count: number;
  last_tested_date: string;
  tested_dates: string[];
  penetration_pct?: number | null;
  reward_to_risk: number;
  odds_enhancer_score: number;
  ml_bounce_probability: number;
  institutional_footprint_score: number;
  holding_horizon: string;
  actionable_directive: string;
  is_nested_in_htf: boolean;
  nested_parent_timeframe?: string | null;
  nested_parent_proximal?: number | null;
}

export interface MTFMatrixResponse {
  symbol: string;
  current_price: number;
  macro_curve_location_pct: number;
  macro_curve_status: string;
  composite_alignment_conviction: string;
  deep_understanding_summary: string;
  all_active_zones: MTFZoneRecord[];
  nested_super_zones: MTFZoneRecord[];
}

export interface TacticalChecklistItem {
  id: number;
  question: string;
  status: string;
  passed: boolean;
  metric: string;
  explanation: string;
}

export interface PullbackConditionItem {
  condition_id: number;
  name: string;
  parameter: string;
  required_criteria: string;
  actual_value: string;
  passed: boolean;
  status: string;
  audit_note: string;
}

export interface PullbackDiagnosis {
  symbol: string;
  current_price: number;
  recent_swing_high: number;
  swing_high_date: string;
  pullback_depth_pct: number;
  classification: string; // SHALLOW_PULLBACK, HEALTHY_PULLBACK, STRONG_PULLBACK, TREND_REVERSAL_BREAKDOWN
  classification_badge: string;
  classification_explanation: string;
  all_5_conditions_cleared: boolean;
  conditions_cleared_count: number;
  conditions_max: number;
  nearest_support_type: string;
  nearest_support_level: number;
  distance_to_support_pct: number;
  ema20: number;
  ema50: number;
  sma200: number;
  rsi_14: number;
  rsi_peak_at_high: number;
  rsi_cooldown_delta: number;
  selling_volume_ratio: number;
  volume_dry_up_confirmed: boolean;
  candlestick_pattern: string;
  reversal_candlestick_detected: boolean;
  confirmation_turn_detected: boolean;
  confirmation_volume_expansion: boolean;
  reversal_risk_score: number;
  actionable_directive: string;
  condition_items: PullbackConditionItem[];
}

export interface StockThesis {
  symbol: string;
  company_name: string;
  industry: string;
  current_price: number;
  as_of_date: string;
  fundamental_tier: string;
  fundamental_quality_score: number;
  piotroski_f_score: number;
  pe_ratio: number;
  industry_pe: number;
  valuation_status: string;
  roe_pct: number;
  roce_pct: number;
  debt_to_equity: number;
  fcf_yield_pct: number;
  promoter_holding_pct: number;
  news_sentiment_badge: string;
  news_sentiment_score: number;
  top_news_catalyst: string;
  conviction_score_360: number;
  executive_verdict: string;
  why_to_buy: string[];
  why_to_hold: string[];
  why_not_to_buy: string[];
  // 5-Pillar Institutional Deep Intelligence
  weekly_trend_verdict?: string;
  weekly_trend_detail?: string;
  daily_support_level?: number;
  daily_support_activity?: string;
  daily_support_detail?: string;
  volume_demand_behavior?: string;
  volume_demand_detail?: string;
  quarterly_sales_growth_pct?: number;
  quarterly_profit_growth_pct?: number;
  valuation_support_verdict?: string;
  valuation_support_detail?: string;
  fii_holding_pct?: number;
  fii_holding_change_qoq?: number;
  dii_holding_pct?: number;
  dii_holding_change_qoq?: number;
  total_institutional_holding_pct?: number;
  institutional_holding_trend?: string;
  institutional_holding_detail?: string;
  // 12-Question Tactical Trade Thesis
  tactical_readiness_score?: number;
  tactical_readiness_max?: number;
  tactical_thesis_items?: TacticalChecklistItem[];
  // Pullback Quality & Reversal Diagnosis
  pullback_diagnosis?: PullbackDiagnosis;
}

export interface Position {
  position_id: string;
  symbol: string;
  sector_id: string;
  entry_date: string;
  entry_price: number;
  quantity: number;
  current_price: number;
  stop_loss: number;
  target: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  days_held: number;
  initial_stop_loss: number;
}

export interface ClosedTrade {
  trade_id: string;
  symbol: string;
  sector_id: string;
  entry_date: string;
  exit_date: string;
  entry_price: number;
  exit_price: number;
  quantity: number;
  net_pnl: number;
  pnl_pct: number;
  exit_reason: string;
  slippage_and_fees: number;
}

export interface PortfolioSummary {
  total_equity: number;
  current_cash: number;
  open_positions_count: number;
  total_closed_trades: number;
  win_rate_pct: number;
  total_return_pct: number;
  positions: Position[];
  recent_closed_trades: ClosedTrade[];
}

export interface AutoTradeResult {
  success: boolean;
  message: string;
  new_positions_opened: number;
  positions_closed: number;
  stops_updated: number;
  open_positions: Position[];
  execution_details: string[];
}

export interface AutoTradeStatus {
  enabled: boolean;
  max_positions: number;
  risk_per_trade_pct: number;
  min_cash_reserve_pct: number;
  last_run_timestamp: string | null;
  active_rules: string[];
}

export interface ExecuteTradeRequest {
  symbol: string;
  action?: string;
  entry_trigger: number;
  stop_loss: number;
  target_zone: number;
  position_size_shares?: number;
  gate_reason?: string;
}

export interface DualSourceCheck {
  symbol: string;
  nse_close: number;
  yahoo_close: number;
  drift_pct: number;
  status: string; // MATCHED_VERIFIED, ACCEPTABLE_SPREAD, FLAGGED_ANOMALY
  notes: string;
}

export interface MarketSyncResponse {
  success: boolean;
  message: string;
  latest_trading_date: string;
  total_bars_synced: number;
  symbols_synced: number;
  data_health_score: number;
  verification_checks: DualSourceCheck[];
}

export interface MasterChecklistItem {
  sl_no: number;
  category: string;
  parameter: string;
  preferred_criteria: string;
  actual_value: string;
  passed: boolean;
  audit_note: string;
}

export interface CategorySummary {
  category: string;
  total_items: number;
  passed_items: number;
  pass_rate_pct: number;
  grade: string;
}

export interface Master123Response {
  symbol: string;
  company_name: string;
  current_price: number;
  total_score_123: number;
  max_score_123: number;
  composite_pass_rate_pct: number;
  institutional_tier: string;
  hard_gate_cleared: boolean;
  key_strengths: string[];
  key_red_flags: string[];
  category_summaries: CategorySummary[];
  all_123_items: MasterChecklistItem[];
}

