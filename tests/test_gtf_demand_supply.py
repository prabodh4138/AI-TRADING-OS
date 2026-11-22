"""
Unit tests for Pure Institutional Demand & Supply Zone Engine (GTF Method)
and dedicated Machine Learning Predictor (analytics/demand_supply_zones.py, ai/demand_supply_ml.py, scanner/gtf_scanner.py).
"""

from datetime import date, timedelta
import pandas as pd
import pytest

from ai.demand_supply_ml import MLDemandSupplyPredictor
from analytics.demand_supply_zones import (
    DemandSupplyZoneEngine,
    PriceLocation,
    ZoneFreshness,
    ZoneType,
)
from scanner.gtf_scanner import GTFTradeScanner


@pytest.fixture
def synthetic_dbr_pattern_data():
    """
    Creates a clean DBR (Drop-Base-Rally) Demand Zone pattern:
    - Days 0-2: Drop (Red candles)
    - Days 3-4: Base (2 Boring candles, small bodies)
    - Day 5: Rally (Green Exciting candle exploding above base)
    - Days 6-10: Pullback testing proximal line (Entry!)
    """
    rows = []
    base_date = date(2026, 1, 1)

    # 1. Leg-in: Drop
    rows.append({"trading_date": base_date + timedelta(days=0), "open": 105.0, "high": 106.0, "low": 98.0, "close": 99.0, "volume": 10000})
    rows.append({"trading_date": base_date + timedelta(days=1), "open": 99.0, "high": 100.0, "low": 92.0, "close": 93.0, "volume": 12000})

    # 2. Base: 2 Boring candles around 90-93
    rows.append({"trading_date": base_date + timedelta(days=2), "open": 92.5, "high": 93.0, "low": 90.0, "close": 92.2, "volume": 8000}) # range 3.0, body 0.3 -> boring
    rows.append({"trading_date": base_date + timedelta(days=3), "open": 92.2, "high": 93.5, "low": 90.5, "close": 92.8, "volume": 7500}) # range 3.0, body 0.6 -> boring

    # 3. Leg-out: Explosive Green Rally
    rows.append({"trading_date": base_date + timedelta(days=4), "open": 93.0, "high": 102.0, "low": 92.5, "close": 101.5, "volume": 35000}) # range 9.5, body 8.5 -> exciting!

    # 4. Continuation & pullback to proximal line
    rows.append({"trading_date": base_date + timedelta(days=5), "open": 101.5, "high": 105.0, "low": 101.0, "close": 104.0, "volume": 20000})
    rows.append({"trading_date": base_date + timedelta(days=6), "open": 103.5, "high": 104.0, "low": 98.0, "close": 99.0, "volume": 15000})
    rows.append({"trading_date": base_date + timedelta(days=7), "open": 98.5, "high": 99.0, "low": 93.0, "close": 93.2, "volume": 18000}) # Pulled back to proximal line 92.8!

    df = pd.DataFrame(rows)
    df["symbol"] = "TEST_DBR"
    return df


def test_dbr_demand_zone_detection(synthetic_dbr_pattern_data):
    """Verifies that DBR pattern is detected with exact Proximal and Distal boundaries."""
    engine = DemandSupplyZoneEngine()
    demand_zones, _ = engine.find_all_zones(synthetic_dbr_pattern_data, symbol="TEST_DBR")

    assert len(demand_zones) >= 1
    d_zone = demand_zones[0]
    assert d_zone.zone_type == ZoneType.DEMAND_DBR
    assert d_zone.proximal_line == 92.8  # Highest body of the base
    assert d_zone.distal_line == 90.0    # Lowest wick of the base
    assert d_zone.zone_width == round(92.8 - 90.0, 2)
    assert d_zone.base_candle_count == 2
    assert d_zone.odds_enhancer_score >= 6.0


def test_gtf_dedicated_ml_model(synthetic_dbr_pattern_data):
    """Verifies dedicated MLDemandSupplyPredictor produces calibrated probabilities and uncertainty."""
    engine = DemandSupplyZoneEngine()
    demand_zones, _ = engine.find_all_zones(synthetic_dbr_pattern_data, symbol="TEST_DBR")
    assert len(demand_zones) >= 1

    ml_predictor = MLDemandSupplyPredictor()
    pred = ml_predictor.predict_zone(demand_zones[0])

    assert 0.0 <= pred.success_probability <= 1.0
    assert 0.0 <= pred.uncertainty_score <= 1.0
    assert pred.conviction_tier in {"VERY_HIGH", "HIGH", "MODERATE", "AVOID"}
    assert pred.reward_to_risk >= 1.0
    assert pred.model_score > 0.0


