"""
Unit tests for Multi-Timeframe GTF Engine (analytics/multi_timeframe_gtf.py).
Tests Monthly, Quarterly, Half-Yearly, and Yearly resampling, curve analysis, and alignment grading.
"""

from datetime import date, timedelta
import pandas as pd
import pytest

from analytics.multi_timeframe_gtf import (
    AlignmentGrade,
    CurveLocation,
    MultiTimeframeGTFEngine,
)


@pytest.fixture
def multi_month_sample_data():
    """Generates 90 days of synthetic daily bars spanning multiple months."""
    rows = []
    base_date = date(2025, 1, 1)

    for i in range(90):
        t_date = base_date + timedelta(days=i)
        p = 100.0 + (i * 0.5)  # Steady upward trend
        rows.append({
            "trading_date": t_date,
            "open": p - 0.2,
            "high": p + 1.0,
            "low": p - 0.5,
            "close": p,
            "volume": 20000,
            "symbol": "GROWTH_STOCK",
        })

    return pd.DataFrame(rows)


def test_multi_timeframe_resampling(multi_month_sample_data):
    """Verifies resampling from daily into Monthly, Quarterly, Half-Yearly, and Yearly bars."""
    engine = MultiTimeframeGTFEngine()
    tf_dict = engine.resample_timeframes(multi_month_sample_data)

    assert "Daily" in tf_dict
    assert "Monthly" in tf_dict
    assert "Quarterly" in tf_dict
    assert "Half-Yearly" in tf_dict
    assert "Yearly" in tf_dict

    assert len(tf_dict["Monthly"]) >= 2
    assert len(tf_dict["Quarterly"]) >= 1
    assert len(tf_dict["Yearly"]) >= 1


def test_curve_location_and_alignment(multi_month_sample_data):
    """Verifies that Location on the Curve and Alignment Grade are computed correctly."""
    engine = MultiTimeframeGTFEngine()
    alignment = engine.evaluate_stock_alignment(multi_month_sample_data, symbol="GROWTH_STOCK")

    assert alignment.symbol == "GROWTH_STOCK"
    assert 0.0 <= alignment.curve_location_pct <= 100.0
    assert alignment.curve_state in {
        CurveLocation.VERY_LOW,
        CurveLocation.LOW,
        CurveLocation.EQUILIBRIUM,
        CurveLocation.HIGH,
        CurveLocation.VERY_HIGH,
    }
    assert alignment.alignment_grade in {
        AlignmentGrade.GRADE_A_PLUS,
        AlignmentGrade.GRADE_A,
        AlignmentGrade.GRADE_B,
        AlignmentGrade.GRADE_C,
        AlignmentGrade.AVOID_TRAP,
    }
    assert 0.0 <= alignment.alignment_score <= 100.0


def test_macro_market_condition(multi_month_sample_data):
    """Verifies NIFTY 50 macro market posture evaluation."""
    engine = MultiTimeframeGTFEngine()
    posture = engine.evaluate_macro_market_condition(multi_month_sample_data, benchmark_symbol="GROWTH_STOCK")

    assert posture.overall_posture in {
        "AGGRESSIVE_BULLISH",
        "MODERATE_BULLISH",
        "DEFENSIVE_CHOPPY",
        "BEARISH_DISTRIBUTION",
    }
    assert posture.sizing_recommendation in {1.0, 0.75, 0.50, 0.0}
    assert len(posture.summary_notes) >= 1
