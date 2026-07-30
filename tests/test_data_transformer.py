"""
=========================================================
AI Trading OS

Test Module
------------
test_data_transformer.py

Purpose
-------
Unit tests for the enterprise DataTransformer.

Author
------
AI Trading OS
=========================================================
"""

from __future__ import annotations

import logging

import pandas as pd

from data_engine.transformer.data_transformer import (
    DataTransformer,
)


class TestDataTransformer:
    """
    Unit tests for DataTransformer.
    """

    def setup_method(self) -> None:
        """
        Create reusable objects for each test.
        """
        self.logger = logging.getLogger(
            "test_data_transformer"
        )

        self.transformer = DataTransformer(
            logger=self.logger
        )

        self.sample_dataframe = pd.DataFrame(
            {
                " SYMBOL ": [
                    " RELIANCE ",
                    " TCS ",
                ],
                "SERIES": [
                    " EQ ",
                    " EQ ",
                ],
                "trading_date": [
                    "24-Jul-2026",
                    "25-Jul-2026",
                ],
                "OPEN": [
                    "1500.50",
                    "3800.00",
                ],
                "HIGH": [
                    "1525.00",
                    "3850.00",
                ],
                "LOW": [
                    "1495.00",
                    "3795.00",
                ],
                "CLOSE": [
                    "1510.25",
                    "3825.75",
                ],
                "LAST": [
                    "1511.00",
                    "3826.00",
                ],
                "PREVCLOSE": [
                    "1498.50",
                    "3790.50",
                ],
                "TOTTRDQTY": [
                    "150000",
                    "98000",
                ],
                "TOTTRDVAL": [
                    "225000000",
                    "375000000",
                ],
            }
        )

    def test_dataframe_created(
        self,
    ) -> None:
        """
        Verify sample dataframe creation.
        """
        assert not self.sample_dataframe.empty

        assert len(
            self.sample_dataframe
        ) == 2

    def test_transformer_created(
        self,
    ) -> None:
        """
        Verify DataTransformer initialization.
        """
        assert self.transformer is not None

        assert isinstance(
            self.transformer,
            DataTransformer,
        )
    def test_normalize_columns(
        self,
    ) -> None:
        """
        Verify dataframe column normalization.
        """
        transformed_df = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        expected_columns = [
            "symbol",
            "series",
            "trading_date",
            "open",
            "high",
            "low",
            "close",
            "last",
            "prevclose",
            "tottrdqty",
            "tottrdval",
        ]

        assert list(
            transformed_df.columns
        ) == expected_columns

    def test_normalize_columns_duplicate_names(
        self,
    ) -> None:
        """
        Verify duplicate normalized column names
        raise ValueError.
        """
        duplicate_df = pd.DataFrame(
            columns=[
                "Close Price",
                "Close-Price",
            ]
        )

        try:
            self.transformer._normalize_columns(
                duplicate_df
            )

            assert False, (
                "Expected ValueError was not raised."
            )

        except ValueError:
            assert True

    def test_normalize_columns_original_dataframe_unchanged(
        self,
    ) -> None:
        """
        Verify original dataframe is not modified.
        """
        original_columns = list(
            self.sample_dataframe.columns
        )

        self.transformer._normalize_columns(
            self.sample_dataframe
        )

        assert list(
            self.sample_dataframe.columns
        ) == original_columns
    def test_clean_strings(
        self,
    ) -> None:
        """
        Verify string cleaning.
        """
        normalized_df = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        cleaned_df = (
            self.transformer._clean_strings(
                normalized_df
            )
        )

        assert cleaned_df.loc[0, "symbol"] == "RELIANCE"
        assert cleaned_df.loc[1, "symbol"] == "TCS"

        assert cleaned_df.loc[0, "series"] == "EQ"
        assert cleaned_df.loc[1, "series"] == "EQ"

    def test_clean_strings_multiple_spaces(
        self,
    ) -> None:
        """
        Verify multiple spaces are collapsed.
        """
        dataframe = pd.DataFrame(
            {
                "SYMBOL": [
                    "ABC     LTD",
                ],
                "SERIES": [
                    " EQ ",
                ],
            }
        )

        dataframe = (
            self.transformer._normalize_columns(
                dataframe
            )
        )

        cleaned_df = (
            self.transformer._clean_strings(
                dataframe
            )
        )

        assert (
            cleaned_df.loc[0, "symbol"]
            == "ABC LTD"
        )

        assert (
            cleaned_df.loc[0, "series"]
            == "EQ"
        )

    def test_clean_strings_blank_to_na(
        self,
    ) -> None:
        """
        Verify blank strings become pandas NA.
        """
        dataframe = pd.DataFrame(
            {
                "SYMBOL": [
                    "",
                ],
                "SERIES": [
                    "     ",
                ],
            }
        )

        dataframe = (
            self.transformer._normalize_columns(
                dataframe
            )
        )

        cleaned_df = (
            self.transformer._clean_strings(
                dataframe
            )
        )

        assert pd.isna(
            cleaned_df.loc[0, "symbol"]
        )

        assert pd.isna(
            cleaned_df.loc[0, "series"]
        )

    def test_clean_strings_missing_columns(
        self,
    ) -> None:
        """
        Verify missing configured columns
        do not raise an exception.
        """
        dataframe = pd.DataFrame(
            {
                "company": [
                    "ABC",
                ],
            }
        )

        cleaned_df = (
            self.transformer._clean_strings(
                dataframe
            )
        )

        assert "company" in cleaned_df.columns

    def test_clean_strings_original_dataframe_unchanged(
        self,
    ) -> None:
        """
        Verify original dataframe
        remains unchanged.
        """
        normalized_df = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        original_df = normalized_df.copy(
            deep=True
        )

        self.transformer._clean_strings(
            normalized_df
        )

        pd.testing.assert_frame_equal(
            normalized_df,
            original_df,
        )
    def test_convert_numeric_columns(
        self,
    ) -> None:
        """
        Verify numeric column conversion.
        """
        normalized_df = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        converted_df = (
            self.transformer._convert_numeric_columns(
                normalized_df
            )
        )

        assert pd.api.types.is_numeric_dtype(
            converted_df["open"]
        )

        assert pd.api.types.is_numeric_dtype(
            converted_df["close"]
        )

        assert converted_df.loc[0, "open"] == 1500.50
        assert converted_df.loc[1, "close"] == 3825.75

    def test_convert_numeric_columns_invalid_values(
        self,
    ) -> None:
        """
        Verify invalid numeric values become NaN.
        """
        dataframe = pd.DataFrame(
            {
                "OPEN": [
                    "ABC",
                ],
                "HIGH": [
                    "100",
                ],
            }
        )

        dataframe = (
            self.transformer._normalize_columns(
                dataframe
            )
        )

        converted_df = (
            self.transformer._convert_numeric_columns(
                dataframe
            )
        )

        assert pd.isna(
            converted_df.loc[0, "open"]
        )

        assert converted_df.loc[0, "high"] == 100.0

    def test_convert_numeric_columns_missing_columns(
        self,
    ) -> None:
        """
        Verify missing numeric columns
        do not raise an exception.
        """
        dataframe = pd.DataFrame(
            {
                "symbol": [
                    "ABC",
                ],
            }
        )

        converted_df = (
            self.transformer._convert_numeric_columns(
                dataframe
            )
        )

        assert "symbol" in converted_df.columns

    def test_convert_date_columns(
        self,
    ) -> None:
        """
        Verify date column conversion.
        """
        normalized_df = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        converted_df = (
            self.transformer._convert_date_columns(
                normalized_df
            )
        )

        assert pd.api.types.is_datetime64_any_dtype(
            converted_df["trading_date"]
        )

    def test_convert_date_columns_invalid_date(
        self,
    ) -> None:
        """
        Verify invalid dates become NaT.
        """
        dataframe = pd.DataFrame(
            {
                "trading_date": [
                    "Invalid Date",
                ],
            }
        )

        dataframe = (
            self.transformer._normalize_columns(
                dataframe
            )
        )

        converted_df = (
            self.transformer._convert_date_columns(
                dataframe
            )
        )

        assert pd.isna(
            converted_df.loc[0, "trading_date"]
        )

    def test_convert_date_columns_missing_columns(
        self,
    ) -> None:
        """
        Verify missing date columns
        do not raise an exception.
        """
        dataframe = pd.DataFrame(
            {
                "symbol": [
                    "ABC",
                ],
            }
        )

        converted_df = (
            self.transformer._convert_date_columns(
                dataframe
            )
        )

        assert "symbol" in converted_df.columns

    def test_convert_numeric_columns_original_dataframe_unchanged(
        self,
    ) -> None:
        """
        Verify original dataframe remains unchanged
        after numeric conversion.
        """
        normalized_df = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        original_df = normalized_df.copy(
            deep=True
        )

        self.transformer._convert_numeric_columns(
            normalized_df
        )

        pd.testing.assert_frame_equal(
            normalized_df,
            original_df,
        )

    def test_convert_date_columns_original_dataframe_unchanged(
        self,
    ) -> None:
        """
        Verify original dataframe remains unchanged
        after date conversion.
        """
        normalized_df = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        original_df = normalized_df.copy(
            deep=True
        )

        self.transformer._convert_date_columns(
            normalized_df
        )

        pd.testing.assert_frame_equal(
            normalized_df,
            original_df,
        )
    def test_add_derived_columns(
        self,
    ) -> None:
        """
        Verify derived columns are added.
        """
        normalized_df = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        derived_df = (
            self.transformer._add_derived_columns(
                normalized_df
            )
        )

        assert "processed_at" in derived_df.columns

        assert pd.api.types.is_datetime64_any_dtype(
            derived_df["processed_at"]
        )

    def test_add_derived_columns_not_overwritten(
        self,
    ) -> None:
        """
        Verify existing derived columns
        are not overwritten.
        """
        dataframe = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        existing_timestamp = pd.Timestamp(
            "2026-07-26 10:00:00",
            tz="UTC",
        )

        dataframe["processed_at"] = existing_timestamp

        derived_df = (
            self.transformer._add_derived_columns(
                dataframe
            )
        )

        assert (
            derived_df.loc[0, "processed_at"]
            == existing_timestamp
        )

    def test_add_derived_columns_original_dataframe_unchanged(
        self,
    ) -> None:
        """
        Verify original dataframe remains unchanged.
        """
        normalized_df = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        original_df = normalized_df.copy(
            deep=True
        )

        self.transformer._add_derived_columns(
            normalized_df
        )

        pd.testing.assert_frame_equal(
            normalized_df,
            original_df,
        )

    def test_reorder_columns(
        self,
    ) -> None:
        """
        Verify dataframe columns
        are reordered correctly.
        """
        dataframe = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        dataframe = (
            self.transformer._add_derived_columns(
                dataframe
            )
        )

        reordered_df = (
            self.transformer._reorder_columns(
                dataframe
            )
        )

        expected_columns = [
            "symbol",
            "series",
            "trading_date",
            "open",
            "high",
            "low",
            "close",
            "last",
            "prevclose",
            "tottrdqty",
            "tottrdval",
            "processed_at",
        ]

        assert (
            list(reordered_df.columns)
            == expected_columns
        )

    def test_reorder_columns_preserve_unknown_columns(
        self,
    ) -> None:
        """
        Verify unknown columns are preserved
        after preferred columns.
        """
        dataframe = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        dataframe["broker"] = [
            "ABC",
            "XYZ",
        ]

        dataframe = (
            self.transformer._add_derived_columns(
                dataframe
            )
        )

        reordered_df = (
            self.transformer._reorder_columns(
                dataframe
            )
        )

        assert reordered_df.columns[-1] == "broker"

    def test_reorder_columns_original_dataframe_unchanged(
        self,
    ) -> None:
        """
        Verify original dataframe remains unchanged
        after column reordering.
        """
        dataframe = (
            self.transformer._normalize_columns(
                self.sample_dataframe
            )
        )

        dataframe = (
            self.transformer._add_derived_columns(
                dataframe
            )
        )

        original_df = dataframe.copy(
            deep=True
        )

        self.transformer._reorder_columns(
            dataframe
        )

        pd.testing.assert_frame_equal(
            dataframe,
            original_df,
        )
    def test_transform_pipeline(
        self,
    ) -> None:
        """
        Verify complete transformation pipeline.
        """
        transformed_df = (
            self.transformer.transform(
                self.sample_dataframe
            )
        )

        assert isinstance(
            transformed_df,
            pd.DataFrame,
        )

        assert "processed_at" in transformed_df.columns

        assert pd.api.types.is_numeric_dtype(
            transformed_df["open"]
        )

        assert pd.api.types.is_datetime64_any_dtype(
            transformed_df["trading_date"]
        )

        expected_order = [
            "symbol",
            "series",
            "trading_date",
            "open",
            "high",
            "low",
            "close",
            "last",
            "prevclose",
            "tottrdqty",
            "tottrdval",
            "processed_at",
        ]

        assert (
            list(transformed_df.columns)
            == expected_order
        )

    def test_transform_original_dataframe_unchanged(
        self,
    ) -> None:
        """
        Verify original dataframe
        is never modified.
        """
        original_df = self.sample_dataframe.copy(
            deep=True
        )

        self.transformer.transform(
            self.sample_dataframe
        )

        pd.testing.assert_frame_equal(
            self.sample_dataframe,
            original_df,
        )

    def test_transform_empty_dataframe(
        self,
    ) -> None:
        """
        Verify transformation of an
        empty dataframe.
        """
        dataframe = pd.DataFrame()

        transformed_df = (
            self.transformer.transform(
                dataframe
            )
        )

        assert isinstance(
            transformed_df,
            pd.DataFrame,
        )

        assert transformed_df.empty

        assert "processed_at" in transformed_df.columns

    def test_transform_invalid_numeric_values(
        self,
    ) -> None:
        """
        Verify invalid numeric values
        become NaN.
        """
        dataframe = pd.DataFrame(
            {
                "SYMBOL": ["ABC"],
                "SERIES": ["EQ"],
                "trading_date": ["01-01-2026"],
                "OPEN": ["INVALID"],
                "HIGH": ["100"],
                "LOW": ["90"],
                "CLOSE": ["95"],
            }
        )

        transformed_df = (
            self.transformer.transform(
                dataframe
            )
        )

        assert pd.isna(
            transformed_df.loc[0, "open"]
        )

        assert (
            transformed_df.loc[0, "high"]
            == 100.0
        )

    def test_transform_invalid_date(
        self,
    ) -> None:
        """
        Verify invalid dates
        become NaT.
        """
        dataframe = pd.DataFrame(
            {
                "SYMBOL": ["ABC"],
                "SERIES": ["EQ"],
                "trading_date": ["INVALID"],
            }
        )

        transformed_df = (
            self.transformer.transform(
                dataframe
            )
        )

        assert pd.isna(
            transformed_df.loc[0, "trading_date"]
        )

    def test_transform_missing_optional_columns(
        self,
    ) -> None:
        """
        Verify transformation succeeds
        with missing optional columns.
        """
        dataframe = pd.DataFrame(
            {
                "SYMBOL": ["ABC"],
                "OPEN": ["100"],
            }
        )

        transformed_df = (
            self.transformer.transform(
                dataframe
            )
        )

        assert "symbol" in transformed_df.columns

        assert "open" in transformed_df.columns

    def test_transform_returns_new_dataframe(
        self,
    ) -> None:
        """
        Verify transform returns
        a new dataframe object.
        """
        transformed_df = (
            self.transformer.transform(
                self.sample_dataframe
            )
        )

        assert (
            transformed_df
            is not self.sample_dataframe
        )