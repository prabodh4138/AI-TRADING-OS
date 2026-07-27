"""
AI Trading Operating System
Sprint 8.5.4

Transformation Result Model
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TransformationResult:
    """
    Stores execution statistics produced by the
    Symbol Transformer.

    This object contains only operational
    information about the transformation process.
    It does NOT contain business data.
    """

    # ---------------------------------------------------------
    # Execution Status
    # ---------------------------------------------------------

    success: bool = False

    # ---------------------------------------------------------
    # Processing Statistics
    # ---------------------------------------------------------

    rows_processed: int = 0

    columns_processed: int = 0

    transformation_time: float = 0.0

    # ---------------------------------------------------------
    # Diagnostics
    # ---------------------------------------------------------

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)

    # ---------------------------------------------------------
    # Helper Methods
    # ---------------------------------------------------------

    def add_warning(self, message: str) -> None:
        """
        Add a warning message.
        """

        self.warnings.append(message)

    def add_error(self, message: str) -> None:
        """
        Add an error message.
        """

        self.errors.append(message)

    def reset(self) -> None:
        """
        Reset the object for reuse.
        """

        self.success = False

        self.rows_processed = 0

        self.columns_processed = 0

        self.transformation_time = 0.0

        self.warnings.clear()

        self.errors.clear()