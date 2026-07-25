"""
AI Trading Operating System
Enterprise Generic Repository
"""

from __future__ import annotations

from typing import Generic, Iterable, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Enterprise Generic Repository.

    All repositories should inherit from this class.

    Provides:
        - add()
        - add_many()
        - get_by_id()
        - get_all()
        - delete()
        - delete_many()
        - count()
        - exists()
        - refresh()
        - flush()
    """

    model = None

    def __init__(self, session: Session):
        if self.model is None:
            raise ValueError(
                f"{self.__class__.__name__} must define 'model'."
            )

        self.session = session

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def add(self, entity: T) -> T:
        """
        Add a single entity.
        """
        self.session.add(entity)
        return entity

    def add_many(self, entities: Iterable[T]) -> list[T]:
        """
        Add multiple entities.
        """
        entities = list(entities)

        if entities:
            self.session.add_all(entities)

        return entities

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, entity_id):
        """
        Get entity by primary key.
        """
        return self.session.get(self.model, entity_id)

    def get_all(self) -> list[T]:
        """
        Return all records.
        """
        stmt = (
            select(self.model)
            .order_by(*self.model.__table__.primary_key.columns)
        )

        return self.session.scalars(stmt).all()

    def exists(self, entity_id) -> bool:
        """
        Check if entity exists.
        """
        return self.get_by_id(entity_id) is not None

    def count(self) -> int:
        """
        Return total row count.
        """
        stmt = (
            select(func.count())
            .select_from(self.model)
        )

        return self.session.scalar(stmt) or 0

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, entity: T) -> None:
        """
        Delete a single entity.
        """
        self.session.delete(entity)

    def delete_many(self, entities: Iterable[T]) -> None:
        """
        Delete multiple entities.
        """
        for entity in entities:
            self.session.delete(entity)

    # ------------------------------------------------------------------
    # Session Operations
    # ------------------------------------------------------------------

    def refresh(self, entity: T) -> T:
        """
        Refresh entity from database.
        """
        self.session.refresh(entity)
        return entity

    def flush(self) -> None:
        """
        Flush current transaction.
        """
        self.session.flush()