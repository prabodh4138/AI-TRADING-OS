"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    file_manager.py

Purpose
-------
Centralized file management for the Data Engine.

Responsibilities
----------------
1. Create directories
2. Build filenames
3. Build output paths
4. Check file existence
5. Save text files
6. Read text files
7. Delete files (future)

This module is provider-independent and can be reused
by NSE, Yahoo, Polygon, or any future data source.

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

import logging
from pathlib import Path


class FileManager:
    """
    Generic file manager.

    Handles all filesystem operations for the
    Data Engine.
    """

    def __init__(
        self,
        root_directory: Path,
        logger: logging.Logger | None = None,
    ) -> None:

        self.root_directory = Path(root_directory)

        self.logger = logger or logging.getLogger(__name__)

        self.root_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    # --------------------------------------------------
    # Directory
    # --------------------------------------------------

    def ensure_directory(
        self,
        directory: Path,
    ) -> Path:
        """
        Create directory if it does not exist.
        """

        directory = Path(directory)

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return directory

    # --------------------------------------------------
    # Filename
    # --------------------------------------------------

    def build_filename(
        self,
        prefix: str,
        extension: str,
        identifier: str,
    ) -> str:
        """
        Build a standardized filename.

        Example
        -------
        sec_bhavdata_full_01012025.csv
        """

        extension = extension.lstrip(".")

        return f"{prefix}{identifier}.{extension}"

    # --------------------------------------------------
    # Path
    # --------------------------------------------------

    def build_path(
        self,
        filename: str,
    ) -> Path:
        """
        Build full output path.
        """

        return self.root_directory / filename

    # --------------------------------------------------
    # Exists
    # --------------------------------------------------

    def exists(
        self,
        path: Path,
    ) -> bool:
        """
        Check whether a file exists.
        """

        return Path(path).exists()

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    def save_text(
        self,
        path: Path,
        content: str,
        encoding: str = "utf-8",
    ) -> Path:
        """
        Save text to disk.
        """

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content,
            encoding=encoding,
        )

        self.logger.info(
            "Saved file: %s",
            path.name,
        )

        return path

    # --------------------------------------------------
    # Read
    # --------------------------------------------------

    def read_text(
        self,
        path: Path,
        encoding: str = "utf-8",
    ) -> str:
        """
        Read text from disk.
        """

        return Path(path).read_text(
            encoding=encoding,
        )

    # --------------------------------------------------
    # Delete
    # --------------------------------------------------

    def delete(
        self,
        path: Path,
    ) -> bool:
        """
        Delete a file if it exists.

        Returns
        -------
        bool
            True if deleted.
            False if file not found.
        """

        path = Path(path)

        if not path.exists():
            return False

        path.unlink()

        self.logger.info(
            "Deleted file: %s",
            path.name,
        )

        return True