"""
=========================================================
AI Trading Operating System
Import Execution Model
=========================================================

Represents the execution of a single CSV file within
an import batch.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from common.enums.import_status import ImportStatus
from database.base_model import BaseModel

if TYPE_CHECKING:
    from database.models.import_batch import ImportBatch


class ImportExecution(BaseModel):
    """
    Represents one imported CSV file.
    """

    __tablename__ = "import_execution"

    __table_args__ = (
        Index(
            "ix_import_execution_batch",
            "batch_id",
        ),
        Index(
            "ix_import_execution_status",
            "status",
        ),
        Index(
            "ix_import_execution_file",
            "file_name",
        ),
    )

    # ---------------------------------------------------------
    # Primary Key
    # ---------------------------------------------------------

    execution_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ---------------------------------------------------------
    # Batch Relationship
    # ---------------------------------------------------------

    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "import_batch.batch_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        
    )

    batch: Mapped["ImportBatch"] = relationship(
        back_populates="executions",
    )

    # ---------------------------------------------------------
    # File Information
    # ---------------------------------------------------------

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[ImportStatus] = mapped_column(
        Enum(
            ImportStatus,
            name="import_status",
        ),
        default=ImportStatus.PENDING,
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    # ---------------------------------------------------------
    # Execution Statistics
    # ---------------------------------------------------------

    rows_read: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    rows_imported: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    rows_failed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # ---------------------------------------------------------
    # Error Information
    # ---------------------------------------------------------

    message: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    exception: Mapped[str | None] = mapped_column(
        String(4000),
        nullable=True,
    )

    # ---------------------------------------------------------
    # Computed Properties
    # ---------------------------------------------------------

    @property
    def duration_seconds(self) -> float | None:
        """
        Returns execution duration in seconds.
        """

        if (
            self.started_at is None
            or self.completed_at is None
        ):
            return None

        return (
            self.completed_at - self.started_at
        ).total_seconds()

    @property
    def success_rate(self) -> float:
        """
        Returns row import success percentage.
        """

        if self.rows_read == 0:
            return 0.0

        return (
            self.rows_imported
            / self.rows_read
        ) * 100.0

    @property
    def has_errors(self) -> bool:
        """
        Returns True if the execution contains errors.
        """

        return (
            self.status == ImportStatus.FAILED
            or self.rows_failed > 0
        )

    @property
    def is_completed(self) -> bool:
        """
        Returns True if execution has completed.
        """

        return self.status in (
            ImportStatus.SUCCESS,
            ImportStatus.FAILED,
            ImportStatus.CANCELLED,
        )

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"<ImportExecution("
            f"file='{self.file_name}', "
            f"status={self.status.value}, "
            f"rows={self.rows_imported}/"
            f"{self.rows_read})>"
        )