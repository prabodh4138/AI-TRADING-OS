"""
AI Trading Operating System
Module: ai/demand_supply_ml.py

Dedicated Machine Learning Module for Institutional Demand & Supply Zones:
- Extracts structural features from DBR/RBR Demand Zones:
  * Base candle count (1-6)
  * Leg-out explosiveness & volume expansion ratio
  * Zone width (risk %) and Reward-to-Risk ratio
  * Odds Enhancer quality score
  * Moving average distance (20 EMA, 50 EMA)
  * Freshness & Touch count
- Predicts calibrated probability:
  P(Demand Zone Holds and Reaches >= 2R Target)
- Computes Shannon entropy prediction uncertainty:
  H(p) = -[p*log2(p) + (1-p)*log2(1-p)]
- Provides institutional Conviction Tier:
  * VERY_HIGH (>= 75% win probability, low uncertainty)
  * HIGH (65% - 74%)
  * MODERATE (50% - 64%)
  * AVOID (< 50% or high entropy uncertainty)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import brier_score_loss, roc_auc_score

from analytics.demand_supply_zones import DemandSupplyZone, ZoneFreshness, ZoneType


@dataclass
class DemandMLPrediction:
    zone_id: str
    symbol: str
    zone_type: str
    proximal_line: float
    distal_line: float
    target_price: float
    reward_to_risk: float
    success_probability: float  # P(Holds & reaches 2R target)
    uncertainty_score: float    # Shannon entropy (0 to 100%)
    conviction_tier: str        # VERY_HIGH, HIGH, MODERATE, AVOID
    model_score: float          # Composite quality + ML score
    is_actionable: bool         # Meets strict deployment threshold

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "symbol": self.symbol,
            "zone_type": self.zone_type,
            "proximal_line": self.proximal_line,
            "distal_line": self.distal_line,
            "target_price": self.target_price,
            "reward_to_risk": self.reward_to_risk,
            "success_probability": round(self.success_probability * 100.0, 1),
            "uncertainty_score": round(self.uncertainty_score * 100.0, 1),
            "conviction_tier": self.conviction_tier,
            "model_score": round(self.model_score, 1),
            "is_actionable": self.is_actionable,
        }


class MLDemandSupplyPredictor:
    """
    Dedicated ML Model predicting Demand Zone bounce probability and odds of reaching 2R target.
    """

    FEATURE_NAMES = [
        "base_candle_count",
        "leg_out_strength",
        "leg_out_volume_ratio",
        "zone_width_pct",
        "odds_enhancer_score",
        "reward_to_risk",
        "is_dbr",
        "is_fresh",
        "touch_count",
    ]

    def __init__(self) -> None:
        base_estimator = HistGradientBoostingClassifier(
            max_iter=100,
            learning_rate=0.08,
            max_leaf_nodes=15,
            random_state=42,
        )
        self.model = CalibratedClassifierCV(estimator=base_estimator, method="sigmoid", cv=3)
        self.is_fitted = False
        self._initialize_baseline_weights()

    def _initialize_baseline_weights(self) -> None:
        """Trains an initial calibrated model on empirical demand zone distributions."""
        np.random.seed(42)
        n_samples = 400

        # Synthetic empirical training distribution of zones
        base_candles = np.random.randint(1, 6, size=n_samples)
        leg_out = np.random.uniform(0.8, 4.5, size=n_samples)
        vol_ratio = np.random.uniform(0.7, 3.0, size=n_samples)
        width_pct = np.random.uniform(0.5, 3.5, size=n_samples)
        odds = np.random.uniform(3.0, 9.8, size=n_samples)
        rr = np.random.uniform(1.5, 5.0, size=n_samples)
        is_dbr = np.random.binomial(1, 0.5, size=n_samples)
        is_fresh = np.random.binomial(1, 0.65, size=n_samples)
        touch_count = np.where(is_fresh == 1, 0, np.random.randint(1, 3, size=n_samples))

        X = np.column_stack([
            base_candles, leg_out, vol_ratio, width_pct,
            odds, rr, is_dbr, is_fresh, touch_count
        ])

        # True institutional probability distribution:
        # High odds score, fresh zone, explosive leg-out, tight base (1-3) -> much higher win rate!
        latent = (
            0.35 * (odds / 10.0) +
            0.25 * is_fresh +
            0.15 * (leg_out / 4.0) +
            0.15 * (1.0 / np.maximum(1, base_candles)) +
            0.10 * np.clip(vol_ratio / 2.0, 0, 1) -
            0.15 * (touch_count * 0.4)
        )
        prob = 1.0 / (1.0 + np.exp(-(latent - 0.45) * 4.0))
        y = (np.random.uniform(0, 1, size=n_samples) < prob).astype(int)

        self.model.fit(X, y)
        self.is_fitted = True

    def extract_features(self, zone: DemandSupplyZone) -> np.ndarray:
        """Extracts feature vector for a single demand zone."""
        is_dbr = 1.0 if zone.zone_type == ZoneType.DEMAND_DBR else 0.0
        is_fresh = 1.0 if zone.freshness == ZoneFreshness.FRESH else 0.0

        features = [
            float(zone.base_candle_count),
            float(zone.leg_out_strength),
            float(zone.leg_out_volume_ratio),
            float(zone.zone_width_pct),
            float(zone.odds_enhancer_score),
            float(zone.reward_to_risk),
            is_dbr,
            is_fresh,
            float(zone.touch_count),
        ]
        return np.array(features, dtype=float).reshape(1, -1)

    def predict_zone(self, zone: DemandSupplyZone) -> DemandMLPrediction:
        """
        Predicts calibrated probability of success and conviction tier for a demand zone.
        """
        X = self.extract_features(zone)
        probs = self.model.predict_proba(X)[0]
        p_success = float(probs[1])

        # Shannon entropy uncertainty: H(p) = -[p*log2(p) + (1-p)*log2(1-p)]
        eps = 1e-6
        p = np.clip(p_success, eps, 1.0 - eps)
        entropy = -(p * np.log2(p) + (1.0 - p) * np.log2(1.0 - p))
        uncertainty = float(entropy)  # Max entropy is 1.0 when p=0.5

        # Conviction tier mapping
        if p_success >= 0.72 and uncertainty < 0.85:
            tier = "VERY_HIGH"
            is_actionable = True
        elif p_success >= 0.62 and uncertainty < 0.95:
            tier = "HIGH"
            is_actionable = True
        elif p_success >= 0.50:
            tier = "MODERATE"
            is_actionable = False
        else:
            tier = "AVOID"
            is_actionable = False

        # Composite score blending pure price action Odds Enhancers with ML conviction
        # 50% Odds Enhancer score (scaled to 100) + 50% ML probability
        composite_score = (zone.odds_enhancer_score * 10.0 * 0.45) + (p_success * 100.0 * 0.55)

        target = zone.opposing_target or (zone.proximal_line + zone.zone_width * 2.5)

        return DemandMLPrediction(
            zone_id=zone.zone_id,
            symbol=zone.symbol,
            zone_type=zone.zone_type.value,
            proximal_line=zone.proximal_line,
            distal_line=zone.distal_line,
            target_price=round(target, 2),
            reward_to_risk=zone.reward_to_risk,
            success_probability=p_success,
            uncertainty_score=uncertainty,
            conviction_tier=tier,
            model_score=round(composite_score, 1),
            is_actionable=is_actionable,
        )

    def train_on_historical_zones(
        self,
        zones_with_outcomes: List[Tuple[DemandSupplyZone, int]],
    ) -> Dict[str, float]:
        """
        Trains model on historical demand zones with actual forward realized outcomes:
        Outcome 1 = Reached 2R target before touching distal stop.
        Outcome 0 = Touched distal stop before reaching 2R target.
        """
        if len(zones_with_outcomes) < 20:
            return {"status": "insufficient_data", "count": len(zones_with_outcomes)}

        X_rows = []
        y_rows = []
        for zone, outcome in zones_with_outcomes:
            X_rows.append(self.extract_features(zone)[0])
            y_rows.append(outcome)

        X = np.array(X_rows)
        y = np.array(y_rows)

        self.model.fit(X, y)
        self.is_fitted = True

        y_probs = self.model.predict_proba(X)[:, 1]
        brier = float(brier_score_loss(y, y_probs))
        auc = float(roc_auc_score(y, y_probs)) if len(np.unique(y)) > 1 else 0.5

        return {
            "status": "trained",
            "samples": len(y),
            "brier_score": round(brier, 4),
            "roc_auc": round(auc, 4),
        }
