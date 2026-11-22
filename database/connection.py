"""SQLAlchemy engine and PostgreSQL connectivity."""
from __future__ import annotations
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from core.logger import get_logger
from core.settings import settings

class DatabaseManager:
    def __init__(self) -> None:
        self.logger = get_logger()
        self._engine: Engine | None = None

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = create_engine(
                settings.database_url,
                pool_size=int(settings.database.get("pool", {}).get("size", 10)),
                max_overflow=int(settings.database.get("pool", {}).get("overflow", 20)),
                pool_recycle=int(settings.database.get("pool", {}).get("recycle", 3600)),
                pool_pre_ping=True,
                echo=bool(settings.database.get("echo_sql", False)),
                future=True,
            )
        return self._engine

    def test_connection(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.logger.info("PostgreSQL connection established successfully.")
            return True
        except SQLAlchemyError:
            self.logger.exception("PostgreSQL connection failed.")
            return False

    def shutdown(self) -> None:
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None

database = DatabaseManager()
