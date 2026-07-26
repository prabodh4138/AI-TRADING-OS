"""
AI Trading Operating System
Configuration Loader
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class Settings:
    """
    Application configuration loader.

    Reads configuration from config/application.yaml
    and provides dictionary-style access.
    """

    def __init__(self):

        self._config = {}

        config_file = (
            Path(__file__).resolve().parent / "application.yaml"
        )

        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_file}"
            )

        with config_file.open(
            "r",
            encoding="utf-8",
        ) as fp:

            self._config = yaml.safe_load(fp) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Returns a configuration section.

        Example:
            settings.get("database")
            settings.get("symbol_master")
        """
        return self._config.get(key, default)

    @property
    def config(self):
        return self._config


settings = Settings()