"""
=========================================================
AI Trading OS
Enterprise Data Engine

Module:
    exceptions.py

Purpose
-------
Centralized exception hierarchy for the Data Engine.

All Data Engine components should raise these exceptions
instead of generic Exception.

Author:
    AI Trading OS
=========================================================
"""

from __future__ import annotations


class DataEngineException(Exception):
    """
    Base exception for all Data Engine errors.
    """

    pass


# =====================================================
# Downloader
# =====================================================

class DownloadException(DataEngineException):
    """
    Raised when download fails.
    """

    pass


class SessionException(DownloadException):
    """
    Raised when session initialization fails.
    """

    pass


class NetworkException(DownloadException):
    """
    Raised when network communication fails.
    """

    pass


# =====================================================
# Validation
# =====================================================

class ValidationException(DataEngineException):
    """
    Base validation exception.
    """

    pass


class ResponseValidationException(ValidationException):
    """
    Invalid HTTP response.
    """

    pass


class CsvValidationException(ValidationException):
    """
    CSV validation failed.
    """

    pass


class SchemaValidationException(ValidationException):
    """
    Schema validation failed.
    """

    pass


# =====================================================
# Storage
# =====================================================

class StorageException(DataEngineException):
    """
    File storage error.
    """

    pass


# =====================================================
# Loader
# =====================================================

class LoaderException(DataEngineException):
    """
    Database loading error.
    """

    pass


# =====================================================
# Pipeline
# =====================================================

class PipelineException(DataEngineException):
    """
    Pipeline execution error.
    """

    pass


# =====================================================
# Audit
# =====================================================

class AuditException(DataEngineException):
    """
    Audit logging error.
    """

    pass