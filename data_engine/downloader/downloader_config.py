"""
==============================================================
AI Trading Operating System
Sprint 9.2.1 : Download Configuration
==============================================================

Central configuration for the Download Engine.

Responsibilities
----------------
- Download directories
- Supported data providers
- Dataset configuration
- Retry policy
- Timeout settings
- File naming conventions
- Checksum algorithm
- Archive configuration

Author : AI Trading OS
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


# ==========================================================
# Download Root
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOWNLOAD_ROOT = PROJECT_ROOT / "downloads"

RAW_DOWNLOAD_DIR = DOWNLOAD_ROOT / "raw"

ARCHIVE_DIR = DOWNLOAD_ROOT / "archive"

FAILED_DIR = DOWNLOAD_ROOT / "failed"

TEMP_DIR = DOWNLOAD_ROOT / "temp"


# ==========================================================
# Directory Creation
# ==========================================================

for directory in (
    DOWNLOAD_ROOT,
    RAW_DOWNLOAD_DIR,
    ARCHIVE_DIR,
    FAILED_DIR,
    TEMP_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)


# ==========================================================
# Provider Configuration
# ==========================================================

DEFAULT_PROVIDER = "NSE"


# ==========================================================
# Dataset Configuration
# ==========================================================

@dataclass(frozen=True)
class DatasetConfig:
    """
    Configuration for one downloadable dataset.
    """

    provider: str
    dataset: str
    filename_pattern: str
    extension: str
    compressed: bool = False


SUPPORTED_DATASETS: Dict[str, DatasetConfig] = {

    "bhavcopy": DatasetConfig(
        provider="NSE",
        dataset="bhavcopy",
        filename_pattern="bhavcopy_{date}",
        extension=".csv",
    ),

    "delivery": DatasetConfig(
        provider="NSE",
        dataset="delivery",
        filename_pattern="delivery_{date}",
        extension=".csv",
    ),

    "symbols": DatasetConfig(
        provider="NSE",
        dataset="symbols",
        filename_pattern="symbols",
        extension=".csv",
    ),
}


# ==========================================================
# Network Configuration
# ==========================================================

DOWNLOAD_TIMEOUT = 60

CONNECT_TIMEOUT = 15

READ_TIMEOUT = 60

MAX_RETRY = 3

RETRY_DELAY_SECONDS = 5


# ==========================================================
# File Validation
# ==========================================================

CHECKSUM_ALGORITHM = "sha256"

MINIMUM_FILE_SIZE = 100

ALLOW_EMPTY_FILE = False


# ==========================================================
# Download Behaviour
# ==========================================================

OVERWRITE_EXISTING = False

VERIFY_AFTER_DOWNLOAD = True

ARCHIVE_AFTER_IMPORT = True

DELETE_TEMP_AFTER_SUCCESS = True


# ==========================================================
# Logging
# ==========================================================

LOG_PROGRESS = True

LOG_DOWNLOAD_SPEED = True

LOG_CHECKSUM = True


# ==========================================================
# Helper Functions
# ==========================================================

def get_dataset(dataset: str) -> DatasetConfig:
    """
    Return dataset configuration.
    """

    key = dataset.lower()

    if key not in SUPPORTED_DATASETS:
        raise ValueError(f"Unsupported dataset: {dataset}")

    return SUPPORTED_DATASETS[key]


def get_download_path(dataset: str) -> Path:
    """
    Download location for dataset.
    """

    return RAW_DOWNLOAD_DIR / dataset.lower()


def get_archive_path(dataset: str) -> Path:
    """
    Archive location.
    """

    return ARCHIVE_DIR / dataset.lower()


def ensure_dataset_directories() -> None:
    """
    Create directories for all datasets.
    """

    for dataset in SUPPORTED_DATASETS:

        get_download_path(dataset).mkdir(
            parents=True,
            exist_ok=True,
        )

        get_archive_path(dataset).mkdir(
            parents=True,
            exist_ok=True,
        )


ensure_dataset_directories()