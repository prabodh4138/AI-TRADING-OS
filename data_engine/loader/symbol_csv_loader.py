"""
AI Trading Operating System
Sprint 8.5.2

Symbol CSV Loader
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.logger import get_logger

logger = get_logger()


class SymbolCSVLoader:
    """
    Loads the downloaded NSE Symbol Master CSV into a pandas DataFrame.
    """

    def __init__(self):
        logger.debug("SymbolCSVLoader initialized.")

    def load(self, file_path: Path) -> pd.DataFrame:
        """
        Load NSE Symbol Master CSV into a pandas DataFrame.
        """

        if not isinstance(file_path, Path):
            raise TypeError("file_path must be pathlib.Path")

        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        if not file_path.is_file():
            raise FileNotFoundError(f"Invalid CSV file: {file_path}")

        logger.info("Loading Symbol Master CSV: {}", file_path)

        try:
            df = pd.read_csv(
                file_path,
                encoding="utf-8",
                keep_default_na=False,
                low_memory=False,
            )

        except UnicodeDecodeError:
            logger.warning("UTF-8 decoding failed. Retrying with latin-1.")

            try:
                df = pd.read_csv(
                    file_path,
                    encoding="latin-1",
                    keep_default_na=False,
                    low_memory=False,
                )
            except Exception as ex:
                raise RuntimeError(f"Unable to decode CSV: {ex}") from ex

        except pd.errors.EmptyDataError as ex:
            raise ValueError("Symbol Master CSV is empty.") from ex

        except pd.errors.ParserError as ex:
            raise RuntimeError(f"CSV parsing failed: {ex}") from ex

        except Exception as ex:
            raise RuntimeError(f"Unable to load CSV: {ex}") from ex

        #
        # Normalize column names
        #

        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )

        if df.empty:
            raise ValueError("Loaded DataFrame is empty.")

        logger.info("CSV loaded successfully.")
        logger.info("Rows    : {}", len(df))
        logger.info("Columns : {}", len(df.columns))
        logger.debug("Detected columns: {}", list(df.columns))

        return df

    def preview(
        self,
        df: pd.DataFrame,
        rows: int = 5,
    ) -> pd.DataFrame:
        """
        Return the first few rows of the DataFrame.
        """
        return df.head(rows)