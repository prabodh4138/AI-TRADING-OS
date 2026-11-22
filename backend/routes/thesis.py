"""
AI Trading Operating System (AI-TOS)
Stock Thesis & 360-Degree Fundamental Intelligence Routes.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from backend.schemas import StockThesisDTO, Master123ResponseDTO, PullbackDiagnosisDTO
from backend.services.thesis_service import ThesisService

router = APIRouter(prefix="/api/thesis", tags=["Stock Thesis"])


@router.get("/pullback/{symbol}", response_model=PullbackDiagnosisDTO)
def get_pullback_diagnosis(symbol: str):
    """
    Returns 5-Condition Pullback Qualification and Pullback vs Reversal Classification:
    1. Price approaching 20/50 EMA or Support Zone
    2. Selling volume contraction (dry-up on down-days)
    3. RSI cooldown towards 50–65
    4. Bullish reversal candlestick (Hammer, Bullish Engulfing, Strong Bullish Close)
    5. Confirmation turn with improving volume
    Classifications: SHALLOW_PULLBACK, HEALTHY_PULLBACK, STRONG_PULLBACK, TREND_REVERSAL_BREAKDOWN
    """
    ts = ThesisService.get_instance()
    diag = ts.get_pullback_diagnosis(symbol)
    if not diag:
        raise HTTPException(status_code=404, detail=f"Pullback diagnosis not found for symbol '{symbol}'")
    return diag


@router.get("/master-123/{symbol}", response_model=Master123ResponseDTO)
def get_master_123_checklist(symbol: str):
    """
    Returns the comprehensive 123-point institutional qualification audit across 10 categories:
    Fundamental, Technical, Sector, Institutional, News, Global, Market, Volume, Risk, Execution.
    """
    ts = ThesisService.get_instance()
    result = ts.get_master_checklist(symbol)
    if not result:
        raise HTTPException(status_code=404, detail=f"123-Point checklist audit not found for symbol '{symbol}'")
    return result


@router.get("/{symbol}", response_model=StockThesisDTO)
def get_stock_thesis(symbol: str):
    """Returns 360-degree fundamental evaluation, Piotroski F-score, news sentiment, and why to buy/hold/avoid."""
    ts = ThesisService.get_instance()
    thesis = ts.get_thesis(symbol)
    if not thesis:
        raise HTTPException(status_code=404, detail=f"Stock thesis not found for symbol '{symbol}'")
    return thesis
