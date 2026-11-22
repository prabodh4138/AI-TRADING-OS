"""
AI Trading Operating System
Module: data_engine/historical_data.py

Multi-Year Historical Market Data Generator & Ingestion Engine.
Generates and populates 1 to 2 years of daily OHLCV bars for:
- Indices: NIFTY 50, NIFTY BANK, NIFTY IT, NIFTY AUTO, NIFTY FMCG
- Major NIFTY 500 constituents across sectors:
  RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK, MARUTI, LT, SUNPHARMA,
  TATAMOTORS, BHARTIARTL, ITC, KOTAKBANK, AXISBANK, TITAN, BAJFINANCE.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sys
from typing import Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import pandas as pd
from sqlalchemy import text

from database.connection import database as db_mgr
from database.base import Base
import database.models as _models


# Representative constituent stocks and initial prices
STOCK_CATALOG = {
    "NIFTY 50": {"sector": "BROAD", "start": 21500.0, "drift": 0.0006, "vol": 0.009},
    "NIFTY BANK": {"sector": "BANKING", "start": 48000.0, "drift": 0.0007, "vol": 0.012},
    "NIFTY IT": {"sector": "IT", "start": 35000.0, "drift": 0.0008, "vol": 0.013},
    "RELIANCE": {"sector": "ENERGY", "start": 2600.0, "drift": 0.0005, "vol": 0.012},
    "TCS": {"sector": "IT", "start": 3600.0, "drift": 0.0007, "vol": 0.011},
    "INFY": {"sector": "IT", "start": 1500.0, "drift": 0.0008, "vol": 0.014},
    "HDFCBANK": {"sector": "FIN_SERVICE", "start": 1550.0, "drift": 0.0006, "vol": 0.011},
    "ICICIBANK": {"sector": "FIN_SERVICE", "start": 1050.0, "drift": 0.0009, "vol": 0.013},
    "MARUTI": {"sector": "AUTO", "start": 10500.0, "drift": 0.0008, "vol": 0.013},
    "LT": {"sector": "CAP_GOODS", "start": 3400.0, "drift": 0.0007, "vol": 0.013},
    "SUNPHARMA": {"sector": "HEALTHCARE", "start": 1400.0, "drift": 0.0009, "vol": 0.011},
    "TATAMOTORS": {"sector": "AUTO", "start": 850.0, "drift": 0.0010, "vol": 0.018},
    "BHARTIARTL": {"sector": "TELECOM", "start": 1200.0, "drift": 0.0011, "vol": 0.012},
    "ITC": {"sector": "FMCG", "start": 420.0, "drift": 0.0004, "vol": 0.009},
    "KOTAKBANK": {"sector": "FIN_SERVICE", "start": 1800.0, "drift": 0.0005, "vol": 0.012},
    "AXISBANK": {"sector": "FIN_SERVICE", "start": 1100.0, "drift": 0.0008, "vol": 0.014},
    "TITAN": {"sector": "CONSUMER_SVC", "start": 3400.0, "drift": 0.0006, "vol": 0.014},
    "BAJFINANCE": {"sector": "FIN_SERVICE", "start": 7000.0, "drift": 0.0006, "vol": 0.016},
}


def generate_historical_market_dataset(
    trading_days: int = 252,  # 1 full year of daily sessions
    end_date: Optional[date] = None,
    output_path: str | Path = "downloads/raw/historical_nifty500_dataset.csv",
) -> pd.DataFrame:
    """
    Generates a realistic 1-year daily market dataset following Geometric Brownian Motion
    with realistic volume, delivery percentages, and intermarket correlation.
    """
    np.random.seed(42)
    end = end_date or date(2026, 9, 25)

    # Generate business trading days (excluding weekends)
    dates: List[date] = []
    curr = end
    while len(dates) < trading_days:
        if curr.weekday() < 5:  # Monday to Friday
            dates.append(curr)
        curr -= timedelta(days=1)
    dates.reverse()

    all_rows = []

    # Common market factor (broad index shock)
    market_shocks = np.random.normal(0, 0.008, size=trading_days)

    for symbol, meta in STOCK_CATALOG.items():
        base_price = meta["start"]
        drift = meta["drift"]
        vol = meta["vol"]
        prices = [base_price]

        for t in range(1, trading_days):
            # Idiosyncratic shock + beta to market factor
            beta = 1.0 if "NIFTY" in symbol else 1.15
            shock = beta * market_shocks[t] + np.random.normal(0, vol * 0.7)
            ret = drift + shock
            new_p = max(5.0, prices[-1] * (1.0 + ret))
            prices.append(new_p)

        for i, dt in enumerate(dates):
            close_p = round(prices[i], 2)
            prev_p = round(prices[i - 1], 2) if i > 0 else round(close_p * 0.995, 2)
            open_p = round(prev_p * (1.0 + np.random.normal(0, 0.003)), 2)
            high_p = round(max(open_p, close_p) * (1.0 + abs(np.random.normal(0, 0.006))), 2)
            low_p = round(min(open_p, close_p) * (1.0 - abs(np.random.normal(0, 0.006))), 2)

            # Volume and turnover
            vol_base = 500000 if "NIFTY" not in symbol else 2000000
            vol_noisy = int(vol_base * np.random.uniform(0.6, 1.8))
            turnover_lacs = round((close_p * vol_noisy) / 100000.0, 2)
            deliv_pct = round(float(np.random.uniform(35.0, 70.0)), 2)
            deliv_qty = int(vol_noisy * (deliv_pct / 100.0))

            all_rows.append({
                "symbol": symbol,
                "series": "EQ" if "NIFTY" not in symbol else "IN",
                "trading_date": dt,
                "open": open_p,
                "high": high_p,
                "low": low_p,
                "close": close_p,
                "last": close_p,
                "prevclose": prev_p,
                "volume": vol_noisy,
                "turnover": turnover_lacs,
                "trade_count": int(vol_noisy / 25),
                "delivery_volume": deliv_qty,
                "delivery_percent": deliv_pct,
                "vwap": round((open_p + high_p + low_p + close_p) / 4, 2),
            })

    df = pd.DataFrame(all_rows)
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)
    print(f"Generated {len(df):,} rows across {df['symbol'].nunique()} symbols from {dates[0]} to {dates[-1]}.")
    print(f"Saved to: {p}")
    return df


def populate_postgresql_historical_data(df: pd.DataFrame) -> None:
    """
    Creates tables if not existing and loads historical symbols & market data into PostgreSQL.
    """
    Base.metadata.create_all(bind=db_mgr.engine)

    with db_mgr.engine.connect() as conn:
        print("Populating PostgreSQL symbols...")
        symbol_id_map = {}
        for sym in df["symbol"].unique():
            meta = STOCK_CATALOG.get(sym, {"sector": "OTHER"})
            conn.execute(
                text("""
                    INSERT INTO symbol (symbol_id, symbol_code, symbol_name, exchange, instrument_type, sector, is_fno, lot_size, tick_size, is_active, created_at, updated_at)
                    VALUES (gen_random_uuid(), :code, :name, 'NSE', 'EQUITY', :sector, false, 1, 0.05, true, NOW(), NOW())
                    ON CONFLICT (symbol_code) DO UPDATE SET sector = EXCLUDED.sector, updated_at = NOW();
                """),
                {"code": sym, "name": f"{sym} Ltd", "sector": meta["sector"]},
            )
            # Retrieve symbol_id
            sid = conn.execute(text("SELECT symbol_id FROM symbol WHERE symbol_code = :c"), {"c": sym}).scalar()
            symbol_id_map[sym] = sid
        conn.commit()

        print(f"Total symbols configured: {len(symbol_id_map)}")
        print("Populating PostgreSQL historical market_data...")

        # Insert market data records
        for _, row in df.iterrows():
            sym = row["symbol"]
            sid = symbol_id_map.get(sym)
            if not sid:
                continue
            conn.execute(
                text("""
                    INSERT INTO market_data (
                        market_data_id, symbol_id, trading_date,
                        open_price, high_price, low_price, close_price, adjusted_close,
                        volume, delivery_volume, delivery_percent, trade_count,
                        is_active, created_at, updated_at
                    ) VALUES (
                        gen_random_uuid(), :sid, :tdate,
                        :open_p, :high_p, :low_p, :close_p, :close_p,
                        :vol, :deliv_vol, :deliv_pct, :trades,
                        true, NOW(), NOW()
                    )
                    ON CONFLICT (symbol_id, trading_date) DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        volume = EXCLUDED.volume,
                        updated_at = NOW();
                """),
                {
                    "sid": sid,
                    "tdate": row["trading_date"],
                    "open_p": row["open"],
                    "high_p": row["high"],
                    "low_p": row["low"],
                    "close_p": row["close"],
                    "vol": row["volume"],
                    "deliv_vol": row["delivery_volume"],
                    "deliv_pct": row["delivery_percent"],
                    "trades": row["trade_count"],
                },
            )
        conn.commit()

        total_syms = conn.execute(text("SELECT count(*) FROM symbol")).scalar()
        total_md = conn.execute(text("SELECT count(*) FROM market_data")).scalar()
        dates = conn.execute(text("SELECT min(trading_date), max(trading_date), count(distinct trading_date) FROM market_data")).fetchone()
        print(f"SUCCESS: PostgreSQL populated with {total_syms} symbols and {total_md:,} historical market data bars.")
        print(f"Date range: {dates[0]} to {dates[1]} ({dates[2]} trading sessions / 1 year).")


if __name__ == "__main__":
    df = generate_historical_market_dataset(trading_days=252)
    populate_postgresql_historical_data(df)
