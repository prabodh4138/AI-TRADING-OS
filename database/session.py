"""
AI Trading Operating System
Database Session Manager
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from core.logger import get_logger
from database.connection import database


logger = get_logger()


# ---------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------

SessionFactory = sessionmaker(
    bind=database.engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------
# Context Manager
# ---------------------------------------------------------------------

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Create a transactional database session.

    Usage:
        with get_session() as session:
            ...
    """
    session = SessionFactory()

    try:
        yield session
        session.commit()

    except Exception:
        session.rollback()
        logger.exception("Database transaction rolled back.")
        raise

    finally:
        session.close()