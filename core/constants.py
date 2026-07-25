"""
AI Trading Operating System
Core Constants

This module contains immutable application-wide constants.
Do not store configuration values or secrets here.
"""

from pathlib import Path

# ==========================================================
# Application Information
# ==========================================================

APP_NAME: str = "AI Trading Operating System"
APP_SHORT_NAME: str = "AI-TOS"
APP_VERSION: str = "1.0.0"
APP_AUTHOR: str = "Prabodh Kumar Rana"

# ==========================================================
# Environment
# ==========================================================

ENV_DEVELOPMENT: str = "development"
ENV_TESTING: str = "testing"
ENV_PRODUCTION: str = "production"

DEFAULT_ENVIRONMENT: str = ENV_DEVELOPMENT

# ==========================================================
# Exchanges
# ==========================================================

EXCHANGE_NSE: str = "NSE"
EXCHANGE_BSE: str = "BSE"

SUPPORTED_EXCHANGES = (
    EXCHANGE_NSE,
    EXCHANGE_BSE,
)

# ==========================================================
# Timeframes
# ==========================================================

TIMEFRAME_1D = "1D"
TIMEFRAME_1W = "1W"
TIMEFRAME_1M = "1M"

SUPPORTED_TIMEFRAMES = (
    TIMEFRAME_1D,
    TIMEFRAME_1W,
    TIMEFRAME_1M,
)

# ==========================================================
# Project Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
REPORT_DIR = PROJECT_ROOT / "reports"
CONFIG_DIR = PROJECT_ROOT / "config"

# ==========================================================
# Logging
# ==========================================================

DEFAULT_LOG_FILE = "application.log"

# ==========================================================
# Database
# ==========================================================

DEFAULT_DATABASE_SCHEMA = "public"