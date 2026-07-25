"""
AI Trading Operating System
Base Validator
"""

from __future__ import annotations


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class BaseValidator:
    """
    Base validator for all DTOs.
    """

    def validate(self, dto):
        raise NotImplementedError