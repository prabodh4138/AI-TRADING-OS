import pandas as pd
import pytest

from data_engine.validator.symbol_validator import SymbolValidator


@pytest.fixture
def validator():
    return SymbolValidator()


@pytest.fixture
def valid_symbol_dataframe():
    return pd.DataFrame(
        {
            "SYMBOL": ["ABC", "XYZ"],
            "NAME OF COMPANY": [
                "ABC Limited",
                "XYZ Limited",
            ],
            "SERIES": ["EQ", "EQ"],
            "DATE OF LISTING": [
                "01-JAN-2020",
                "02-FEB-2021",
            ],
            "PAID UP VALUE": [10, 10],
            "MARKET LOT": [1, 1],
            "ISIN NUMBER": [
                "INE000A01001",
                "INE000B01002",
            ],
            "FACE VALUE": [10, 10],
        }
    )


def test_valid_symbol_master_passes(
    validator,
    valid_symbol_dataframe,
):
    result = validator.validate(
        valid_symbol_dataframe
    )

    assert result is valid_symbol_dataframe
    assert validator.validation_result().success is True
    assert (
        validator.validation_result().rows_checked
        == 2
    )


def test_duplicate_symbol_is_rejected(
    validator,
    valid_symbol_dataframe,
):
    dataframe = valid_symbol_dataframe.copy()

    dataframe.loc[1, "SYMBOL"] = "ABC"

    with pytest.raises(
        ValueError,
        match="Duplicate SYMBOL values found",
    ):
        validator.validate(dataframe)


def test_duplicate_isin_is_rejected(
    validator,
    valid_symbol_dataframe,
):
    dataframe = valid_symbol_dataframe.copy()

    dataframe.loc[1, "ISIN NUMBER"] = "INE000A01001"

    with pytest.raises(
        ValueError,
        match="Duplicate ISIN NUMBER values found",
    ):
        validator.validate(dataframe)


def test_duplicate_isin_with_whitespace_and_case_is_rejected(
    validator,
    valid_symbol_dataframe,
):
    dataframe = valid_symbol_dataframe.copy()

    dataframe.loc[0, "ISIN NUMBER"] = "ine000a01001"
    dataframe.loc[1, "ISIN NUMBER"] = " INE000A01001 "

    with pytest.raises(
        ValueError,
        match="Duplicate ISIN NUMBER values found",
    ):
        validator.validate(dataframe)


def test_missing_required_column_is_rejected(
    validator,
    valid_symbol_dataframe,
):
    dataframe = valid_symbol_dataframe.drop(
        columns=["ISIN NUMBER"]
    )

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        validator.validate(dataframe)


def test_blank_isin_is_rejected(
    validator,
    valid_symbol_dataframe,
):
    dataframe = valid_symbol_dataframe.copy()

    dataframe.loc[0, "ISIN NUMBER"] = ""

    with pytest.raises(
        ValueError,
        match="Column 'ISIN NUMBER' contains",
    ):
        validator.validate(dataframe)
