"""
AI Trading Operating System
Universe Repository
"""

from __future__ import annotations

from datetime import date
from typing import Sequence
from uuid import UUID

from sqlalchemy import and_, or_, select

from database.models.symbol import Symbol
from database.models.universe import Universe
from database.models.universe_constituent import UniverseConstituent
from database.repositories.base_repository import BaseRepository


class UniverseRepository(BaseRepository[Universe]):
    """
    Repository for Universe-specific database operations.

    Historical membership queries intentionally do not depend on
    is_active. A membership may be inactive today but still be valid
    for a historical date.

    Transaction control remains with UnitOfWork.
    """

    model = Universe

    # ------------------------------------------------------------------
    # Universe Lookup
    # ------------------------------------------------------------------

    def get_by_universe_code(
        self,
        universe_code: str,
    ) -> Universe | None:
        """Return a universe by its unique code."""

        stmt = (
            select(Universe)
            .where(Universe.universe_code == universe_code)
        )

        return self.session.scalar(stmt)

    def get_active_universes(
        self,
    ) -> Sequence[Universe]:
        """Return all active universes ordered by code."""

        stmt = (
            select(Universe)
            .where(Universe.is_active.is_(True))
            .order_by(Universe.universe_code)
        )

        return self.session.scalars(stmt).all()

    def get_by_type(
        self,
        universe_type: str,
    ) -> Sequence[Universe]:
        """Return universes of a specific type."""

        stmt = (
            select(Universe)
            .where(Universe.universe_type == universe_type)
            .order_by(Universe.universe_code)
        )

        return self.session.scalars(stmt).all()

    # ------------------------------------------------------------------
    # Universe Constituents
    # ------------------------------------------------------------------

    def get_constituents(
        self,
        universe_id: UUID,
        as_of_date: date | None = None,
        active_only: bool = True,
    ) -> Sequence[UniverseConstituent]:
        """
        Return universe constituents.

        Current query:
            Returns open-ended active memberships.

        Historical query:
            Returns memberships valid on as_of_date regardless of
            their current is_active status.

        This distinction is required for historical backtesting.
        """

        conditions = [
            UniverseConstituent.universe_id == universe_id,
        ]

        if as_of_date is None:
            conditions.append(
                UniverseConstituent.effective_to.is_(None)
            )

            if active_only:
                conditions.append(
                    UniverseConstituent.is_active.is_(True)
                )

        else:
            conditions.extend(
                [
                    UniverseConstituent.effective_from <= as_of_date,
                    or_(
                        UniverseConstituent.effective_to.is_(None),
                        UniverseConstituent.effective_to >= as_of_date,
                    ),
                ]
            )

        stmt = (
            select(UniverseConstituent)
            .where(and_(*conditions))
            .order_by(
                UniverseConstituent.effective_from,
                UniverseConstituent.symbol_id,
            )
        )

        return self.session.scalars(stmt).all()

    def get_constituent_symbols(
        self,
        universe_id: UUID,
        as_of_date: date | None = None,
        active_only: bool = True,
    ) -> Sequence[Symbol]:
        """
        Return Symbol records belonging to a universe.

        Historical queries return symbols that were constituents on
        the requested date, even if their membership is now closed.
        """

        conditions = [
            UniverseConstituent.universe_id == universe_id,
        ]

        if as_of_date is None:
            conditions.append(
                UniverseConstituent.effective_to.is_(None)
            )

            if active_only:
                conditions.append(
                    UniverseConstituent.is_active.is_(True)
                )

        else:
            conditions.extend(
                [
                    UniverseConstituent.effective_from <= as_of_date,
                    or_(
                        UniverseConstituent.effective_to.is_(None),
                        UniverseConstituent.effective_to >= as_of_date,
                    ),
                ]
            )

        stmt = (
            select(Symbol)
            .join(
                UniverseConstituent,
                UniverseConstituent.symbol_id == Symbol.symbol_id,
            )
            .where(and_(*conditions))
            .order_by(Symbol.symbol_code)
        )

        return self.session.scalars(stmt).all()

    # ------------------------------------------------------------------
    # Membership Lookup
    # ------------------------------------------------------------------

    def get_membership(
        self,
        universe_id: UUID,
        symbol_id: UUID,
        effective_from: date,
    ) -> UniverseConstituent | None:
        """Return a specific membership period."""

        stmt = (
            select(UniverseConstituent)
            .where(
                UniverseConstituent.universe_id == universe_id,
                UniverseConstituent.symbol_id == symbol_id,
                UniverseConstituent.effective_from == effective_from,
            )
        )

        return self.session.scalar(stmt)

    def get_symbol_memberships(
        self,
        symbol_id: UUID,
        as_of_date: date | None = None,
    ) -> Sequence[UniverseConstituent]:
        """
        Return universe memberships for a symbol.

        Historical queries ignore current is_active status and evaluate
        membership using the effective date range.
        """

        conditions = [
            UniverseConstituent.symbol_id == symbol_id,
        ]

        if as_of_date is None:
            conditions.extend(
                [
                    UniverseConstituent.effective_to.is_(None),
                    UniverseConstituent.is_active.is_(True),
                ]
            )

        else:
            conditions.extend(
                [
                    UniverseConstituent.effective_from <= as_of_date,
                    or_(
                        UniverseConstituent.effective_to.is_(None),
                        UniverseConstituent.effective_to >= as_of_date,
                    ),
                ]
            )

        stmt = (
            select(UniverseConstituent)
            .where(and_(*conditions))
            .order_by(
                UniverseConstituent.effective_from,
                UniverseConstituent.universe_id,
            )
        )

        return self.session.scalars(stmt).all()

    def is_symbol_in_universe(
        self,
        universe_id: UUID,
        symbol_id: UUID,
        as_of_date: date | None = None,
    ) -> bool:
        """
        Check whether a symbol belongs to a universe.

        Current checks use active/open membership.

        Historical checks use effective dates only so that closed
        memberships remain valid for their historical period.
        """

        conditions = [
            UniverseConstituent.universe_id == universe_id,
            UniverseConstituent.symbol_id == symbol_id,
        ]

        if as_of_date is None:
            conditions.extend(
                [
                    UniverseConstituent.effective_to.is_(None),
                    UniverseConstituent.is_active.is_(True),
                ]
            )

        else:
            conditions.extend(
                [
                    UniverseConstituent.effective_from <= as_of_date,
                    or_(
                        UniverseConstituent.effective_to.is_(None),
                        UniverseConstituent.effective_to >= as_of_date,
                    ),
                ]
            )

        stmt = (
            select(UniverseConstituent.universe_constituent_id)
            .where(and_(*conditions))
            .limit(1)
        )

        return self.session.scalar(stmt) is not None

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def count_constituents(
        self,
        universe_id: UUID,
        as_of_date: date | None = None,
        active_only: bool = True,
    ) -> int:
        """Return the number of valid constituents."""

        conditions = [
            UniverseConstituent.universe_id == universe_id,
        ]

        if as_of_date is None:
            conditions.append(
                UniverseConstituent.effective_to.is_(None)
            )

            if active_only:
                conditions.append(
                    UniverseConstituent.is_active.is_(True)
                )

        else:
            conditions.extend(
                [
                    UniverseConstituent.effective_from <= as_of_date,
                    or_(
                        UniverseConstituent.effective_to.is_(None),
                        UniverseConstituent.effective_to >= as_of_date,
                    ),
                ]
            )

        stmt = (
            select(UniverseConstituent.universe_constituent_id)
            .where(and_(*conditions))
        )

        return len(self.session.scalars(stmt).all())
