"""
AI Trading Operating System
Symbol Master Service

Business service for NSE Symbol Master ingestion.
"""

from __future__ import annotations

from contextlib import nullcontext
from datetime import date
from decimal import Decimal
from typing import Any

import pandas as pd

from database.unit_of_work import UnitOfWork
from validators.base_validator import ValidationError


class SymbolMasterService:
    """
    Business service responsible for importing transformed
    NSE Symbol Master data.

    Responsibilities
    ----------------
    1. Validate transformed DataFrame structure.
    2. Determine new and existing symbols.
    3. Map canonical NSE data to the Symbol model.
    4. Perform transactional bulk upsert.
    5. Return import statistics.

    This service does not:
        - Read CSV files.
        - Parse raw NSE CSV files.
        - Perform DataFrame source validation.
        - Execute SQL directly.
        - Delete symbols missing from the source file.
    """

    REQUIRED_COLUMNS = {
        "symbol_code",
        "company_name",
        "series",
        "listing_date",
        "market_lot",
        "isin",
        "face_value",
    }

    DEFAULT_EXCHANGE = "NSE"
    DEFAULT_INSTRUMENT_TYPE = "EQUITY"
    DEFAULT_TICK_SIZE = Decimal("0.05")
    DEFAULT_IS_FNO = False

    def import_dataframe(
        self,
        dataframe: pd.DataFrame,
        uow: UnitOfWork | None = None,
    ) -> dict[str, int]:
        """
        Import a transformed Symbol Master DataFrame.
        """

        if dataframe is None:
            raise ValidationError(
                "Symbol Master DataFrame cannot be None."
            )

        if dataframe.empty:
            return {
                "received": 0,
                "new": 0,
                "updated": 0,
                "affected": 0,
            }

        self._validate_columns(dataframe)

        records = self._dataframe_to_records(
            dataframe
        )

        if not records:
            return {
                "received": 0,
                "new": 0,
                "updated": 0,
                "affected": 0,
            }

        context = (
            nullcontext(uow)
            if uow is not None
            else UnitOfWork()
        )

        with context as active_uow:
            return self._import_records(
                active_uow,
                records,
            )

    # ------------------------------------------------------------------
    # Transaction-bound Import
    # ------------------------------------------------------------------

    def _import_records(
        self,
        uow: UnitOfWork,
        records: list[dict[str, Any]],
    ) -> dict[str, int]:
        """
        Import records using the supplied UnitOfWork.
        """

        symbol_codes = [
            record["symbol_code"]
            for record in records
        ]

        existing_codes = set(
            uow.symbols.get_all_symbol_codes()
        )

        incoming_codes = set(
            symbol_codes
        )

        new_count = len(
            incoming_codes - existing_codes
        )

        updated_count = len(
            incoming_codes & existing_codes
        )

        result = uow.symbols.bulk_upsert(
            records
        )

        return {
            "received": len(records),
            "new": new_count,
            "updated": updated_count,
            "affected": result["affected"],
        }

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Validate the structure expected from SymbolTransformer.
        """

        missing = (
            self.REQUIRED_COLUMNS
            - set(dataframe.columns)
        )

        if missing:
            raise ValidationError(
                "Symbol Master DataFrame is missing "
                "required column(s): "
                + ", ".join(sorted(missing))
            )

    # ------------------------------------------------------------------
    # DataFrame -> Database Records
    # ------------------------------------------------------------------

    def _dataframe_to_records(
        self,
        dataframe: pd.DataFrame,
    ) -> list[dict[str, Any]]:
        """
        Convert transformed DataFrame rows into dictionaries
        suitable for SymbolRepository.bulk_upsert().
        """

        records: list[dict[str, Any]] = []

        for row in dataframe.to_dict(
            orient="records"
        ):
            symbol_code = self._clean_string(
                row.get("symbol_code")
            )

            company_name = self._clean_string(
                row.get("company_name")
            )

            series = self._clean_string(
                row.get("series")
            )

            isin = self._clean_string(
                row.get("isin")
            )

            if not symbol_code:
                raise ValidationError(
                    "Symbol Master contains a blank symbol_code."
                )

            if not company_name:
                raise ValidationError(
                    f"Symbol '{symbol_code}' has a blank company_name."
                )

            if not isin:
                raise ValidationError(
                    f"Symbol '{symbol_code}' has a blank ISIN."
                )

            records.append(
                {
                    "symbol_code": symbol_code,
                    "symbol_name": company_name,
                    "exchange": self.DEFAULT_EXCHANGE,
                    "instrument_type": self.DEFAULT_INSTRUMENT_TYPE,
                    "series": series,
                    "sector": None,
                    "industry": None,
                    "isin": isin,
                    "lot_size": self._to_int(
                        row.get("market_lot"),
                        default=1,
                    ),
                    "tick_size": self.DEFAULT_TICK_SIZE,
                    "face_value": self._to_decimal(
                        row.get("face_value")
                    ),
                    "listing_date": self._to_date(
                        row.get("listing_date")
                    ),
                    "is_fno": self.DEFAULT_IS_FNO,
                }
            )

        return records

    # ------------------------------------------------------------------
    # Value Conversion
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_string(
        value: Any,
    ) -> str | None:
        """
        Convert a value to a clean string.

        pandas NA/NaN values become None.
        """

        if value is None:
            return None

        if pd.isna(value):
            return None

        value = str(value).strip()

        return value if value else None

    @staticmethod
    def _to_int(
        value: Any,
        *,
        default: int,
    ) -> int:
        """
        Convert a value to integer.
        """

        if value is None or pd.isna(value):
            return default

        return int(value)

    @staticmethod
    def _to_decimal(
        value: Any,
    ) -> Decimal | None:
        """
        Convert a numeric value to Decimal.
        """

        if value is None or pd.isna(value):
            return None

        return Decimal(str(value))

    @staticmethod
    def _to_date(
        value: Any,
    ) -> date | None:
        """
        Convert pandas/Python date values to Python date.
        """

        if value is None or pd.isna(value):
            return None

        if isinstance(value, pd.Timestamp):
            return value.date()

        if isinstance(value, date):
            return value

        return pd.to_datetime(
            value
        ).date()
