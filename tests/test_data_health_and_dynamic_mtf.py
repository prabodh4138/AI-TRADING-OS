"""
Unit & Integration Tests for Data Health, CMP Reconciliation, and Dynamic MTF Demand Zone Engine.
"""

from datetime import date, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from analytics.dynamic_mtf_zones import (
    DynamicMTFZoneEngine,
    DynamicMTFZoneMatrix,
    DynamicProximityStatus,
    DynamicZoneRecord,
    TimeframeHorizon,
)
from data_engine.data_health import (
    DataHealthEngine,
    DataHealthReport,
    DatabaseHealthSummary,
    SymbolPriceMismatch,
)


@pytest.fixture
def sample_multi_month_df() -> pd.DataFrame:
    """Generates 200 trading days of synthetic OHLCV data for RELIANCE."""
    np.random.seed(42)
    start_date = date(2025, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(250)]
    # Filter weekends
    trading_dates = [d for d in dates if d.weekday() < 5][:180]

    rows = []
    price = 1200.0
    for idx, d in enumerate(trading_dates):
        # Create an institutional rally base rally around day 40-50
        if 40 <= idx <= 43:
            # Base candles
            o = price
            c = price + np.random.uniform(-2, 2)
            h = max(o, c) + 3
            l = min(o, c) - 3
        elif idx == 44:
            # Leg out exciting green
            o = price
            c = price + 35.0
            h = c + 5.0
            l = o - 2.0
            price = c
        else:
            shock = np.random.normal(0.5, 8.0)
            o = price
            c = price + shock
            h = max(o, c) + abs(np.random.normal(0, 5))
            l = min(o, c) - abs(np.random.normal(0, 5))
            price = c

        rows.append({
            "symbol": "RELIANCE",
            "series": "EQ",
            "trading_date": d,
            "open": round(o, 2),
            "high": round(h, 2),
            "low": round(l, 2),
            "close": round(c, 2),
            "volume": int(np.random.uniform(50000, 200000)),
        })

    return pd.DataFrame(rows)


class TestDataHealthEngine:
    def test_run_health_check_returns_report(self):
        engine = DataHealthEngine()
        report = engine.run_health_check()

        assert isinstance(report, DataHealthReport)
        assert 0.0 <= report.overall_health_score <= 100.0
        assert report.health_status in ["PRISTINE_HEALTH", "GOOD", "NEEDS_RECONCILIATION", "CRITICAL_MISMATCH"]
        assert isinstance(report.database_summary, DatabaseHealthSummary)
        assert isinstance(report.price_mismatches, list)
        assert len(report.reconciliation_recommendations) > 0

    def test_format_terminal_report_output(self):
        engine = DataHealthEngine()
        report = engine.run_health_check()
        formatted = report.format_terminal_report()

        assert "AI-TOS DATA HEALTH, CMP INTEGRITY & DATABASE RECONCILIATION AUDIT" in formatted
        assert "POSTGRESQL DATABASE REPOSITORY STATUS" in formatted
        assert "CURRENT MARKET PRICE (CMP) RECONCILIATION" in formatted
        assert "ACTIONABLE RECONCILIATION & REMEDIATION STEPS" in formatted

    def test_sync_bhavcopy_to_database_handles_missing_file_or_syncs(self):
        engine = DataHealthEngine(bhavcopy_csv_path="non_existent_bhavcopy.csv")
        res = engine.sync_bhavcopy_to_database()
        assert res["status"] == "ERROR"
        assert "not found" in res["message"]


class TestDynamicMTFZoneEngine:
    def test_resample_all_timeframes(self, sample_multi_month_df):
        engine = DynamicMTFZoneEngine()
        tf_map = engine.resample_all_timeframes(sample_multi_month_df)

        assert TimeframeHorizon.DAILY.value in tf_map
        assert TimeframeHorizon.MONTHLY.value in tf_map
        assert TimeframeHorizon.QUARTERLY.value in tf_map
        assert TimeframeHorizon.HALF_YEARLY.value in tf_map
        assert TimeframeHorizon.YEARLY.value in tf_map

        assert len(tf_map["Daily"]) == len(sample_multi_month_df)
        assert len(tf_map["Monthly"]) > 0
        assert len(tf_map["Quarterly"]) > 0

    def test_evaluate_symbol_zones(self, sample_multi_month_df):
        engine = DynamicMTFZoneEngine()
        mat = engine.evaluate_symbol_zones(symbol="RELIANCE", daily_df=sample_multi_month_df)

        assert isinstance(mat, DynamicMTFZoneMatrix)
        assert mat.symbol == "RELIANCE"
        assert mat.current_price > 0
        assert len(mat.all_active_zones) > 0
        assert 0.0 <= mat.macro_curve_location_pct <= 100.0
        assert mat.macro_curve_status in ["VERY_LOW", "LOW", "EQUILIBRIUM", "HIGH", "VERY_HIGH"]

        # Check zone record attributes
        z = mat.all_active_zones[0]
        assert isinstance(z, DynamicZoneRecord)
        assert z.proximal_line >= z.distal_line
        assert z.zone_width >= 0
        assert 0.0 <= z.ml_bounce_probability <= 100.0
        assert 0.0 <= z.institutional_footprint_score <= 100.0
        assert len(z.deep_understanding_thesis) > 0
        assert len(z.actionable_directive) > 0

    def test_format_terminal_matrix_output(self, sample_multi_month_df):
        engine = DynamicMTFZoneEngine()
        mat = engine.evaluate_symbol_zones(symbol="RELIANCE", daily_df=sample_multi_month_df)
        matrix_text = mat.format_terminal_matrix()

        assert "DYNAMIC MULTI-TIMEFRAME DEMAND ZONE MATRIX: RELIANCE" in matrix_text
        assert "Timeframe" in matrix_text
        assert "Proximal" in matrix_text
        assert "Distal" in matrix_text
        assert "DEEP UNDERSTANDING & INSTITUTIONAL ORDER FLOW THESIS" in matrix_text

    def test_scan_universe_dynamic_zones(self, sample_multi_month_df):
        # Duplicate dataframe for a second symbol
        tcs_df = sample_multi_month_df.copy()
        tcs_df["symbol"] = "TCS"
        tcs_df["close"] = tcs_df["close"] * 2.5
        tcs_df["open"] = tcs_df["open"] * 2.5
        tcs_df["high"] = tcs_df["high"] * 2.5
        tcs_df["low"] = tcs_df["low"] * 2.5

        universe_df = pd.concat([sample_multi_month_df, tcs_df], ignore_index=True)
        engine = DynamicMTFZoneEngine()
        res = engine.scan_universe_dynamic_zones(universe_df)

        assert "all_zones_records" in res
        assert "yearly_demand_stocks" in res
        assert "monthly_demand_stocks" in res
        assert "all_zones_df" in res
        assert len(res["all_zones_records"]) >= 2
        assert isinstance(res["all_zones_df"], pd.DataFrame)
        assert not res["all_zones_df"].empty
        assert "proximity_status" in res["all_zones_df"].columns
