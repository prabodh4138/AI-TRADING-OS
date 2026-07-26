"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    nse_downloader.py

Purpose
-------
Enterprise NSE Bhavcopy Downloader

Responsibilities
----------------
1. Session Management
2. Health Check
3. Download Daily Bhavcopy
4. Return Raw HTTP Response
5. Resource Cleanup

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

import logging

from datetime import date
from datetime import datetime

import requests

from requests import Response
from requests import Session

from data_engine.downloader.base_downloader import BaseDownloader
from data_engine.exceptions import DownloadException
import time

from requests.exceptions import (
    ConnectionError,
    HTTPError,
    Timeout,
)


class NSEDownloader(BaseDownloader):
    """
    Enterprise NSE Downloader.

    This class is responsible ONLY for
    communicating with NSE.

    It DOES NOT:

    - Save files
    - Validate responses
    - Load database
    """

    HOME_URL = "https://www.nseindia.com"

    REPORT_URL = (
        "https://www.nseindia.com/api/reports"
    )

    DEFAULT_TIMEOUT = 60
    MAX_RETRIES = 3

    RETRY_DELAY = 2

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        logger: logging.Logger | None = None,
    ) -> None:

        self.timeout = timeout

        self.logger = (
            logger
            or logging.getLogger(__name__)
        )

        self.session: Session | None = None
                # ==============================================
        # Download Statistics
        # ==============================================

        self.download_count = 0

        self.success_count = 0

        self.failure_count = 0

        self.total_download_time = 0.0

        self.last_download_date: date | None = None

        self.last_error: str | None = None

        self.logger.info(
            "NSEDownloader initialized."
        )
            # ==================================================
    # Private Helpers
    # ==================================================

    def _build_headers(self) -> dict[str, str]:
        """
        Build HTTP headers required by NSE.

        These headers are based on the existing
        working download implementation.
        """

        return {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64)"
            ),
            "Accept": "text/csv,*/*",
        }

    def _format_trade_date(
        self,
        trade_date: date,
    ) -> str:
        """
        Convert trade date to NSE format.

        Example
        -------
        25-Jul-2026
        """

        return trade_date.strftime("%d-%b-%Y")

    def _build_request_params(
        self,
        trade_date: date,
    ) -> dict[str, str]:
        """
        Build request parameters for NSE
        Bhavcopy download.
        """

        return {
            "archives":
                '[{"name":"Full Bhavcopy and Security Deliverable data",'
                '"type":"daily-reports",'
                '"category":"capital-market",'
                '"section":"equities"}]',
            "date": self._format_trade_date(trade_date),
            "type": "equities",
            "mode": "single",
        }
    # ==================================================
    # Session Management
    # ==================================================

    def initialize(self) -> None:
        """
        Initialize the NSE HTTP session.

        The NSE API requires a valid session with
        cookies obtained from the home page.
        """

        if self.session is not None:
            self.logger.debug(
                "NSE session already initialized."
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
                self.HOME_URL,
                timeout=self.timeout,
            )

            response.raise_for_status()

            self.session = session

            self.logger.info(
                "NSE session established successfully."
            )

        except Exception as ex:

            self.logger.exception(
                "Failed to initialize NSE session."
            )

            raise DownloadException(
                f"Unable to initialize NSE session: {ex}"
            ) from ex

    # ==================================================
    # Health Check
    # ==================================================

    def health_check(self) -> bool:
        """
        Verify that the downloader has a valid
        and usable HTTP session.

        Returns
        -------
        bool
            True if the session is available.
        """

        try:

            if self.session is None:
                self.initialize()

            return self.session is not None

        except Exception:

            self.logger.exception(
                "NSE health check failed."
            )

            return False
    # ==================================================
    # Download
    # ==================================================

    def download(
        self,
        trade_date: date,
    ) -> Response:
        """
        Download NSE Bhavcopy.

        Returns
        -------
        Response
            Raw HTTP response.

        Raises
        ------
        DownloadException
        """

        if self.session is None:
            self.initialize()

        last_exception = None

        for attempt in range(
            1,
            self.MAX_RETRIES + 1,
        ):

            try:

                start_time = time.perf_counter()

                self.logger.info(
                    "Downloading %s (Attempt %d/%d)",
                    trade_date,
                    attempt,
                    self.MAX_RETRIES,
                )

                response = self.session.get(
                    self.REPORT_URL,
                    params=self._build_request_params(
                        trade_date
                    ),
                    headers=self._build_headers(),
                    timeout=self.timeout,
                )

                response.raise_for_status()

                elapsed = (
                    time.perf_counter()
                    - start_time
                )

                self.download_count += 1

                self.success_count += 1

                self.total_download_time += elapsed

                self.last_download_date = trade_date

                self.last_error = None

                self.logger.info(
                    "Download completed in %.2f seconds",
                    elapsed,
                )

                return response

            except (
                Timeout,
                ConnectionError,
            ) as ex:

                last_exception = ex

                self.logger.warning(
                    "Network error on attempt %d/%d : %s",
                    attempt,
                    self.MAX_RETRIES,
                    ex,
                )

                self.close()

                self.initialize()

                time.sleep(
                    self.RETRY_DELAY
                )

            except HTTPError as ex:

                last_exception = ex

                self.logger.error(
                    "HTTP Error : %s",
                    ex,
                )

                break

            except Exception as ex:

                last_exception = ex

                self.logger.exception(
                    "Unexpected download error."
                )

                break

        raise DownloadException(
            f"Download failed for "
            f"{trade_date} "
            f"after "
            f"{self.MAX_RETRIES} attempts."
        ) from last_exception

    # ==================================================
    # Convenience Method
    # ==================================================

    def download_today(
        self,
    ) -> Response:
        """
        Download today's Bhavcopy.

        Returns
        -------
        Response
            Raw HTTP response.
        """

        return self.download(
            date.today()
        )
            # ==================================================
    # Statistics
    # ==================================================

    def statistics(self) -> dict[str, object]:
        """
        Return runtime download statistics.
        """

        average_time = 0.0

        if self.success_count:

            average_time = (
                self.total_download_time
                / self.success_count
            )

        return {

            "downloads": self.download_count,

            "successful": self.success_count,

            "failed": self.failure_count,

            "average_time": round(
                average_time,
                3,
            ),

            "last_download": self.last_download_date,

            "last_error": self.last_error,
        }
        def reset_statistics(self) -> None:
            """
             Reset runtime statistics.
            """

        self.download_count = 0

        self.success_count = 0

        self.failure_count = 0

        self.total_download_time = 0.0

        self.last_download_date = None

        self.last_error = None
    # ==================================================
    # Properties
    # ==================================================

    @property
    def is_initialized(self) -> bool:
        """
        Check whether the HTTP session has been initialized.

        Returns
        -------
        bool
            True if a valid session exists.
        """

        return self.session is not None

    # ==================================================
    # Cleanup
    # ==================================================

    def close(self) -> None:
        """
        Close the HTTP session and release resources.
        """

        if self.session is not None:

            self.logger.info(
                "Closing NSE session."
            )

            self.session.close()

            self.session = None

            self.logger.info(
                "NSE session closed."
            )

    # ==================================================
    # Context Manager Support
    # ==================================================

    def __enter__(self) -> "NSEDownloader":
        """
        Context manager entry.

        Example
        -------
        with NSEDownloader() as downloader:
            response = downloader.download(date.today())
        """

        self.initialize()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        """
        Context manager exit.
        """

        self.close()