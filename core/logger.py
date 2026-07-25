"""
AI Trading Operating System
Enterprise Logger
"""

from loguru import logger
import sys
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logger.remove()

logger.add(
    sys.stdout,
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}"
)

logger.add(
    LOG_DIR / "application.log",
    rotation="10 MB",
    retention="30 days",
    level="DEBUG"
)

def get_logger():
    return logger
