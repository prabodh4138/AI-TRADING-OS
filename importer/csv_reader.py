"""
CSV Reader using Polars
"""

from pathlib import Path

import polars as pl


class CSVReader:

    REQUIRED_COLUMNS = [
        "SYMBOL",
        "DATE",
        "OPEN",
        "HIGH",
        "LOW",
        "CLOSE",
        "VOLUME",
    ]

    def read(self, file_path: str | Path) -> pl.DataFrame:

        df = pl.read_csv(file_path)

        missing = [
            c for c in self.REQUIRED_COLUMNS
            if c not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing required columns: {missing}"
            )

        return df