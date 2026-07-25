"""
AI Trading Operating System
Configuration Manager

Loads YAML configuration files once and caches them.
"""

from pathlib import Path
from typing import Any

import yaml

from core.constants import CONFIG_DIR
from core.exceptions import ConfigurationError


class Settings:
    """Central configuration manager."""

    def __init__(self) -> None:
        self._cache: dict[str, dict[str, Any]] = {}

    def _load(self, filename: str) -> dict[str, Any]:
        path = CONFIG_DIR / filename

        if not path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {path}"
            )

        with open(path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

    def config(self, filename: str) -> dict[str, Any]:
        if filename not in self._cache:
            self._cache[filename] = self._load(filename)

        return self._cache[filename]

    @property
    def application(self) -> dict[str, Any]:
        return self.config("application.yaml")

    @property
    def database(self) -> dict[str, Any]:
        return self.config("database.yaml")

    @property
    def logging(self) -> dict[str, Any]:
        return self.config("logging.yaml")

    @property
    def market(self) -> dict[str, Any]:
        return self.config("market.yaml")

    @property
    def risk(self) -> dict[str, Any]:
        return self.config("risk.yaml")


settings = Settings()