"""
AI Trading Operating System
Custom Exception Hierarchy

All application-specific exceptions inherit from AITradingError.
"""


class AITradingError(Exception):
    """Base class for all application exceptions."""


# ==========================================================
# Configuration
# ==========================================================

class ConfigurationError(AITradingError):
    """Raised when application configuration is invalid."""


# ==========================================================
# Database
# ==========================================================

class DatabaseError(AITradingError):
    """Raised when a database operation fails."""


class DatabaseConnectionError(DatabaseError):
    """Raised when the database connection cannot be established."""


# ==========================================================
# Market Data
# ==========================================================

class MarketDataError(AITradingError):
    """Raised when market data cannot be retrieved or processed."""


# ==========================================================
# Scanner
# ==========================================================

class ScannerError(AITradingError):
    """Raised when the scanner encounters an error."""


# ==========================================================
# Strategy
# ==========================================================

class StrategyError(AITradingError):
    """Raised when strategy execution or validation fails."""


# ==========================================================
# Risk
# ==========================================================

class RiskManagementError(AITradingError):
    """Raised when risk rules are violated."""


# ==========================================================
# Portfolio
# ==========================================================

class PortfolioError(AITradingError):
    """Raised for portfolio management errors."""