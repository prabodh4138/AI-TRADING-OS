"""
AI Trading Operating System
Import Service

Business service responsible for orchestrating the complete
market data import pipeline.

Responsibilities
----------------
- Coordinate CSV import workflow
- Invoke loader, validator, transformer and service layers
- Produce import statistics
- Handle import level logging

This class intentionally contains no database logic,
no dataframe transformation logic and no SQL.
"""

from __future__ import annotations

import logging
from pathlib import Path

from data_engine.loader.csv_loader import CSVLoader
from data_engine.transformer.data_transformer import DataTransformer
from data_engine.validator.csv_validator import CSVValidator

from dto.import_statistics import ImportStatistics
from services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)


class ImportService:
    """
    Coordinates the complete historical market-data import pipeline.

    This service orchestrates the end-to-end import workflow by
    delegating responsibilities to specialized components.

    Workflow
    --------
    CSV File
        ↓
    CSVLoader
        ↓
    CSVValidator
        ↓
    DataTransformer
        ↓
    MarketDataService
        ↓
    Repository
        ↓
    PostgreSQL
    """

    def __init__(
        self,
        loader: CSVLoader | None = None,
        validator: CSVValidator | None = None,
        transformer: DataTransformer | None = None,
        market_data_service: MarketDataService | None = None,
    ) -> None:
        """
        Initialize the import pipeline.

        Parameters
        ----------
        loader : CSVLoader | None, optional
            CSV loader implementation.
        validator : CSVValidator | None, optional
            CSV validator implementation.
        transformer : DataTransformer | None, optional
            Data transformation implementation.
        market_data_service : MarketDataService | None, optional
            Service responsible for persisting market data.

        Notes
        -----
        Dependencies may be injected during testing.
        When omitted, default implementations are created.
        """

        self.loader = loader or CSVLoader()
        self.validator = validator or CSVValidator()
        self.transformer = transformer or DataTransformer()
        self.market_data_service = (
            market_data_service or MarketDataService()
        )

    from pathlib import Path

    def import_file(
        self,
        file_path: str | Path,
    ) -> int:
        """
        Import a single market data CSV file.

        Parameters
        ----------
        file_path =path(file_path)
            Path to the CSV file.

        Returns
        -------
        int
            Number of successfully imported records.
        """

        logger.info("Starting import: %s", file_path)

        # Step 1: Load CSV
        dataframe = self.loader.load(file_path)

        # Step 2: Validate CSV structure
        self.validator.validate(dataframe)

        # Step 3: Transform raw data
        dataframe = self.transformer.transform(dataframe)

        # Step 4: Persist records
        inserted = self.market_data_service.import_market_data(
            dataframe
        )

        logger.info(
            "Import completed: %s (%d records imported)",
            file_path,
            inserted,
        )

        return inserted

    def import_directory(
        self,
        directory: str,
    ) -> ImportStatistics:
        """
        Import all CSV files from a directory.

        Parameters
        ----------
        directory : str
            Directory containing CSV files.

        Returns
        -------
        ImportStatistics
            Summary of the import operation.

        Raises
        ------
        FileNotFoundError
            If the specified directory does not exist.
        """

        directory_path = Path(directory)

        if not directory_path.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {directory}"
            )

        summary = ImportStatistics()

        csv_files = sorted(directory_path.glob("*.csv"))

        logger.info(
            "Found %d CSV file(s) in %s",
            len(csv_files),
            directory,
        )

        for csv_file in csv_files:
            try:
                inserted = self.import_file(str(csv_file))

                summary.files_processed += 1
                summary.records_imported += inserted

            except Exception:
                logger.exception(
                    "Failed to import file: %s",
                    csv_file,
                )

                summary.files_failed += 1

        logger.info(
            (
                "Directory import completed. "
                "Processed=%d, Failed=%d, Imported=%d, Skipped=%d"
            ),
            summary.files_processed,
            summary.files_failed,
            summary.records_imported,
            summary.records_skipped,
        )

        return summary