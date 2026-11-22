"""
AI Trading Operating System
Universe Constituent Model

Maintains historical membership of symbols within a universe.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base_model import BaseModel

if TYPE_CHECKING:
    from .symbol import Symbol
    from .universe import Universe


class UniverseConstituent(BaseModel):
    """
    Historical membership of a Symbol within a Universe.

    effective_from:
        First date on which membership is valid.

    effective_to:
        Last date on which membership is valid.
        NULL means membership remains open-ended/current.
    """

    __tablename__ = "universe_constituent"

    __table_args__ = (
        UniqueConstraint(
            "universe_id",
            "symbol_id",
            "effective_from",
            name="uq_universe_constituent_period",
        ),
        Index(
            "ix_universe_constituent_universe_date",
            "universe_id",
            "effective_from",
            "effective_to",
        ),
        Index(
            "ix_universe_constituent_symbol_date",
            "symbol_id",
            "effective_from",
            "effective_to",
        ),
    )

    universe_constituent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    universe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "universe.universe_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    symbol_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "symbol.symbol_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    effective_from: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    effective_to: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    universe: Mapped["Universe"] = relationship(
        back_populates="constituents",
    )

    symbol: Mapped["Symbol"] = relationship()

    def __repr__(self) -> str:
        return (
            f"<UniverseConstituent("
            f"universe_id={self.universe_id}, "
            f"symbol_id={self.symbol_id}, "
            f"from={self.effective_from}, "
            f"to={self.effective_to})>"
        )
