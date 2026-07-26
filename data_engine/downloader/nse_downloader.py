"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    nse_downloader.py

Purpose:
    Enterprise NSE Bhavcopy Downloader

Responsibilities
----------------
1. Session Management
2. Health Check
3. Download Daily Bhavcopy
4. Download Historical Data
5. Statistics
6. Cleanup

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path
from typing import Iterable

import requests
from requests import Session

from .base_downloader import BaseDownloader
from ..exceptions import DownloadException


class NSEDownloader(BaseDownloader):
    """
    Enterprise NSE Downloader.

    Downloads NSE historical bhavcopy data.

    This class is responsible ONLY for downloading.

    Validation, staging and database loading are handled
    by separate enterprise modules.
    """

    def __init__(
        self,
        download_dir: Path,
        timeout: int = 30,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialize downloader.

        Parameters
        ----------
        download_dir
            Directory where downloaded CSV files
            will be stored.

        timeout
            HTTP timeout in seconds.

        logger
            Optional application logger.
        """

        self.download_dir = Path(download_dir)
        self.timeout = timeout

        self.logger = logger or logging.getLogger(__name__)

        self.session: Session | None = None

        self.home_url = "https://www.nseindia.com"

        self.base_url = (
            "https://www.nseindia.com/api/historical/cm/equity"
        )

        self.download_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.logger.info(
            "NSE Downloader initialized."
        )

    # --------------------------------------------------
    # Session Management
    # --------------------------------------------------

    def _build_headers(self) -> dict[str, str]:
        """
        Build default request headers.
        """

        return {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/138.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Referer": self.home_url,
        }

    def initialize(self) -> None:
        """
        Initialize HTTP session.

        Visiting the NSE home page creates
        the cookies required for subsequent
        API requests.
        """

        if self.session is not None:
            self.logger.debug(
                "Session already initialized."
            )
            return

        try:

            self.logger.info(
                "Creating NSE session..."
            )

            session = requests.Session()

            session.headers.update(
                self._build_headers()
            )

            response = session.get(
                self.home_url,
                timeout=self.timeout,
            )

            response.raise_for_status()

            self.session = session

            self.logger.info(
                "NSE session established successfully."
            )

        except Exception as ex:

            raise DownloadException(
                f"Unable to initialize NSE session: {ex}"
            ) from ex

    @property
    def is_initialized(self) -> bool:
        """
        Returns True when HTTP session exists.
        """

        return self.session is not None

    # --------------------------------------------------
    # Placeholder methods
    # These will be implemented in later sprints.
    # --------------------------------------------------

    def health_check(self) -> bool:
        raise NotImplementedError

    def download_by_date(
        self,
        trade_date: date,
        output_dir: Path,
    ) -> Path:
        raise NotImplementedError

    def download_range(
        self,
        dates: Iterable[date],
        output_dir: Path,
    ) -> list[Path]:
        raise NotImplementedError

    def close(self) -> None:
        if self.session is not None:
            self.session.close()
            self.session = None
            self.logger.info("Session closed.")