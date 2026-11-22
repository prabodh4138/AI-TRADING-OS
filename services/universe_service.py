"""
AI Trading Operating System
Universe Service

Business Service for Universe and Universe Constituent Management.
"""

from __future__ import annotations

from datetime import date
from typing import Optional, Sequence
from uuid import UUID

from database.models.symbol import Symbol
from database.models.universe import Universe
from database.models.universe_constituent import UniverseConstituent
from database.unit_of_work import UnitOfWork

from services.base_service import BaseService
from validators.base_validator import ValidationError


class UniverseService(BaseService):
    """
    Business Service for Universe operations.
    """

    # ---------------------------------------------------------
    # Validation Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _validate_text(
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize a required text field."""

        if value is None:
            raise ValidationError(
                f"{field_name} is required."
            )

        value = value.strip()

        if not value:
            raise ValidationError(
                f"{field_name} cannot be blank."
            )

        return value

    @staticmethod
    def _validate_membership_dates(
        effective_from: date,
        effective_to: date | None,
    ) -> None:
        """Validate a membership date range."""

        if effective_from is None:
            raise ValidationError(
                "effective_from is required."
            )

        if (
            effective_to is not None
            and effective_to < effective_from
        ):
            raise ValidationError(
                "effective_to cannot be earlier than effective_from."
            )

    # ---------------------------------------------------------
    # Universe Create
    # ---------------------------------------------------------

    def create_universe(
        self,
        universe_code: str,
        universe_name: str,
        universe_type: str = "INDEX",
        provider: str | None = None,
        description: str | None = None,
    ) -> Universe:
        """
        Create a new universe.

        Universe code is globally unique.
        """

        universe_code = self._validate_text(
            universe_code,
            "universe_code",
        )

        universe_name = self._validate_text(
            universe_name,
            "universe_name",
        )

        universe_type = self._validate_text(
            universe_type,
            "universe_type",
        )

        if provider is not None:
            provider = provider.strip() or None

        if description is not None:
            description = description.strip() or None

        with UnitOfWork() as uow:

            existing = uow.universes.get_by_universe_code(
                universe_code
            )

            if existing:
                raise ValidationError(
                    f"Universe '{universe_code}' already exists."
                )

            universe = Universe(
                universe_code=universe_code,
                universe_name=universe_name,
                universe_type=universe_type,
                provider=provider,
                description=description,
            )

            uow.universes.add(universe)

            uow.flush()

            return universe

    # ---------------------------------------------------------
    # Read
    # ---------------------------------------------------------

    def get_universe(
        self,
        universe_id: UUID,
    ) -> Optional[Universe]:

        with UnitOfWork() as uow:
            return uow.universes.get_by_id(universe_id)

    def get_by_universe_code(
        self,
        universe_code: str,
    ) -> Optional[Universe]:

        universe_code = self._validate_text(
            universe_code,
            "universe_code",
        )

        with UnitOfWork() as uow:
            return uow.universes.get_by_universe_code(
                universe_code
            )

    def get_all_universes(
        self,
    ) -> Sequence[Universe]:

        with UnitOfWork() as uow:
            return uow.universes.get_all()

    def get_active_universes(
        self,
    ) -> Sequence[Universe]:

        with UnitOfWork() as uow:
            return uow.universes.get_active_universes()

    def get_by_type(
        self,
        universe_type: str,
    ) -> Sequence[Universe]:

        universe_type = self._validate_text(
            universe_type,
            "universe_type",
        )

        with UnitOfWork() as uow:
            return uow.universes.get_by_type(
                universe_type
            )

    # ---------------------------------------------------------
    # Universe Status
    # ---------------------------------------------------------

    def activate_universe(
        self,
        universe_id: UUID,
    ) -> None:

        with UnitOfWork() as uow:

            universe = uow.universes.get_by_id(
                universe_id
            )

            self.require_not_none(
                universe,
                "Universe",
            )

            universe.is_active = True

            uow.flush()

    def deactivate_universe(
        self,
        universe_id: UUID,
    ) -> None:

        with UnitOfWork() as uow:

            universe = uow.universes.get_by_id(
                universe_id
            )

            self.require_not_none(
                universe,
                "Universe",
            )

            universe.is_active = False

            uow.flush()

    # ---------------------------------------------------------
    # Membership
    # ---------------------------------------------------------

    def add_membership(
        self,
        universe_id: UUID,
        symbol_id: UUID,
        effective_from: date,
        effective_to: date | None = None,
    ) -> UniverseConstituent:
        """
        Add a symbol to a universe for a defined period.

        Existing identical membership periods are rejected.
        """

        self._validate_membership_dates(
            effective_from,
            effective_to,
        )

        with UnitOfWork() as uow:

            universe = uow.universes.get_by_id(
                universe_id
            )

            self.require_not_none(
                universe,
                "Universe",
            )

            symbol = uow.symbols.get_by_id(
                symbol_id
            )

            self.require_not_none(
                symbol,
                "Symbol",
            )

            existing = uow.universes.get_membership(
                universe_id=universe_id,
                symbol_id=symbol_id,
                effective_from=effective_from,
            )

            if existing:
                raise ValidationError(
                    "Universe membership already exists "
                    f"for symbol '{symbol.symbol_code}' "
                    f"from {effective_from}."
                )

            membership = UniverseConstituent(
                universe_id=universe_id,
                symbol_id=symbol_id,
                effective_from=effective_from,
                effective_to=effective_to,
                is_active=True,
            )

            uow.session.add(membership)

            uow.flush()

            return membership

    def close_membership(
        self,
        universe_id: UUID,
        symbol_id: UUID,
        effective_to: date,
        effective_from: date | None = None,
    ) -> UniverseConstituent:
        """
        Close an open-ended membership.

        effective_to must not be earlier than effective_from.
        """

        with UnitOfWork() as uow:

            if effective_from is not None:
                membership = uow.universes.get_membership(
                    universe_id=universe_id,
                    symbol_id=symbol_id,
                    effective_from=effective_from,
                )
            else:
                memberships = uow.universes.get_symbol_memberships(
                    symbol_id=symbol_id,
                )

                membership = next(
                    (
                        item
                        for item in memberships
                        if item.universe_id == universe_id
                        and item.effective_to is None
                    ),
                    None,
                )

            self.require_not_none(
                membership,
                "Universe membership",
            )

            self._validate_membership_dates(
                membership.effective_from,
                effective_to,
            )

            if membership.effective_to is not None:
                raise ValidationError(
                    "Universe membership is already closed."
                )

            membership.effective_to = effective_to
            membership.is_active = False

            uow.flush()

            return membership

    # ---------------------------------------------------------
    # Membership Queries
    # ---------------------------------------------------------

    def get_constituents(
        self,
        universe_id: UUID,
        as_of_date: date | None = None,
    ) -> Sequence[UniverseConstituent]:

        with UnitOfWork() as uow:
            return uow.universes.get_constituents(
                universe_id=universe_id,
                as_of_date=as_of_date,
            )

    def get_constituent_symbols(
        self,
        universe_id: UUID,
        as_of_date: date | None = None,
    ) -> Sequence[Symbol]:

        with UnitOfWork() as uow:
            return uow.universes.get_constituent_symbols(
                universe_id=universe_id,
                as_of_date=as_of_date,
            )

    def get_symbol_memberships(
        self,
        symbol_id: UUID,
        as_of_date: date | None = None,
    ) -> Sequence[UniverseConstituent]:

        with UnitOfWork() as uow:
            return uow.universes.get_symbol_memberships(
                symbol_id=symbol_id,
                as_of_date=as_of_date,
            )

    def is_symbol_in_universe(
        self,
        universe_id: UUID,
        symbol_id: UUID,
        as_of_date: date | None = None,
    ) -> bool:

        with UnitOfWork() as uow:
            return uow.universes.is_symbol_in_universe(
                universe_id=universe_id,
                symbol_id=symbol_id,
                as_of_date=as_of_date,
            )

    def count_constituents(
        self,
        universe_id: UUID,
        as_of_date: date | None = None,
    ) -> int:

        with UnitOfWork() as uow:
            return uow.universes.count_constituents(
                universe_id=universe_id,
                as_of_date=as_of_date,
            )
