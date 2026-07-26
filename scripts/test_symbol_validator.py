"""
AI Trading Operating System
Sprint 8.5.3

Test Symbol Validator
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
    logger.info("SYMBOL VALIDATOR TEST")
    logger.info("=" * 70)

    #
    # Download
    #

    download_service = ServiceFactory.symbol_download_service()

    download_result = download_service.download_symbol_master()

    if not download_result.success:

        logger.error(
            "Download failed: {}",
            download_result.error,
        )

        return

    #
    # Load
    #

    loader = ServiceFactory.symbol_csv_loader()

    df = loader.load(download_result.file_path)

    #
    # Validate
    #

    validator = ServiceFactory.symbol_validator()

    validated_df = validator.validate(df)

    result = validator.validation_result()

    logger.info("")
    logger.info("=" * 70)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 70)

    logger.info("Success          : {}", result.success)
    logger.info("Rows Checked     : {}", result.rows_checked)
    logger.info("Columns Checked  : {}", result.columns_checked)
    logger.info("Warnings         : {}", len(result.warnings))
    logger.info("Errors           : {}", len(result.errors))
    logger.info(
        "Validation Time  : {:.4f} sec",
        result.validation_time,
    )

    if result.warnings:

        logger.warning("Warning List")

        for warning in result.warnings:
            logger.warning("  {}", warning)

    if result.errors:

        logger.error("Error List")

        for error in result.errors:
            logger.error("  {}", error)

    logger.info("")
    logger.info("Validated Rows : {}", len(validated_df))

    logger.info("=" * 70)


if __name__ == "__main__":
    main()