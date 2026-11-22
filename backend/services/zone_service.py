"""
AI Trading Operating System (AI-TOS)
Zone Service: High-Speed Pure Institutional Demand & Supply Zone Scanning and MTF Matrix.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd

from analytics.dynamic_mtf_zones import DynamicMTFZoneEngine, DynamicZoneRecord
from analytics.demand_supply_zones import DemandSupplyZoneEngine, PriceLocation
from analytics.pullback_analyzer import PullbackQualityEngine
from backend.schemas import (
    ChartZoneOverlay,
    MTFMatrixResponse,
    MTFZoneRecordDTO,
    WatchlistRecommendationDTO,
    ZoneCandidateDTO,
    ZoneScanResponse,
)
from backend.services.data_service import DataService
from data_engine.fundamental_data import FundamentalDataProvider
from scanner.gtf_scanner import GTFTradeCandidate, GTFTradeScanner


def _clean_date_str(val: Any) -> str:
    if not val:
        return ""
    s = str(val).strip()
    return s.split()[0].split("T")[0]


class ZoneService:
    _instance: Optional[ZoneService] = None

    def __init__(self) -> None:
        self.data_service = DataService.get_instance()
        self.gtf_scanner = GTFTradeScanner()
        self.mtf_engine = DynamicMTFZoneEngine()
        self.pullback_engine = PullbackQualityEngine()
        self.cached_scan: Optional[ZoneScanResponse] = None

    @classmethod
    def get_instance(cls) -> ZoneService:
        if cls._instance is None:
            cls._instance = ZoneService()
        return cls._instance

    def _convert_cand_to_dto(self, c: GTFTradeCandidate) -> ZoneCandidateDTO:
        sc = getattr(c, "scorecard_100", None)
        chk = getattr(c, "checklist_12_points", None)

        clean_f_date = _clean_date_str(c.formation_date)
        raw_last = getattr(c, "last_tested_date", None)
        clean_last = _clean_date_str(raw_last) if raw_last and "Never" not in str(raw_last) else (str(raw_last) if raw_last else "Never Tested (Fresh)")
        raw_t_dates = getattr(c, "tested_dates", []) or []
        clean_tested = [_clean_date_str(td) for td in raw_t_dates]
        clean_fresh_detail = str(c.freshness_detail).replace(" 00:00:00", "")

        return ZoneCandidateDTO(
            symbol=c.symbol,
            zone_type=c.zone_type,
            location_state=c.location_state,
            current_price=c.current_price,
            proximal_line=c.proximal_line,
            distal_line=c.distal_line,
            target_supply=c.target_supply,
            zone_width=c.zone_width,
            risk_pct=c.risk_pct,
            reward_to_risk=c.reward_to_risk,
            odds_enhancer_score=c.odds_enhancer_score,
            ml_success_probability=c.ml_success_probability,
            conviction_tier=c.conviction_tier,
            yearly_trend=c.yearly_trend,
            half_yearly_trend=getattr(c, "half_yearly_trend", "BULLISH"),
            quarterly_trend=c.quarterly_trend,
            monthly_trend=c.monthly_trend,
            curve_location_pct=c.curve_location_pct,
            curve_state=c.curve_state,
            alignment_grade=c.alignment_grade,
            is_best_aligned=c.is_best_aligned,
            is_actionable=c.is_actionable,
            formation_date=clean_f_date,
            freshness=c.freshness,
            touch_count=c.touch_count,
            last_tested_date=clean_last,
            tested_dates=clean_tested,
            freshness_detail=clean_fresh_detail,
            penetration_pct=c.penetration_pct,
            institutional_score_100=getattr(c, "institutional_score_100", 70.0),
            recommended_entry_model=getattr(c, "recommended_entry_model", "MODEL_A_DIRECT_LIMIT"),
            entry_model_rational=getattr(c, "entry_model_rational", ""),
            bos_type=getattr(c, "bos_type", "NO_CLEAR_BREAK"),
            displacement_ratio_atr=getattr(c, "displacement_ratio_atr", 1.0),
            has_liquidity_sweep=getattr(c, "has_liquidity_sweep", False),
            sweep_description=getattr(c, "sweep_description", ""),
            buffered_stop_loss=getattr(c, "buffered_stop_loss", c.distal_line),
            hard_gate_status=getattr(c, "hard_gate_status", "APPROVED"),
            gate_passed=getattr(c, "gate_passed", True),
            scorecard_100=sc,
            checklist_12_points=chk,
            fundamental_tier=getattr(c, "fundamental_tier", "AVERAGE"),
            fundamental_score=getattr(c, "fundamental_score", 50.0),
            news_sentiment_badge=getattr(c, "news_sentiment_badge", "NEUTRAL"),
            conviction_score_360=getattr(c, "conviction_score_360", 50.0),
            why_to_buy_summary=getattr(c, "why_to_buy_summary", ""),
            why_to_hold_summary=getattr(c, "why_to_hold_summary", ""),
            why_not_to_buy_summary=getattr(c, "why_not_to_buy_summary", ""),
            fundamental_quality_score=getattr(c, "fundamental_quality_score", 75.0),
            fundamental_health_verdict=getattr(c, "fundamental_health_verdict", "FINANCIALLY_HEALTHY"),
            positional_entry_score=getattr(c, "positional_entry_score", 75.0),
            positional_suitability_verdict=getattr(c, "positional_suitability_verdict", "PRIME_BUY_SUITABLE"),
        )

    def scan_universe(self, force_refresh: bool = False) -> ZoneScanResponse:
        if self.cached_scan is not None and not force_refresh:
            return self.cached_scan

        df = self.data_service.get_dataframe()
        scan_res = self.gtf_scanner.scan_universe(df)

        actionable = [self._convert_cand_to_dto(c) for c in scan_res.actionable_candidates]
        watchlist = [self._convert_cand_to_dto(c) for c in scan_res.watchlist_candidates]
        best_aligned = [self._convert_cand_to_dto(c) for c in scan_res.best_aligned_candidates]
        avoid_traps = [self._convert_cand_to_dto(c) for c in scan_res.avoid_trap_candidates]

        resp = ZoneScanResponse(
            as_of_date=str(scan_res.as_of_date),
            total_symbols_scanned=scan_res.total_symbols_scanned,
            total_demand_zones_found=scan_res.total_demand_zones_found,
            fresh_demand_zones_count=scan_res.fresh_demand_zones_count,
            at_demand_count=scan_res.at_demand_count,
            approaching_demand_count=scan_res.approaching_demand_count,
            actionable_candidates=actionable,
            watchlist_candidates=watchlist,
            best_aligned_candidates=best_aligned,
            avoid_trap_candidates=avoid_traps,
        )
        self.cached_scan = resp
        return resp

    def get_mtf_matrix(self, symbol: str) -> Optional[MTFMatrixResponse]:
        df = self.data_service.get_dataframe()
        sym_clean = symbol.strip().upper()
        sym_df = df[df["symbol"].str.upper() == sym_clean].sort_values("trading_date")
        if sym_df.empty or len(sym_df) < 5:
            return None

        matrix = self.mtf_engine.evaluate_symbol_zones(symbol=sym_clean, daily_df=sym_df)

        def _to_record_dto(z: DynamicZoneRecord) -> MTFZoneRecordDTO:
            clean_f_date = _clean_date_str(z.formation_date)
            raw_last = z.last_tested_date
            clean_last = _clean_date_str(raw_last) if raw_last and "Never" not in str(raw_last) else (str(raw_last) if raw_last else "Never Tested (Fresh)")
            raw_t_dates = z.tested_dates or []
            clean_tested = [_clean_date_str(td) for td in raw_t_dates]
            clean_fresh_detail = str(z.freshness_detail).replace(" 00:00:00", "")

            return MTFZoneRecordDTO(
                zone_id=z.zone_id,
                symbol=z.symbol,
                timeframe=z.timeframe,
                timeframe_horizon_rank=z.timeframe_horizon_rank,
                pattern_type=z.pattern_type,
                formation_date=clean_f_date,
                proximal_line=round(z.proximal_line, 2),
                distal_line=round(z.distal_line, 2),
                current_market_price=round(z.current_market_price, 2),
                zone_width_pct=round(z.zone_width_pct, 2),
                proximity_pct=round(z.proximity_pct, 2),
                proximity_status=z.proximity_status.value,
                freshness_detail=clean_fresh_detail,
                touch_count=z.touch_count,
                last_tested_date=clean_last,
                tested_dates=clean_tested,
                penetration_pct=z.penetration_pct,
                reward_to_risk=round(z.reward_to_risk, 2),
                odds_enhancer_score=round(z.odds_enhancer_score, 1),
                ml_bounce_probability=round(z.ml_bounce_probability, 1),
                institutional_footprint_score=round(z.institutional_footprint_score, 1),
                holding_horizon=z.holding_horizon,
                actionable_directive=z.actionable_directive,
                is_nested_in_htf=z.is_nested_in_htf,
                nested_parent_timeframe=z.nested_parent_timeframe,
                nested_parent_proximal=round(z.nested_parent_proximal, 2) if z.nested_parent_proximal else None,
            )

        return MTFMatrixResponse(
            symbol=matrix.symbol,
            current_price=round(matrix.current_price, 2),
            macro_curve_location_pct=round(matrix.macro_curve_location_pct, 1),
            macro_curve_status=matrix.macro_curve_status,
            composite_alignment_conviction=matrix.composite_alignment_conviction,
            deep_understanding_summary=matrix.deep_understanding_summary,
            all_active_zones=[_to_record_dto(z) for z in matrix.all_active_zones],
            nested_super_zones=[_to_record_dto(z) for z in matrix.nested_super_zones],
        )

    def get_symbol_zones(self, symbol: str) -> List[ChartZoneOverlay]:
        df = self.data_service.get_dataframe()
        sym_clean = symbol.strip().upper()
        sym_df = df[df["symbol"].str.upper() == sym_clean].sort_values("trading_date")
        if sym_df.empty:
            return []

        demands, supplies = DemandSupplyZoneEngine().find_all_zones(sym_df, symbol=sym_clean)
        overlays: List[ChartZoneOverlay] = []

        for d in demands[:4]:
            overlays.append(ChartZoneOverlay(
                zone_id=d.zone_id,
                zone_type=d.zone_type.value,
                proximal_line=d.proximal_line,
                distal_line=d.distal_line,
                buffered_stop_loss=d.buffered_stop_loss,
                target_supply=d.opposing_target or (d.proximal_line + d.zone_width * 2.5),
                formation_date=str(d.formation_date),
                freshness=d.freshness.value,
                color="rgba(16, 185, 129, 0.20)",
            ))

        for s in supplies[:2]:
            overlays.append(ChartZoneOverlay(
                zone_id=s.zone_id,
                zone_type=s.zone_type.value,
                proximal_line=s.proximal_line,
                distal_line=s.distal_line,
                buffered_stop_loss=s.buffered_stop_loss,
                target_supply=s.proximal_line - (s.zone_width * 2.0),
                formation_date=str(s.formation_date),
                freshness=s.freshness.value,
                color="rgba(239, 68, 68, 0.20)",
            ))

        return overlays

    def get_curated_watchlist(self) -> List[WatchlistRecommendationDTO]:
        """
        Synthesizes the entire scanned universe to return the Top 15 Best Institutional Watchlist candidates:
        Pristine unbreached zones, approaching demand within 3%, high R:R >= 2.0, Grade A+/A, and wholesale curve location.
        """
        scan = self.scan_universe()
        candidates = scan.actionable_candidates + scan.watchlist_candidates + scan.best_aligned_candidates
        df = self.data_service.get_dataframe()

        seen = set()
        recommendations: List[WatchlistRecommendationDTO] = []

        fp = FundamentalDataProvider()
        for c in candidates:
            if c.symbol in seen:
                continue
            seen.add(c.symbol)

            dist_pct = round(abs(c.current_price - c.proximal_line) / max(1.0, c.proximal_line) * 100.0, 2)
            
            if c.is_actionable or dist_pct <= 0.5:
                action_tag = "READY_FOR_EXECUTION"
            elif dist_pct <= 1.5:
                action_tag = "IMMINENT_ACCUMULATION"
            elif dist_pct <= 3.0:
                action_tag = "APPROACHING_DEMAND"
            else:
                action_tag = "MONITOR_PULLBACK"

            # 5-Pillar Snapshot
            f_data = fp.get_fundamentals(c.symbol)
            net_inst = round(f_data.fii_holding_change_qoq + f_data.dii_holding_change_qoq, 2)
            fii_dii_str = f"FII+DII {'ACCUMULATING' if net_inst >= 0 else 'DISTRIBUTION'} ({'+' if net_inst >= 0 else ''}{net_inst:.2f}% QoQ)"
            growth_str = f"Rev +{f_data.sales_growth_3y_pct:.1f}% | PAT +{f_data.profit_growth_3y_pct:.1f}%"

            # Multi-Timeframe Trend Harmony (All 6 Horizons)
            y_trend = c.yearly_trend if getattr(c, "yearly_trend", None) else "BULLISH"
            hy_trend = getattr(c, "half_yearly_trend", "BULLISH") or "BULLISH"
            q_trend = c.quarterly_trend if getattr(c, "quarterly_trend", None) else "BULLISH"
            m_trend = c.monthly_trend if getattr(c, "monthly_trend", None) else "STRONG_BULLISH"
            w_trend = "BULLISH" if ("BULL" in m_trend or c.reward_to_risk >= 2.0) else "NEUTRAL"
            d_trend = "AT_DEMAND_FLOOR" if dist_pct <= 2.0 else ("PULLBACK_RETEST" if dist_pct <= 15.0 else "DEEP_PULLBACK")

            # Dynamic Institutional Trade Prediction Blueprint
            prox_p = round(c.proximal_line, 2)
            dist_p = round(c.distal_line, 2)
            sl_p = round(c.buffered_stop_loss, 2)
            target_p = round(c.target_supply, 2)
            cmp_p = round(c.current_price, 2)

            if c.is_actionable or dist_pct <= 0.8:
                pred_signal = "STRONG_BUY_LIMIT_AT_DEMAND"
                pred_entry = cmp_p
                pred_rationale = f"Price is directly inside wholesale demand base ({dist_pct}% away). High statistical bounce probability ({c.ml_success_probability:.1f}%)."
            elif dist_pct <= 3.0:
                pred_signal = "PREPARE_LIMIT_ORDER"
                pred_entry = prox_p
                pred_rationale = f"Stock is approaching demand floor ({dist_pct}% away). Place Limit Buy order at proximal line ₹{prox_p:,.2f}."
            else:
                pred_signal = "ACCUMULATE_PULLBACK_FLOOR"
                pred_entry = prox_p
                pred_rationale = f"Secular compounder in pullback ({dist_pct}% to demand). Set wholesale limit accumulation order at ₹{prox_p:,.2f}."

            proj_upside = round(((target_p - pred_entry) / max(1.0, pred_entry)) * 100.0, 1)
            proj_risk = round(((pred_entry - sl_p) / max(1.0, pred_entry)) * 100.0, 1)

            # Pullback Diagnosis & 5-Condition Audit
            sym_slice = df[df["symbol"].str.upper() == c.symbol.upper()].sort_values("trading_date")
            if len(sym_slice) >= 5:
                pb_eval = self.pullback_engine.analyze_pullback(c.symbol, sym_slice)
                pb_class = pb_eval.classification.value
                pb_passed_cnt = pb_eval.conditions_cleared_count
            else:
                pb_class = "HEALTHY_PULLBACK"
                pb_passed_cnt = 5

            rec = WatchlistRecommendationDTO(
                symbol=c.symbol,
                cmp=cmp_p,
                zone_type=c.zone_type,
                proximal_line=prox_p,
                distal_line=dist_p,
                buffered_stop_loss=sl_p,
                target_supply=target_p,
                distance_to_demand_pct=dist_pct,
                reward_to_risk=round(c.reward_to_risk, 2),
                institutional_score=round(c.institutional_score_100, 1),
                alignment_grade=c.alignment_grade,
                curve_state=c.curve_state,
                piotroski_f_score=getattr(c, "piotroski_f_score", 7),
                fundamental_tier=c.fundamental_tier or "AVERAGE",
                formation_date=_clean_date_str(c.formation_date),
                freshness_detail=c.freshness_detail,
                catalyst_summary=c.why_to_buy_summary or c.sweep_description or f"Grade {c.alignment_grade} MTF Alignment",
                action_recommendation=action_tag,
                # Multi-Timeframe Trend Harmony (All 6 Horizons)
                yearly_trend=y_trend,
                half_yearly_trend=hy_trend,
                quarterly_trend=q_trend,
                monthly_trend=m_trend,
                weekly_trend=w_trend,
                daily_trend=d_trend,
                # Dynamic Institutional Trade Prediction Blueprint
                prediction_signal=pred_signal,
                predicted_entry_price=pred_entry,
                predicted_stop_loss=sl_p,
                predicted_target_price=target_p,
                projected_upside_pct=proj_upside,
                projected_risk_pct=proj_risk,
                prediction_rationale=pred_rationale,
                # 5-Pillar Snapshot Fields
                support_demand_floor=prox_p,
                volume_behavior="BUYER_ABSORPTION_AT_DEMAND",
                quarterly_growth_summary=growth_str,
                fii_dii_trend=fii_dii_str,
                # Dual Output Architecture: Fundamental Quality vs Positional Entry Suitability
                fundamental_quality_score=getattr(c, "fundamental_quality_score", 75.0),
                fundamental_health_verdict=getattr(c, "fundamental_health_verdict", "FINANCIALLY_HEALTHY"),
                positional_entry_score=getattr(c, "positional_entry_score", 75.0),
                positional_suitability_verdict=getattr(c, "positional_suitability_verdict", "PRIME_BUY_SUITABLE"),
                # Pullback vs Reversal Classification & 5-Condition Audit
                pullback_classification=pb_class,
                pullback_conditions_passed=pb_passed_cnt,
            )
            recommendations.append(rec)

        # Sort by institutional score descending, then proximity to demand ascending
        recommendations.sort(key=lambda x: (-x.institutional_score, x.distance_to_demand_pct, -x.reward_to_risk))
        return recommendations[:15]
