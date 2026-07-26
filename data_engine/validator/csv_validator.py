"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    csv_validator.py

Purpose
-------
Validate market data loaded from CSV files.

Responsibilities
----------------
1. Validate DataFrame structure
2. Validate mandatory columns
3. Validate data completeness
4. Raise validation exceptions

This class MUST NOT

- Modify data
- Convert datatypes
- Rename columns
- Insert into database

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

import logging

import pandas as pd


class CSVValidationException(Exception):
    """
    Raised when CSV validation fails.
    """


class CSVValidator:
    """
    Enterprise CSV Validator.

    Performs structural validation on market
    data before transformation and database
    loading.
    """

    REQUIRED_COLUMNS: tuple[str, ...] = (
        "SYMBOL",
        "SERIES",
        "OPEN",
        "HIGH",
        "LOW",
        "CLOSE",
        "LAST",
        "PREVCLOSE",
        "TOTTRDQTY",
        "TOTTRDVAL",
        "TIMESTAMP",
    )

    def __init__(
        self,
        logger: logging.Logger | None = None,
    ) -> None:

        self.logger = (
            logger
            or logging.getLogger(__name__)
        )

        self.logger.info(
            "CSVValidator initialized."
        )
    # ==================================================
    # Validate DataFrame
    # ==================================================

    def validate(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Validate a DataFrame.

        Parameters
        ----------
        dataframe
            DataFrame to validate.

        Returns
        -------
        pandas.DataFrame
            The validated DataFrame.

        Raises
        ------
        CSVValidationException
            If validation fails.
        """

        self.logger.info(
            "Starting CSV validation."
        )

        self.validate_not_empty(
            dataframe
        )

        self.validate_required_columns(
            dataframe
        )

        self.validate_duplicate_columns(
            dataframe
        )

        self.validate_null_values(
            dataframe
        )

        self.validate_minimum_rows(
            dataframe
        )

        self.validate_column_count(
            dataframe
        )

        self.logger.info(
            "CSV validation completed successfully."
        )

        return dataframe
    # ==================================================
    # Validate DataFrame Is Not Empty
    # ==================================================

    def validate_not_empty(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Validate that the DataFrame is not empty.

        Raises
        ------
        CSVValidationException
            If the DataFrame is empty.
        """

        if dataframe.empty:

            raise CSVValidationException(
                "CSV contains no data."
            )

        self.logger.debug(
            "DataFrame contains %d row(s).",
            len(dataframe),
        )

    # ==================================================
    # Validate Required Columns
    # ==================================================

    def validate_required_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Validate that all required columns exist.

        Raises
        ------
        CSVValidationException
            If one or more required columns are missing.
        """

        available_columns = {
            str(column).strip()
            for column in dataframe.columns
        }

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in available_columns
        ]

        if missing_columns:

            raise CSVValidationException(
                "Missing required column(s): "
                + ", ".join(missing_columns)
            )

        self.logger.debug(
            "All required columns are present."
        )
            # ==================================================
    # Validate Duplicate Columns
    # ==================================================

    def validate_duplicate_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Validate that the DataFrame does not contain
        duplicate column names.

        Raises
        ------
        CSVValidationException
            If duplicate columns are found.
        """

        normalized_columns = [
            str(column).strip()
            for column in dataframe.columns
        ]

        duplicates = sorted(
            {
                column
                for column in normalized_columns
                if normalized_columns.count(column) > 1
            }
        )

        if duplicates:

            raise CSVValidationException(
                "Duplicate column(s) found: "
                + ", ".join(duplicates)
            )

        self.logger.debug(
            "No duplicate columns found."
        )

    # ==================================================
    # Validate Mandatory Null Values
    # ==================================================

    def validate_null_values(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Validate that mandatory columns do not
        contain null values.

        Raises
        ------
        CSVValidationException
            If mandatory columns contain null values.
        """

        mandatory_columns = (
            "SYMBOL",
            "SERIES",
            "OPEN",
            "HIGH",
            "LOW",
            "CLOSE",
            "LAST",
            "PREVCLOSE",
            "TOTTRDQTY",
            "TOTTRDVAL",
            "TIMESTAMP",
        )

        columns_with_nulls: list[str] = []

        for column in mandatory_columns:

            if dataframe[column].isnull().any():

                columns_with_nulls.append(
                    column
                )

        if columns_with_nulls:

            raise CSVValidationException(
                "Null values found in mandatory column(s): "
                + ", ".join(columns_with_nulls)
            )

        self.logger.debug(
            "Mandatory columns contain no null values."
        )
            # ==================================================
    # Validate Minimum Rows
    # ==================================================

    def validate_minimum_rows(
        self,
        dataframe: pd.DataFrame,
        minimum_rows: int = 1,
    ) -> None:
        """
        Validate that the DataFrame contains at least
        the specified number of rows.

        Parameters
        ----------
        dataframe
            DataFrame to validate.

        minimum_rows
            Minimum acceptable number of rows.

        Raises
        ------
        CSVValidationException
            If the DataFrame contains fewer than the
            required number of rows.
        """

        row_count = len(dataframe)

        if row_count < minimum_rows:

            raise CSVValidationException(
                f"Expected at least {minimum_rows} row(s), "
                f"found {row_count}."
            )

        self.logger.debug(
            "Row count validation passed (%d rows).",
            row_count,
        )

    # ==================================================
    # Validate Column Count
    # ==================================================

    def validate_column_count(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Validate that the DataFrame contains at least
        the required number of columns.

        Raises
        ------
        CSVValidationException
            If the DataFrame contains fewer columns than
            required.
        """

        expected_columns = len(
            self.REQUIRED_COLUMNS
        )

        actual_columns = len(
            dataframe.columns
        )

        if actual_columns < expected_columns:

            raise CSVValidationException(
                f"Expected at least {expected_columns} "
                f"columns, found {actual_columns}."
            )

        self.logger.debug(
            "Column count validation passed "
            "(%d columns).",
            actual_columns,
        )