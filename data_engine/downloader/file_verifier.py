"""
==============================================================
AI Trading Operating System
Sprint 9.2.2
File Verification Engine
==============================================================
"""

from __future__ import annotations

import csv
import hashlib
import logging

from dataclasses import dataclass
from pathlib import Path


LOGGER = logging.getLogger(__name__)


# ==========================================================
# Verification Result
# ==========================================================


@dataclass(slots=True)
class VerificationResult:

    is_valid: bool

    file_exists: bool

    file_size: int

    checksum: str | None

    row_count: int

    error: str | None = None


# ==========================================================
# File Verifier
# ==========================================================


class FileVerifier:

    def __init__(
        self,
        minimum_file_size: int = 100,
        logger: logging.Logger | None = None,
    ) -> None:

        self.minimum_file_size = minimum_file_size

        self.logger = logger or LOGGER

    # ------------------------------------------------------

    def verify(
        self,
        file_path: Path,
    ) -> VerificationResult:

        if not file_path.exists():

            return VerificationResult(
                is_valid=False,
                file_exists=False,
                file_size=0,
                checksum=None,
                row_count=0,
                error="File does not exist.",
            )

        file_size = file_path.stat().st_size

        if file_size == 0:

            return VerificationResult(
                False,
                True,
                file_size,
                None,
                0,
                "File is empty.",
            )

        if file_size < self.minimum_file_size:

            return VerificationResult(
                False,
                True,
                file_size,
                None,
                0,
                "File size below minimum threshold.",
            )

        checksum = self.calculate_checksum(file_path)

        try:

            row_count = self.validate_csv(file_path)

        except Exception as ex:

            return VerificationResult(
                False,
                True,
                file_size,
                checksum,
                0,
                str(ex),
            )

        return VerificationResult(
            is_valid=True,
            file_exists=True,
            file_size=file_size,
            checksum=checksum,
            row_count=row_count,
            error=None,
        )

    # ------------------------------------------------------

    @staticmethod
    def calculate_checksum(
        file_path: Path,
    ) -> str:

        sha = hashlib.sha256()

        with file_path.open("rb") as file:

            while chunk := file.read(8192):

                sha.update(chunk)

        return sha.hexdigest()

    # ------------------------------------------------------

    @staticmethod
    def validate_csv(
        file_path: Path,
    ) -> int:

        rows = 0

        with file_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:

            reader = csv.reader(file)

            for _ in reader:
                rows += 1

        if rows == 0:

            raise ValueError("CSV contains no rows.")

        return rows