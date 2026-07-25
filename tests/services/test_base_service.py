"""
AI Trading Operating System
Base Service Tests
"""

from services.base_service import BaseService


def test_base_service_creation():
    service = BaseService()

    assert service is not None
    assert service.uow is not None
    assert service.logger is not None


def test_require_not_none_success():
    BaseService.require_not_none("ABC", "value")


def test_require_not_none_failure():
    try:
        BaseService.require_not_none(None, "symbol")
    except ValueError as exc:
        assert "symbol" in str(exc)


def test_require_success():
    BaseService.require(True, "Should not fail")


def test_require_failure():
    try:
        BaseService.require(False, "Validation failed")
    except ValueError as exc:
        assert str(exc) == "Validation failed"