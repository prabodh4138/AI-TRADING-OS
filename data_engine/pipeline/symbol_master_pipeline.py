"""
AI Trading Operating System
Enterprise Symbol Master Import Pipeline
=========================================

Module:
    symbol_master_pipeline.py

Purpose
-------
Orchestrates the complete NSE Symbol Master import workflow.

Workflow
--------
NSE Symbol Master CSV
        ↓
SymbolCSVLoader
        ↓
SymbolValidator
        ↓
SymbolTransformer
        ↓
SymbolMasterService
        ↓
PostgreSQL
        ↓
ImportBatch / ImportExecution audit

The pipeline is responsible for orchestration only.
Business rules, transformation logic and database SQL
remain delegated to their respective components.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from data_engine.loader.symbol_csv_loader import SymbolCSVLoader
from data_engine.transformer.symbol_transformer import SymbolTransformer
from data_engine.validator.symbol_validator import SymbolValidator
from database.unit_of_work import UnitOfWork
from dto.import_result import ImportResult
from services.import_batch_service import ImportBatchService
from services.symbol_master_service import SymbolMasterService


class SymbolMasterPipeline:
    """
    Enterprise NSE Symbol Master import pipeline.

    Coordinates:

        Load
        ↓
        Validate
        ↓
        Transform
        ↓
        Import
        ↓
        Audit

    The pipeline owns the transaction boundary for a successful
    import. Symbol data and successful import audit records are
    committed together.
    """

    def __init__(
        self,
        loader: SymbolCSVLoader | None = None,
        validator: SymbolValidator | None = None,
        transformer: SymbolTransformer | None = None,
        service: SymbolMasterService | None = None,
        logger: logging.Logger | None = None,
    ) -> None:

        self.logger = (
            logger
            or logging.getLogger(__name__)
        )

        self.loader = (
            loader
            or SymbolCSVLoader()
        )

        self.validator = (
            validator
            or SymbolValidator()
        )

        self.transformer = (
            transformer
            or SymbolTransformer()
        )

        self.service = (
            service
            or SymbolMasterService()
        )

        self.logger.info(
            "SymbolMasterPipeline initialized."
        )

    # ==============================================================
    # Import CSV
    # ==============================================================

    def import_csv(
        self,
        file_path: str | Path,
    ) -> ImportResult:
        """
        Execute the complete NSE Symbol Master import workflow.

        Parameters
        ----------
        file_path:
            Path to the NSE Symbol Master CSV.

        Returns
        -------
        ImportResult
            Complete import summary.
        """

        started_at = datetime.now()

        file_path = Path(file_path)

        rows_read = 0
        rows_imported = 0
        rows_failed = 0

        batch = None
        execution = None

        self.logger.info(
            "Starting Symbol Master import: %s",
            file_path,
        )

        # ----------------------------------------------------------
        # Load
        # ----------------------------------------------------------

        try:
            self.logger.info(
                "Loading NSE Symbol Master CSV..."
            )

            dataframe = self.loader.load(
                file_path
            )

            rows_read = len(dataframe)

            self.logger.info(
                "Symbol Master CSV loaded successfully."
            )

            self.logger.info(
                "Rows loaded: %d",
                rows_read,
            )

        except FileNotFoundError as ex:

            completed_at = datetime.now()

            self.logger.exception(
                "Symbol Master CSV file not found."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=0,
                rows_imported=0,
                rows_failed=0,
                started_at=started_at,
                completed_at=completed_at,
                message="Symbol Master CSV file not found.",
                exception=str(ex),
            )

        except Exception as ex:

            completed_at = datetime.now()

            self.logger.exception(
                "Failed to load Symbol Master CSV."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=0,
                rows_imported=0,
                rows_failed=0,
                started_at=started_at,
                completed_at=completed_at,
                message="Failed to load Symbol Master CSV.",
                exception=str(ex),
            )

        # ----------------------------------------------------------
        # Validate
        # ----------------------------------------------------------

        try:
            self.logger.info(
                "Validating NSE Symbol Master..."
            )

            dataframe = self.validator.validate(
                dataframe
            )

            self.logger.info(
                "Symbol Master validation completed successfully."
            )

        except Exception as ex:

            completed_at = datetime.now()

            rows_failed = rows_read

            self.logger.exception(
                "Symbol Master validation failed."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=rows_read,
                rows_imported=0,
                rows_failed=rows_failed,
                started_at=started_at,
                completed_at=completed_at,
                message="Symbol Master validation failed.",
                exception=str(ex),
            )

        # ----------------------------------------------------------
        # Transform
        # ----------------------------------------------------------

        try:
            self.logger.info(
                "Transforming NSE Symbol Master..."
            )

            dataframe = self.transformer.transform(
                dataframe
            )

            self.logger.info(
                "Symbol Master transformation completed successfully."
            )

        except Exception as ex:

            completed_at = datetime.now()

            rows_failed = rows_read

            self.logger.exception(
                "Symbol Master transformation failed."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=rows_read,
                rows_imported=0,
                rows_failed=rows_failed,
                started_at=started_at,
                completed_at=completed_at,
                message="Symbol Master transformation failed.",
                exception=str(ex),
            )

        # ----------------------------------------------------------
        # Database import + audit
        # ----------------------------------------------------------

        try:

            with UnitOfWork() as uow:

                batch_service = ImportBatchService(
                    uow.import_batches
                )

                batch = batch_service.start_batch(
                    batch_name="NSE_SYMBOL_MASTER",
                    total_files=1,
                )

                execution = (
                    batch_service.register_execution(
                        batch_id=batch.batch_id,
                        file_name=file_path.name,
                    )
                )

                batch_service.start_execution(
                    execution
                )

                self.logger.info(
                    "Import batch started: %s",
                    batch.batch_id,
                )

                self.logger.info(
                    "Importing symbols into PostgreSQL..."
                )

                stats = self.service.import_dataframe(
                    dataframe,
                    uow=uow,
                )

                rows_imported = stats["affected"]

                rows_failed = max(
                    0,
                    rows_read - rows_imported,
                )

                batch_service.finish_execution(
                    execution=execution,
                    rows_read=rows_read,
                    rows_imported=rows_imported,
                    rows_failed=rows_failed,
                    message=(
                        "NSE Symbol Master imported successfully."
                    ),
                    exception=None,
                )

                batch_service.complete_batch(
                    batch
                )

                self.logger.info(
                    "Symbol Master database import completed."
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
                    "New Symbols    : %d",
                    stats["new"],
                )

                self.logger.info(
                    "Updated Symbols: %d",
                    stats["updated"],
                )

                self.logger.info(
                    "Rows Failed    : %d",
                    rows_failed,
                )

        except Exception as ex:

            completed_at = datetime.now()

            rows_failed = rows_read - rows_imported

            if rows_failed < 0:
                rows_failed = rows_read

            self.logger.exception(
                "Symbol Master database import failed."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=rows_read,
                rows_imported=rows_imported,
                rows_failed=rows_failed,
                started_at=started_at,
                completed_at=completed_at,
                message="Symbol Master database import failed.",
                exception=str(ex),
            )

        completed_at = datetime.now()

        self.logger.info(
            "Symbol Master import completed successfully."
        )

        self.logger.info(
            "Duration: %.2f seconds",
            (
                completed_at - started_at
            ).total_seconds(),
        )

        return ImportResult(
            success=True,
            file_name=file_path.name,
            rows_read=rows_read,
            rows_imported=rows_imported,
            rows_failed=rows_failed,
            started_at=started_at,
            completed_at=completed_at,
            message="NSE Symbol Master imported successfully.",
        )

    # ==============================================================
    # Import Latest CSV
    # ==============================================================

    def import_latest_csv(
        self,
        directory: str | Path,
        pattern: str = "*.csv",
    ) -> ImportResult:
        """
        Import the latest CSV from a directory.

        SymbolCSVLoader intentionally exposes only explicit
        file loading, so latest-file discovery is handled here.
        """

        directory = Path(directory)

        if not directory.exists():
            completed_at = datetime.now()

            return ImportResult(
                success=False,
                file_name="LATEST_CSV",
                rows_read=0,
                rows_imported=0,
                rows_failed=0,
                started_at=completed_at,
                completed_at=completed_at,
                message="Symbol Master directory not found.",
                exception=str(directory),
            )

        files = [
            path
            for path in directory.glob(pattern)
            if path.is_file()
        ]

        if not files:

            completed_at = datetime.now()

            return ImportResult(
                success=False,
                file_name="LATEST_CSV",
                rows_read=0,
                rows_imported=0,
                rows_failed=0,
                started_at=completed_at,
                completed_at=completed_at,
                message="No Symbol Master CSV files found.",
                exception=(
                    f"No files matching '{pattern}' "
                    f"found in {directory}"
                ),
            )

        latest_file = max(
            files,
            key=lambda path: path.stat().st_mtime,
        )

        return self.import_csv(
            latest_file
        )
