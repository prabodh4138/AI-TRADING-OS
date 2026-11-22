"""
Unit tests for Fundamental Analysis Engine, News Sentiment Engine,
and 360-Degree Stock Thesis Engine.
"""

from datetime import date, timedelta
import pandas as pd
import pytest

from analytics.fundamental_engine import (
    FundamentalAnalysisEngine,
    FundamentalQualityTier,
)
from analytics.stock_thesis_engine import StockThesisEngine
from data_engine.fundamental_data import (
    CompanyFundamentals,
    FundamentalDataProvider,
)
from data_engine.news_engine import NewsEngine, NewsItem
from scanner.gtf_scanner import GTFTradeScanner


@pytest.fixture
def sample_dbr_data():
    rows = []
    base_date = date(2026, 1, 1)

    # Drop
    rows.append({"trading_date": base_date + timedelta(days=0), "open": 105.0, "high": 106.0, "low": 98.0, "close": 99.0, "volume": 10000})
    rows.append({"trading_date": base_date + timedelta(days=1), "open": 99.0, "high": 100.0, "low": 92.0, "close": 93.0, "volume": 12000})
    # Base
    rows.append({"trading_date": base_date + timedelta(days=2), "open": 92.5, "high": 93.0, "low": 90.0, "close": 92.2, "volume": 8000})
    rows.append({"trading_date": base_date + timedelta(days=3), "open": 92.2, "high": 93.5, "low": 90.5, "close": 92.8, "volume": 7500})
    # Rally
    rows.append({"trading_date": base_date + timedelta(days=4), "open": 93.0, "high": 102.0, "low": 92.5, "close": 101.5, "volume": 35000})
    # Pullback to proximal line
    rows.append({"trading_date": base_date + timedelta(days=5), "open": 101.5, "high": 105.0, "low": 101.0, "close": 104.0, "volume": 20000})
    rows.append({"trading_date": base_date + timedelta(days=6), "open": 103.5, "high": 104.0, "low": 98.0, "close": 99.0, "volume": 15000})
    rows.append({"trading_date": base_date + timedelta(days=7), "open": 98.5, "high": 99.0, "low": 93.0, "close": 93.2, "volume": 18000})

    df = pd.DataFrame(rows)
    df["symbol"] = "RELIANCE"
    return df


def test_fundamental_data_provider_curated_and_synthetic():
    provider = FundamentalDataProvider()

    # Curated leader
    rel = provider.get_fundamentals("RELIANCE")
    assert rel.symbol == "RELIANCE"
    assert rel.market_cap_category == "LARGE_CAP"
    assert rel.pe_ratio > 0
    assert rel.roe_pct > 0
    assert rel.total_institutional_holding_pct > 20.0
    assert rel.institutional_trend in {"STRONG_ACCUMULATION", "MILD_ACCUMULATION", "NEUTRAL", "DISTRIBUTION"}

    # Synthetic fallback for arbitrary symbol
    syn = provider.get_fundamentals("UNKNOWN_TICKER_XYZ")
    assert syn.symbol == "UNKNOWN_TICKER_XYZ"
    assert syn.pe_ratio > 0
    assert syn.piotroski_f_score >= 0


def test_fundamental_analysis_engine_scoring():
    engine = FundamentalAnalysisEngine()
    rep = engine.analyze_stock("TCS")

    assert rep.symbol == "TCS"
    assert rep.company_name == "Tata Consultancy Services Ltd"
    assert 0.0 <= rep.overall_fundamental_score <= 100.0
    assert 0.0 <= rep.valuation_score <= 25.0
    assert 0.0 <= rep.profitability_score <= 25.0
    assert 0.0 <= rep.solvency_score <= 25.0
    assert 0.0 <= rep.growth_institutional_score <= 25.0
    assert rep.quality_tier == FundamentalQualityTier.INSTITUTIONAL_COMPOUNDER
    assert len(rep.strengths) >= 1
    assert len(rep.red_flags) >= 1


