"""
AI Trading Operating System
Generic Repository
"""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select, func
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Generic repository for all ORM entities.
    """

    model = None

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, entity_id):
        return self.session.get(self.model, entity_id)

    def get_all(self):
        return (
            self.session.execute(
                select(self.model)
            )
            .scalars()
            .all()
        )

    def add(self, entity: T):
        self.session.add(entity)
        return entity

    def delete(self, entity: T):
        self.session.delete(entity)

    def flush(self):
        self.session.flush()

    def count(self) -> int:
        return self.session.scalar(
        select(func.count()).select_from(self.model)
    )

    def exists(self, entity_id):
        return self.get_by_id(entity_id) is not None