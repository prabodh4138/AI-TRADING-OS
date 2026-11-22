"""Concrete market-data loader; idempotent by symbol/date."""
from __future__ import annotations
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session
from data_engine.database.base_loader import BaseLoader
from database.models.market_data import MarketData
from database.models.symbol import Symbol

class MarketDataLoader(BaseLoader):
    REQUIRED = ("symbol", "trading_date", "open", "high", "low", "close", "volume")
    def validate(self, dataframe: pd.DataFrame) -> None:
        missing = [c for c in self.REQUIRED if c not in dataframe.columns]
        if missing: raise ValueError(f"Missing required columns: {missing}")
        if dataframe.empty: raise ValueError("Market data is empty")
        if dataframe[["open","high","low","close","volume"]].isna().any().any(): raise ValueError("OHLCV contains null values")
    def load(self, dataframe: pd.DataFrame) -> int:
        self.validate(dataframe)
        inserted = 0
        for batch in self.get_batches(dataframe):
            symbols = {s: None for s in batch["symbol"].astype(str).str.strip().unique()}
            rows = self.session.scalars(select(Symbol).where(Symbol.symbol_code.in_(symbols))).all()
            symbols = {x.symbol_code: x.symbol_id for x in rows}
            for row in batch.itertuples(index=False):
                symbol_id = symbols.get(str(row.symbol).strip())
                if symbol_id is None: continue
                exists = self.session.scalar(select(MarketData.market_data_id).where(MarketData.symbol_id==symbol_id, MarketData.trading_date==row.trading_date))
                if exists: continue
                self.session.add(MarketData(symbol_id=symbol_id, trading_date=row.trading_date, open_price=row.open, high_price=row.high, low_price=row.low, close_price=row.close, adjusted_close=getattr(row,"adjusted_close",None), volume=int(row.volume), delivery_volume=getattr(row,"delivery_volume",None), delivery_percent=getattr(row,"delivery_percent",None), turnover=getattr(row,"turnover",None), vwap=getattr(row,"vwap",None), trade_count=getattr(row,"trade_count",None)))
                inserted += 1
            self.session.flush()
        return inserted
