from __future__ import annotations

import sys
from pathlib import Path
from datetime import date

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.download_service import DownloadService


def print_result(result) -> None:
    print("\nRESULT")
    print("-" * 60)
    print(f"Success      : {result.success}")
    print(f"Dataset      : {result.dataset}")
    print(f"Trade Date   : {result.trade_date}")
    print(f"File         : {result.file_path}")
    print(f"Checksum     : {result.checksum}")
    print(f"File Size    : {result.file_size}")
    print(f"Rows         : {result.row_count}")
    #print(f"Downloaded   : {result.downloaded}")
    #print(f"Skipped      : {result.skipped}")
    print(f"Error        : {result.error}")


def main() -> None:
    print("=" * 60)
    print(" AI Trading OS - DownloadService Integration Test")
    print("=" * 60)

    service = DownloadService()

    trade_date = date.today()

    print(f"\nDownloading data for : {trade_date}")

    result = service.download(
        trade_date=trade_date,
        dataset="bhavcopy",
    )

    print_result(result)

    print("\nTest Completed")


if __name__ == "__main__":
    main()