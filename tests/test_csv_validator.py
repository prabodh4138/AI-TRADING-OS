import pandas as pd
import pytest

from data_engine.validator.csv_validator import (
    CSVValidationException,
    CSVValidator,
)


@pytest.fixture
def validator():
    return CSVValidator()


@pytest.fixture
def valid_dataframe():
    return pd.DataFrame(
        {
            "SYMBOL": ["ABC"],
            "SERIES": ["EQ"],
            "DATE1": ["25-JUL-2026"],
            "PREV_CLOSE": [98.0],
            "OPEN_PRICE": [100.0],
            "HIGH_PRICE": [105.0],
            "LOW_PRICE": [99.0],
            "LAST_PRICE": [104.0],
            "CLOSE_PRICE": [104.0],
            "AVG_PRICE": [102.0],
            "TTL_TRD_QNTY": [100000],
            "TURNOVER_LACS": [105.0],
            "NO_OF_TRADES": [500],
            "DELIV_QTY": [70000],
            "DELIV_PER": [70.0],
        }
    )


def test_validate_success(
    validator,
    valid_dataframe,
):
    result = validator.validate(valid_dataframe)

    pd.testing.assert_frame_equal(
        result,
        valid_dataframe,
    )

    assert result is not valid_dataframe


def test_empty_dataframe(
    validator,
):
    dataframe = pd.DataFrame()

    with pytest.raises(
        CSVValidationException
    ):
        validator.validate_not_empty(
            dataframe
        )


def test_missing_required_column(
    validator,
    valid_dataframe,
):
    dataframe = valid_dataframe.drop(
        columns=["HIGH_PRICE"]
    )

    with pytest.raises(
        CSVValidationException
    ):
        validator.validate_required_columns(
            dataframe
        )


def test_duplicate_columns(
    validator,
):
    dataframe = pd.DataFrame(
        [[1, 2]],
        columns=[
            "OPEN",
            "OPEN",
        ],
    )

    with pytest.raises(
        CSVValidationException
    ):
        validator.validate_duplicate_columns(
            dataframe
        )


def test_null_values(
    validator,
    valid_dataframe,
):
    dataframe = valid_dataframe.copy()

    dataframe.loc[
        0,
        "SYMBOL",
    ] = None

    with pytest.raises(
        CSVValidationException
    ):
        validator.validate_null_values(
            dataframe
        )


def test_minimum_rows(
    validator,
    valid_dataframe,
):
    dataframe = valid_dataframe.iloc[0:0]

    with pytest.raises(
        CSVValidationException
    ):
        validator.validate_minimum_rows(
            dataframe
        )


def test_column_count(
    validator,
    valid_dataframe,
):
    dataframe = valid_dataframe[
        [
            "SYMBOL",
            "SERIES",
        ]
    ]

    with pytest.raises(
        CSVValidationException
    ):
        validator.validate_column_count(
            dataframe
        )