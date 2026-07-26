"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    base_loader.py

Purpose
-------
Abstract base class for all database loaders.

Responsibilities
----------------
1. Define loader interface
2. Hold SQLAlchemy session
3. Configure batch loading
4. Provide enterprise logging

This class MUST NOT

- Load specific business entities
- Contain SQL statements
- Know table schemas
=========================================================
"""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod

import pandas as pd
from sqlalchemy.orm import Session


class BaseLoader(ABC):
    """
    Enterprise abstract database loader.
    """

    DEFAULT_BATCH_SIZE: int = 1000

    def __init__(
        self,
        session: Session,
        logger: logging.Logger | None = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """
        Initialize database loader.

        Parameters
        ----------
        session : Session
            SQLAlchemy database session.

        logger : logging.Logger | None
            Optional logger.

        batch_size : int
            Number of rows per database batch.
        """
        self.session = session
        self.batch_size = batch_size
        self.logger = logger or logging.getLogger(
            self.__class__.__name__
        )

        self.logger.info(
            "%s initialized.",
            self.__class__.__name__,
        )

    @abstractmethod
    def load(
        self,
        dataframe: pd.DataFrame,
    ) -> int:
        """
        Load dataframe into database.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Transformed dataframe.

        Returns
        -------
        int
            Number of inserted records.
        """
        raise NotImplementedError

    @abstractmethod
    def validate(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Validate dataframe before loading.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Input dataframe.

        Raises
        ------
        ValueError
            If dataframe cannot be loaded.
        """
        raise NotImplementedError

    @property
    def name(
        self,
    ) -> str:
        """
        Return loader name.
        """
        return self.__class__.__name__
    def begin_transaction(
        self,
    ) -> None:
        """
        Begin a database transaction.

        Notes
        -----
        SQLAlchemy automatically starts a transaction
        when required. This method exists to provide
        consistent enterprise logging.
        """
        self.logger.info(
            "Starting database transaction."
        )

    def flush(
        self,
    ) -> None:
        """
        Flush pending changes to the database
        without committing.
        """
        self.logger.debug(
            "Flushing database session."
        )

        self.session.flush()

    def refresh(
        self,
        entity: object,
    ) -> None:
        """
        Refresh an ORM entity from the database.

        Parameters
        ----------
        entity : object
            ORM entity instance.
        """
        self.logger.debug(
            "Refreshing ORM entity."
        )

        self.session.refresh(entity)

    def commit(
        self,
    ) -> None:
        """
        Commit the active transaction.
        """
        self.logger.info(
            "Committing database transaction."
        )

        self.session.commit()

    def rollback(
        self,
    ) -> None:
        """
        Roll back the active transaction.
        """
        self.logger.warning(
            "Rolling back database transaction."
        )

        self.session.rollback()

    def close(
        self,
    ) -> None:
        """
        Close the SQLAlchemy session.
        """
        self.logger.info(
            "Closing database session."
        )

        self.session.close()

    def transaction(
        self,
    ):
        """
        Return SQLAlchemy transaction context.

        Returns
        -------
        SessionTransaction
            SQLAlchemy transaction context manager.
        """
        return self.session.begin()
    def get_batches(
        self,
        dataframe: pd.DataFrame,
    ) -> list[pd.DataFrame]:
        """
        Split a dataframe into configurable batches.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Input dataframe.

        Returns
        -------
        list[pd.DataFrame]
            List of dataframe batches.
        """
        self.logger.info(
            "Creating dataframe batches (batch_size=%d).",
            self.batch_size,
        )

        batches: list[pd.DataFrame] = []

        total_rows = len(dataframe)

        for start in range(
            0,
            total_rows,
            self.batch_size,
        ):
            end = start + self.batch_size

            batches.append(
                dataframe.iloc[start:end].copy()
            )

        self.logger.info(
            "Created %d batch(es).",
            len(batches),
        )

        return batches

    def get_total_batches(
        self,
        dataframe: pd.DataFrame,
    ) -> int:
        """
        Calculate the number of batches.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Input dataframe.

        Returns
        -------
        int
            Total number of batches.
        """
        total_rows = len(dataframe)

        if total_rows == 0:
            return 0

        return (
            total_rows
            + self.batch_size
            - 1
        ) // self.batch_size

    def create_load_statistics(
        self,
    ) -> dict[str, int]:
        """
        Create an empty loading statistics dictionary.

        Returns
        -------
        dict[str, int]
            Initial loading statistics.
        """
        return {
            "total_rows": 0,
            "processed_rows": 0,
            "successful_rows": 0,
            "failed_rows": 0,
            "total_batches": 0,
            "processed_batches": 0,
        }

    def update_statistics(
        self,
        statistics: dict[str, int],
        *,
        processed_rows: int = 0,
        successful_rows: int = 0,
        failed_rows: int = 0,
        processed_batches: int = 0,
    ) -> None:
        """
        Update loading statistics.

        Parameters
        ----------
        statistics : dict[str, int]
            Statistics dictionary.

        processed_rows : int
            Number of processed rows.

        successful_rows : int
            Number of successful rows.

        failed_rows : int
            Number of failed rows.

        processed_batches : int
            Number of processed batches.
        """
        statistics["processed_rows"] += processed_rows
        statistics["successful_rows"] += successful_rows
        statistics["failed_rows"] += failed_rows
        statistics["processed_batches"] += (
            processed_batches
        )

    def log_statistics(
        self,
        statistics: dict[str, int],
    ) -> None:
        """
        Log loading statistics.

        Parameters
        ----------
        statistics : dict[str, int]
            Loading statistics.
        """
        self.logger.info(
            (
                "Load Summary | "
                "Rows=%d | "
                "Processed=%d | "
                "Success=%d | "
                "Failed=%d | "
                "Batches=%d/%d"
            ),
            statistics["total_rows"],
            statistics["processed_rows"],
            statistics["successful_rows"],
            statistics["failed_rows"],
            statistics["processed_batches"],
            statistics["total_batches"],
        )
