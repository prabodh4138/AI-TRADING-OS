"""
AI Trading Operating System
Base Service Tests
"""

from services.base_service import BaseService


def test_base_service_creation():
    """
    BaseService should initialize only common infrastructure.

    It should NOT own a UnitOfWork.
    """
    service = BaseService()

    assert service is not None
    assert service.logger is not None

    # BaseService intentionally does not own a UnitOfWork.
    assert not hasattr(service, "uow")


def test_require_not_none_success():
    BaseService.require_not_none("ABC", "value")


def test_require_not_none_failure():
    try:
        BaseService.require_not_none(None, "symbol")
    except ValueError as exc:
        assert "symbol" in str(exc)
    else:
        assert False, "ValueError was not raised"


def test_require_success():
    BaseService.require(True, "Should not fail")


def test_require_failure():
    try:
        BaseService.require(False, "Validation failed")
    except ValueError as exc:
        assert str(exc) == "Validation failed"
    else:
        assert False, "ValueError was not raised"


def test_logging_methods_exist():
    """
    Verify logging helper methods are available.
    """
    service = BaseService()

    assert callable(service.log_info)
    assert callable(service.log_warning)
    assert callable(service.log_error)


def test_logging_methods_execute():
    """
    Logging methods should execute without raising exceptions.
    """
    service = BaseService()

    service.log_info("Information message")
    service.log_warning("Warning message")
    service.log_error("Error message")