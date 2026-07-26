"""
==============================================================
AI Trading Operating System
Enterprise Synchronization Service
Sprint 9.2.6
==============================================================

Coordinates the complete synchronization workflow.

Workflow
--------
Download
    ↓
Verify
    ↓
Record History
    ↓
Import CSV
    ↓
Store Market Data

Author : AI Trading OS
"""

from __future__ import annotations

import logging

from dataclasses import dataclass
from datetime import date

from data_engine.downloader.download_manager import DownloadResult
from services.download_service import DownloadService
from services.import_service import ImportService


LOGGER = logging.getLogger(__name__)


# ==========================================================
# Synchronization Result
# ==========================================================

@dataclass(slots=True)
class SynchronizationResult:
    """
    Result of one synchronization cycle.
    """

    success: bool

    trading_date: date

    dataset: str

    download_result: DownloadResult | None

    records_imported: int

    error: str | None = None


# ==========================================================
# Synchronization Service
# ==========================================================

class SynchronizationService:

    def __init__(
        self,
        download_service: DownloadService | None = None,
        import_service: ImportService | None = None,
        logger: logging.Logger | None = None,
    ) -> None:

        self.download_service = (
            download_service
            or DownloadService()
        )

        self.import_service = (
            import_service
            or ImportService()
        )

        self.logger = logger or LOGGER

    # ------------------------------------------------------

    def synchronize(
        self,
        trading_date: date,
        dataset: str = "bhavcopy",
    ) -> SynchronizationResult:
        """
        Synchronize a single trading day.
        """

        self.logger.info(
            "Starting synchronization for %s (%s)",
            trading_date,
            dataset,
        )

        download_result = self.download_service.download(
            trade_date=trading_date,
            dataset=dataset,
        )

        if not download_result.success:

            self.logger.error(
                "Download failed: %s",
                download_result.error,
            )

            return SynchronizationResult(
                success=False,
                trading_date=trading_date,
                dataset=dataset,
                download_result=download_result,
                records_imported=0,
                error=download_result.error,
            )

        if download_result.file_path is None:

            return SynchronizationResult(
                success=False,
                trading_date=trading_date,
                dataset=dataset,
                download_result=download_result,
                records_imported=0,
                error="Downloaded file not found.",
            )

        try:

            records = self.import_service.import_file(
                str(download_result.file_path)
            )

            self.logger.info(
                "Synchronization completed successfully."
            )

            return SynchronizationResult(
                success=True,
                trading_date=trading_date,
                dataset=dataset,
                download_result=download_result,
                records_imported=records,
                error=None,
            )

        except Exception as ex:

            self.logger.exception(
                "Import failed."
            )

            return SynchronizationResult(
                success=False,
                trading_date=trading_date,
                dataset=dataset,
                download_result=download_result,
                records_imported=0,
                error=str(ex),
            )

    # ------------------------------------------------------

    def synchronize_today(
        self,
        dataset: str = "bhavcopy",
    ) -> SynchronizationResult:
        """
        Synchronize today's market data.
        """

        return self.synchronize(
            trading_date=date.today(),
            dataset=dataset,
        )

    # ------------------------------------------------------

    def synchronize_range(
        self,
        start_date: date,
        end_date: date,
        dataset: str = "bhavcopy",
    ) -> list[SynchronizationResult]:
        """
        Synchronize a date range.
        """

        results: list[SynchronizationResult] = []

        current = start_date

        while current <= end_date:

            results.append(
                self.synchronize(
                    trading_date=current,
                    dataset=dataset,
                )
            )

            current = current.fromordinal(
                current.toordinal() + 1
            )

        return results