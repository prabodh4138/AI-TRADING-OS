"""
AI Trading Operating System
Sprint 8.5.1

Symbol Download Service

Downloads the latest NSE Symbol Master CSV and stores it locally.
"""

from __future__ import annotations

import hashlib
import shutil
import tempfile
import time
from datetime import date
from pathlib import Path

import requests

from config.settings import settings
from core.logger import get_logger
from exceptions.download_exception import DownloadException
from models.download_result import DownloadResult

logger = get_logger()


class SymbolDownloadService:
    """
    Downloads the latest NSE Symbol Master.
    """

    def __init__(self):

        cfg = settings.get("symbol_master")

        if cfg is None:
            raise ValueError(
                "Missing 'symbol_master' configuration in application.yaml"
            )

        self.url = cfg["url"]
        self.download_directory = Path(cfg["download_directory"])
        self.timeout = cfg.get("timeout", 30)
        self.retry_count = cfg.get("retry_count", 3)
        self.retry_delay = cfg.get("retry_delay", 2)
        self.user_agent = cfg.get("user_agent", "AI Trading OS/1.0")
        self.overwrite = cfg.get("overwrite", True)

        self.download_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def download_symbol_master(self) -> DownloadResult:

        start_time = time.perf_counter()

        filename = f"symbol_master_{date.today():%Y%m%d}.csv"

        destination = self.download_directory / filename

        headers = {
            "User-Agent": self.user_agent
        }

        last_error = None

        for attempt in range(1, self.retry_count + 1):

            temp_path = None

            try:

                logger.info(
                    "Downloading NSE Symbol Master (Attempt {}/{})",
                    attempt,
                    self.retry_count,
                )

                response = requests.get(
                    self.url,
                    headers=headers,
                    timeout=self.timeout,
                    stream=True,
                )

                response.raise_for_status()

                with tempfile.NamedTemporaryFile(delete=False) as tmp:

                    for chunk in response.iter_content(8192):

                        if chunk:
                            tmp.write(chunk)

                    temp_path = Path(tmp.name)

                if destination.exists():

                    if self.overwrite:

                        destination.unlink()

                    else:

                        raise DownloadException(
                            f"File already exists: {destination}"
                        )

                shutil.move(temp_path, destination)

                checksum = self._calculate_checksum(destination)

                row_count = self._count_rows(destination)

                duration = round(
                    time.perf_counter() - start_time,
                    2,
                )

                logger.info("Download completed successfully.")
                logger.info("File : {}", destination)
                logger.info("Rows : {}", row_count)

                return DownloadResult(
                    success=True,
                    dataset="symbol_master",
                    trade_date=date.today(),
                    file_path=destination,
                    row_count=row_count,
                    checksum=checksum,
                    file_size=destination.stat().st_size,
                    duration_seconds=duration,
                )

            except Exception as ex:

                last_error = str(ex)

                logger.warning(
                    "Attempt {} failed: {}",
                    attempt,
                    last_error,
                )

                if temp_path and temp_path.exists():

                    temp_path.unlink(missing_ok=True)

                if attempt < self.retry_count:

                    time.sleep(self.retry_delay)

        duration = round(
            time.perf_counter() - start_time,
            2,
        )

        logger.error("Symbol Master download failed.")

        return DownloadResult(
            success=False,
            dataset="symbol_master",
            trade_date=date.today(),
            duration_seconds=duration,
            error=last_error,
        )

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_checksum(file_path: Path) -> str:

        sha = hashlib.sha256()

        with file_path.open("rb") as fp:

            while True:

                block = fp.read(65536)

                if not block:
                    break

                sha.update(block)

        return sha.hexdigest()

    @staticmethod
    def _count_rows(file_path: Path) -> int:

        with file_path.open(
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as fp:

            return max(sum(1 for _ in fp) - 1, 0)