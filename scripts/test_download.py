"""
==============================================================
AI Trading Operating System
Download Integration Test
==============================================================

Purpose
-------
Tests the complete download pipeline:

NSE
 ↓
DownloadManager
 ↓
FileVerifier
 ↓
CSV File

No database operations are performed.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_engine.downloader.download_manager import DownloadManager


def main() -> None:

    print("=" * 60)
    print(" AI Trading OS - Download Integration Test")
    print("=" * 60)

    manager = DownloadManager()

    trade_date = date.today()

    print(f"\nDownloading data for : {trade_date}")

    result = manager.download(
        trade_date=trade_date,
        dataset="bhavcopy",
    )

    print("\nRESULT")
    print("-" * 60)

    print(f"Success      : {result.success}")
    print(f"Dataset      : {result.dataset}")
    print(f"Trade Date   : {result.trade_date}")
    print(f"File         : {result.file_path}")
    print(f"Checksum     : {result.checksum}")
    print(f"File Size    : {result.file_size}")
    print(f"Rows         : {result.row_count}")
    print(f"Error        : {result.error}")

    print("\nDownloader Statistics")
    print("-" * 60)

    for key, value in manager.statistics().items():
        print(f"{key:<20}: {value}")

    print("\nTest Completed")


if __name__ == "__main__":
    main()