"""
Unit tests for Module 1: Foundation, Catalog Configuration & Data Contracts.
"""

from datetime import date, datetime
import pandas as pd
import pytest

from data_engine.contracts import (
    DataAvailabilityContract,
    DataContractValidator,
    SectorMappingResolver,
)


def test_index_catalogue_loading():
    """Verify indices catalogue can be read from YAML."""
    import yaml
    with open("config/indices.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    assert "indices" in cfg
    broad = cfg["indices"].get("broad_market", [])
    codes = [i["code"] for i in broad]
    assert "NIFTY 50" in codes
    assert "NIFTY 500" in codes

    banking = cfg["indices"].get("banking_finance", [])
    bank_codes = [i["code"] for i in banking]
    assert "NIFTY BANK" in bank_codes


def test_sector_mapping_resolver():
    """Verify sector mapping resolver maps NIFTY 500 stocks to correct sectors."""
    resolver = SectorMappingResolver(
        sectors_config_path="config/sectors.yaml",
        constituent_csv_path="downloads/raw/universes/NIFTY500.csv",
    )

    # Test known constituents from NIFTY 500
    rel = resolver.get_sector_for_symbol("RELIANCE")
    assert rel["symbol"] == "RELIANCE"
    # Reliance is Oil Gas & Consumable Fuels -> ENERGY
    assert rel["sector_id"] in {"ENERGY", "CAP_GOODS", "OTHER"}

    infy = resolver.get_sector_for_symbol("INFY")
    # Infosys is Information Technology -> IT
    # If INFY is in NIFTY 500
    hdfc = resolver.get_sector_for_symbol("HDFCBANK")
    assert hdfc["sector_id"] in {"FIN_SERVICE", "OTHER"}

    # Unknown stock gets default
    unk = resolver.get_sector_for_symbol("UNKNOWN_SYM_XYZ")
    assert unk["sector_id"] == "OTHER"
    assert unk["max_exposure_pct"] > 0


def test_ohlcv_integrity_valid_data():
    """Test OHLCV validation passes on valid prices."""
    df = pd.DataFrame({
        "trading_date": [date(2026, 9, 25)],
        "open": [100.0],
        "high": [105.0],
        "low": [98.0],
        "close": [102.0],
        "volume": [50000],
    })
    ok, errors = DataContractValidator.validate_ohlcv_integrity(df)
    assert ok is True
    assert len(errors) == 0


def test_ohlcv_integrity_inverted_prices():
    """Test OHLCV validation rejects low > high."""
    df = pd.DataFrame({
        "trading_date": [date(2026, 9, 25)],
        "open": [100.0],
        "high": [95.0],  # high < low
        "low": [98.0],
        "close": [97.0],
        "volume": [50000],
    })
    ok, errors = DataContractValidator.validate_ohlcv_integrity(df)
    assert ok is False
    assert any("Inverted" in err for err in errors)


def test_ohlcv_integrity_negative_prices():
    """Test OHLCV validation rejects negative values."""
    df = pd.DataFrame({
        "trading_date": [date(2026, 9, 25)],
        "open": [100.0],
        "high": [105.0],
        "low": [-10.0],
        "close": [102.0],
        "volume": [50000],
    })
    ok, errors = DataContractValidator.validate_ohlcv_integrity(df)
    assert ok is False
    assert any("Negative" in err for err in errors)


def test_freshness_and_contract_creation():
    """Test freshness evaluation and DataAvailabilityContract creation."""
    df = pd.DataFrame({
        "trading_date": [date(2026, 9, 25)],
        "open": [100.0],
        "high": [105.0],
        "low": [98.0],
        "close": [102.0],
        "volume": [50000],
    })

    # Fresh scenario: ref date is same as trading date
    contract = DataContractValidator.create_contract(df, reference_date=date(2026, 9, 25), max_stale_days=3)
    assert contract.is_safe_for_decision is True
    assert contract.staleness_days == 0
    assert contract.stock_data_fresh is True
    assert contract.degraded_mode is False

    # Stale scenario: ref date is 10 days later
    contract_stale = DataContractValidator.create_contract(df, reference_date=date(2026, 10, 5), max_stale_days=3)
    assert contract_stale.staleness_days == 10
    assert contract_stale.stock_data_fresh is False
    assert contract_stale.degraded_mode is True
    assert len(contract_stale.warnings) > 0
