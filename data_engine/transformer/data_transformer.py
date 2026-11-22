"""
AI Trading OS
Enterprise Data Engine

Module:
    data_transformer.py

Purpose
-------
Transform validated NSE market data into a clean,
typed canonical DataFrame ready for database loading.
"""

from __future__ import annotations

import logging
import re

import pandas as pd


class DataTransformer:
    """
    Enterprise Data Transformer.

    Converts validated NSE Bhavcopy data into the
    canonical internal market-data representation.
    """

    # --------------------------------------------------
    # Raw NSE → canonical field mapping
    # --------------------------------------------------

    COLUMN_MAPPING: dict[str, str] = {
        "symbol": "symbol",
        "series": "series",
        "date1": "trading_date",
        "prev_close": "prevclose",
        "open_price": "open",
        "high_price": "high",
        "low_price": "low",
        "last_price": "last",
        "close_price": "close",
        "avg_price": "vwap",
        "ttl_trd_qnty": "volume",
        "turnover_lacs": "turnover",
        "no_of_trades": "trade_count",
        "deliv_qty": "delivery_volume",
        "deliv_per": "delivery_percent",
    }

    NUMERIC_COLUMNS: tuple[str, ...] = (
        "open",
        "high",
        "low",
        "close",
        "last",
        "prevclose",
        "volume",
        "delivery_volume",
        "delivery_percent",
        "turnover",
        "vwap",
        "tottrdqty",
        "tottrdval",
    )

    DATE_COLUMNS: tuple[str, ...] = (
        "trading_date",
    )

    STRING_COLUMNS: tuple[str, ...] = (
        "symbol",
        "series",
    )

    def __init__(
        self,
        logger: logging.Logger | None = None,
    ) -> None:

        self.logger = logger or logging.getLogger(__name__)

        self.logger.info(
            "DataTransformer initialized."
        )

    # ==================================================
    # Public transformation
    # ==================================================

    def transform(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        self.logger.info(
            "Starting data transformation."
        )

        df = dataframe.copy()

        df = self._normalize_columns(df)
        df = self._map_source_columns(df)
        df = self._clean_strings(df)
        df = self._convert_numeric_columns(df)
        df = self._convert_date_columns(df)
        df = self._add_derived_columns(df)
        df = self._reorder_columns(df)

        self.logger.info(
            "Data transformation completed successfully."
        )

        return df

    # ==================================================
    # Normalize columns
    # ==================================================

    def _normalize_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        df = dataframe.copy()

        normalized_columns: list[str] = []

        for column in df.columns:

            normalized = str(column).strip().lower()

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

            raise ValueError(
                "Duplicate column names after normalization: "
                f"{duplicates}"
            )

        df.columns = normalized_columns

        return df

    # ==================================================
    # Map raw source columns
    # ==================================================

    def _map_source_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        df = dataframe.copy()

        rename_map = {
            source: target
            for source, target in self.COLUMN_MAPPING.items()
            if source in df.columns
            and source != target
        }

        if rename_map:

            self.logger.info(
                "Mapping source columns: %s",
                rename_map,
            )

            df = df.rename(
                columns=rename_map
            )

        return df

    # ==================================================
    # Clean strings
    # ==================================================

    def _clean_strings(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        df = dataframe.copy()

        for column in self.STRING_COLUMNS:

            if column not in df.columns:
                continue

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
                .str.replace(
                    r"\s+",
                    " ",
                    regex=True,
                )
            )

            df[column] = df[column].replace(
                "",
                pd.NA,
            )

        return df

    # ==================================================
    # Numeric conversion
    # ==================================================

    def _convert_numeric_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        df = dataframe.copy()

        for column in self.NUMERIC_COLUMNS:

            if column not in df.columns:
                continue

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

        return df

    # ==================================================
    # Date conversion
    # ==================================================

    def _convert_date_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        df = dataframe.copy()

        for column in self.DATE_COLUMNS:

            if column not in df.columns:
                continue

            df[column] = pd.to_datetime(
                df[column],
                errors="coerce",
                dayfirst=True,
            )

        return df

    # ==================================================
    # Derived columns
    # ==================================================

    def _add_derived_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        df = dataframe.copy()

        if "processed_at" not in df.columns:

            df["processed_at"] = pd.Timestamp.now(
                tz="UTC"
            )

        return df

    # ==================================================
    # Reorder columns
    # ==================================================

    def _reorder_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        df = dataframe.copy()

        preferred_order = [
            "symbol",
            "series",
            "trading_date",
            "open",
            "high",
            "low",
            "close",
            "last",
            "prevclose",
            "volume",
            "delivery_volume",
            "delivery_percent",
            "trade_count",
            "turnover",
            "vwap",
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

        return df[
            ordered_columns + remaining_columns
        ]


