"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module
------
download_pipeline.py

Purpose
-------
Coordinates the complete download workflow.

Workflow
--------
Downloader
    ↓
Response Validator
    ↓
File Manager
    ↓
Saved CSV

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from pathlib import Path

from data_engine.downloader.base_downloader import BaseDownloader
from data_engine.storage.file_manager import FileManager
from data_engine.validator.response_validator import ResponseValidator


class DownloadPipeline:
    """
    Enterprise Download Pipeline.

    This class coordinates the complete
    download workflow.

    Responsibilities
    ----------------

    1. Download data
    2. Validate response
    3. Save response
    4. Return saved file

    This class MUST NOT

    - Build filenames
    - Parse CSV
    - Insert database
    """

    def __init__(
        self,
        downloader: BaseDownloader,
        validator: ResponseValidator,
        file_manager: FileManager,
        logger: logging.Logger | None = None,
    ) -> None:

        self.downloader = downloader

        self.validator = validator

        self.file_manager = file_manager

        self.logger = (
            logger
            or logging.getLogger(__name__)
        )

        self.logger.info(
            "DownloadPipeline initialized."
        )
            # ==================================================
    # Execute Pipeline
    # ==================================================

    def execute(
        self,
        trade_date: date,
    ) -> Path:
        """
        Execute the complete download workflow.

        Workflow
        --------
        1. Download response
        2. Validate response
        3. Save response
        4. Return saved file path

        Parameters
        ----------
        trade_date
            Trading date to download.

        Returns
        -------
        Path
            Path of the saved CSV file.
        """

        self.logger.info(
            "Starting download pipeline for %s",
            trade_date.isoformat(),
        )

        # ----------------------------------------------
        # Download
        # ----------------------------------------------

        response = self.downloader.download(
            trade_date
        )

        self.logger.info(
            "Download completed."
        )

        # ----------------------------------------------
        # Validate
        # ----------------------------------------------

        self.validator.validate(
            response
        )

        self.logger.info(
            "Response validation successful."
        )

        # ----------------------------------------------
        # Save
        # ----------------------------------------------

        saved_file = self.file_manager.save_response(
            trade_date=trade_date,
            response=response,
        )

        self.logger.info(
            "Response saved to %s",
            saved_file,
        )

        return saved_file
        # ==================================================
    # Execute Today's Download
    # ==================================================

    def execute_today(self) -> Path:
        """
        Download today's Bhavcopy.

        Returns
        -------
        Path
            Path of the saved CSV file.
        """

        return self.execute(
            date.today()
        )

        # ==================================================
    # Execute Date Range
    # ==================================================

    def execute_range(
        self,
        start_date: date,
        end_date: date,
        continue_on_error: bool = True,
    ) -> list[Path]:
        """
        Download Bhavcopy for a date range.

        Parameters
        ----------
        start_date
            First trading date.

        end_date
            Last trading date.

        continue_on_error
            Continue processing remaining dates if one
            download fails.

        Returns
        -------
        list[Path]
            List of successfully saved files.
        """

        if end_date < start_date:

            raise ValueError(
                "end_date must be greater than or equal to start_date."
            )

        saved_files: list[Path] = []

        current_date = start_date

        while current_date <= end_date:

            try:

                saved_file = self.execute(
                    current_date
                )

                saved_files.append(
                    saved_file
                )

            except Exception as ex:

                self.logger.exception(
                    "Pipeline failed for %s : %s",
                    current_date,
                    ex,
                )

                if not continue_on_error:
                    raise

            current_date += timedelta(
                days=1
            )

        self.logger.info(
            "Download pipeline completed."
        )

        self.logger.info(
            "Successfully downloaded %d file(s).",
            len(saved_files),
        )

        return saved_files