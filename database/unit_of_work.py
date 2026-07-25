"""
AI Trading Operating System
Unit of Work
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from database.repositories.market_data_repository import MarketDataRepository
from database.repositories.symbol_repository import SymbolRepository
from database.session import SessionFactory


class UnitOfWork:
    """
    Enterprise Unit of Work.

    Provides one transaction across multiple repositories.
    """

    def __init__(self):

        self.session: Session = SessionFactory()

        self.symbols = SymbolRepository(self.session)

        self.market_data = MarketDataRepository(self.session)

    def commit(self):

        self.session.commit()

    def rollback(self):

        self.session.rollback()

    def close(self):

        self.session.close()

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        if exc_type is None:

            self.commit()

        else:

            self.rollback()

        self.close()