"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    market_data_loader.py

Purpose
-------
Concrete database loader for market data.
=========================================================
"""

from __future__ import annotations

import logging

import pandas as pd

from data_engine.database.base_loader import BaseLoader
from database.models.market_data import MarketData


class MarketDataLoader(BaseLoader):
    """
    Enterprise loader for MarketData.
    """

    REQUIRED_COLUMNS: tuple[str, ...] = (
        "symbol",
        "series",
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "last",
        "prevclose",
        "tottrdqty",
        "tottrdval",
    )

    def __init__(
        self,
        session,
        logger: logging.Logger | None = None,
        batch_size: int = BaseLoader.DEFAULT_BATCH_SIZE,
    ) -> None:
        """
        Initialize MarketDataLoader.
        """
        super().__init__(
            session=session,
            logger=logger,
            batch_size=batch_size,
        )

    def validate(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Validate transformed dataframe.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Transformed dataframe.

        Raises
        ------
        ValueError
            If required columns are missing.
        """
        self.logger.info(
            "Validating market data."
        )

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                f"{missing_columns}"
            )

    def dataframe_to_entities(
        self,
        dataframe: pd.DataFrame,
    ) -> list[MarketData]:
        """
        Convert dataframe into ORM entities.

        Parameters
        ----------
        dataframe : pd.DataFrame

        Returns
        -------
        list[MarketData]
        """
        self.logger.info(
            "Creating ORM entities."
        )

        entities: list[MarketData] = []

        for row in dataframe.itertuples(index=False):

            entity = MarketData(
                symbol=row.symbol,
                series=row.series,
                timestamp=row.timestamp,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
                last=row.last,
                prevclose=row.prevclose,
                tottrdqty=row.tottrdqty,
                tottrdval=row.tottrdval,
            )

            entities.append(entity)

        self.logger.info(
            "Created %d ORM entities.",
            len(entities),
        )

        return entities

    def load(
        self,
        dataframe: pd.DataFrame,
    ) -> int:
        """
        Load transformed market data into PostgreSQL.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Transformed dataframe.

        Returns
        -------
        int
            Number of successfully inserted records.
        """
        start_time = time.perf_counter()

        self.logger.info(
            "Starting market data loading."
        )

        self.validate(dataframe)

        statistics = (
            self.create_load_statistics()
        )

        statistics["total_rows"] = len(
            dataframe
        )

        statistics["total_batches"] = (
            self.get_total_batches(
                dataframe
            )
        )

        self.begin_transaction()

        try:

            batches = self.get_batches(
                dataframe
            )

            for batch_number, batch_df in enumerate(
                batches,
                start=1,
            ):

                batch_start = time.perf_counter()

                self.logger.info(
                    "Processing batch %d/%d (%d rows).",
                    batch_number,
                    statistics["total_batches"],
                    len(batch_df),
                )

                entities = (
                    self.dataframe_to_entities(
                        batch_df
                    )
                )

                self.session.add_all(
                    entities
                )

                self.flush()

                batch_duration = (
                    time.perf_counter()
                    - batch_start
                )

                self.logger.info(
                    (
                        "Batch %d completed "
                        "in %.3f seconds."
                    ),
                    batch_number,
                    batch_duration,
                )

                self.update_statistics(
                    statistics,
                    processed_rows=len(batch_df),
                    successful_rows=len(batch_df),
                    processed_batches=1,
                )

            self.commit()

            self.logger.info(
                "Database transaction committed."
            )

        except Exception as exc:

            self.rollback()

            statistics["failed_rows"] = (
                statistics["total_rows"]
                - statistics["successful_rows"]
            )

            self.logger.exception(
                "Market data loading failed: %s",
                exc,
            )

            raise

        finally:

            elapsed = (
                time.perf_counter()
                - start_time
            )

            throughput = (
                statistics["successful_rows"]
                / elapsed
                if elapsed > 0
                else 0.0
            )

            success_rate = (
                (
                    statistics["successful_rows"]
                    / statistics["total_rows"]
                ) * 100
                if statistics["total_rows"] > 0
                else 0.0
            )

            failure_rate = (
                (
                    statistics["failed_rows"]
                    / statistics["total_rows"]
                ) * 100
                if statistics["total_rows"] > 0
                else 0.0
            )

            self.log_statistics(
                statistics
            )

            self.logger.info(
                (
                    "Performance Summary | "
                    "Duration=%.3f sec | "
                    "Throughput=%.2f rows/sec | "
                    "Success Rate=%.2f%% | "
                    "Failure Rate=%.2f%%"
                ),
                elapsed,
                throughput,
                success_rate,
                failure_rate,
            )

            self.close()

        return statistics[
            "successful_rows"
        ]        