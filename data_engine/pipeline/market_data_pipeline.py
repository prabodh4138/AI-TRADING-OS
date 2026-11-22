"""
=========================================================
AI Trading OS
Enterprise Market Data Import Pipeline
=========================================================

Module:
    market_data_pipeline.py

Purpose
-------
Orchestrates the complete market data import workflow.

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
PostgreSQL

Responsibilities
----------------
1. Load CSV files
2. Validate market data
3. Transform validated data
4. Import transformed data
5. Return ImportResult
6. Record execution statistics

This class MUST NOT

- Validate business rules
- Transform individual columns
- Execute SQL directly
- Access repositories directly

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from data_engine.loader.csv_loader import CSVLoader
from data_engine.transformer.data_transformer import DataTransformer
from data_engine.validator.csv_validator import (
    CSVValidationException,
    CSVValidator,
)
from dto.import_result import ImportResult
from services.market_data_service import MarketDataService


class MarketDataPipeline:
    """
    Enterprise Market Data Import Pipeline.

    Coordinates the complete ETL workflow while
    delegating all business logic to dedicated
    components.
    """

    # ==========================================================
    # Constructor
    # ==========================================================

    def __init__(
        self,
        loader: CSVLoader | None = None,
        validator: CSVValidator | None = None,
        transformer: DataTransformer | None = None,
        service: MarketDataService | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialize the pipeline.

        Parameters
        ----------
        loader
            CSV loader implementation.

        validator
            CSV validator implementation.

        transformer
            Data transformer implementation.

        service
            Market data service implementation.

        logger
            Optional logger.
        """

        self.logger = (
            logger
            or logging.getLogger(__name__)
        )

        self.loader = (
            loader
            or CSVLoader(
                logger=self.logger,
            )
        )

        self.validator = (
            validator
            or CSVValidator(
                logger=self.logger,
            )
        )

        self.transformer = (
            transformer
            or DataTransformer(
                logger=self.logger,
            )
        )

        # Current MarketDataService constructor
        # does not accept a logger.
        self.service = (
            service
            or MarketDataService()
        )

        self.logger.info(
            "MarketDataPipeline initialized."
        )

    # ==========================================================
    # Import CSV
    # ==========================================================
    def import_csv(
        self,
        file_path: str | Path,
    ) -> ImportResult:
        """
        Execute the complete market data import pipeline.

        Workflow
        --------
        1. Load CSV
        2. Validate CSV
        3. Transform data
        4. Import into database
        5. Return ImportResult

        Parameters
        ----------
        file_path
            Path to the CSV file.

        Returns
        -------
        ImportResult
            Summary of the import operation.
        """

        started_at = datetime.now()

        rows_read = 0
        rows_imported = 0
        rows_failed = 0

        file_path = Path(file_path)

        self.logger.info(
            "Starting market data import: %s",
            file_path,
        )

        try:

            # ==================================================
            # Load CSV
            # ==================================================

            self.logger.info(
                "Loading CSV file..."
            )

            dataframe = self.loader.load(
                file_path
            )

            rows_read = len(dataframe)

            self.logger.info(
                "CSV loaded successfully."
            )

            self.logger.info(
                "Rows loaded: %d",
                rows_read,
            )

            # ==================================================
            # Validate CSV
            # ==================================================

            self.logger.info(
                "Validating CSV..."
            )

            dataframe = self.validator.validate(
                dataframe
            )

            self.logger.info(
                "CSV validation completed successfully."
            )

            # ==================================================
            # Transform Data
            # ==================================================

            self.logger.info(
                "Transforming market data..."
            )

            dataframe = self.transformer.transform(
                dataframe
            )

            self.logger.info(
                "Data transformation completed successfully."
            )

            # ==================================================
            # Import Market Data
            # ==================================================

            self.logger.info(
                "Importing market data into PostgreSQL..."
            )

            rows_imported = (
                self.service.import_market_data(
                    dataframe,
                    universe_code="NIFTY500",
                )
            )

            rows_failed = max(
                0,
                rows_read - rows_imported,
            )

            completed_at = datetime.now()

            self.logger.info(
                "Market data import completed successfully."
            )

            self.logger.info(
                "Rows Read      : %d",
                rows_read,
            )

            self.logger.info(
                "Rows Imported  : %d",
                rows_imported,
            )

            self.logger.info(
                "Rows Failed    : %d",
                rows_failed,
            )

            self.logger.info(
                "Duration       : %.2f seconds",
                (
                    completed_at
                    - started_at
                ).total_seconds(),
            )

            self.logger.debug(
                "Creating ImportResult object."
            )

            return ImportResult(
                success=True,
                file_name=file_path.name,
                rows_read=rows_read,
                rows_imported=rows_imported,
                rows_failed=rows_failed,
                started_at=started_at,
                completed_at=completed_at,
                message="Market data imported successfully.",
            )
        # ==================================================
        # CSV Validation Error
        # ==================================================

        except CSVValidationException as ex:

            completed_at = datetime.now()

            rows_failed = rows_read

            self.logger.exception(
                "CSV validation failed."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=rows_read,
                rows_imported=rows_imported,
                rows_failed=rows_failed,
                started_at=started_at,
                completed_at=completed_at,
                message="CSV validation failed.",
                exception=str(ex),
            )

        # ==================================================
        # File Not Found
        # ==================================================

        except FileNotFoundError as ex:

            completed_at = datetime.now()

            self.logger.exception(
                "CSV file not found."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=rows_read,
                rows_imported=rows_imported,
                rows_failed=rows_failed,
                started_at=started_at,
                completed_at=completed_at,
                message="CSV file not found.",
                exception=str(ex),
            )

        # ==================================================
        # Invalid Data
        # ==================================================

        except ValueError as ex:

            completed_at = datetime.now()

            rows_failed = rows_read

            self.logger.exception(
                "Invalid market data."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=rows_read,
                rows_imported=rows_imported,
                rows_failed=rows_failed,
                started_at=started_at,
                completed_at=completed_at,
                message="Invalid market data.",
                exception=str(ex),
            )

        # ==================================================
        # Unexpected Error
        # ==================================================

        except Exception as ex:

            completed_at = datetime.now()

            rows_failed = rows_read

            self.logger.exception(
                "Unexpected error occurred during market data import."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=rows_read,
                rows_imported=rows_imported,
                rows_failed=rows_failed,
                started_at=started_at,
                completed_at=completed_at,
                message="Market data import failed.",
                exception=str(ex),
            )
    # ==========================================================
    # Import Latest CSV
    # ==========================================================

    def import_latest_csv(
        self,
        directory: str | Path,
        pattern: str = "*.csv",
    ) -> ImportResult:
        """
        Import the most recently modified CSV file
        from a directory.

        Parameters
        ----------
        directory
            Directory containing CSV files.

        pattern
            File search pattern.

        Returns
        -------
        ImportResult
            Summary of the import operation.
        """

        directory = Path(directory)

        self.logger.info(
            "Importing latest CSV from %s",
            directory,
        )

        try:

            # Reuse the loader's responsibility
            dataframe = self.loader.load_latest(
                directory=directory,
                pattern=pattern,
            )

            rows_read = len(dataframe)

            started_at = datetime.now()

            dataframe = self.validator.validate(
                dataframe
            )

            dataframe = self.transformer.transform(
                dataframe
            )

            rows_imported = (
                self.service.import_market_data(
                    dataframe
                )
            )

            completed_at = datetime.now()

            return ImportResult(
                success=True,
                file_name="LATEST_CSV",
                rows_read=rows_read,
                rows_imported=rows_imported,
                rows_failed=max(
                    0,
                    rows_read - rows_imported,
                ),
                started_at=started_at,
                completed_at=completed_at,
                message="Latest CSV imported successfully.",
            )

        except Exception as ex:

            completed_at = datetime.now()

            self.logger.exception(
                "Failed to import latest CSV."
            )

            return ImportResult(
                success=False,
                file_name="LATEST_CSV",
                rows_read=0,
                rows_imported=0,
                rows_failed=0,
                started_at=completed_at,
                completed_at=completed_at,
                message="Latest CSV import failed.",
                exception=str(ex),
            )