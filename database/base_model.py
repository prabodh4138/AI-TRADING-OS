"""
AI Trading Operating System
Base ORM Model

All database tables inherit from this class.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class BaseModel(Base):
    """
    Abstract base model.

    Provides common audit columns for every table.
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )