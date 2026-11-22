"""Abstract database loader primitives."""
from __future__ import annotations
import logging
from abc import ABC, abstractmethod
import pandas as pd
from sqlalchemy.orm import Session

class BaseLoader(ABC):
    DEFAULT_BATCH_SIZE = 1000
    def __init__(self, session: Session, logger: logging.Logger | None = None, batch_size: int = DEFAULT_BATCH_SIZE) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        self.session, self.batch_size = session, batch_size
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    @abstractmethod
    def load(self, dataframe: pd.DataFrame) -> int: ...
    @abstractmethod
    def validate(self, dataframe: pd.DataFrame) -> None: ...
    def get_batches(self, dataframe: pd.DataFrame) -> list[pd.DataFrame]:
        return [dataframe.iloc[i:i+self.batch_size].copy() for i in range(0, len(dataframe), self.batch_size)]
