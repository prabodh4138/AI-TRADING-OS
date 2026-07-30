"""
=========================================================
AI Trading Operating System
Import Batch Repository
=========================================================

Repository responsible only for persistence of
ImportBatch and ImportExecution entities.

Transaction management is intentionally NOT handled
inside this repository. The caller (Pipeline / Unit of
Work) owns commit and rollback.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models.import_batch import ImportBatch
from database.models.import_execution import ImportExecution
from common.enums.import_status import ImportStatus


class ImportBatchRepository:
    """
    Repository responsible for persistence of
    ImportBatch and ImportExecution.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # =====================================================
    # Batch
    # =====================================================

    def create_batch(
        self,
        batch: ImportBatch,
    ) -> ImportBatch:

        self._session.add(batch)
        self._session.flush()

        return batch

    def get_batch(
        self,
        batch_id: uuid.UUID,
    ) -> ImportBatch | None:

        return self._session.get(
            ImportBatch,
            batch_id,
        )

    def update_batch(
        self,
        batch: ImportBatch,
    ) -> None:

        self._session.flush()

    def update_batch_status(
        self,
        batch: ImportBatch,
        status: ImportStatus,
    ) -> None:

        batch.status = status

        self._session.flush()

    def list_batches(
        self,
        limit: int = 100,
    ) -> list[ImportBatch]:

        stmt = (
            select(ImportBatch)
            .order_by(
                ImportBatch.started_at.desc()
            )
            .limit(limit)
        )

        return list(
            self._session.scalars(stmt)
        )

    # =====================================================
    # Execution
    # =====================================================

    def create_execution(
        self,
        execution: ImportExecution,
    ) -> ImportExecution:

        self._session.add(execution)
        self._session.flush()

        return execution

    def update_execution(
        self,
        execution: ImportExecution,
    ) -> None:

        self._session.flush()

    def get_execution(
        self,
        execution_id: uuid.UUID,
    ) -> ImportExecution | None:

        return self._session.get(
            ImportExecution,
            execution_id,
        )

    def list_executions(
        self,
        batch_id: uuid.UUID,
    ) -> list[ImportExecution]:

        stmt = (
            select(ImportExecution)
            .where(
                ImportExecution.batch_id == batch_id
            )
            .order_by(
                ImportExecution.file_name
            )
        )

        return list(
            self._session.scalars(stmt)
        )