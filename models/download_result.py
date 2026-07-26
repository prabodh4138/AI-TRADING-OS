from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class DownloadResult:
    """
    Standard result returned by all download services.
    """

    success: bool

    dataset: str

    trade_date: Optional[date] = None

    file_path: Optional[Path] = None

    row_count: int = 0

    checksum: str = ""

    file_size: int = 0

    duration_seconds: float = 0.0

    error: Optional[str] = None