"""
AI Trading Operating System
Application Facade for CLI, API, and UI entry points.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import pandas as pd

from data_engine.market_data import read_market_csv
from scanner.engine import ScanReport, Scanner


class Application:
    """Enterprise application facade."""

    def __init__(self, scanner: Optional[Scanner] = None) -> None:
        self.scanner = scanner or Scanner()

    def scan_file(self, path: str | Path, top_n: int = 50) -> ScanReport:
        """Loads market data CSV, executes multi-layer intelligence, and returns ScanReport."""
        df = read_market_csv(path)
        return self.scanner.scan(df, top_n=top_n)

    def scan_dataframe(self, df: pd.DataFrame, top_n: int = 50) -> ScanReport:
        """Executes multi-layer intelligence scan directly on a normalized DataFrame."""
        return self.scanner.scan(df, top_n=top_n)
