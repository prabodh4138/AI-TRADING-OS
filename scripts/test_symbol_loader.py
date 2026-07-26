"""
AI Trading Operating System
Sprint 8.5.2

Test Symbol CSV Loader
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.logger import get_logger
from services.service_factory import ServiceFactory

logger = get_logger()


def main():

    logger.info("=" * 70)
    logger.info("SYMBOL CSV LOADER TEST")
    logger.info("=" * 70)

    #
    # Step 1 : Download Symbol Master
    #
    download_service = ServiceFactory.symbol_download_service()

    download_result = download_service.download_symbol_master()

    if not download_result.success:

        logger.error(
            "Download failed : {}",
            download_result.error,
        )

        return

    #
    # Step 2 : Load CSV
    #
    loader = ServiceFactory.symbol_csv_loader()

    df = loader.load(download_result.file_path)

    logger.info("")
    logger.info("DataFrame Summary")
    logger.info("------------------------------")

    logger.info("Rows    : {}", len(df))
    logger.info("Columns : {}", len(df.columns))

    logger.info("")
    logger.info("Column Names")

    for column in df.columns:

        logger.info("  {}", column)

    logger.info("")
    logger.info("First Five Records")

    logger.info("\n{}", loader.preview(df))

    logger.info("")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()