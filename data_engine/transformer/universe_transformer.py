from __future__ import annotations

from datetime import date

import pandas as pd


class UniverseTransformer:
    """Transform validated universe membership data into canonical records."""

    OUTPUT_COLUMNS = [
        "universe_code",
        "universe_name",
        "universe_type",
        "provider",
        "symbol_code",
        "effective_from",
        "effective_to",
    ]

    @staticmethod
    def _clean_text(value) -> str | None:
        if pd.isna(value):
            return None

        value = str(value).strip()

        return value if value else None

    @staticmethod
    def _clean_code(value) -> str | None:
        value = UniverseTransformer._clean_text(value)

        if value is None:
            return None

        return value.upper()

    @staticmethod
    def _to_date(value) -> date | None:
        if pd.isna(value):
            return None

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return None

        if isinstance(value, pd.Timestamp):
            if pd.isna(value):
                return None
            return value.date()

        if isinstance(value, date):
            return value

        parsed = pd.to_datetime(
            value,
            format="mixed",
            errors="coerce",
        )

        if pd.isna(parsed):
            return None

        return parsed.date()

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform validated DataFrame into canonical DataFrame."""

        if df is None:
            raise ValueError("Universe DataFrame cannot be None.")

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Universe data must be a pandas DataFrame.")

        missing_columns = [
            column
            for column in self.OUTPUT_COLUMNS
            if column not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}"
            )

        transformed = pd.DataFrame(index=range(len(df)))

        transformed["universe_code"] = pd.Series(
            [self._clean_code(value) for value in df["universe_code"]],
            dtype=object,
        )

        transformed["universe_name"] = pd.Series(
            [self._clean_text(value) for value in df["universe_name"]],
            dtype=object,
        )

        transformed["universe_type"] = pd.Series(
            [self._clean_code(value) for value in df["universe_type"]],
            dtype=object,
        )

        transformed["provider"] = pd.Series(
            [self._clean_text(value) for value in df["provider"]],
            dtype=object,
        )

        transformed["symbol_code"] = pd.Series(
            [self._clean_code(value) for value in df["symbol_code"]],
            dtype=object,
        )

        transformed["effective_from"] = pd.Series(
            [self._to_date(value) for value in df["effective_from"]],
            dtype=object,
        )

        transformed["effective_to"] = pd.Series(
            [self._to_date(value) for value in df["effective_to"]],
            dtype=object,
        )

        return transformed[self.OUTPUT_COLUMNS].reset_index(drop=True)

    def transform_records(self, df: pd.DataFrame) -> list[dict]:
        """Transform DataFrame into database-ready dictionaries."""

        transformed = self.transform(df)

        return transformed.to_dict(orient="records")
