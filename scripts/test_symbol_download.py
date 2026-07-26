"""
Test Script
Sprint 8.5.1
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.logger import get_logger
from services.symbol_download_service import SymbolDownloadService


logger = get_logger()


def main():

    logger.info("=" * 70)
    logger.info("NSE SYMBOL MASTER DOWNLOAD TEST")
    logger.info("=" * 70)

    service = SymbolDownloadService()

    result = service.download_symbol_master()

    logger.info("")

    logger.info("Download Summary")
    logger.info("------------------------------")

    logger.info("Success      : {}", result.success)
    logger.info("Dataset      : {}", result.dataset)
    logger.info("Trade Date   : {}", result.trade_date)
    logger.info("File         : {}", result.file_path)
    logger.info("Rows         : {}", result.row_count)
    logger.info("Checksum     : {}", result.checksum)
    logger.info("File Size    : {} bytes", result.file_size)
    logger.info("Duration     : {} sec", result.duration_seconds)

    if result.error:
        logger.error("Error        : {}", result.error)

    logger.info("=" * 70)


if __name__ == "__main__":
    main()