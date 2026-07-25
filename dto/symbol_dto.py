"""
AI Trading Operating System
Symbol DTO
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class SymbolCreateDTO:
    symbol_code: str
    symbol_name: str
    exchange: str
    instrument_type: str
    sector: str
    industry: str
    isin: str
    lot_size: int
    tick_size: float
    face_value: float
    listing_date: date | None = None
    is_fno: bool = False