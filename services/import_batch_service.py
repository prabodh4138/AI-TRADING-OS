"""
=========================================================
AI Trading Operating System
Import Batch Service
=========================================================

Business service responsible for coordinating
ImportBatch and ImportExecution.

This service DOES NOT own transactions.
The caller (MarketDataPipeline) is responsible for
commit() and rollback().
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from common.enums.import_status import ImportStatus
from database.models.import_batch import ImportBatch
from database.models.import_execution import ImportExecution
from database.repositories.import_batch_repository import (
    ImportBatchRepository,
)


class ImportBatchService:
    """
    Business service responsible for import workflow.
    """

    def __init__(
        self,
        repository: ImportBatchRepository,
    ) -> None:

        self.repository = repository

    # =====================================================
    # Batch
    # =====================================================

    def start_batch(
        self,
        batch_name: str,
        total_files: int,
    ) -> ImportBatch:
        """
        Creates a new import batch.
        """

        batch = ImportBatch(
            batch_name=batch_name,
            status=ImportStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
            total_files=total_files,
            successful_files=0,
            failed_files=0,
            total_rows_read=0,
            total_rows_imported=0,
            total_rows_failed=0,
        )

        return self.repository.create_batch(batch)

    def complete_batch(
        self,
        batch: ImportBatch,
    ) -> None:
        """
        Marks batch as completed.
        """

        batch.completed_at = datetime.now(timezone.utc)

        if batch.failed_files == 0:
            batch.status = ImportStatus.SUCCESS
        else:
            batch.status = ImportStatus.FAILED

        self.repository.update_batch(batch)

    def fail_batch(
        self,
        batch: ImportBatch,
    ) -> None:
        """
        Marks batch as failed.
        """

        batch.status = ImportStatus.FAILED
        batch.completed_at = datetime.now(timezone.utc)

        self.repository.update_batch(batch)

    # =====================================================
    # Execution
    # =====================================================

    def register_execution(
        self,
        batch_id: UUID,
        file_name: str,
    ) -> ImportExecution:
        """
        Registers a CSV file execution.
        """

        execution = ImportExecution(
            batch_id=batch_id,
            file_name=file_name,
            status=ImportStatus.PENDING,
        )

        return self.repository.create_execution(
            execution
        )

    def start_execution(
        self,
        execution: ImportExecution,
    ) -> None:
        """
        Starts execution.
        """

        execution.status = ImportStatus.RUNNING
        execution.started_at = datetime.now(timezone.utc)

        self.repository.update_execution(execution)

    def finish_execution(
        self,
        execution: ImportExecution,
        rows_read: int,
        rows_imported: int,
        rows_failed: int,
        message: str | None = None,
        exception: str | None = None,
    ) -> None:
        """
        Completes execution and updates
        aggregate batch statistics.
        """

        execution.completed_at = datetime.now(
            timezone.utc
        )

        execution.rows_read = rows_read
        execution.rows_imported = rows_imported
        execution.rows_failed = rows_failed

        execution.message = message
        execution.exception = exception

        execution.status = (
            ImportStatus.SUCCESS
            if rows_failed == 0
            else ImportStatus.FAILED
        )

        batch = execution.batch

        batch.total_rows_read += rows_read
        batch.total_rows_imported += rows_imported
        batch.total_rows_failed += rows_failed

        if execution.status == ImportStatus.SUCCESS:
            batch.successful_files += 1
        else:
            batch.failed_files += 1

        self.repository.update_execution(
            execution
        )

        self.repository.update_batch(batch)