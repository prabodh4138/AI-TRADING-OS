"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    data_transformer.py

Purpose
-------
Transform validated market data into a clean,
typed DataFrame ready for database loading.

Responsibilities
----------------
1. Normalize DataFrame
2. Clean string values
3. Convert numeric columns
4. Convert date columns
5. Add derived columns

This class MUST NOT

- Read CSV files
- Validate data
- Insert into database
- Download market data

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

import logging
import re

import pandas as pd


class DataTransformer:
    """
    Enterprise Data Transformer.

    Performs data transformation without modifying
    the original DataFrame.
    """

    NUMERIC_COLUMNS: tuple[str, ...] = (
        "OPEN",
        "HIGH",
        "LOW",
        "CLOSE",
        "LAST",
        "PREVCLOSE",
        "TOTTRDQTY",
        "TOTTRDVAL",
    )

    DATE_COLUMNS: tuple[str, ...] = (
        "TIMESTAMP",
    )

    STRING_COLUMNS: tuple[str, ...] = (
        "SYMBOL",
        "SERIES",
    )

    def __init__(
        self,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialize the DataTransformer.

        Parameters
        ----------
        logger : logging.Logger | None
            Optional logger instance.
        """
        self.logger = logger or logging.getLogger(__name__)

        self.logger.info(
            "DataTransformer initialized."
        )

    def transform(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Transform validated market data.

        Workflow
        --------
        1. Copy dataframe
        2. Normalize column names
        3. Clean string values
        4. Convert numeric columns
        5. Convert date columns
        6. Add derived columns
        7. Reorder columns

        Parameters
        ----------
        dataframe : pd.DataFrame
            Validated input dataframe.

        Returns
        -------
        pd.DataFrame
            Fully transformed dataframe.
        """
        self.logger.info(
            "Starting data transformation."
        )

        df = dataframe.copy()

        df = self._normalize_columns(df)
        df = self._clean_strings(df)
        df = self._convert_numeric_columns(df)
        df = self._convert_date_columns(df)
        df = self._add_derived_columns(df)
        df = self._reorder_columns(df)

        self.logger.info(
            "Data transformation completed successfully."
        )

        return df

    def _normalize_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Normalize dataframe column names.

        Rules
        -----
        1. Remove leading/trailing whitespace.
        2. Convert to lowercase.
        3. Replace spaces with underscores.
        4. Replace hyphens with underscores.
        5. Collapse multiple underscores.
        6. Remove special characters.
        7. Validate duplicate names.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Input dataframe.

        Returns
        -------
        pd.DataFrame
            Dataframe with normalized column names.

        Raises
        ------
        ValueError
            If duplicate column names exist after
            normalization.
        """
        self.logger.info(
            "Normalizing dataframe columns."
        )

        df = dataframe.copy()

        normalized_columns: list[str] = []

        for column in df.columns:

            normalized = str(column)

            normalized = normalized.strip().lower()

            normalized = normalized.replace(
                " ",
                "_",
            )

            normalized = normalized.replace(
                "-",
                "_",
            )

            normalized = re.sub(
                r"_+",
                "_",
                normalized,
            )

            normalized = re.sub(
                r"[^a-z0-9_]",
                "",
                normalized,
            )

            normalized_columns.append(normalized)

        duplicates = sorted(
            {
                column
                for column in normalized_columns
                if normalized_columns.count(column) > 1
            }
        )

        if duplicates:

            self.logger.error(
                "Duplicate normalized columns detected: %s",
                duplicates,
            )

            raise ValueError(
                "Duplicate column names after normalization: "
                f"{duplicates}"
            )

        df.columns = normalized_columns

        self.logger.info(
            "Column normalization completed."
        )

        return df

    def _clean_strings(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Clean string columns.

        Operations
        ----------
        1. Remove leading and trailing whitespace.
        2. Replace multiple consecutive spaces with a single space.
        3. Convert empty strings to pandas NA.
        4. Preserve non-string values.
        5. Skip columns that do not exist.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Input dataframe.

        Returns
        -------
        pd.DataFrame
            DataFrame with cleaned string values.
        """
        self.logger.info(
            "Cleaning string columns."
        )

        df = dataframe.copy()

        for column in self.STRING_COLUMNS:

            normalized_column = column.lower()

            if normalized_column not in df.columns:
                continue

            df[normalized_column] = (
                df[normalized_column]
                .astype("string")
                .str.strip()
                .str.replace(
                    r"\s+",
                    " ",
                    regex=True,
                )
            )

            df[normalized_column] = (
                df[normalized_column]
                .replace(
                    "",
                    pd.NA,
                )
            )

        self.logger.info(
            "String cleaning completed."
        )

        return df

    def _convert_numeric_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Convert configured columns to numeric data types.

        Operations
        ----------
        1. Process only configured numeric columns.
        2. Skip columns that are not present.
        3. Convert values to numeric.
        4. Invalid values become NaN.
        5. Preserve dataframe integrity.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Input dataframe.

        Returns
        -------
        pd.DataFrame
            DataFrame with numeric columns converted.
        """
        self.logger.info(
            "Converting numeric columns."
        )

        df = dataframe.copy()

        for column in self.NUMERIC_COLUMNS:

            normalized_column = column.lower()

            if normalized_column not in df.columns:
                continue

            self.logger.debug(
                "Converting numeric column: %s",
                normalized_column,
            )

            df[normalized_column] = pd.to_numeric(
                df[normalized_column],
                errors="coerce",
            )

        self.logger.info(
            "Numeric column conversion completed."
        )

        return df
    def _convert_date_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Convert configured columns to datetime.

        Operations
        ----------
        1. Process only configured date columns.
        2. Skip columns that are not present.
        3. Convert values to datetime.
        4. Invalid dates become NaT.
        5. Preserve dataframe integrity.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Input dataframe.

        Returns
        -------
        pd.DataFrame
            DataFrame with datetime columns converted.
        """
        self.logger.info(
            "Converting date columns."
        )

        df = dataframe.copy()

        for column in self.DATE_COLUMNS:

            normalized_column = column.lower()

            if normalized_column not in df.columns:
                continue

            self.logger.debug(
                "Converting date column: %s",
                normalized_column,
            )

            df[normalized_column] = pd.to_datetime(
                df[normalized_column],
                errors="coerce",
                dayfirst=True,
            )

        self.logger.info(
            "Date column conversion completed."
        )

        return df
    def _add_derived_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Add derived columns to the dataframe.

        Operations
        ----------
        1. Add processing timestamp.
        2. Preserve existing columns.
        3. Do not overwrite existing derived columns.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Input dataframe.

        Returns
        -------
        pd.DataFrame
            DataFrame with derived columns added.
        """
        self.logger.info(
            "Adding derived columns."
        )

        df = dataframe.copy()

        if "processed_at" not in df.columns:
            df["processed_at"] = pd.Timestamp.utcnow()

        self.logger.info(
            "Derived columns added successfully."
        )

        return df

    def _reorder_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Reorder dataframe columns.

        The preferred business columns are placed first.
        Any additional columns are appended while preserving
        their original order.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Input dataframe.

        Returns
        -------
        pd.DataFrame
            DataFrame with reordered columns.
        """
        self.logger.info(
            "Reordering dataframe columns."
        )

        df = dataframe.copy()

        preferred_order = [
            "symbol",
            "series",
            "timestamp",
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

        ordered_columns = [
            column
            for column in preferred_order
            if column in df.columns
        ]

        remaining_columns = [
            column
            for column in df.columns
            if column not in ordered_columns
        ]

        df = df[
            ordered_columns + remaining_columns
        ]

        self.logger.info(
            "Column reordering completed."
        )

        return df