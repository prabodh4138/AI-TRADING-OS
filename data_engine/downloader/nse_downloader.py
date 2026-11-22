"""
AI Trading OS
Enterprise Data Engine

Module:
    nse_downloader.py

Purpose
-------
Enterprise NSE Bhavcopy Downloader.

Downloads the NSE Full Bhavcopy and Security Deliverable
CSV for a specified trading date.
"""

from __future__ import annotations

import logging
import time
from datetime import date

import requests
from requests import Response, Session
from requests.exceptions import ConnectionError, HTTPError, Timeout

from data_engine.downloader.base_downloader import BaseDownloader
from data_engine.exceptions import DownloadException


class NSEDownloader(BaseDownloader):
    """
    Enterprise NSE Downloader.

    Responsible only for communicating with NSE.
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
        self.logger = logger or logging.getLogger(__name__)
        self.session: Session | None = None

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
    # Headers
    # ==================================================

    def _build_headers(self) -> dict[str, str]:
        """
        Build headers used by the working NSE request.
        """

        return {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/153.0.0.0 "
                "Safari/537.36"
            ),
            "Accept": "text/csv,*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": (
                "https://www.nseindia.com/all-reports"
            ),
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
        }

    # ==================================================
    # Date
    # ==================================================

    def _format_trade_date(
        self,
        trade_date: date,
    ) -> str:
        """
        Convert trading date to NSE format.

        Example:
            25-Sep-2026
        """

        return trade_date.strftime("%d-%b-%Y")

    # ==================================================
    # Request Parameters
    # ==================================================

    def _build_request_params(
        self,
        trade_date: date,
    ) -> dict[str, str]:
        """
        Build parameters for NSE Full Bhavcopy report.
        """

        return {
            "archives": (
                '[{"name":"Full Bhavcopy and Security '
                'Deliverable data",'
                '"type":"daily-reports",'
                '"category":"capital-market",'
                '"section":"equities"}]'
            ),
            "date": self._format_trade_date(
                trade_date
            ),
            "type": "equities",
            "mode": "single",
        }

    # ==================================================
    # Session Management
    # ==================================================

    def initialize(self) -> None:
        """
        Initialize NSE session.

        The reports page is requested first to establish
        the session/cookies required by the reports API.
        """

        if self.session is not None:
            self.logger.debug(
                "NSE session already initialized."
            )
            return

        self.logger.info(
            "Creating NSE session..."
        )

        session = requests.Session()

        session.headers.update(
            self._build_headers()
        )

        try:
            try:
                session.get(
                    self.HOME_URL,
                    headers=self._build_headers(),
                    timeout=self.timeout,
                )
            except Exception:
                pass

            response = session.get(
                f"{self.HOME_URL}/all-reports",
                params={"type": "equities"},
                headers=self._build_headers(),
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
        Verify that the NSE session is usable.
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
        Download NSE Full Bhavcopy.

        Returns
        -------
        Response
            Raw CSV HTTP response.

        Raises
        ------
        DownloadException
        """

        if not isinstance(
            trade_date,
            date,
        ):
            raise DownloadException(
                "trade_date must be a datetime.date instance."
            )

        if self.session is None:
            self.initialize()

        last_exception: Exception | None = None

        for attempt in range(
            1,
            self.MAX_RETRIES + 1,
        ):

            start_time = time.perf_counter()

            try:

                self.logger.info(
                    "Downloading NSE Bhavcopy for %s "
                    "(Attempt %d/%d)",
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

                if not response.content:
                    raise DownloadException(
                        "NSE returned an empty response."
                    )

                content_type = (
                    response.headers.get(
                        "Content-Type",
                        "",
                    ).lower()
                )

                if "text/html" in content_type:
                    raise DownloadException(
                        "NSE returned HTML instead of "
                        "the expected CSV report."
                    )

                # Confirm the expected NSE CSV signature.
                first_line = (
                    response.content
                    .splitlines()[0]
                    .decode(
                        "utf-8",
                        errors="replace",
                    )
                    .strip()
                )

                if not first_line.startswith(
                    "SYMBOL"
                ):
                    raise DownloadException(
                        "NSE response does not contain "
                        "the expected Bhavcopy CSV header."
                    )

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
                    "NSE Bhavcopy download completed "
                    "successfully in %.2f seconds "
                    "(%d bytes).",
                    elapsed,
                    len(response.content),
                )

                return response

            except (
                Timeout,
                ConnectionError,
            ) as ex:

                last_exception = ex
                self.failure_count += 1
                self.last_error = str(ex)

                self.logger.warning(
                    "Network error on attempt %d/%d: %s",
                    attempt,
                    self.MAX_RETRIES,
                    ex,
                )

                if attempt < self.MAX_RETRIES:

                    self.close()

                    time.sleep(
                        self.RETRY_DELAY
                    )

                    self.initialize()

            except HTTPError as ex:

                last_exception = ex
                self.failure_count += 1
                self.last_error = str(ex)

                status_code = getattr(
                    ex.response,
                    "status_code",
                    None,
                )

                self.logger.error(
                    "NSE HTTP error "
                    "(status=%s): %s",
                    status_code,
                    ex,
                )

                break

            except DownloadException as ex:

                last_exception = ex
                self.failure_count += 1
                self.last_error = str(ex)

                self.logger.error(
                    "NSE download validation error: %s",
                    ex,
                )

                break

            except Exception as ex:

                last_exception = ex
                self.failure_count += 1
                self.last_error = str(ex)

                self.logger.exception(
                    "Unexpected NSE download error."
                )

                break

        raise DownloadException(
            f"Download failed for "
            f"{trade_date} "
            f"after "
            f"{self.MAX_RETRIES} attempts."
        ) from last_exception

    # ==================================================
    # Convenience
    # ==================================================

    def download_today(self) -> Response:
        """
        Download today's NSE Bhavcopy.
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
        Reset runtime download statistics.
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
        Return whether the NSE session exists.
        """

        return self.session is not None

    # ==================================================
    # Cleanup
    # ==================================================

    def close(self) -> None:
        """
        Close the NSE HTTP session.
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
    # Context Manager
    # ==================================================

    def __enter__(self) -> "NSEDownloader":
        """
        Context manager entry.
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
