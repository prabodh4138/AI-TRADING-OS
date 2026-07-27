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
    Transforms validated NSE Symbol Master data into
    the AI-TOS canonical format.
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

    def __init__(self):
        logger.debug("SymbolTransformer initialized.")

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform validated NSE Symbol Master DataFrame into
        AI-TOS canonical schema.
        """

        logger.info("Starting Symbol Master transformation.")

        transformed_df = df.copy(deep=True)

        logger.info("Renaming columns...")

        transformed_df.rename(
            columns=self.COLUMN_MAPPING,
            inplace=True,
        )

        transformed_df = transformed_df[
            self.CANONICAL_ORDER
        ]

        logger.info("Column mapping completed.")
        logger.info(
            "Columns mapped: {}",
            len(self.CANONICAL_ORDER),
        )

        return transformed_df