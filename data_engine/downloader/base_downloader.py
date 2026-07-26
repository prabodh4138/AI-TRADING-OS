"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    base_downloader.py

Purpose
-------
Defines the contract for all download providers.

Every provider (NSE, Yahoo, Polygon, etc.)
must implement this interface.

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from datetime import date

from requests import Response


class BaseDownloader(ABC):
    """
    Base class for all download providers.

    Responsibilities
    ----------------
    1. Create session
    2. Verify connectivity
    3. Download data
    4. Close resources

    This class MUST NOT know anything about:

    - File saving
    - Validation
    - Database
    """

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize provider session.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verify provider availability.
        """
        raise NotImplementedError

    @abstractmethod
    def download(
        self,
        trade_date: date,
    ) -> Response:
        """
        Download market data for a single trading day.

        Parameters
        ----------
        trade_date
            Trading date.

        Returns
        -------
        Response
            Raw HTTP response.

        Notes
        -----
        This method MUST NOT:

        - Save files
        - Validate response
        - Load database
        """

        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        Release provider resources.
        """
        raise NotImplementedError