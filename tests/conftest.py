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
from database.connection import database
from database.session import SessionFactory

# ---------------------------------------------------------------------
# Shared Application Engine
# ---------------------------------------------------------------------

engine = database.engine


# ---------------------------------------------------------------------
# Create / Drop Schema
# ---------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Create all ORM tables before the test session starts
    and drop them after the session completes.
    """

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)


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


# ---------------------------------------------------------------------
# Automatic Cleanup
# ---------------------------------------------------------------------

@pytest.fixture(autouse=True)
def cleanup_session(db_session):
    """
    Roll back any pending work after each test.
    """

    yield

    if db_session.is_active:
        db_session.rollback()