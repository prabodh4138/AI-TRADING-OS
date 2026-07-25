"""
AI Trading Operating System
Application Bootstrap
"""

from core.constants import APP_NAME, APP_VERSION
from core.logger import get_logger
from core.settings import settings
from database.connection import database


class Bootstrap:

    def __init__(self) -> None:

        self.logger = get_logger()
        self.database = database

    def initialize(self) -> None:

        app = settings.application

        self.logger.info("Bootstrapping application...")
        self.logger.info(
            f"{APP_NAME} v{APP_VERSION} "
            f"({app['application']['environment']})"
        )

        if not self.database.test_connection():
            raise RuntimeError("Unable to connect to PostgreSQL.")