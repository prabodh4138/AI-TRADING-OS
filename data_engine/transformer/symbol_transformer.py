"""
AI Trading Operating System
Sprint 8.5.4

Symbol Transformer
"""

from __future__ import annotations

import time

import pandas as pd

from core.logger import get_logger
from models.transformation_result import TransformationResult

logger = get_logger()


class SymbolTransformer:
    """
    Transforms validated NSE Symbol Master DataFrame
    into AI-TOS canonical format.

    Responsibilities
    ----------------
    1. Rename columns
    2. Normalize text
    3. Convert data types
    4. Produce transformation statistics

    Notes
    -----
    Validation is performed by SymbolValidator.
    Database loading is performed by DatabaseLoader.
    """

    COLUMN_MAPPING = {
        "SYMBOL": "symbol_code",
        "NAME OF COMPANY": "company_name",
        "SERIES": "series",
        "DATE OF LISTING": "listing_date",
        "PAID UP VALUE": "paid_up_value",
        "MARKET LOT": "market_lot",
        "ISIN NUMBER": "isin",
        "FACE VALUE": "face_value",
    }

    CANONICAL_ORDER = [
        "symbol_code",
        "company_name",
        "series",
        "listing_date",
        "paid_up_value",
        "market_lot",
        "isin",
        "face_value",
    ]

    TEXT_COLUMNS = [
        "symbol_code",
        "company_name",
        "series",
        "isin",
    ]

    def __init__(self):
        logger.debug("SymbolTransformer initialized.")
        self.result = TransformationResult()

    # ==========================================================
    # Public API
    # ==========================================================

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform validated Symbol Master DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            Validated DataFrame.

        Returns
        -------
        pd.DataFrame
            Canonical transformed DataFrame.
        """

        start_time = time.perf_counter()

        self.result.reset()

        logger.info("Starting Symbol Master transformation.")

        try:

            transformed_df = df.copy(deep=True)

            self._rename_columns(transformed_df)

            transformed_df = transformed_df[
                self.CANONICAL_ORDER
            ]

            self._normalize_text(transformed_df)

            self._convert_data_types(transformed_df)

            #
            # Statistics
            #

            self.result.success = True
            self.result.rows_processed = len(transformed_df)
            self.result.columns_processed = len(
                transformed_df.columns
            )
            self.result.transformation_time = (
                time.perf_counter() - start_time
            )

            logger.info(
                "Symbol transformation completed successfully."
            )

            logger.info(
                "Rows transformed : {}",
                self.result.rows_processed,
            )

            logger.info(
                "Columns mapped : {}",
                self.result.columns_processed,
            )

            logger.info(
                "Transformation Time : {:.4f} sec",
                self.result.transformation_time,
            )

            return transformed_df

        except Exception as ex:

            self.result.success = False

            self.result.transformation_time = (
                time.perf_counter() - start_time
            )

            self.result.add_error(str(ex))

            logger.exception(
                "Symbol transformation failed."
            )

            raise

    # ==========================================================
    # Column Mapping
    # ==========================================================

    def _rename_columns(
        self,
        df: pd.DataFrame,
    ) -> None:
        """
        Rename NSE columns to AI-TOS standard names.
        """

        logger.info("Renaming columns...")

        df.rename(
            columns=self.COLUMN_MAPPING,
            inplace=True,
        )

        logger.info("Column mapping completed.")

    # ==========================================================
    # Text Normalization
    # ==========================================================

    def _normalize_text(
        self,
        df: pd.DataFrame,
    ) -> None:
        """
        Normalize text fields.

        Operations
        ----------
        • Strip leading/trailing spaces
        • Collapse multiple spaces
        • Convert empty strings to None
        """

        logger.info("Normalizing text columns...")

        for column in self.TEXT_COLUMNS:

            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
                .str.replace(
                    r"\s+",
                    " ",
                    regex=True,
                )
            )

            df.loc[
                df[column] == "",
                column,
            ] = None

        logger.info(
            "Normalized {} text columns.",
            len(self.TEXT_COLUMNS),
        )

    # ==========================================================
    # Data Type Conversion
    # ==========================================================

    def _convert_data_types(
        self,
        df: pd.DataFrame,
    ) -> None:
        """
        Convert canonical columns
        to enterprise data types.
        """

        logger.info("Converting data types...")

        #
        # Date
        #

        df["listing_date"] = pd.to_datetime(
            df["listing_date"],
            format="%d-%b-%Y",
            errors="coerce",
        )

        #
        # Numeric
        #

        df["paid_up_value"] = pd.to_numeric(
            df["paid_up_value"],
            errors="coerce",
        )

        df["face_value"] = pd.to_numeric(
            df["face_value"],
            errors="coerce",
        )

        df["market_lot"] = (
            pd.to_numeric(
                df["market_lot"],
                errors="coerce",
            )
            .astype("Int64")
        )

        #
        # String
        #

        for column in self.TEXT_COLUMNS:
            df[column] = df[column].astype("string")

        logger.info(
            "Data type conversion completed."
        )

    # ==========================================================
    # Result
    # ==========================================================

    def transformation_result(
        self,
    ) -> TransformationResult:
        """
        Return latest transformation result.
        """

        return self.result