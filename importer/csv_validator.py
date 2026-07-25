"""
CSV Validator
"""

from __future__ import annotations

import polars as pl


class CSVValidator:

    REQUIRED_COLUMNS = [
        "SYMBOL",
        "DATE",
        "OPEN",
        "HIGH",
        "LOW",
        "CLOSE",
        "VOLUME",
    ]

    def validate(self, df: pl.DataFrame) -> None:

        missing = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing required columns: {missing}"
            )