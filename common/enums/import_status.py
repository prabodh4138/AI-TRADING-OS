"""
=========================================================
AI Trading Operating System
Import Status Enumeration
=========================================================

Defines all valid import execution states.
"""

from __future__ import annotations

from enum import StrEnum


class ImportStatus(StrEnum):
    """
    Import execution status.
    """

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"