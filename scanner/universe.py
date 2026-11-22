"""Versioned local universe loader; never invents constituent membership."""
from __future__ import annotations
from pathlib import Path
import pandas as pd

def load_symbols(path: str|Path) -> set[str]:
    p=Path(path)
    if not p.exists(): raise FileNotFoundError(f"Universe file not found: {p}")
    df=pd.read_csv(p)
    col=next((c for c in df.columns if str(c).strip().lower() in {"symbol","symbols","ticker"}),None)
    if col is None: raise ValueError("Universe file must contain a symbol column")
    return set(df[col].dropna().astype(str).str.strip().str.upper())

def filter_universe(data: pd.DataFrame, symbols: set[str]) -> pd.DataFrame:
    if "symbol" not in data: raise ValueError("Market data requires symbol")
    return data[data["symbol"].astype(str).str.upper().isin(symbols)].copy()
