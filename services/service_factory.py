"""
Central Service Factory
"""

from services.symbol_download_service import SymbolDownloadService


class ServiceFactory:
    """
    Creates singleton service instances.
    """

    _symbol_download_service = None

    @classmethod
    def symbol_download_service(cls):

        if cls._symbol_download_service is None:
            cls._symbol_download_service = SymbolDownloadService()

        return cls._symbol_download_service