"""
AI Trading Operating System
Application Kernel
"""

from core.logger import get_logger
from core.bootstrap import Bootstrap


class ApplicationKernel:
    """
    Central application lifecycle manager.
    """

    def __init__(self) -> None:
        self.logger = get_logger()
        self.bootstrap = Bootstrap()

    def initialize(self) -> None:
        """Initialize all application components."""
        self.bootstrap.initialize()

    def run(self) -> None:
        """Start the application."""

        self.initialize()

        self.logger.info("Application kernel started successfully.")

        print()
        print("=" * 60)
        print(" AI Trading Operating System")
        print(" Enterprise Kernel Running")
        print("=" * 60)

    def shutdown(self) -> None:
        """Shutdown application resources."""
        self.logger.info("Application shutdown completed.")