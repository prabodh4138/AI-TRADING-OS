"""
==============================================================
AI Trading Operating System
Enterprise Download Service
Sprint 9.2.5
==============================================================

Business layer for market data downloads.

Responsibilities
----------------
- Prevent duplicate downloads
- Coordinate DownloadManager
- Persist download history
- Expose business operations

Author : AI Trading OS
"""

from __future__ import annotations

import logging

from datetime import date
from enum import Enum
from pathlib import Path

from data_engine.downloader.download_manager import (
    DownloadManager,
    DownloadResult,
)
from data_engine.downloader.downloader_config import get_dataset
from database.models.download_history import DownloadHistory
from database.unit_of_work import UnitOfWork


LOGGER = logging.getLogger(__name__)


class DownloadStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class DownloadService:

    def __init__(
        self,
        download_manager: DownloadManager | None = None,
        unit_of_work: UnitOfWork | None = None,
        logger: logging.Logger | None = None,
    ) -> None:

        self.download_manager = (
            download_manager
            or DownloadManager()
        )

        self.unit_of_work = (
            unit_of_work
            or UnitOfWork()
        )

        self.logger = logger or LOGGER

    # ---------------------------------------------------------

    def download(
        self,
        trade_date: date,
        dataset: str = "bhavcopy",
    ) -> DownloadResult:

        config = get_dataset(dataset)

        with self.unit_of_work as uow:

            existing = (
                uow.download_history.get_by_date(
                    provider=config.provider,
                    dataset=config.dataset,
                    trading_date=trade_date,
                )
            )

            # -------------------------------------------------
            # Already downloaded
            # -------------------------------------------------

            if existing:

                self.logger.info(
                    "Download already exists for %s (%s)",
                    trade_date,
                    dataset,
                )

                return DownloadResult(
                    success=True,
                    trade_date=trade_date,
                    dataset=dataset,
                    file_path=(
                        Path(existing.file_path)
                        if existing.file_path
                        else None
                    ),
                    checksum=existing.checksum,
                    file_size=existing.file_size,
                    row_count=0,
                    error=None,
                )

            # -------------------------------------------------
            # Fresh download
            # -------------------------------------------------

            result = self.download_manager.download(
                trade_date=trade_date,
                dataset=dataset,
            )

            history = DownloadHistory(
                provider=config.provider,
                dataset=config.dataset,
                trading_date=trade_date,
                filename=(
                    result.file_path.name
                    if result.file_path
                    else ""
                ),
                file_path=(
                    str(result.file_path)
                    if result.file_path
                    else ""
                ),
                checksum=result.checksum,
                file_size=result.file_size,
                status=(
                    DownloadStatus.SUCCESS.value
                    if result.success
                    else DownloadStatus.FAILED.value
                ),
            )

            uow.download_history.add(history)

            return result

    # ---------------------------------------------------------

    def download_today(
        self,
        dataset: str = "bhavcopy",
    ) -> DownloadResult:

        return self.download(
            trade_date=date.today(),
            dataset=dataset,
        )

    # ---------------------------------------------------------

    def already_downloaded(
        self,
        trade_date: date,
        dataset: str = "bhavcopy",
    ) -> bool:

        config = get_dataset(dataset)

        with self.unit_of_work as uow:

            return uow.download_history.exists(
                provider=config.provider,
                dataset=config.dataset,
                trading_date=trade_date,
            )

    # ---------------------------------------------------------

    def failed_downloads(self):

        with self.unit_of_work as uow:

            return uow.download_history.list_failed()