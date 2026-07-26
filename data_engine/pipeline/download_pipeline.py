"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    download_pipeline.py

Purpose
-------
Coordinates the complete download workflow.

Responsibilities
----------------
1. Download response
2. Validate response
3. Save file
4. Return saved file path

This class does not know anything about NSE,
Yahoo, Polygon, or any specific provider.

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

from pathlib import Path
from datetime import date

from requests import Response

from data_engine.downloader.base_downloader import BaseDownloader
from data_engine.storage.file_manager import FileManager
from data_engine.validator.response_validator import ResponseValidator


class DownloadPipeline:
    """
    Coordinates the download workflow.

    Workflow
    --------

    Downloader
        ↓
    ResponseValidator
        ↓
    FileManager
        ↓
    Return saved file
    """

    def __init__(
        self,
        downloader: BaseDownloader,
        validator: ResponseValidator,
        file_manager: FileManager,
    ) -> None:
        """
        Initialize pipeline.
        """

        self.downloader = downloader
        self.validator = validator
        self.file_manager = file_manager

    # ==================================================
    # Public API
    # ==================================================

    def execute(
        self,
        trade_date: date,
    ) -> Path:
        """
        Execute complete download pipeline.

        Parameters
        ----------
        trade_date
            Trading date to download.

        Returns
        -------
        Path
            Saved CSV file.
        """

        response = self._download(trade_date)

        self._validate(response)

        filename = self.downloader.build_filename(
            trade_date
        )

        path = self.file_manager.build_path(
            filename
        )

        self._save(
            path,
            response.text,
        )

        return path

    # ==================================================
    # Download
    # ==================================================

    def _download(
        self,
        trade_date: date,
    ) -> Response:
        """
        Download response.
        """

        return self.downloader.download(
            trade_date
        )

    # ==================================================
    # Validation
    # ==================================================

    def _validate(
        self,
        response: Response,
    ) -> None:
        """
        Validate response.
        """

        self.validator.validate(
            response
        )

    # ==================================================
    # Save
    # ==================================================

    def _save(
        self,
        path: Path,
        text: str,
    ) -> Path:
        """
        Save response.
        """

        return self.file_manager.save_text(
            path,
            text,
        )