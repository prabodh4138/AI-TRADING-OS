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

from services.market_data_service import MarketDataService
from dto.import_statistics import ImportStatistics

logger = logging.getLogger(__name__)


class ImportService:
    """
    Coordinates the complete historical market-data import pipeline.
    """

    def __init__(self) -> None:
        """
        Initialize all pipeline components.
        """

        self.loader = CSVLoader()

        self.validator = CSVValidator()

        self.transformer = DataTransformer()

        self.market_data_service = MarketDataService()
def import_file(
    self,
    file_path: str,
) -> int:
    """
    Import a single market data CSV file.

    Parameters
    ----------
    file_path : str
        Path to the CSV file.

    Returns
    -------
    int
        Number of imported records.
    """

    logger.info("Starting import: %s", file_path)

    # Step 1: Load CSV
    dataframe = self.loader.load(file_path)

    # Step 2: Validate structure
    self.validator.validate(dataframe)

    # Step 3: Transform data
    dataframe = self.transformer.transform(dataframe)

    # Step 4: Persist data
    inserted = self.market_data_service.import_market_data(
        dataframe
    )

    logger.info(
        "Import completed: %s (%d records)",
        file_path,
        inserted,
    )

    return inserted
def import_directory(
    self,
    directory: str,
) -> dict[str, int]:
    """
    Import every CSV file from a directory.

    Parameters
    ----------
    directory : str
        Directory containing CSV files.

    Returns
    -------
    dict[str, int]
        Import summary.
    """

    directory_path = Path(directory)

    if not directory_path.exists():
        raise FileNotFoundError(
            f"Directory does not exist: {directory}"
        )

    csv_files = sorted(directory_path.glob("*.csv"))

    summary = ImportStatistics()

    for csv_file in csv_files:

        try:

            inserted = self.import_file(
                str(csv_file)
            )

            summary.files_processed += 1
            summary.records_imported += inserted

        except Exception:

            logger.exception(
                "Failed to import %s",
                csv_file,
            )

            summary.files_failed += 1

    logger.info(
        "Directory import completed: %s",
        summary,
    )

    return summary