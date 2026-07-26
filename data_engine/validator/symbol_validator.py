"""
AI Trading Operating System
Sprint 8.5.3

Symbol Validator
"""

from __future__ import annotations

import time

import pandas as pd

from core.logger import get_logger
from models.validation_result import ValidationResult

logger = get_logger()


class SymbolValidator:
    """
    Validates the NSE Symbol Master DataFrame.

    Responsibilities
    ----------------
    1. Validate required schema.
    2. Validate mandatory fields.
    3. Validate duplicate symbols.
    4. Generate validation statistics.
    """

    REQUIRED_COLUMNS = [
        "SYMBOL",
        "NAME OF COMPANY",
        "SERIES",
        "DATE OF LISTING",
        "PAID UP VALUE",
        "MARKET LOT",
        "ISIN NUMBER",
        "FACE VALUE",
    ]

    def __init__(self):
        logger.debug("SymbolValidator initialized.")
        self.result = ValidationResult()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate Symbol Master DataFrame.
        """

        start_time = time.perf_counter()

        self.result = ValidationResult()

        logger.info("Starting Symbol Master validation.")
        logger.info("Rows    : {}", len(df))
        logger.info("Columns : {}", len(df.columns))

        try:
            self._validate_schema(df)
            self._validate_blank_values(df)
            self._validate_duplicate_symbols(df)

            self.result.success = True
            self.result.rows_checked = len(df)
            self.result.columns_checked = len(df.columns)
            self.result.validation_time = (
                time.perf_counter() - start_time
            )

            logger.info("Data validation completed successfully.")

            return df

        except Exception as ex:

            self.result.success = False
            self.result.rows_checked = len(df)
            self.result.columns_checked = len(df.columns)
            self.result.validation_time = (
                time.perf_counter() - start_time
            )
            self.result.errors.append(str(ex))

            logger.exception("Validation failed.")

            raise

    # ------------------------------------------------------------------
    # Schema Validation
    # ------------------------------------------------------------------

    def _validate_schema(self, df: pd.DataFrame) -> None:
        """
        Validate required columns.
        """

        logger.info("Validating DataFrame schema...")

        missing = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                "Missing required columns:\n"
                + "\n".join(missing)
            )

        logger.info("Schema validation successful.")
        logger.info("Detected {} columns.", len(df.columns))

    # ------------------------------------------------------------------
    # Mandatory Fields
    # ------------------------------------------------------------------

    def _validate_blank_values(self, df: pd.DataFrame) -> None:
        """
        Ensure important fields are not blank.
        """

        logger.info("Validating mandatory fields...")

        mandatory = [
            "SYMBOL",
            "NAME OF COMPANY",
            "ISIN NUMBER",
        ]

        for column in mandatory:

            blank_rows = (
                df[column]
                .astype(str)
                .str.strip()
                .eq("")
                .sum()
            )

            if blank_rows > 0:
                raise ValueError(
                    f"Column '{column}' contains "
                    f"{blank_rows} blank values."
                )

        logger.info("Mandatory field validation successful.")

    # ------------------------------------------------------------------
    # Duplicate Validation
    # ------------------------------------------------------------------

    def _validate_duplicate_symbols(
        self,
        df: pd.DataFrame,
    ) -> None:
        """
        Detect duplicate symbols.
        """

        logger.info("Checking duplicate symbols...")

        duplicates = (
            df["SYMBOL"]
            .astype(str)
            .str.strip()
            .duplicated()
            .sum()
        )

        if duplicates > 0:
            raise ValueError(
                f"Duplicate SYMBOL values found: {duplicates}"
            )

        logger.info("No duplicate symbols found.")

    # ------------------------------------------------------------------
    # Validation Result
    # ------------------------------------------------------------------

    def validation_result(self) -> ValidationResult:
        """
        Return the latest validation result.
        """

        return self.result