def test_news_engine_sentiment_and_catalysts():
    engine = NewsEngine(request_timeout_seconds=0.1)

    # 1. Lexicon sentiment classification
    pos_text = "Company reports record profit surges 25% and bags order of Rs 5000 Cr"
    label, score, cat = engine._analyze_text_sentiment(pos_text)
    assert label == "POSITIVE"
    assert score > 0.5
    assert cat in {"EARNINGS", "ORDER_WIN"}

    neg_text = "SEBI notice issued and penalty imposed after profit slumps"
    label_neg, score_neg, cat_neg = engine._analyze_text_sentiment(neg_text)
    assert label_neg == "NEGATIVE"
    assert score_neg < -0.5
    assert cat_neg in {"REGULATORY", "EARNINGS"}

    # 2. Stock news profile retrieval (offline fallback verification)
    prof = engine.fetch_stock_news("RELIANCE")
    assert prof.symbol == "RELIANCE"
    assert len(prof.news_items) >= 1
    assert -1.0 <= prof.aggregate_sentiment_score <= 1.0
    assert prof.sentiment_badge in {"BULLISH_CATALYST", "NEUTRAL_BALANCED", "BEARISH_RISK"}
    assert len(prof.top_catalysts) >= 1


def test_stock_thesis_engine_comprehensive(sample_dbr_data):
    thesis_engine = StockThesisEngine()
    thesis = thesis_engine.generate_stock_thesis("RELIANCE", price_history=sample_dbr_data)

    assert thesis.symbol == "RELIANCE"
    assert thesis.company_name == "Reliance Industries Limited"
    assert 0.0 <= thesis.conviction_score_360 <= 100.0
    assert thesis.executive_verdict in {
        "STRONG_CONVICTION_BUY",
        "PULLBACK_ACCUMULATE",
        "HOLD_AND_TRAIL",
        "NEUTRAL_WATCHLIST",
        "AVOID_DO_NOT_BUY",
    }
    assert 0.0 <= thesis.technical_gtf_score <= 35.0
    assert 0.0 <= thesis.ml_forecast_score <= 25.0
    assert 0.0 <= thesis.fundamental_quality_score <= 25.0
    assert 0.0 <= thesis.news_sentiment_score <= 15.0

    # Verify Actionable Notes
    assert len(thesis.why_to_buy) >= 3
    assert len(thesis.why_to_hold) >= 2
    assert len(thesis.why_not_to_buy) >= 2

    # Verify Terminal report formatting doesn't fail
    report_text = thesis.format_terminal_report()
    assert "AI-TOS 360-DEGREE INSTITUTIONAL STOCK THESIS" in report_text
    assert "EXECUTIVE VERDICT" in report_text
    assert "[+] WHY TO BUY" in report_text
    assert "[=] WHY TO HOLD" in report_text
    assert "[!] WHY NOT TO BUY" in report_text


def test_gtf_scanner_integration_with_fundamentals(sample_dbr_data):
    scanner = GTFTradeScanner(min_odds_score=5.0, min_ml_probability=0.50)
    res = scanner.scan_universe(sample_dbr_data)

    assert res.total_symbols_scanned == 1
    assert len(res.best_aligned_candidates) >= 1 or len(res.actionable_candidates) >= 1 or len(res.watchlist_candidates) >= 1

    cand = (res.actionable_candidates or res.best_aligned_candidates or res.watchlist_candidates)[0]
    assert hasattr(cand, "fundamental_tier")
    assert hasattr(cand, "fundamental_score")
    assert hasattr(cand, "news_sentiment_badge")
    assert hasattr(cand, "conviction_score_360")
    assert cand.conviction_score_360 > 0.0

    # Verify formatted report contains 360 section
    rep_text = res.format_terminal_report()
    assert "360-DEGREE INSTITUTIONAL CONVICTION" in rep_text
    assert "[+] WHY TO BUY" in rep_text
