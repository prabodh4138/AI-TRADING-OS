"""
AI Trading Operating System
Download History Model
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Enum, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base_model import BaseModel


class DownloadStatus(str, enum.Enum):
    """
    Status of a download operation.
    """

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class DownloadHistory(BaseModel):
    """
    Stores the history of every market-data download.

    Each record represents one logical download attempt for a
    provider, dataset and trading date.
    """

    __tablename__ = "download_history"

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "dataset",
            "trading_date",
            name="uq_download_history_provider_dataset_date",
        ),
    )

    download_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    provider: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    dataset: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    trading_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    file_size: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
    )

    checksum: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    status: Mapped[DownloadStatus] = mapped_column(
    Enum(
        DownloadStatus,
        name="download_status_enum",
        native_enum=True,
        create_constraint=True,
    ),
        nullable=False,
        default=DownloadStatus.PENDING,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<DownloadHistory("
            f"provider='{self.provider}', "
            f"dataset='{self.dataset}', "
            f"trading_date='{self.trading_date}', "
            f"status='{self.status.value}')>"
        )