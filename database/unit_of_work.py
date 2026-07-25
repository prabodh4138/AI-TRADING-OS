"""
AI Trading Operating System
Enterprise Unit of Work
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from database.repositories.symbol_repository import SymbolRepository
from database.repositories.market_data_repository import MarketDataRepository
from database.repositories.indicator_repository import IndicatorRepository
from database.session import SessionFactory


class UnitOfWork:
    """
    Enterprise Unit of Work.

    Maintains a single database session across all repositories.

    Usage:
        with UnitOfWork() as uow:
            symbols = uow.symbols.get_all()
            market = uow.market_data.get_latest_price(symbol_id)
            indicators = uow.indicators.get_latest(symbol_id)
    """

    def __init__(self) -> None:
        self.session: Session = SessionFactory()

        # -------------------------------------------------------------
        # Repositories
        # -------------------------------------------------------------
        self.symbols = SymbolRepository(self.session)
        self.market_data = MarketDataRepository(self.session)
        self.indicators = IndicatorRepository(self.session)

    # -------------------------------------------------------------
    # Transaction Management
    # -------------------------------------------------------------

    def commit(self) -> None:
        """
        Commit current transaction.
        """
        self.session.commit()

    def rollback(self) -> None:
        """
        Roll back current transaction.
        """
        self.session.rollback()

    def flush(self) -> None:
        """
        Flush pending SQL statements.
        """
        self.session.flush()

    def close(self) -> None:
        """
        Close database session.
        """
        self.session.close()

    # -------------------------------------------------------------
    # Context Manager
    # -------------------------------------------------------------

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> bool:

        if exc_type is None:
            self.commit()
        else:
            self.rollback()

        self.close()

        # Never suppress exceptions
        return False