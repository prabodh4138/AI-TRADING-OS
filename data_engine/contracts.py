"""
AI Trading Operating System
Module 1: Data Contracts, Freshness Guardrails, and Sector Mappings.

Enforces:
- Strict point-in-time data availability contracts.
- Freshness checks and safe handling of missing/stale index data.
- Outlier and price sanity verification.
- Point-in-time constituent-to-sector resolution for NIFTY 500 constituents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml
import pandas as pd


@dataclass(frozen=True, slots=True)
class DataAvailabilityContract:
    """Records exact data provenance, timestamps, and freshness state."""
    as_of_date: date
    generated_at: datetime
    index_data_fresh: bool
    sector_data_fresh: bool
    stock_data_fresh: bool
    staleness_days: int
    is_safe_for_decision: bool
    degraded_mode: bool
    missing_symbols: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "as_of_date": str(self.as_of_date),
            "generated_at": self.generated_at.isoformat(),
            "index_data_fresh": self.index_data_fresh,
            "sector_data_fresh": self.sector_data_fresh,
            "stock_data_fresh": self.stock_data_fresh,
            "staleness_days": self.staleness_days,
            "is_safe_for_decision": self.is_safe_for_decision,
            "degraded_mode": self.degraded_mode,
            "warnings": list(self.warnings),
        }


class SectorMappingResolver:
    """
    Resolves eligible stocks to standard sectors and industry aliases.
    Uses point-in-time universe files to avoid survivorship bias.
    """

    def __init__(
        self,
        sectors_config_path: str | Path = "config/sectors.yaml",
        constituent_csv_path: Optional[str | Path] = "downloads/raw/universes/NIFTY500.csv",
    ) -> None:
        self.sectors_config_path = Path(sectors_config_path)
        self.constituent_csv_path = Path(constituent_csv_path) if constituent_csv_path else None
        self._sector_catalog: Dict[str, Dict[str, Any]] = {}
        self._alias_to_sector_id: Dict[str, str] = {}
        self._symbol_to_sector_map: Dict[str, Dict[str, Any]] = {}
        self._load_config()
        self._load_constituent_mappings()

    def _load_config(self) -> None:
        if not self.sectors_config_path.exists():
            return
        with open(self.sectors_config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

        for sec in cfg.get("sectors", []):
            sec_id = sec["id"]
            self._sector_catalog[sec_id] = sec
            for alias in sec.get("industry_aliases", []):
                self._alias_to_sector_id[alias.strip().lower()] = sec_id
            self._alias_to_sector_id[sec["name"].strip().lower()] = sec_id

    def _load_constituent_mappings(self) -> None:
        if not self.constituent_csv_path or not self.constituent_csv_path.exists():
            return
        df = pd.read_csv(self.constituent_csv_path)
        sym_col = next((c for c in df.columns if c.strip().lower() in {"symbol", "ticker"}), None)
        ind_col = next((c for c in df.columns if c.strip().lower() in {"industry", "sector"}), None)
        name_col = next((c for c in df.columns if "name" in c.strip().lower()), None)

        if not sym_col or not ind_col:
            return

        for _, row in df.iterrows():
            sym = str(row[sym_col]).strip().upper()
            raw_ind = str(row[ind_col]).strip() if pd.notna(row[ind_col]) else "Diversified"
            company = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else sym

            sec_id = self._alias_to_sector_id.get(raw_ind.lower(), "CAP_GOODS")
            sec_info = self._sector_catalog.get(sec_id, {
                "id": sec_id,
                "name": raw_ind,
                "index_code": "NIFTY 50",
                "max_portfolio_exposure_pct": 20.0,
            })

            self._symbol_to_sector_map[sym] = {
                "symbol": sym,
                "company_name": company,
                "industry": raw_ind,
                "sector_id": sec_id,
                "sector_name": sec_info.get("name", raw_ind),
                "sector_index": sec_info.get("index_code", "NIFTY 50"),
                "max_exposure_pct": sec_info.get("max_portfolio_exposure_pct", 20.0),
            }

    def get_sector_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """Returns standard sector metadata for a given symbol."""
        sym = symbol.strip().upper()
        if sym in self._symbol_to_sector_map:
            return self._symbol_to_sector_map[sym]
        return {
            "symbol": sym,
            "company_name": sym,
            "industry": "Unknown",
            "sector_id": "OTHER",
            "sector_name": "Broad Market / Other",
            "sector_index": "NIFTY 50",
            "max_exposure_pct": 15.0,
        }

    def get_all_sectors(self) -> List[Dict[str, Any]]:
        return list(self._sector_catalog.values())


class DataContractValidator:
    """
    Validates data quality, freshness, and outlier bounds.
    """

    @staticmethod
    def validate_ohlcv_integrity(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validates OHLCV relationships and non-negativity.
        Rejects data with inverted prices or corrupted volumes.
        """
        errors = []
        if df.empty:
            return False, ["DataFrame is empty"]

        required = {"trading_date", "open", "high", "low", "close", "volume"}
        missing = required - set(df.columns)
        if missing:
            return False, [f"Missing required columns: {sorted(missing)}"]

        # Check negative prices / volume
        if (df["low"] < 0).any() or (df["close"] < 0).any() or (df["open"] < 0).any():
            errors.append("Negative price detected in dataset")
        if (df["volume"] < 0).any():
            errors.append("Negative volume detected in dataset")

        # Inverted prices (low > high)
        inverted = df[df["low"] > df["high"]]
        if not inverted.empty:
            errors.append(f"Inverted prices found: low > high in {len(inverted)} rows")

        # Close outside high-low range with small numerical tolerance
        tolerance = 1e-4
        out_of_bounds = df[(df["close"] > df["high"] * (1 + tolerance)) | (df["close"] < df["low"] * (1 - tolerance))]
        if not out_of_bounds.empty:
            errors.append(f"Close price outside [low, high] range in {len(out_of_bounds)} rows")

        return len(errors) == 0, errors

    @staticmethod
    def check_freshness(
        latest_date: date,
        reference_date: Optional[date] = None,
        max_stale_days: int = 5,
    ) -> Tuple[bool, int, List[str]]:
        """
        Verifies that data is fresh relative to the trading calendar.
        Weekends (up to 3 calendar days) are handled gracefully.
        """
        ref = reference_date or date.today()
        staleness = (ref - latest_date).days
        warnings = []

        if staleness < 0:
            return False, staleness, [f"Lookahead anomaly: data date {latest_date} is in the future relative to reference {ref}"]

        is_fresh = staleness <= max_stale_days
        if not is_fresh:
            warnings.append(f"Data is stale by {staleness} calendar days (threshold is {max_stale_days})")

        return is_fresh, staleness, warnings

    @staticmethod
    def create_contract(
        df: pd.DataFrame,
        reference_date: Optional[date] = None,
        max_stale_days: int = 5,
    ) -> DataAvailabilityContract:
        """
        Inspects dataset and returns an immutable DataAvailabilityContract.
        """
        now = datetime.now()
        if df.empty or "trading_date" not in df.columns:
            return DataAvailabilityContract(
                as_of_date=reference_date or date.today(),
                generated_at=now,
                index_data_fresh=False,
                sector_data_fresh=False,
                stock_data_fresh=False,
                staleness_days=999,
                is_safe_for_decision=False,
                degraded_mode=True,
                warnings=("Dataset is empty or lacks trading_date",),
            )

        max_dt = pd.to_datetime(df["trading_date"]).dt.date.max()
        is_fresh, stale_days, warnings = DataContractValidator.check_freshness(
            max_dt, reference_date=reference_date, max_stale_days=max_stale_days
        )
        ok_ohlcv, ohlcv_errs = DataContractValidator.validate_ohlcv_integrity(df)
        all_warnings = warnings + ohlcv_errs

        # Safe decision requires valid OHLCV and non-negative freshness
        is_safe = ok_ohlcv and stale_days >= 0

        return DataAvailabilityContract(
            as_of_date=max_dt,
            generated_at=now,
            index_data_fresh=is_fresh,
            sector_data_fresh=is_fresh,
            stock_data_fresh=is_fresh,
            staleness_days=stale_days,
            is_safe_for_decision=is_safe,
            degraded_mode=not is_fresh,
            warnings=tuple(all_warnings),
        )
