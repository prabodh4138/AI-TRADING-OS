"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    constants.py

Purpose
-------
Shared constants used across the Data Engine.

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations


# =====================================================
# HTTP
# =====================================================

HTTP_OK = 200

DEFAULT_TIMEOUT = 30

DOWNLOAD_TIMEOUT = 60


# =====================================================
# Downloader
# =====================================================

HOME_URL = "https://www.nseindia.com"

REPORT_URL = "https://www.nseindia.com/api/reports"

DEFAULT_LOOKBACK_DAYS = 400


# =====================================================
# Validation
# =====================================================

DEFAULT_REQUIRED_HEADER = "SYMBOL"

DEFAULT_MINIMUM_RESPONSE_SIZE = 100


# =====================================================
# File
# =====================================================

DEFAULT_ENCODING = "utf-8"

CSV_EXTENSION = "csv"

TEXT_EXTENSION = "txt"


# =====================================================
# Logging
# =====================================================

LOG_DOWNLOAD_STARTED = "Download started"

LOG_DOWNLOAD_COMPLETED = "Download completed"

LOG_FILE_SAVED = "File saved"

LOG_FILE_DELETED = "File deleted"

LOG_SESSION_CREATED = "Session created"

LOG_SESSION_CLOSED = "Session closed"