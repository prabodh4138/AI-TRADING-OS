from datetime import date

import pandas as pd
import pytest

from data_engine.transformer.universe_transformer import UniverseTransformer


def _valid_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "universe_code": " nifty500 ",
                "universe_name": " NIFTY 500 ",
                "universe_type": " index ",
                "provider": " NSE Indices ",
                "symbol_code": " 20microns ",
                "effective_from": "2026-09-01",
                "effective_to": None,
            },
            {
                "universe_code": "nifty500",
                "universe_name": "NIFTY 500",
                "universe_type": "INDEX",
                "provider": "NSE Indices",
                "symbol_code": "360one",
                "effective_from": pd.Timestamp("2026-09-01"),
                "effective_to": "2026-09-30",
            },
        ]
    )


def test_transform_normalizes_codes_and_text():
    transformer = UniverseTransformer()

    result = transformer.transform(_valid_dataframe())

    assert result.loc[0, "universe_code"] == "NIFTY500"
    assert result.loc[0, "universe_name"] == "NIFTY 500"
    assert result.loc[0, "universe_type"] == "INDEX"
    assert result.loc[0, "provider"] == "NSE Indices"
    assert result.loc[0, "symbol_code"] == "20MICRONS"


def test_transform_converts_dates_to_python_date():
    transformer = UniverseTransformer()

    result = transformer.transform(_valid_dataframe())

    assert result.loc[0, "effective_from"] == date(2026, 9, 1)
    assert result.loc[0, "effective_to"] is None

    assert result.loc[1, "effective_from"] == date(2026, 9, 1)
    assert result.loc[1, "effective_to"] == date(2026, 9, 30)


def test_transform_preserves_expected_columns():
    transformer = UniverseTransformer()

    result = transformer.transform(_valid_dataframe())

    assert list(result.columns) == UniverseTransformer.OUTPUT_COLUMNS


def test_transform_resets_index():
    transformer = UniverseTransformer()

    df = _valid_dataframe()
    df.index = [10, 20]

    result = transformer.transform(df)

    assert list(result.index) == [0, 1]


def test_transform_records_returns_list_of_dicts():
    transformer = UniverseTransformer()

    records = transformer.transform_records(_valid_dataframe())

    assert isinstance(records, list)
    assert len(records) == 2
    assert isinstance(records[0], dict)

    assert records[0]["universe_code"] == "NIFTY500"
    assert records[0]["symbol_code"] == "20MICRONS"
    assert records[0]["effective_from"] == date(2026, 9, 1)


def test_none_dataframe_is_rejected():
    transformer = UniverseTransformer()

    with pytest.raises(ValueError, match="cannot be None"):
        transformer.transform(None)


def test_non_dataframe_input_is_rejected():
    transformer = UniverseTransformer()

    with pytest.raises(TypeError, match="pandas DataFrame"):
        transformer.transform([])


def test_missing_required_column_is_rejected():
    transformer = UniverseTransformer()

    df = _valid_dataframe().drop(columns=["symbol_code"])

    with pytest.raises(ValueError, match="Missing required columns"):
        transformer.transform(df)


def test_blank_optional_provider_becomes_none():
    transformer = UniverseTransformer()

    df = _valid_dataframe()
    df.loc[0, "provider"] = "   "

    result = transformer.transform(df)

    assert result.loc[0, "provider"] is None


def test_blank_effective_to_becomes_none():
    transformer = UniverseTransformer()

    df = _valid_dataframe()
    df.loc[0, "effective_to"] = ""

    result = transformer.transform(df)

    assert result.loc[0, "effective_to"] is None
