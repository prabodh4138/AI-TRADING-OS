"""Lazy SQLAlchemy session factory; importing AI-TOS never requires a live DB."""
from __future__ import annotations
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session, sessionmaker
from database.connection import database
from core.logger import get_logger
logger=get_logger()
SessionFactory=sessionmaker(autoflush=False, autocommit=False, expire_on_commit=False)

def new_session() -> Session:
    return SessionFactory(bind=database.engine)

@contextmanager
def get_session() -> Generator[Session,None,None]:
    session=new_session()
    try:
        yield session; session.commit()
    except Exception:
        session.rollback(); logger.exception("Database transaction rolled back."); raise
    finally: session.close()
