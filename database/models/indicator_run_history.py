"""
AI Trading Operating System
Indicator Run History Model
"""

from __future__ import annotations

import uuid

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base_model import BaseModel


class IndicatorRunHistory(BaseModel):
    __tablename__ = "indicator_run_history"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    run_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    symbols_processed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    records_processed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    started_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    completed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    remarks: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )