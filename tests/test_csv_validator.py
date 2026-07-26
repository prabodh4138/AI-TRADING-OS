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
            "OPEN": [100.0],
            "HIGH": [105.0],
            "LOW": [99.0],
            "CLOSE": [104.0],
            "LAST": [104.0],
            "PREVCLOSE": [98.0],
            "TOTTRDQTY": [100000],
            "TOTTRDVAL": [10500000.0],
            "TIMESTAMP": ["25-JUL-2026"],
        }
    )


def test_validate_success(
    validator,
    valid_dataframe,
):

    assert (
        validator.validate(valid_dataframe)
        is valid_dataframe
    )


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
        columns=["HIGH"]
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