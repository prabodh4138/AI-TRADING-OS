from __future__ import annotations

import time

import pandas as pd

from core.logger import get_logger
from models.validation_result import ValidationResult


logger = get_logger()


class UniverseCSVValidator:
    """
    Validates AI-TOS Universe Constituent CSV data.

    Expected columns
    ----------------
    universe_code
    universe_name
    universe_type
    provider
    symbol_code
    effective_from
    effective_to
    """

    REQUIRED_COLUMNS = [
        "universe_code",
        "universe_name",
        "universe_type",
        "provider",
        "symbol_code",
        "effective_from",
        "effective_to",
    ]

    MANDATORY_COLUMNS = [
        "universe_code",
        "universe_name",
        "universe_type",
        "symbol_code",
        "effective_from",
    ]

    def __init__(self) -> None:
        logger.debug("UniverseCSVValidator initialized.")
        self.result = ValidationResult()

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate Universe Constituent DataFrame.

        Returns the original DataFrame when validation succeeds.
        Raises ValueError when validation fails.
        """
        start_time = time.perf_counter()
        self.result = ValidationResult()

        logger.info("Starting Universe CSV validation.")
        logger.info("Rows    : {}", len(df))
        logger.info("Columns : {}", len(df.columns))

        try:
            self._validate_schema(df)
            self._validate_mandatory_fields(df)
            self._validate_dates(df)
            self._validate_duplicate_memberships(df)

            self.result.success = True
            self.result.rows_checked = len(df)
            self.result.columns_checked = len(df.columns)
            self.result.validation_time = time.perf_counter() - start_time

            logger.info("Universe CSV validation completed successfully.")

            return df

        except Exception as ex:
            self.result.success = False
            self.result.rows_checked = len(df)
            self.result.columns_checked = len(df.columns)
            self.result.validation_time = time.perf_counter() - start_time
            self.result.errors.append(str(ex))

            logger.exception("Universe CSV validation failed.")

            raise

    def _validate_schema(self, df: pd.DataFrame) -> None:
        """Validate required columns."""

        missing = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                "Missing required columns:\n" + "\n".join(missing)
            )

    def _validate_mandatory_fields(self, df: pd.DataFrame) -> None:
        """Ensure mandatory fields are not blank."""

        for column in self.MANDATORY_COLUMNS:
            blank_rows = (
                df[column]
                .isna()
                .sum()
            )

            if blank_rows > 0:
                raise ValueError(
                    f"Column '{column}' contains "
                    f"{blank_rows} blank values."
                )

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

    def _validate_dates(self, df: pd.DataFrame) -> None:
        """Validate effective membership dates."""

        effective_from = pd.to_datetime(
        df["effective_from"],
        errors="coerce",
        format="mixed",
    )

        effective_to = pd.to_datetime(
        df["effective_to"],
        errors="coerce",
        format="mixed",
    )

        invalid_from = (
            effective_from.isna()
            & df["effective_from"].notna()
            & df["effective_from"].astype(str).str.strip().ne("")
        )

        if invalid_from.any():
            raise ValueError(
                "Invalid effective_from date values found."
            )

        invalid_to = (
            effective_to.isna()
            & df["effective_to"].notna()
            & df["effective_to"].astype(str).str.strip().ne("")
        )

        if invalid_to.any():
            raise ValueError(
                "Invalid effective_to date values found."
            )

        invalid_range = (
            effective_to.notna()
            & effective_from.notna()
            & (effective_to < effective_from)
        )

        if invalid_range.any():
            raise ValueError(
                "effective_to cannot be earlier than effective_from."
            )

    def _validate_duplicate_memberships(
        self,
        df: pd.DataFrame,
    ) -> None:
        """Detect duplicate membership periods."""

        normalized = df.copy()

        for column in [
            "universe_code",
            "symbol_code",
        ]:
            normalized[column] = (
                normalized[column]
                .astype(str)
                .str.strip()
                .str.upper()
            )

        normalized["effective_from"] = pd.to_datetime(
            normalized["effective_from"],
            errors="coerce",
        ).dt.date

        duplicates = normalized.duplicated(
            subset=[
                "universe_code",
                "symbol_code",
                "effective_from",
            ],
            keep=False,
        )

        if duplicates.any():
            duplicate_rows = normalized.loc[
                duplicates,
                [
                    "universe_code",
                    "symbol_code",
                    "effective_from",
                ],
            ].drop_duplicates()

            raise ValueError(
                "Duplicate universe membership periods found: "
                f"{duplicate_rows.to_dict('records')}"
            )

    def validation_result(self) -> ValidationResult:
        """Return the latest validation result."""

        return self.result



