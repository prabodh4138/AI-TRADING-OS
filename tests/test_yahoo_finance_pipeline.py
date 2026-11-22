"""
Unit Tests for Yahoo Finance Ingestion, Symbol Mapping, and Broker Reconciliation Pipeline.
"""

from datetime import date
import pandas as pd
import pytest

from data_engine.yahoo_finance_pipeline import (
    YahooFinanceDataPipeline,
    YahooSymbolMapper,
    YahooSyncSummary,
)


class TestYahooSymbolMapper:
    def test_equity_forward_mapping(self):
        assert YahooSymbolMapper.to_yahoo_ticker("RELIANCE") == "RELIANCE.NS"
        assert YahooSymbolMapper.to_yahoo_ticker("TCS") == "TCS.NS"
        assert YahooSymbolMapper.to_yahoo_ticker("INFY") == "INFY.NS"
        assert YahooSymbolMapper.to_yahoo_ticker("HDFCBANK") == "HDFCBANK.NS"

    def test_special_equity_mapping(self):
        assert YahooSymbolMapper.to_yahoo_ticker("M&M") == "M&M.NS"
        assert YahooSymbolMapper.to_yahoo_ticker("BAJAJ-AUTO") == "BAJAJ-AUTO.NS"
        assert YahooSymbolMapper.to_yahoo_ticker("MCDOWELL-N") == "UNITDSPR.NS"

    def test_index_forward_mapping(self):
        assert YahooSymbolMapper.to_yahoo_ticker("NIFTY 50") == "^NSEI"
        assert YahooSymbolMapper.to_yahoo_ticker("NIFTY") == "^NSEI"
        assert YahooSymbolMapper.to_yahoo_ticker("BANK NIFTY") == "^NSEBANK"
        assert YahooSymbolMapper.to_yahoo_ticker("NIFTY BANK") == "^NSEBANK"
        assert YahooSymbolMapper.to_yahoo_ticker("NIFTY IT") == "^CNXIT"
        assert YahooSymbolMapper.to_yahoo_ticker("INDIA VIX") == "^INDIAVIX"

    def test_reverse_mapping(self):
        assert YahooSymbolMapper.to_nse_symbol("RELIANCE.NS") == "RELIANCE"
        assert YahooSymbolMapper.to_nse_symbol("TCS.NS") == "TCS"
        assert YahooSymbolMapper.to_nse_symbol("^NSEI") == "NIFTY 50"
        assert YahooSymbolMapper.to_nse_symbol("^NSEBANK") == "BANK NIFTY"
        assert YahooSymbolMapper.to_nse_symbol("UNITDSPR.NS") == "MCDOWELL-N"

    def test_already_formatted_ticker_handling(self):
        assert YahooSymbolMapper.to_yahoo_ticker("RELIANCE.NS") == "RELIANCE.NS"
        assert YahooSymbolMapper.to_yahoo_ticker("^NSEI") == "^NSEI"


class TestYahooFinanceDataPipeline:
    def test_fetch_symbol_ohlcv_equity(self):
        pipeline = YahooFinanceDataPipeline()
        df = pipeline.fetch_symbol_ohlcv("RELIANCE", period="5d")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            expected_cols = ["symbol", "series", "trading_date", "open", "high", "low", "close", "adjusted_close", "volume"]
            for col in expected_cols:
                assert col in df.columns
            assert df.iloc[-1]["symbol"] == "RELIANCE"
            assert df.iloc[-1]["series"] == "EQ"
            assert df.iloc[-1]["close"] > 0
            # Split-adjusted quote verification (post-bonus RELIANCE is around Rs. 1,000 - 1,500, NOT 2,700)
            assert df.iloc[-1]["close"] < 2000.0

    def test_fetch_symbol_ohlcv_index(self):
        pipeline = YahooFinanceDataPipeline()
        df = pipeline.fetch_symbol_ohlcv("NIFTY 50", period="5d")

        assert isinstance(df, pd.DataFrame)
        if not df.empty:
            assert df.iloc[-1]["symbol"] == "NIFTY 50"
            assert df.iloc[-1]["series"] == "IN"
            assert df.iloc[-1]["close"] > 10000.0

    def test_fetch_universe(self):
        pipeline = YahooFinanceDataPipeline()
        df, summary = pipeline.fetch_universe(
            symbols=["RELIANCE", "TCS"],
            period="5d",
            save_csv=False,
            sync_db=False,
        )

        assert isinstance(summary, YahooSyncSummary)
        assert summary.total_requested == 2
        if not df.empty:
            assert summary.successful_count >= 1
            assert summary.total_bars_fetched > 0
            assert "symbol" in df.columns
            assert "close" in df.columns

    def test_sync_empty_dataframe(self):
        pipeline = YahooFinanceDataPipeline()
        ingested = pipeline.sync_dataframe_to_database(pd.DataFrame())
        assert ingested == 0
