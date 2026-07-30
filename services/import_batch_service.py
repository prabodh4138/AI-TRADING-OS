"""
=========================================================
AI Trading Operating System
Import Batch Service
=========================================================

Business service responsible for coordinating
ImportBatch and ImportExecution.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from common.enums.import_status import ImportStatus
from database.models.import_batch import ImportBatch
from database.models.import_execution import ImportExecution
from database.repositories.import_batch_repository import (
    ImportBatchRepository,
)


class ImportBatchService:
    """
    Business service for batch imports.
    """

    def __init__(
        self,
        repository: ImportBatchRepository,
    ):
        self.repository = repository

    # ---------------------------------------------------------
    # Batch
    # ---------------------------------------------------------

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
            started_at=datetime.utcnow(),
            total_files=total_files,
            successful_files=0,
            failed_files=0,
            total_rows_read=0,
            total_rows_imported=0,
            total_rows_failed=0,
        )

        self.repository.create_batch(batch)
        self.repository.save()

        return batch

    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------

    def register_execution(
        self,
        batch_id: UUID,
        file_name: str,
    ) -> ImportExecution:
        """
        Creates execution record.
        """

        execution = ImportExecution(
            batch_id=batch_id,
            file_name=file_name,
            status=ImportStatus.PENDING,
        )

        self.repository.create_execution(execution)
        self.repository.save()

        return execution

    def start_execution(
        self,
        execution: ImportExecution,
    ) -> None:

        execution.status = ImportStatus.RUNNING
        execution.started_at = datetime.utcnow()

        self.repository.update_execution(execution)
        self.repository.save()

    def finish_execution(
        self,
        execution: ImportExecution,
        rows_read: int,
        rows_imported: int,
        rows_failed: int,
        message: str | None = None,
    ) -> None:
        """
        Marks execution complete.
        """

        execution.completed_at = datetime.utcnow()

        execution.rows_read = rows_read
        execution.rows_imported = rows_imported
        execution.rows_failed = rows_failed

        execution.message = message

        if rows_failed == 0:
            execution.status = ImportStatus.SUCCESS
        else:
            execution.status = ImportStatus.FAILED

        batch = execution.batch

        batch.total_rows_read += rows_read
        batch.total_rows_imported += rows_imported
        batch.total_rows_failed += rows_failed

        if execution.status == ImportStatus.SUCCESS:
            batch.successful_files += 1
        else:
            batch.failed_files += 1

        self.repository.save()

    # ---------------------------------------------------------
    # Batch Completion
    # ---------------------------------------------------------

    def complete_batch(
        self,
        batch: ImportBatch,
    ) -> None:
        """
        Finalizes import batch.
        """

        batch.completed_at = datetime.utcnow()

        if batch.failed_files == 0:
            batch.status = ImportStatus.SUCCESS
        else:
            batch.status = ImportStatus.FAILED

        self.repository.save()

    # ---------------------------------------------------------
    # Error Handling
    # ---------------------------------------------------------

    def fail_batch(
        self,
        batch: ImportBatch,
        message: str | None = None,
    ) -> None:
        """
        Marks entire batch as failed.
        """

        batch.status = ImportStatus.FAILED
        batch.completed_at = datetime.utcnow()

        self.repository.save()

    def rollback(self) -> None:
        """
        Rollback current transaction.
        """

        self.repository.rollback()