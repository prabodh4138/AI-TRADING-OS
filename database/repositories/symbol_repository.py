"""
AI Trading Operating System
Symbol Repository
"""

from __future__ import annotations

from sqlalchemy import select

from database.models.symbol import Symbol
from database.repositories.base_repository import BaseRepository


class SymbolRepository(BaseRepository[Symbol]):
    """
    Repository for Symbol operations.
    """

    model = Symbol

    def get_by_symbol_code(self, symbol_code: str) -> Symbol | None:
        stmt = (
            select(Symbol)
            .where(Symbol.symbol_code == symbol_code)
        )
        return self.session.scalar(stmt)