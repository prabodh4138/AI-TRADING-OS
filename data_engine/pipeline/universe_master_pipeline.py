"""
AI Trading Operating System

Universe Master Import Pipeline
================================

Workflow
--------
Universe CSV
    ↓
UniverseCSVLoader
    ↓
UniverseCSVValidator
    ↓
UniverseTransformer
    ↓
UniverseMasterService
    ↓
PostgreSQL
    ↓
ImportBatch / ImportExecution audit
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from data_engine.loader.universe_csv_loader import UniverseCSVLoader
from data_engine.transformer.universe_transformer import UniverseTransformer
from data_engine.validator.universe_csv_validator import UniverseCSVValidator
from database.unit_of_work import UnitOfWork
from dto.import_result import ImportResult
from services.import_batch_service import ImportBatchService
from services.universe_master_service import UniverseMasterService


class UniverseMasterPipeline:
    """
    Enterprise Universe Master import pipeline.

    The pipeline coordinates ETL and audit operations.
    Business rules remain inside the validator, transformer,
    and service layers.
    """

    BATCH_NAME = "UNIVERSE_MASTER"

    def __init__(
        self,
        loader: UniverseCSVLoader | None = None,
        validator: UniverseCSVValidator | None = None,
        transformer: UniverseTransformer | None = None,
        service: UniverseMasterService | None = None,
        logger: logging.Logger | None = None,
    ) -> None:

        self.logger = (
            logger
            or logging.getLogger(__name__)
        )

        self.loader = (
            loader
            or UniverseCSVLoader()
        )

        self.validator = (
            validator
            or UniverseCSVValidator()
        )

        self.transformer = (
            transformer
            or UniverseTransformer()
        )

        self.service = (
            service
            or UniverseMasterService()
        )

        self.logger.info(
            "UniverseMasterPipeline initialized."
        )

    def import_csv(
        self,
        file_path: str | Path,
    ) -> ImportResult:
        """
        Execute the complete Universe Master import workflow.
        """

        started_at = datetime.now()

        file_path = Path(file_path)

        rows_read = 0
        rows_imported = 0
        rows_failed = 0

        self.logger.info(
            "Starting Universe Master import: %s",
            file_path,
        )

        # ==========================================================
        # LOAD
        # ==========================================================

        try:
            dataframe = self.loader.load(file_path)

            rows_read = len(dataframe)

            self.logger.info(
                "Universe CSV loaded successfully. Rows: %d",
                rows_read,
            )

        except FileNotFoundError as ex:
            completed_at = datetime.now()

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=0,
                rows_imported=0,
                rows_failed=0,
                started_at=started_at,
                completed_at=completed_at,
                message="Universe Master CSV file not found.",
                exception=str(ex),
            )

        except Exception as ex:
            completed_at = datetime.now()

            self.logger.exception(
                "Failed to load Universe Master CSV."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=0,
                rows_imported=0,
                rows_failed=0,
                started_at=started_at,
                completed_at=completed_at,
                message="Failed to load Universe Master CSV.",
                exception=str(ex),
            )

        # ==========================================================
        # VALIDATE
        # ==========================================================

        try:
            dataframe = self.validator.validate(
                dataframe
            )

            self.logger.info(
                "Universe Master validation completed successfully."
            )

        except Exception as ex:
            completed_at = datetime.now()

            rows_failed = rows_read

            self.logger.exception(
                "Universe Master validation failed."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=rows_read,
                rows_imported=0,
                rows_failed=rows_failed,
                started_at=started_at,
                completed_at=completed_at,
                message="Universe Master validation failed.",
                exception=str(ex),
            )

        # ==========================================================
        # TRANSFORM
        # ==========================================================

        try:
            dataframe = self.transformer.transform(
                dataframe
            )

            self.logger.info(
                "Universe Master transformation completed successfully."
            )

        except Exception as ex:
            completed_at = datetime.now()

            rows_failed = rows_read

            self.logger.exception(
                "Universe Master transformation failed."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=rows_read,
                rows_imported=0,
                rows_failed=rows_failed,
                started_at=started_at,
                completed_at=completed_at,
                message="Universe Master transformation failed.",
                exception=str(ex),
            )

        # ==========================================================
        # DATABASE IMPORT + AUDIT
        # ==========================================================

        try:
            records = dataframe.to_dict(
                orient="records"
            )

            with UnitOfWork() as uow:

                batch_service = ImportBatchService(
                    uow.import_batches
                )

                batch = batch_service.start_batch(
                    batch_name=self.BATCH_NAME,
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
                    "Universe import batch started: %s",
                    batch.batch_id,
                )

                stats = self.service.import_records(
                    records,
                    uow,
                )

                rows_imported = stats["imported"]

                skipped = stats["skipped"]

                rows_failed = max(
                    0,
                    rows_read
                    - rows_imported
                    - skipped,
                )

                batch_service.finish_execution(
                    execution=execution,
                    rows_read=rows_read,
                    rows_imported=rows_imported,
                    rows_failed=rows_failed,
                    message=(
                        "Universe Master imported successfully."
                    ),
                    exception=None,
                )

                batch_service.complete_batch(
                    batch
                )

                self.logger.info(
                    "Universe Master database import completed."
                )

        except Exception as ex:
            completed_at = datetime.now()

            rows_failed = max(
                rows_failed,
                rows_read - rows_imported,
            )

            self.logger.exception(
                "Universe Master database import failed."
            )

            return ImportResult(
                success=False,
                file_name=file_path.name,
                rows_read=rows_read,
                rows_imported=rows_imported,
                rows_failed=rows_failed,
                started_at=started_at,
                completed_at=completed_at,
                message="Universe Master database import failed.",
                exception=str(ex),
            )

        completed_at = datetime.now()

        self.logger.info(
            "Universe Master import completed successfully."
        )

        self.logger.info(
            "Rows Read     : %d",
            rows_read,
        )

        self.logger.info(
            "Rows Imported : %d",
            rows_imported,
        )

        self.logger.info(
            "Rows Failed   : %d",
            rows_failed,
        )

        self.logger.info(
            "Duration      : %.2f seconds",
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
            message="Universe Master imported successfully.",
        )

    def import_latest_csv(
        self,
        directory: str | Path,
        pattern: str = "*.csv",
    ) -> ImportResult:
        """
        Import the most recently modified Universe CSV.
        """

        directory = Path(directory)

        if not directory.exists():
            now = datetime.now()

            return ImportResult(
                success=False,
                file_name="LATEST_CSV",
                rows_read=0,
                rows_imported=0,
                rows_failed=0,
                started_at=now,
                completed_at=now,
                message="Universe Master directory not found.",
                exception=str(directory),
            )

        files = [
            path
            for path in directory.glob(pattern)
            if path.is_file()
        ]

        if not files:
            now = datetime.now()

            return ImportResult(
                success=False,
                file_name="LATEST_CSV",
                rows_read=0,
                rows_imported=0,
                rows_failed=0,
                started_at=now,
                completed_at=now,
                message="No Universe Master CSV files found.",
                exception=(
                    f"No files matching '{pattern}' "
                    f"found in {directory}"
                ),
            )

        latest_file = max(
            files,
            key=lambda path: path.stat().st_mtime,
        )

        return self.import_csv(latest_file)
