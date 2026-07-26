"""
==============================================================
AI Trading Operating System
Sprint 9.2.3
Download Manager
==============================================================
"""

from __future__ import annotations

import logging

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from requests import Response

from data_engine.downloader.downloader_config import (
    get_dataset,
    get_download_path,
)
from data_engine.downloader.file_verifier import (
    FileVerifier,
    VerificationResult,
)
from data_engine.downloader.nse_downloader import NSEDownloader


LOGGER = logging.getLogger(__name__)


# ==========================================================
# Download Result
# ==========================================================

@dataclass(slots=True)
class DownloadResult:

    success: bool

    trade_date: date

    dataset: str

    file_path: Path | None

    checksum: str | None

    file_size: int

    row_count: int

    error: str | None = None


# ==========================================================
# Download Manager
# ==========================================================

class DownloadManager:

    def __init__(
        self,
        downloader: NSEDownloader | None = None,
        verifier: FileVerifier | None = None,
        logger: logging.Logger | None = None,
    ) -> None:

        self.downloader = downloader or NSEDownloader()

        self.verifier = verifier or FileVerifier()

        self.logger = logger or LOGGER

    # -----------------------------------------------------

    def download(
        self,
        trade_date: date,
        dataset: str = "bhavcopy",
    ) -> DownloadResult:

        config = get_dataset(dataset)

        download_directory = get_download_path(dataset)

        filename = (
            config.filename_pattern.format(
                date=trade_date.strftime("%Y%m%d")
            )
            + config.extension
        )

        file_path = download_directory / filename

        try:

            self.logger.info(
                "Downloading %s for %s",
                dataset,
                trade_date,
            )

            response = self.downloader.download(
                trade_date
            )

            self._save_response(
                response=response,
                file_path=file_path,
            )

            verification = self.verifier.verify(
                file_path
            )

            if not verification.is_valid:

                self._cleanup(file_path)

                return DownloadResult(
                    success=False,
                    trade_date=trade_date,
                    dataset=dataset,
                    file_path=None,
                    checksum=verification.checksum,
                    file_size=verification.file_size,
                    row_count=verification.row_count,
                    error=verification.error,
                )

            self.logger.info(
                "Download verified successfully."
            )

            return DownloadResult(
                success=True,
                trade_date=trade_date,
                dataset=dataset,
                file_path=file_path,
                checksum=verification.checksum,
                file_size=verification.file_size,
                row_count=verification.row_count,
            )

        except Exception as ex:

            self.logger.exception(
                "Download failed."
            )

            self._cleanup(file_path)

            return DownloadResult(
                success=False,
                trade_date=trade_date,
                dataset=dataset,
                file_path=None,
                checksum=None,
                file_size=0,
                row_count=0,
                error=str(ex),
            )

    # -----------------------------------------------------

    @staticmethod
    def _save_response(
        response: Response,
        file_path: Path,
    ) -> None:

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with file_path.open("wb") as file:

            file.write(response.content)

    # -----------------------------------------------------

    @staticmethod
    def _cleanup(
        file_path: Path,
    ) -> None:

        if file_path.exists():

            file_path.unlink()

    # -----------------------------------------------------

    def statistics(self) -> dict:

        return self.downloader.statistics()