"""
AI Trading Operating System
Enterprise Unit of Work
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from database.repositories.download_history_repository import (
    DownloadHistoryRepository,
)
from database.repositories.import_batch_repository import (
    ImportBatchRepository,
)
from database.repositories.indicator_repository import (
    IndicatorRepository,
)
from database.repositories.market_data_repository import (
    MarketDataRepository,
)
from database.repositories.symbol_repository import (
    SymbolRepository,
)
from database.repositories.universe_repository import (
    UniverseRepository,
)
from database.session import new_session


class UnitOfWork:
    """
    Enterprise Unit of Work.

    Maintains a single database session across all repositories.

    All repositories share the same SQLAlchemy session
    and therefore participate in the same transaction.
    """

    def __init__(self) -> None:
        self.session: Session = new_session()

        # -------------------------------------------------------------
        # Repositories
        # -------------------------------------------------------------

        self.symbols = SymbolRepository(
            self.session
        )

        self.market_data = MarketDataRepository(
            self.session
        )

        self.indicators = IndicatorRepository(
            self.session
        )

        self.download_history = DownloadHistoryRepository(
            self.session
        )

        self.import_batches = ImportBatchRepository(
            self.session
        )

        self.universes = UniverseRepository(
            self.session
        )

    # -------------------------------------------------------------
    # Transaction Management
    # -------------------------------------------------------------

    def commit(self) -> None:
        """Commit the current transaction."""

        self.session.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""

        self.session.rollback()

    def flush(self) -> None:
        """Flush pending SQL statements."""

        self.session.flush()

    def close(self) -> None:
        """Close the database session."""

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

        # Never suppress exceptions.
        return False
