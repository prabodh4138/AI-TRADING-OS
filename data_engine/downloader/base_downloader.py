"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    base_downloader.py

Purpose:
    Defines the abstract interface for all market
    data download providers.

Author:
    AI Trading OS

=========================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import Iterable


class BaseDownloader(ABC):
    """
    Enterprise downloader contract.

    Every market data provider must inherit this class.

    Example Providers
    -----------------
    - NSE
    - Yahoo Finance
    - Polygon
    - Alpha Vantage
    - Custom CSV
    """

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize provider session.

        Example:
            - Create HTTP session
            - Authenticate
            - Load cookies
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verify provider is reachable.

        Returns
        -------
        bool
            True if provider is available.
        """
        raise NotImplementedError

    @abstractmethod
    def download_by_date(
        self,
        trade_date: date,
        output_dir: Path,
    ) -> Path:
        """
        Download market data for one trading day.

        Returns
        -------
        Path
            Downloaded file.
        """
        raise NotImplementedError

    @abstractmethod
    def download_range(
        self,
        dates: Iterable[date],
        output_dir: Path,
    ) -> list[Path]:
        """
        Download multiple trading days.

        Returns
        -------
        list[Path]
        """
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """
        Close provider session.
        """
        raise NotImplementedError