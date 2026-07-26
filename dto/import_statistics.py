"""
AI Trading Operating System
Import Statistics DTO
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ImportStatistics:
    """
    Summary of a market data import operation.
    """

    files_processed: int = 0

    files_failed: int = 0

    records_imported: int = 0

    records_skipped: int = 0