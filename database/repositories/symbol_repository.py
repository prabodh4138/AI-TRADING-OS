"""
AI Trading Operating System
Symbol Repository
"""

from __future__ import annotations

from typing import Sequence

from sqlalchemy import func, select

from database.models.symbol import Symbol
from database.repositories.base_repository import BaseRepository


class SymbolRepository(BaseRepository[Symbol]):
    """
    Repository for Symbol.

    Contains only symbol-specific queries.
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
        """
        Return symbol by symbol code.
        """

        stmt = (
            select(Symbol)
            .where(
                Symbol.symbol_code == symbol_code
            )
        )

        return self.session.scalar(stmt)

    def get_by_exchange(
        self,
        exchange: str,
    ) -> Sequence[Symbol]:
        """
        Return all symbols for an exchange.
        """

        stmt = (
            select(Symbol)
            .where(
                Symbol.exchange == exchange
            )
            .order_by(
                Symbol.symbol_code
            )
        )

        return self.session.scalars(stmt).all()

    def get_active_symbols(self) -> Sequence[Symbol]:
        """
        Return all tradable symbols.

        Currently returns all symbols.
        Reserved for future active/inactive filtering.
        """

        stmt = (
            select(Symbol)
            .order_by(
                Symbol.symbol_code
            )
        )

        return self.session.scalars(stmt).all()

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
            .order_by(
                Symbol.symbol_code
            )
        )

        return self.session.scalars(stmt).all()

    def exists_by_symbol_code(
        self,
        symbol_code: str,
    ) -> bool:
        """
        Check whether a symbol code already exists.
        """

        stmt = (
            select(Symbol.symbol_id)
            .where(
                Symbol.symbol_code == symbol_code
            )
            .limit(1)
        )

        return self.session.scalar(stmt) is not None

    def get_all_symbol_codes(
        self,
    ) -> list[str]:
        """
        Return all symbol codes.
        """

        stmt = (
            select(Symbol.symbol_code)
            .order_by(
                Symbol.symbol_code
            )
        )

        return list(
            self.session.scalars(stmt).all()
        )

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
            .where(
                Symbol.exchange == exchange
            )
        )

        return self.session.scalar(stmt) or 0