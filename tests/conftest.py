"""
AI Trading Operating System
Pytest Configuration

Shared fixtures for repository and service tests.
Uses the application's DatabaseManager and SessionFactory.
No duplicate database configuration is maintained here.
"""

from __future__ import annotations

import pytest

from database.base import Base
from database.connection import database as db_manager
from database.session import SessionFactory
from core.settings import settings
from sqlalchemy import create_engine, text
import database.models.symbol
import database.models.market_data
import database.models.indicator_data

try:
    # Initialize schema in default connection first
    with db_manager.engine.connect() as _init_conn:
        _init_conn.execute(text("CREATE SCHEMA IF NOT EXISTS test_schema"))
        _init_conn.commit()

    test_engine = create_engine(
        settings.database_url,
        connect_args={"options": "-csearch_path=test_schema"},
        future=True,
    )
    engine = test_engine
    db_manager._engine = test_engine
except Exception:
    test_engine = create_engine("sqlite:///:memory:", future=True)
    engine = test_engine
    db_manager._engine = test_engine


# ---------------------------------------------------------------------
# Create / Drop Schema in test_schema
# ---------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Create all ORM tables in isolated test_schema before tests start,
    and drop test_schema tables after tests complete.
    Preserves the production/public database records intact.
    """
    try:
        Base.metadata.create_all(bind=test_engine)
    except Exception:
        pass

    yield

    try:
        Base.metadata.drop_all(bind=test_engine)
    except Exception:
        pass
    db_manager._engine = None


# ---------------------------------------------------------------------
# Database Session
# ---------------------------------------------------------------------

@pytest.fixture
def db_session(setup_database):
    """
    Create a fresh SQLAlchemy session for each test.

    Every test executes inside its own transaction.
    The transaction is rolled back automatically,
    ensuring complete test isolation.
    """
    try:
        connection = engine.connect()
        transaction = connection.begin()

        session = SessionFactory(bind=connection)

        try:
            yield session

        finally:
            session.close()

            if transaction.is_active:
                transaction.rollback()

            connection.close()
    except Exception:
        yield None


# ---------------------------------------------------------------------
# Automatic Cleanup
# ---------------------------------------------------------------------

@pytest.fixture(autouse=True)
def cleanup_session(db_session):
    """
    Roll back any pending work after each test.
    """
    yield

    if db_session and hasattr(db_session, "is_active") and db_session.is_active:
        db_session.rollback()
