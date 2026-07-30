"""
=========================================================
AI Trading OS
Enterprise Import Result DTO
=========================================================

Module:
    import_result.py

Purpose
-------
Represents the outcome of a market data import
operation.

Responsibilities
----------------
1. Store import statistics
2. Report execution status
3. Carry timing information
4. Provide pipeline response object

This DTO MUST NOT

- Read CSV files
- Validate data
- Transform data
- Save to database
- Contain business logic

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ImportResult:
    """
    Enterprise DTO representing the outcome of a
    market data import pipeline execution.
    """

    # --------------------------------------------------
    # Overall Status
    # --------------------------------------------------

    success: bool

    # --------------------------------------------------
    # File Information
    # --------------------------------------------------

    file_name: str

    # --------------------------------------------------
    # Import Statistics
    # --------------------------------------------------

    rows_read: int = 0
    rows_imported: int = 0
    rows_failed: int = 0

    # --------------------------------------------------
    # Timing
    # --------------------------------------------------

    started_at: datetime | None = None
    completed_at: datetime | None = None

    # --------------------------------------------------
    # Status Information
    # --------------------------------------------------

    message: str = ""
    exception : str = ""

    # --------------------------------------------------
    # Computed Property
    # --------------------------------------------------

    @property
    def duration_seconds(self) -> float:
        """
        Returns the execution duration in seconds.

        Returns
        -------
        float
        """

        if (
            self.started_at is None
            or self.completed_at is None
        ):
            return 0.0

        return (
            self.completed_at
            - self.started_at
        ).total_seconds()

    # --------------------------------------------------
    # Convenience Property
    # --------------------------------------------------

    @property
    def has_failures(self) -> bool:
        """
        Returns True if one or more rows failed.
        """

        return self.rows_failed > 0

    # --------------------------------------------------
    # String Representation
    # --------------------------------------------------

    def __str__(self) -> str:

        return (
            f"ImportResult("
            f"success={self.success}, "
            f"file='{self.file_name}', "
            f"rows_read={self.rows_read}, "
            f"rows_imported={self.rows_imported}, "
            f"rows_failed={self.rows_failed}, "
            f"duration={self.duration_seconds:.2f}s)"
        )