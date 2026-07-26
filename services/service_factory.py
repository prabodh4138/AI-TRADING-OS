"""
AI Trading Operating System
Service Factory
"""

from services.symbol_download_service import SymbolDownloadService
from data_engine.loader.symbol_csv_loader import SymbolCSVLoader
from data_engine.validator.symbol_validator import SymbolValidator


class ServiceFactory:
    """
    Central factory for application services.
    """

    _symbol_download_service = None
    _symbol_csv_loader = None
    _symbol_validator = None

    @classmethod
    def symbol_download_service(cls):

        if cls._symbol_download_service is None:
            cls._symbol_download_service = SymbolDownloadService()

        return cls._symbol_download_service

    @classmethod
    def symbol_csv_loader(cls):

        if cls._symbol_csv_loader is None:
            cls._symbol_csv_loader = SymbolCSVLoader()

        return cls._symbol_csv_loader
    @classmethod
    def symbol_validator(cls):

        if cls._symbol_validator is None:
            cls._symbol_validator = SymbolValidator()

        return cls._symbol_validator