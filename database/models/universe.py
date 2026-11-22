"""
AI Trading Operating System
Universe Master Model

Defines reusable market universes such as NIFTY 500,
NIFTY 100, sector indices, and custom universes.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base_model import BaseModel

if TYPE_CHECKING:
    from .universe_constituent import UniverseConstituent


class Universe(BaseModel):
    """
    Master definition of a market universe.

    Examples:
        NIFTY500
        NIFTY100
        NIFTY200
        CUSTOM_POSitional
    """

    __tablename__ = "universe"

    universe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    universe_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    universe_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    universe_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="INDEX",
        index=True,
    )

    provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    constituents: Mapped[list["UniverseConstituent"]] = relationship(
        back_populates="universe",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<Universe("
            f"code='{self.universe_code}', "
            f"name='{self.universe_name}')>"
        )
