"""
AI Trading Operating System
Database Connection Manager

Responsibilities:
- Create SQLAlchemy Engine
- Manage Connection Pool
- Test PostgreSQL Connectivity
- Provide Engine Instance
- Graceful Shutdown
"""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import SQLAlchemyError

from core.logger import get_logger
from core.settings import settings
from core.exceptions import DatabaseConnectionError


class DatabaseManager:
    """
    Singleton-style Database Manager.

    Responsible only for creating and managing the SQLAlchemy Engine.
    """

    def __init__(self) -> None:
        self.logger = get_logger()

        db_config = settings.database.get("database", {})
        pool_config = settings.database.get("pool", {})

        required_keys = [
            "host",
            "port",
            "name",
            "user",
            "password",
        ]

        missing = [key for key in required_keys if not db_config.get(key)]

        if missing:
            raise DatabaseConnectionError(
                f"Missing database configuration: {', '.join(missing)}"
            )

        # Build a safe SQLAlchemy URL.
        # Handles passwords containing @, :, #, %, /, etc.
        self._url = URL.create(
            drivername="postgresql+psycopg2",
            username=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["name"],
        )

        self.logger.info(
            "Initializing PostgreSQL connection to database '{}'.",
            db_config["name"],
        )

        self._engine: Engine = create_engine(
            self._url,
            pool_size=pool_config.get("size", 10),
            max_overflow=pool_config.get("overflow", 20),
            pool_recycle=pool_config.get("recycle", 3600),
            pool_pre_ping=True,
            future=True,
            echo=settings.database.get("echo_sql", False),
        )

    @property
    def engine(self) -> Engine:
        """
        Return SQLAlchemy Engine.
        """
        return self._engine

    def test_connection(self) -> bool:
        """
        Verify PostgreSQL connectivity.
        """

        try:
            with self._engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            self.logger.info("PostgreSQL connection established successfully.")
            return True

        except SQLAlchemyError as exc:
            self.logger.exception("Database connection failed.")
            self.logger.exception(exc)
            return False

    def shutdown(self) -> None:
        """
        Close all pooled connections.
        """

        self.logger.info("Closing database connection pool...")
        self._engine.dispose()
        self.logger.info("Database connection pool closed.")


# ---------------------------------------------------------------------
# Global Database Manager Instance
# ---------------------------------------------------------------------

database = DatabaseManager()