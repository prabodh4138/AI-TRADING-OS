"""
Unit tests for Machine Learning Models (Sections 1, 4, 6, 7).
"""

import pytest
import numpy as np

from ai.ml_models import (
    MLMarketRegimeClassifier,
    MLModelEvaluator,
    MLStockOpportunityForecaster,
)


def test_ml_market_regime_classifier():
    """Verify ML regime classifier produces valid calibrated probabilities and entropy uncertainty."""
    clf = MLMarketRegimeClassifier()
    assert clf.is_trained is True

    bull_features = {
        "ret_5d": 3.0,
        "ret_20d": 6.0,
        "ret_50d": 12.0,
        "realised_vol_20d": 12.5,
        "atr_ratio": 1.0,
        "rsi14": 65.0,
        "ad_ratio": 2.2,
        "pct_above_20dma": 75.0,
    }

    pred = clf.predict_regime(bull_features)
    assert pred.predicted_regime in MLMarketRegimeClassifier.CLASSES
    assert 0.0 <= pred.confidence <= 100.0
    assert 0.0 <= pred.uncertainty <= 100.0

    # Probabilities must sum to ~1.0
    total_prob = sum(pred.probabilities.values())
    assert pytest.approx(total_prob, 0.01) == 1.0
    assert len(pred.feature_importances) == len(MLMarketRegimeClassifier.FEATURE_NAMES)


def test_ml_stock_opportunity_forecaster():
    """Verify ML stock opportunity forecaster produces alpha score and model uncertainty."""
    forecaster = MLStockOpportunityForecaster()
    assert forecaster.is_trained is True

    features = {
        "price_vs_ema20_pct": 2.5,
        "ema20_vs_ema50_pct": 1.8,
        "rsi14": 60.0,
        "adx14": 28.0,
        "macd_hist_norm": 0.5,
        "supertrend_dir": 1.0,
        "stock_vs_sector_strength": 3.5,
        "relative_volume": 1.4,
        "dist_to_resistance_pct": 4.0,
    }

    res = forecaster.forecast_stock("TCS", features)
    assert res.symbol == "TCS"
    assert 0.0 <= res.opportunity_probability <= 1.0
    assert 0.0 <= res.expected_alpha_score <= 100.0
    assert 0.0 <= res.model_uncertainty <= 100.0
    assert res.direction in {"BULLISH", "NEUTRAL", "BEARISH"}


def test_ml_model_calibration_evaluator():
    """Verify Brier Score and ROC-AUC computation for Section 7 validation."""
    y_true = [1, 1, 1, 0, 0, 0]
    y_prob = [0.9, 0.8, 0.7, 0.3, 0.2, 0.1]

    metrics = MLModelEvaluator.evaluate_calibration(y_true, y_prob)
    assert metrics["brier_score"] < 0.1  # Excellent calibration
    assert metrics["roc_auc"] == 1.0     # Perfect discrimination
    assert metrics["sample_size"] == 6
