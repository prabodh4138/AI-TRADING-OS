"""Canonical CSV normalization for common NSE and simple OHLCV formats."""
from __future__ import annotations
from pathlib import Path
import re
import pandas as pd

ALIASES = {
    "symbol": ["symbol", "SYMBOL"], "series": ["series", "SERIES"],
    "trading_date": ["trading_date", "date", "DATE", "DATE1"],
    "open": ["open", "OPEN", "OPEN_PRICE"], "high": ["high", "HIGH", "HIGH_PRICE"],
    "low": ["low", "LOW", "LOW_PRICE"], "close": ["close", "CLOSE", "CLOSE_PRICE"],
    "last": ["last", "LAST", "LAST_PRICE"], "prevclose": ["prevclose", "PREV_CLOSE"],
    "volume": ["volume", "VOLUME", "TTL_TRD_QNTY"], "turnover": ["turnover", "TURNOVER_LACS", "TOTTRDVAL"],
    "trade_count": ["trade_count", "NO_OF_TRADES"], "delivery_volume": ["delivery_volume", "DELIV_QTY"],
    "delivery_percent": ["delivery_percent", "DELIV_PER"], "vwap": ["vwap", "AVG_PRICE"],
}

def _norm(c: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_")

def read_market_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    df = pd.read_csv(path)
    lookup = {_norm(c): c for c in df.columns}
    out = pd.DataFrame()
    for target, candidates in ALIASES.items():
        source = next((lookup[_norm(c)] for c in candidates if _norm(c) in lookup), None)
        if source is not None: out[target] = df[source]
    required = ["symbol","trading_date","open","high","low","close","volume"]
    missing = [c for c in required if c not in out.columns]
    if missing: raise ValueError(f"Unsupported market CSV; missing {missing}")
    out["symbol"] = out["symbol"].astype(str).str.strip().str.upper()
    out["trading_date"] = pd.to_datetime(out["trading_date"], format="mixed", errors="coerce").dt.date
    for c in ["open","high","low","close","last","prevclose","volume","turnover","trade_count","delivery_volume","delivery_percent","vwap"]:
        if c in out: out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=required).drop_duplicates(["symbol","trading_date"]).sort_values(["symbol","trading_date"]).reset_index(drop=True)
    if (out[["high","low"]].lt(0)).any().any() or (out["volume"] < 0).any(): raise ValueError("Invalid negative market values")
    return out
