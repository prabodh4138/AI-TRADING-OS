"""
AI Trading Operating System

Universe CSV Loader
===================

Loads generic universe-membership CSV files for the
Universe Master import pipeline.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.logger import get_logger


logger = get_logger()


class UniverseCSVLoader:
    """
    Loads a generic Universe Master CSV into a pandas DataFrame.

    The loader is intentionally independent of any particular
    universe such as NIFTY 500.
    """

    def __init__(self) -> None:
        logger.debug("UniverseCSVLoader initialized.")

    def load(self, file_path: Path) -> pd.DataFrame:
        """
        Load a Universe Master CSV into a pandas DataFrame.

        Parameters
        ----------
        file_path:
            Path to the CSV file.

        Returns
        -------
        pd.DataFrame
            Loaded and normalized DataFrame.
        """

        if not isinstance(file_path, Path):
            raise TypeError("file_path must be pathlib.Path")

        if not file_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {file_path}"
            )

        if not file_path.is_file():
            raise FileNotFoundError(
                f"Invalid CSV file: {file_path}"
            )

        logger.info(
            "Loading Universe Master CSV: {}",
            file_path,
        )

        try:
            dataframe = pd.read_csv(
                file_path,
                encoding="utf-8",
                keep_default_na=False,
                low_memory=False,
            )

        except UnicodeDecodeError:
            logger.warning(
                "UTF-8 decoding failed. Retrying with latin-1."
            )

            try:
                dataframe = pd.read_csv(
                    file_path,
                    encoding="latin-1",
                    keep_default_na=False,
                    low_memory=False,
                )
            except Exception as ex:
                raise RuntimeError(
                    f"Unable to decode CSV: {ex}"
                ) from ex

        except pd.errors.EmptyDataError as ex:
            raise ValueError(
                "Universe Master CSV is empty."
            ) from ex

        except pd.errors.ParserError as ex:
            raise RuntimeError(
                f"CSV parsing failed: {ex}"
            ) from ex

        except Exception as ex:
            raise RuntimeError(
                f"Unable to load CSV: {ex}"
            ) from ex

        # Normalize column names.
        dataframe.columns = (
            dataframe.columns.astype(str)
            .str.strip()
            .str.replace(
                r"\s+",
                " ",
                regex=True,
            )
        )

        if dataframe.empty:
            raise ValueError(
                "Loaded Universe Master DataFrame is empty."
            )

        logger.info(
            "Universe Master CSV loaded successfully."
        )

        logger.info(
            "Rows    : {}",
            len(dataframe),
        )

        logger.info(
            "Columns : {}",
            len(dataframe.columns),
        )

        logger.debug(
            "Detected columns: {}",
            list(dataframe.columns),
        )

        return dataframe

    def preview(
        self,
        dataframe: pd.DataFrame,
        rows: int = 5,
    ) -> pd.DataFrame:
        """
        Return the first few rows of the DataFrame.
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(
                "dataframe must be pandas.DataFrame"
            )

        if rows < 0:
            raise ValueError(
                "rows must be greater than or equal to zero."
            )

        return dataframe.head(rows)
