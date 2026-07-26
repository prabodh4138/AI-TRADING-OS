from __future__ import annotations

import sys
from pathlib import Path
from datetime import date

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.synchronization_service import SynchronizationService


def print_result(result) -> None:
    print("\nRESULT")
    print("-" * 60)
    print(f"Success            : {result.success}")
    print(f"Trade Date         : {result.trading_date}")
    print(f"Dataset            : {result.dataset}")
    print(f"Records Imported   : {result.records_imported}")

    if result.download_result:
        print("\nDownload Result")
        print("-" * 60)
        print(f"Success            : {result.download_result.success}")
        print(f"Trade Date         : {result.download_result.trade_date}")
        print(f"Dataset            : {result.download_result.dataset}")
        print(f"File               : {result.download_result.file_path}")
        print(f"Rows               : {result.download_result.row_count}")
        print(f"Checksum           : {result.download_result.checksum}")

    print(f"\nError              : {result.error}")


def main() -> None:
    print("=" * 70)
    print(" AI Trading OS - Synchronization Integration Test")
    print("=" * 70)

    service = SynchronizationService()

    trade_date = date.today()

    print(f"\nSynchronizing : {trade_date}")

    result = service.synchronize(
        trading_date=trade_date,
        dataset="bhavcopy",
    )

    print_result(result)

    print("\nSynchronization Test Completed")


if __name__ == "__main__":
    main()