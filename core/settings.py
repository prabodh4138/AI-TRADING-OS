"""Central configuration with environment-variable overrides."""
from __future__ import annotations
import os
from functools import lru_cache
from pathlib import Path
from typing import Any
import yaml
from dotenv import load_dotenv
from core.constants import CONFIG_DIR
from core.exceptions import ConfigurationError

load_dotenv()

class Settings:
    def __init__(self) -> None:
        self._cache: dict[str, dict[str, Any]] = {}

    def _load(self, filename: str) -> dict[str, Any]:
        path = CONFIG_DIR / filename
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {path}")
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

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
    def market(self) -> dict[str, Any]:
        return self.config("market.yaml")

    @property
    def risk(self) -> dict[str, Any]:
        return self.config("risk.yaml")

    @property
    def environment(self) -> str:
        return os.getenv("ENVIRONMENT", self.application.get("application", {}).get("environment", "development"))

    @property
    def database_url(self) -> str:
        value = os.getenv("DATABASE_URL", "").strip()
        if value:
            return value
        db = self.database.get("database", {})
        password = db.get("password", "")
        if not password:
            raise ConfigurationError("DATABASE_URL is not set and database.password is empty. Configure the database via environment variables.")
        from sqlalchemy.engine import URL
        return URL.create("postgresql+psycopg2", username=db["user"], password=password, host=db["host"], port=int(db["port"]), database=db["name"]).render_as_string(hide_password=False)

    @property
    def max_positions(self) -> int:
        return int(os.getenv("MAX_POSITIONS", self.risk.get("risk", {}).get("max_positions", 20)))

    @property
    def risk_per_trade_pct(self) -> float:
        return float(os.getenv("RISK_PER_TRADE_PCT", self.risk.get("risk", {}).get("max_risk_per_trade", 1.0)))

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
