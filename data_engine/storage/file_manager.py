"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    file_manager.py

Purpose
-------
Provides file storage services for the Data Engine.

Responsibilities
----------------
1. Create directories
2. Generate filenames
3. Build file paths
4. Save files
5. Read files
6. Delete files

This class does NOT know anything about:
- NSE
- Yahoo
- Database
- HTTP
- Validation

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

from datetime import date
from pathlib import Path


class FileManager:
    """
    Handles all file system operations.
    """

    def __init__(
        self,
        root_directory: str | Path,
        extension: str = ".csv",
    ) -> None:
        """
        Initialize FileManager.
        """

        self.root_directory = Path(root_directory)
        self.extension = extension

        self.ensure_directory()

    # ==================================================
    # Directory
    # ==================================================

    def ensure_directory(self) -> None:
        """
        Create the root directory if it does not exist.
        """

        self.root_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==================================================
    # Legacy Filename Builder (Backward Compatibility)
    # ==================================================

    def build_filename(
        self,
        prefix: str,
        extension: str,
        identifier: str,
    ) -> str:
        """
        Build a filename.

        This method is retained for backward compatibility
        with existing tests and callers.

        Example
        -------
        sec_bhavdata_full_01012025.csv
        """

        extension = extension.lstrip(".")

        return f"{prefix}{identifier}.{extension}"

    # ==================================================
    # New Enterprise Filename Builder
    # ==================================================

    def build_daily_filename(
        self,
        trade_date: date,
        prefix: str = "bhavcopy",
    ) -> str:
        """
        Generate a daily filename.

        Example
        -------
        bhavcopy_20260725.csv
        """

        return (
            f"{prefix}_"
            f"{trade_date:%Y%m%d}"
            f"{self.extension}"
        )

    # ==================================================
    # Path
    # ==================================================

    def build_path(
        self,
        filename: str,
    ) -> Path:
        """
        Build an absolute file path.
        """

        return self.root_directory / filename

    # ==================================================
    # Exists
    # ==================================================

    def exists(
        self,
        filename: str,
    ) -> bool:
        """
        Check whether a file exists.
        """

        return self.build_path(filename).exists()

    # ==================================================
    # Save
    # ==================================================

    def save_text(
        self,
        path: Path,
        text: str,
        encoding: str = "utf-8",
    ) -> Path:
        """
        Save text to a file.
        """

        path.write_text(
            text,
            encoding=encoding,
        )

        return path

    # ==================================================
    # Read
    # ==================================================

    def read_text(
        self,
        path: Path,
        encoding: str = "utf-8",
    ) -> str:
        """
        Read text from a file.
        """

        return path.read_text(
            encoding=encoding,
        )

    # ==================================================
    # Delete
    # ==================================================

    def delete(
        self,
        path: Path,
    ) -> bool:
        """
        Delete a file.

        Returns
        -------
        bool
            True if the file was deleted.
            False if the file did not exist.
        """

        if path.exists():
            path.unlink()
            return True

        return False