def test_gtf_scanner_end_to_end(synthetic_dbr_pattern_data):
    """Verifies GTFTradeScanner scans dataset and generates structured report."""
    scanner = GTFTradeScanner(min_odds_score=5.0, min_ml_probability=0.50)
    result = scanner.scan_universe(synthetic_dbr_pattern_data)

    assert result.total_symbols_scanned == 1
    assert result.total_demand_zones_found >= 1
    output = result.format_terminal_report()
    assert "GTF INSTITUTIONAL MULTI-TIMEFRAME DEMAND & SUPPLY SCANNER" in output
    assert "GTF INSTITUTIONAL EXECUTION MANDATE" in output


def test_gtf_zone_test_dates_and_penetration():
    """
    Verifies that the engine records the exact date when a zone is tested,
    tracks distinct test events, and measures penetration depth.
    """
    base_date = date(2026, 2, 1)
    rows = [
        # Leg-in drop
        {"trading_date": base_date + timedelta(days=0), "open": 105.0, "high": 106.0, "low": 98.0, "close": 99.0, "volume": 10000},
        # Base (Boring candle)
        {"trading_date": base_date + timedelta(days=1), "open": 92.0, "high": 93.0, "low": 90.0, "close": 92.5, "volume": 8000},
        # Leg-out rally (Exciting candle, formation date = 2026-02-03)
        {"trading_date": base_date + timedelta(days=2), "open": 93.0, "high": 105.0, "low": 93.0, "close": 104.0, "volume": 30000},
        # Day 3: Away
        {"trading_date": base_date + timedelta(days=3), "open": 104.0, "high": 106.0, "low": 102.0, "close": 105.0, "volume": 15000},
        # Day 4: Pullback into zone on 2026-02-05 (low=91.0 tests proximal=92.5)
        {"trading_date": base_date + timedelta(days=4), "open": 102.0, "high": 102.5, "low": 91.0, "close": 94.0, "volume": 22000},
        # Day 5: Bounces out of zone on 2026-02-06
        {"trading_date": base_date + timedelta(days=5), "open": 94.0, "high": 99.0, "low": 94.0, "close": 98.5, "volume": 16000},
        # Day 6: Second test on 2026-02-07 (low=90.5 enters zone again!)
        {"trading_date": base_date + timedelta(days=6), "open": 98.0, "high": 98.5, "low": 90.5, "close": 95.0, "volume": 25000},
    ]
    df = pd.DataFrame(rows)
    df["symbol"] = "TEST_RETEST"

    engine = DemandSupplyZoneEngine()
    demand_zones, _ = engine.find_all_zones(df, symbol="TEST_RETEST")

    assert len(demand_zones) >= 1
    zone = demand_zones[0]

    # Formation date check
    assert zone.formation_date == base_date + timedelta(days=2)  # 2026-02-03

    # Freshness & touch count check
    assert zone.touch_count == 2
    assert zone.freshness == ZoneFreshness.TESTED_2X

    # Exact test dates verification
    test_1_date = base_date + timedelta(days=4)  # 2026-02-05
    test_2_date = base_date + timedelta(days=6)  # 2026-02-07
    assert test_1_date in zone.test_dates
    assert test_2_date in zone.test_dates
    assert zone.last_tested_date == test_2_date

    # Deepest penetration check
    assert zone.deepest_penetration_px == 90.5
    # proximal = 92.5, distal = 90.0, width = 2.5
    # penetration = (92.5 - 90.5) / 2.5 = 2.0 / 2.5 = 80.0%
    assert zone.penetration_pct == pytest.approx(80.0, 0.1)

    # Serialization check
    d = zone.to_dict()
    assert d["last_tested_date"] == str(test_2_date)
    assert len(d["test_dates"]) == 2
    assert "TESTED_2X" in d["freshness_detail"]

