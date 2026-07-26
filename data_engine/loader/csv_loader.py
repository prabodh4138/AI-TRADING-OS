"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    csv_loader.py

Purpose
-------
Load CSV files into pandas DataFrames.

Responsibilities
----------------
1. Read CSV
2. Return DataFrame

This class MUST NOT

- Validate data
- Clean data
- Insert database
- Transform columns

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd


class CSVLoader:
    """
    Enterprise CSV Loader.

    Reads CSV files and returns
    pandas DataFrames.
    """

    def __init__(
        self,
        logger: logging.Logger | None = None,
    ) -> None:

        self.logger = (
            logger
            or logging.getLogger(__name__)
        )

        self.logger.info(
            "CSVLoader initialized."
        )
            # ==================================================
    # Load CSV File
    # ==================================================

    def load(
        self,
        file_path: str | Path,
    ) -> pd.DataFrame:
        """
        Load a CSV file into a pandas DataFrame.

        Parameters
        ----------
        file_path
            Path to the CSV file.

        Returns
        -------
        pandas.DataFrame
            Loaded DataFrame.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.

        ValueError
            If the CSV file is empty.

        RuntimeError
            If the CSV cannot be loaded.
        """

        file_path = Path(file_path)

        self.logger.info(
            "Loading CSV file: %s",
            file_path,
        )

        if not file_path.exists():

            raise FileNotFoundError(
                f"CSV file not found: {file_path}"
            )

        if not file_path.is_file():

            raise FileNotFoundError(
                f"Not a valid file: {file_path}"
            )

        try:

            dataframe = pd.read_csv(
                file_path
            )

        except Exception as ex:

            self.logger.exception(
                "Failed to load CSV file."
            )

            raise RuntimeError(
                f"Unable to load CSV file: {file_path}"
            ) from ex

        if dataframe.empty:

            raise ValueError(
                f"CSV file is empty: {file_path}"
            )

        self.logger.info(
            "CSV loaded successfully. Rows=%d Columns=%d",
            len(dataframe),
            len(dataframe.columns),
        )

        return dataframe
        # ==================================================
    # Load Directory
    # ==================================================

    def load_directory(
        self,
        directory: str | Path,
        pattern: str = "*.csv",
    ) -> dict[Path, pd.DataFrame]:
        """
        Load all CSV files from a directory.

        Parameters
        ----------
        directory
            Directory containing CSV files.

        pattern
            File search pattern.

        Returns
        -------
        dict[Path, pandas.DataFrame]
            Dictionary mapping file paths to DataFrames.

        Raises
        ------
        FileNotFoundError
            If the directory does not exist.

        NotADirectoryError
            If the supplied path is not a directory.
        """

        directory = Path(directory)

        if not directory.exists():

            raise FileNotFoundError(
                f"Directory not found: {directory}"
            )

        if not directory.is_dir():

            raise NotADirectoryError(
                f"Not a directory: {directory}"
            )

        csv_files = sorted(
            directory.glob(pattern)
        )

        self.logger.info(
            "Found %d CSV file(s) in %s",
            len(csv_files),
            directory,
        )

        dataframes: dict[Path, pd.DataFrame] = {}

        for csv_file in csv_files:

            try:

                dataframes[csv_file] = self.load(
                    csv_file
                )

            except Exception:

                self.logger.exception(
                    "Unable to load %s",
                    csv_file,
                )

        self.logger.info(
            "Successfully loaded %d CSV file(s).",
            len(dataframes),
        )

        return dataframes
        # ==================================================
    # Load Latest CSV File
    # ==================================================

    def load_latest(
        self,
        directory: str | Path,
        pattern: str = "*.csv",
    ) -> pd.DataFrame:
        """
        Load the most recently modified CSV file from a directory.

        Parameters
        ----------
        directory
            Directory containing CSV files.

        pattern
            File search pattern.

        Returns
        -------
        pandas.DataFrame
            DataFrame loaded from the latest CSV file.

        Raises
        ------
        FileNotFoundError
            If the directory does not exist or contains no matching CSV files.
        """

        directory = Path(directory)

        if not directory.exists():

            raise FileNotFoundError(
                f"Directory not found: {directory}"
            )

        if not directory.is_dir():

            raise NotADirectoryError(
                f"Not a directory: {directory}"
            )

        csv_files = list(
            directory.glob(pattern)
        )

        if not csv_files:

            raise FileNotFoundError(
                f"No CSV files found in: {directory}"
            )

        latest_file = max(
            csv_files,
            key=lambda file: file.stat().st_mtime,
        )

        self.logger.info(
            "Latest CSV file identified: %s",
            latest_file.name,
        )

        return self.load(
            latest_file
        )
            # ==================================================
    # Check CSV Readability
    # ==================================================

    def can_load(
        self,
        file_path: str | Path,
    ) -> bool:
        """
        Determine whether a CSV file can be loaded.

        Parameters
        ----------
        file_path
            Path to the CSV file.

        Returns
        -------
        bool
            True if the file can be successfully loaded,
            otherwise False.
        """

        try:

            self.load(file_path)

            return True

        except Exception:

            return False