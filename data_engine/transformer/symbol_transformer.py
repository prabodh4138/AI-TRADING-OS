"""
AI Trading Operating System
Sprint 8.5.4

Symbol Transformer
"""

from __future__ import annotations

import pandas as pd

from core.logger import get_logger

logger = get_logger()


class SymbolTransformer:
    """
    Transforms validated NSE Symbol Master DataFrame
    into AI-TOS canonical schema.
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

    # ==========================================================
    # Public API
    # ==========================================================

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform validated Symbol Master into AI-TOS format.
        """

        logger.info("Starting Symbol Master transformation.")

        transformed_df = df.copy(deep=True)

        self._rename_columns(transformed_df)

        transformed_df = transformed_df[self.CANONICAL_ORDER]

        self._normalize_text(transformed_df)

        self._convert_data_types(transformed_df)

        logger.info("Symbol transformation completed successfully.")
        logger.info("Rows transformed : {}", len(transformed_df))
        logger.info("Columns mapped   : {}", len(transformed_df.columns))

        return transformed_df

    # ==========================================================
    # Column Mapping
    # ==========================================================

    def _rename_columns(self, df: pd.DataFrame) -> None:

        logger.info("Renaming columns...")

        df.rename(
            columns=self.COLUMN_MAPPING,
            inplace=True,
        )

        logger.info("Column mapping completed.")

    # ==========================================================
    # Text Normalization
    # ==========================================================

    def _normalize_text(self, df: pd.DataFrame) -> None:

        logger.info("Normalizing text columns...")

        for column in self.TEXT_COLUMNS:

            df[column] = (
                df[column]
                .astype(str)
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
            )

            df.loc[df[column] == "", column] = None

        logger.info(
            "Normalized {} text columns.",
            len(self.TEXT_COLUMNS),
        )

    # ==========================================================
    # Data Type Conversion
    # ==========================================================

    def _convert_data_types(self, df: pd.DataFrame) -> None:
        """
        Convert canonical columns to enterprise data types.
        """

        logger.info("Converting data types...")

        # ---------- Date ----------

        df["listing_date"] = pd.to_datetime(
            df["listing_date"],
            format="%d-%b-%Y",
            errors="coerce",
        )

        # ---------- Numeric ----------

        df["paid_up_value"] = pd.to_numeric(
            df["paid_up_value"],
            errors="coerce",
        )

        df["face_value"] = pd.to_numeric(
            df["face_value"],
            errors="coerce",
        )

        df["market_lot"] = pd.to_numeric(
            df["market_lot"],
            errors="coerce",
        ).astype("Int64")

        # ---------- Strings ----------

        string_columns = [
            "symbol_code",
            "company_name",
            "series",
            "isin",
        ]

        for column in string_columns:
            df[column] = df[column].astype("string")

        logger.info("Data type conversion completed.")