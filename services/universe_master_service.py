from __future__ import annotations

from datetime import date
from typing import Any

from database.models.universe import Universe
from database.models.universe_constituent import UniverseConstituent
from database.unit_of_work import UnitOfWork
from services.base_service import BaseService


class UniverseMasterService(BaseService):
    """Business service for importing universe definitions and memberships."""

    def import_records(
        self,
        records: list[dict[str, Any]],
        uow: UnitOfWork,
    ) -> dict[str, int]:
        if not records:
            raise ValueError("Import records cannot be empty.")

        if uow is None:
            raise ValueError("UnitOfWork cannot be None.")

        universe_codes = {
            str(record.get("universe_code", "")).strip().upper()
            for record in records
        }

        universe_codes.discard("")

        if len(universe_codes) != 1:
            raise ValueError(
                "A single import must contain exactly one universe_code."
            )

        universe_code = next(iter(universe_codes))

        first = records[0]

        universe_name = self._require_text(
            first.get("universe_name"),
            "universe_name",
        )
        universe_type = self._require_text(
            first.get("universe_type"),
            "universe_type",
        )
        provider = self._optional_text(first.get("provider"))

        universe = uow.universes.get_by_universe_code(universe_code)

        if universe is None:
            universe = Universe(
                universe_code=universe_code,
                universe_name=universe_name,
                universe_type=universe_type,
                provider=provider,
            )
            uow.universes.add(universe)
            uow.flush()
        else:
            self._validate_universe_definition(
                universe=universe,
                universe_name=universe_name,
                universe_type=universe_type,
                provider=provider,
            )

        symbol_codes = {
            str(record.get("symbol_code", "")).strip().upper()
            for record in records
        }

        symbol_codes.discard("")

        symbol_id_map = uow.symbols.get_symbol_id_map(
            list(symbol_codes)
        )

        received = len(records)
        imported = 0
        skipped = 0
        failed = 0

        for record in records:
            symbol_code = str(
                record.get("symbol_code", "")
            ).strip().upper()

            if not symbol_code:
                raise ValueError("symbol_code is required.")

            symbol_id = symbol_id_map.get(symbol_code)

            if symbol_id is None:
                raise ValueError(
                    f"Unknown symbol_code: {symbol_code}"
                )

            effective_from = self._require_date(
                record.get("effective_from"),
                "effective_from",
            )

            effective_to = self._optional_date(
                record.get("effective_to")
            )

            if effective_to is not None and effective_to < effective_from:
                raise ValueError(
                    "effective_to cannot be earlier than effective_from."
                )

            existing = uow.universes.get_membership(
                universe_id=universe.universe_id,
                symbol_id=symbol_id,
                effective_from=effective_from,
            )

            if existing is not None:
                skipped += 1
                continue

            membership = UniverseConstituent(
                universe_id=universe.universe_id,
                symbol_id=symbol_id,
                effective_from=effective_from,
                effective_to=effective_to,
            )

            uow.universes.add(membership)

            imported += 1

        uow.flush()

        return {
            "received": received,
            "imported": imported,
            "skipped": skipped,
            "failed": failed,
        }

    @staticmethod
    def _validate_universe_definition(
        universe: Universe,
        universe_name: str,
        universe_type: str,
        provider: str | None,
    ) -> None:
        if universe.universe_name != universe_name:
            raise ValueError(
                f"Universe metadata mismatch for "
                f"{universe.universe_code}: universe_name differs."
            )

        if universe.universe_type != universe_type:
            raise ValueError(
                f"Universe metadata mismatch for "
                f"{universe.universe_code}: universe_type differs."
            )

        if universe.provider != provider:
            raise ValueError(
                f"Universe metadata mismatch for "
                f"{universe.universe_code}: provider differs."
            )

    @staticmethod
    def _require_text(value: Any, field_name: str) -> str:
        if value is None:
            raise ValueError(f"{field_name} is required.")

        value = str(value).strip()

        if not value:
            raise ValueError(f"{field_name} is required.")

        return value

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        if value is None:
            return None

        value = str(value).strip()

        return value or None

    @staticmethod
    def _require_date(value: Any, field_name: str) -> date:
        if value is None:
            raise ValueError(f"{field_name} is required.")

        if not isinstance(value, date):
            raise ValueError(
                f"{field_name} must be a date."
            )

        return value

    @staticmethod
    def _optional_date(value: Any) -> date | None:
        if value is None:
            return None

        if not isinstance(value, date):
            raise ValueError(
                "effective_to must be a date."
            )

        return value
