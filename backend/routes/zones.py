"""
AI Trading Operating System (AI-TOS)
Demand & Supply Zone Routes: GTF Scanning and Multi-Timeframe Matrix.
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, HTTPException, Query
from backend.schemas import MTFMatrixResponse, WatchlistRecommendationDTO, ZoneScanResponse
from backend.services.zone_service import ZoneService

router = APIRouter(prefix="/api/zones", tags=["Demand & Supply Zones"])


@router.get("/scan", response_model=ZoneScanResponse)
def get_zone_scan(force_refresh: bool = Query(default=False)):
    """
    Executes or returns cached pure institutional Demand & Supply scan across universe:
    Returns Actionable (At Demand), Priority Watchlist (Approaching Demand), Best Aligned (Grade A+), and Avoid Traps.
    """
    zs = ZoneService.get_instance()
    return zs.scan_universe(force_refresh=force_refresh)


@router.get("/best-watchlist", response_model=List[WatchlistRecommendationDTO])
def get_curated_watchlist():
    """
    Returns curated Top 15 Best Stocks to add to watchlist with deep institutional ranking:
    Approaching demand (< 3%), high R:R, wholesale curve location, and Grade A+/A alignment.
    """
    zs = ZoneService.get_instance()
    return zs.get_curated_watchlist()


@router.get("/mtf/{symbol}", response_model=MTFMatrixResponse)
def get_mtf_matrix(symbol: str):
    """
    Returns complete 5-timeframe dynamic matrix (Yearly, Half-Yearly, Quarterly, Monthly, Daily)
    with nested super-zones and institutional alignment conviction.
    """
    zs = ZoneService.get_instance()
    matrix = zs.get_mtf_matrix(symbol)
    if not matrix:
        raise HTTPException(status_code=404, detail=f"No MTF matrix available for symbol '{symbol}'")
    return matrix
