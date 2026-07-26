"""
AI Trading Operating System

Validation Result Model
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ValidationResult:
    """
    Stores the outcome of a validation operation.
    """

    success: bool = False

    rows_checked: int = 0

    columns_checked: int = 0

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)

    validation_time: float = 0.0

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0