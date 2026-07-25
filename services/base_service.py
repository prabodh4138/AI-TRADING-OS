"""
AI Trading Operating System
Base Service

Common functionality shared by all business services.
"""

from __future__ import annotations

from typing import Any

from core.logger import get_logger


class BaseService:
    """
    Base class for all business services.

    Responsibilities
    ----------------
    - Logging
    - Common validation helpers
    - Business rule helpers

    NOTE:
    This class DOES NOT own a UnitOfWork.
    Every service method should create its own UnitOfWork:

        with UnitOfWork() as uow:
            ...
    """

    def __init__(self) -> None:
        self.logger = get_logger()

    # ---------------------------------------------------------
    # Validation Helpers
    # ---------------------------------------------------------

    @staticmethod
    def require_not_none(
        value: Any,
        field_name: str,
    ) -> None:

        if value is None:
            raise ValueError(
                f"{field_name} cannot be None."
            )

    @staticmethod
    def require(
        condition: bool,
        message: str,
    ) -> None:

        if not condition:
            raise ValueError(message)

    # ---------------------------------------------------------
    # Logging Helpers
    # ---------------------------------------------------------

    def log_info(self, message: str) -> None:
        self.logger.info(message)

    def log_warning(self, message: str) -> None:
        self.logger.warning(message)

    def log_error(self, message: str) -> None:
        self.logger.error(message)