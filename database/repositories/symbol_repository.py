"""
AI Trading Operating System
Symbol Repository
"""

from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from database.models.symbol import Symbol
from database.repositories.base_repository import BaseRepository


class SymbolRepository(BaseRepository[Symbol]):
    """
    Repository for Symbol-specific database operations.

    Generic CRUD functionality is inherited from BaseRepository.
    """

    model = Symbol

    # ------------------------------------------------------------------
    # Symbol Lookup
    # ------------------------------------------------------------------

    def get_by_symbol_code(
        self,
        symbol_code: str,
    ) -> Symbol | None:
        """Return a symbol by symbol code."""

        stmt = (
            select(Symbol)
            .where(Symbol.symbol_code == symbol_code)
        )

        return self.session.scalar(stmt)

    def get_by_exchange(
        self,
        exchange: str,
    ) -> Sequence[Symbol]:
        """Return all symbols for an exchange."""

        stmt = (
            select(Symbol)
            .where(Symbol.exchange == exchange)
            .order_by(Symbol.symbol_code)
        )

        return self.session.scalars(stmt).all()

    def get_symbol_id_map(
        self,
        symbol_codes: list[str],
    ) -> dict[str, UUID]:
        """Return a mapping of symbol_code -> symbol_id."""

        if not symbol_codes:
            return {}

        stmt = (
            select(
                Symbol.symbol_code,
                Symbol.symbol_id,
            )
            .where(Symbol.symbol_code.in_(symbol_codes))
        )

        rows = self.session.execute(stmt).all()

        return {
            symbol_code: symbol_id
            for symbol_code, symbol_id in rows
        }

    # ------------------------------------------------------------------
    # Bulk Symbol Master Import
    # ------------------------------------------------------------------

    def bulk_upsert(
        self,
        records: list[dict],
    ) -> dict[str, int]:
        """
        Bulk insert or update symbol master records.

        Existing symbols are matched using symbol_code.

        Existing symbols are updated only for fields owned by
        the NSE Symbol Master source.

        Enrichment/operational fields such as sector, industry,
        is_fno, symbol_id and is_active are preserved for existing
        symbols.

        Transaction control remains with UnitOfWork.

        Symbols missing from the source file are NOT deleted.
        """

        if not records:
            return {
                "received": 0,
                "affected": 0,
            }

        stmt = insert(Symbol).values(records)

        # --------------------------------------------------------------
        # Fields owned by the NSE Symbol Master source.
        #
        # Do NOT update:
        #   - sector
        #   - industry
        #   - is_fno
        #   - symbol_id
        #   - is_active
        #
        # These fields are maintained independently from the routine
        # NSE Symbol Master refresh.
        # --------------------------------------------------------------

        update_columns = {
            "symbol_name": stmt.excluded.symbol_name,
            "exchange": stmt.excluded.exchange,
            "instrument_type": stmt.excluded.instrument_type,
            "series": stmt.excluded.series,
            "isin": stmt.excluded.isin,
            "lot_size": stmt.excluded.lot_size,
            "tick_size": stmt.excluded.tick_size,
            "face_value": stmt.excluded.face_value,
            "listing_date": stmt.excluded.listing_date,
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=[
                Symbol.symbol_code
            ],
            set_=update_columns,
        )

        stmt = stmt.returning(
            Symbol.symbol_id
        )

        result = self.session.execute(stmt)

        affected_ids = [
            row[0]
            for row in result.fetchall()
        ]

        # Refresh existing ORM objects that may already be present
        # in the SQLAlchemy session.
        for symbol_id in affected_ids:
            symbol = self.session.get(
                Symbol,
                symbol_id,
            )

            if symbol is not None:
                self.session.refresh(symbol)

        return {
            "received": len(records),
            "affected": len(affected_ids),
        }

    # ------------------------------------------------------------------
    # Active Symbols
    # ------------------------------------------------------------------

    def get_active_symbols(
        self,
    ) -> Sequence[Symbol]:
        """
        Return all active symbols.
        """

        stmt = (
            select(Symbol)
            .where(Symbol.is_active.is_(True))
            .order_by(Symbol.symbol_code)
        )

        return self.session.scalars(stmt).all()

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        keyword: str,
    ) -> Sequence[Symbol]:
        """
        Search by symbol code or symbol name.
        """

        pattern = f"%{keyword}%"

        stmt = (
            select(Symbol)
            .where(
                Symbol.symbol_code.ilike(pattern)
                | Symbol.symbol_name.ilike(pattern)
            )
            .order_by(Symbol.symbol_code)
        )

        return self.session.scalars(stmt).all()

    # ------------------------------------------------------------------
    # Existence
    # ------------------------------------------------------------------

    def exists_by_symbol_code(
        self,
        symbol_code: str,
    ) -> bool:
        """
        Check whether a symbol code already exists.
        """

        stmt = (
            select(Symbol.symbol_id)
            .where(Symbol.symbol_code == symbol_code)
            .limit(1)
        )

        return self.session.scalar(stmt) is not None

    # ------------------------------------------------------------------
    # Symbol Codes
    # ------------------------------------------------------------------

    def get_all_symbol_codes(
        self,
    ) -> list[str]:
        """
        Return all symbol codes.
        """

        stmt = (
            select(Symbol.symbol_code)
            .order_by(Symbol.symbol_code)
        )

        return list(
            self.session.scalars(stmt).all()
        )

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def count_by_exchange(
        self,
        exchange: str,
    ) -> int:
        """
        Return total symbols for an exchange.
        """

        stmt = (
            select(func.count())
            .select_from(Symbol)
            .where(Symbol.exchange == exchange)
        )

        return self.session.scalar(stmt) or 0

    def get_master_statistics(self) -> dict:
        """
        Return a quality/control snapshot of the Symbol Master.

        This method is read-only and performs aggregate queries only.
        """

        total = self.session.scalar(
            select(func.count()).select_from(Symbol)
        ) or 0

        active = self.session.scalar(
            select(func.count())
            .select_from(Symbol)
            .where(Symbol.is_active.is_(True))
        ) or 0

        inactive = self.session.scalar(
            select(func.count())
            .select_from(Symbol)
            .where(Symbol.is_active.is_(False))
        ) or 0

        fno = self.session.scalar(
            select(func.count())
            .select_from(Symbol)
            .where(Symbol.is_fno.is_(True))
        ) or 0

        with_isin = self.session.scalar(
            select(func.count())
            .select_from(Symbol)
            .where(Symbol.isin.is_not(None))
        ) or 0

        with_listing_date = self.session.scalar(
            select(func.count())
            .select_from(Symbol)
            .where(Symbol.listing_date.is_not(None))
        ) or 0

        exchange_rows = self.session.execute(
            select(
                Symbol.exchange,
                func.count().label("count"),
            )
            .group_by(Symbol.exchange)
            .order_by(Symbol.exchange)
        ).all()

        instrument_rows = self.session.execute(
            select(
                Symbol.instrument_type,
                func.count().label("count"),
            )
            .group_by(Symbol.instrument_type)
            .order_by(Symbol.instrument_type)
        ).all()

        series_rows = self.session.execute(
            select(
                Symbol.series,
                func.count().label("count"),
            )
            .group_by(Symbol.series)
            .order_by(Symbol.series)
        ).all()

        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "fno": fno,
            "with_isin": with_isin,
            "without_isin": total - with_isin,
            "with_listing_date": with_listing_date,
            "without_listing_date": total - with_listing_date,
            "by_exchange": {
                exchange: count
                for exchange, count in exchange_rows
            },
            "by_instrument_type": {
                instrument_type: count
                for instrument_type, count in instrument_rows
            },
            "by_series": {
                series: count
                for series, count in series_rows
            },
        }
