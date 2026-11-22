from datetime import date

import pandas as pd
import pytest

from data_engine.validator.universe_csv_validator import UniverseCSVValidator


def _valid_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "universe_code": "NIFTY500",
                "universe_name": "NIFTY 500",
                "universe_type": "INDEX",
                "provider": "NSE Indices",
                "symbol_code": "20MICRONS",
                "effective_from": "2026-09-01",
                "effective_to": None,
            },
            {
                "universe_code": "NIFTY500",
                "universe_name": "NIFTY 500",
                "universe_type": "INDEX",
                "provider": "NSE Indices",
                "symbol_code": "360ONE",
                "effective_from": "2026-09-01",
                "effective_to": None,
            },
        ]
    )


def test_valid_universe_dataframe_passes():
    validator = UniverseCSVValidator()

    result = validator.validate(_valid_dataframe())

    assert len(result) == 2
    assert validator.validation_result().success is True
    assert validator.validation_result().rows_checked == 2


def test_missing_required_column_is_rejected():
    validator = UniverseCSVValidator()
    df = _valid_dataframe().drop(columns=["symbol_code"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validator.validate(df)


def test_blank_symbol_code_is_rejected():
    validator = UniverseCSVValidator()
    df = _valid_dataframe()
    df.loc[0, "symbol_code"] = ""

    with pytest.raises(ValueError, match="symbol_code"):
        validator.validate(df)


def test_blank_universe_code_is_rejected():
    validator = UniverseCSVValidator()
    df = _valid_dataframe()
    df.loc[0, "universe_code"] = "   "

    with pytest.raises(ValueError, match="universe_code"):
        validator.validate(df)


def test_blank_universe_name_is_rejected():
    validator = UniverseCSVValidator()
    df = _valid_dataframe()
    df.loc[0, "universe_name"] = ""

    with pytest.raises(ValueError, match="universe_name"):
        validator.validate(df)


def test_blank_effective_from_is_rejected():
    validator = UniverseCSVValidator()
    df = _valid_dataframe()
    df.loc[0, "effective_from"] = ""

    with pytest.raises(ValueError, match="effective_from"):
        validator.validate(df)


def test_invalid_effective_from_date_is_rejected():
    validator = UniverseCSVValidator()
    df = _valid_dataframe()
    df.loc[0, "effective_from"] = "NOT-A-DATE"

    with pytest.raises(ValueError, match="effective_from"):
        validator.validate(df)


def test_invalid_effective_to_date_is_rejected():
    validator = UniverseCSVValidator()
    df = _valid_dataframe()
    df.loc[0, "effective_to"] = "NOT-A-DATE"

    with pytest.raises(ValueError, match="effective_to"):
        validator.validate(df)


def test_effective_to_before_effective_from_is_rejected():
    validator = UniverseCSVValidator()
    df = _valid_dataframe()
    df.loc[0, "effective_from"] = "2026-09-10"
    df.loc[0, "effective_to"] = "2026-09-01"

    with pytest.raises(
        ValueError,
        match="effective_to cannot be earlier",
    ):
        validator.validate(df)


def test_duplicate_membership_is_rejected():
    validator = UniverseCSVValidator()
    df = pd.concat(
        [_valid_dataframe().iloc[[0]], _valid_dataframe().iloc[[0]]],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError,
        match="Duplicate universe membership",
    ):
        validator.validate(df)


def test_open_ended_membership_is_valid():
    validator = UniverseCSVValidator()
    df = _valid_dataframe()
    df.loc[0, "effective_to"] = None

    result = validator.validate(df)

    assert result.loc[0, "effective_to"] is None


def test_completed_membership_is_valid():
    validator = UniverseCSVValidator()
    df = _valid_dataframe()
    df.loc[0, "effective_from"] = "2026-01-01"
    df.loc[0, "effective_to"] = "2026-09-30"

    result = validator.validate(df)

    assert result.loc[0, "effective_from"] == "2026-01-01"
    assert result.loc[0, "effective_to"] == "2026-09-30"
