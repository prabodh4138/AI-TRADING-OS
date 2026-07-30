"""
=========================================================
AI Trading Operating System
Import Batch Model
=========================================================

Represents a single batch execution of one or more
market data imports.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.import_execution import ImportExecution

from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Index

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from common.enums.import_status import ImportStatus
from database.base_model import BaseModel


class ImportBatch(BaseModel):
    """
    Represents one import batch execution.
    """

    __tablename__ = "import_batch"

    __table_args__ = (
        Index(
            "ix_import_batch_status",
            "status",
        ),
        Index(
            "ix_import_batch_started_at",
            "started_at",
        ),
    )

    # ---------------------------------------------------------
    # Primary Key
    # ---------------------------------------------------------

    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ---------------------------------------------------------
    # Batch Information
    # ---------------------------------------------------------

    batch_name: Mapped[str] = mapped_column(
        String(200),
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
    # Statistics
    # ---------------------------------------------------------

    total_files: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    successful_files: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    failed_files: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    # ---------------------------------------------------------
    # Row Statistics
    # ---------------------------------------------------------

    total_rows_read: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_rows_imported: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_rows_failed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    executions: Mapped[list["ImportExecution"]] = relationship(
        back_populates="batch",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ---------------------------------------------------------
    # Computed Properties
    # ---------------------------------------------------------

    @property
    def duration_seconds(self) -> float | None:
        """
        Returns the total execution time in seconds.
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
    def is_completed(self) -> bool:
        """
        Returns True if the batch has completed.
        """

        return self.status in (
            ImportStatus.SUCCESS,
            ImportStatus.FAILED,
            ImportStatus.CANCELLED,
        )

    @property
    def success_rate(self) -> float:
        """
        Returns file success percentage.
        """

        if self.total_files == 0:
            return 0.0

        return (
            self.successful_files
            / self.total_files
        ) * 100.0

    # ---------------------------------------------------------
    # Representation
    # ---------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"<ImportBatch("
            f"batch_name='{self.batch_name}', "
            f"status={self.status.value}, "
            f"files={self.successful_files}/"
            f"{self.total_files})>"
        )