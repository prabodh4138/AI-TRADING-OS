"""
Market Data Transformer
"""

from __future__ import annotations

import polars as pl


class DataTransformer:

    def transform(self, df: pl.DataFrame) -> pl.DataFrame:

        return (
            df
            .rename({
                "Date": "DATE",
                "Open": "OPEN",
                "High": "HIGH",
                "Low": "LOW",
                "Close": "CLOSE",
                "Volume": "VOLUME",
            }, strict=False)
            .with_columns([
                pl.col("DATE").str.to_date(strict=False),
                pl.col("OPEN").cast(pl.Float64),
                pl.col("HIGH").cast(pl.Float64),
                pl.col("LOW").cast(pl.Float64),
                pl.col("CLOSE").cast(pl.Float64),
                pl.col("VOLUME").cast(pl.Int64),
            ])
        )