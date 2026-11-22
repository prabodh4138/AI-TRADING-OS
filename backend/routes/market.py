"""
AI Trading Operating System (AI-TOS)
Market Data Routes.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.schemas import (
    CandleHistoryResponse,
    DualSourceCheckDTO,
    MarketStatusResponse,
    MarketSyncResponse,
)
from backend.services.data_service import DataService
from backend.services.reconciliation_service import ReconciliationService
from backend.services.websocket_manager import ws_manager
from backend.services.zone_service import ZoneService

router = APIRouter(prefix="/api/market", tags=["Market Data"])


@router.get("/status", response_model=MarketStatusResponse)
def get_market_status():
    """Returns DB status, health score, session date, and NIFTY 50 macro posture."""
    ds = DataService.get_instance()
    return ds.get_market_status()


@router.get("/symbols", response_model=List[str])
def get_symbols():
    """Returns list of active equities in the local database/dataset."""
    ds = DataService.get_instance()
    return ds.get_symbols()


@router.post("/sync-latest", response_model=MarketSyncResponse)
async def sync_latest_market_data(target_date: Optional[str] = Query(default=None, description="Optional target date YYYY-MM-DD")):
    """
    Auto-downloads latest session data from NSE & Yahoo Finance, cross-verifies closing quotes,
    and reconciles clean data into PostgreSQL and the master dataset.
    """
    rec_service = ReconciliationService.get_instance()
    sync_res = rec_service.sync_latest_market_data(target_date=target_date)

    await ws_manager.broadcast({
        "event": "MARKET_DATA_SYNCED",
        "latest_trading_date": sync_res.latest_trading_date,
        "total_bars": sync_res.total_bars_synced,
    })
    return sync_res


@router.get("/verification-audit", response_model=List[DualSourceCheckDTO])
def get_dual_source_verification():
    """
    Returns dual-source price verification audit between NSE Bhavcopy and Yahoo Finance.
    Mathematically verifies zero-drift price correctness and corporate actions.
    """
    rec_service = ReconciliationService.get_instance()
    return rec_service.get_dual_source_audit()


@router.get("/bars/{symbol}", response_model=CandleHistoryResponse)
def get_symbol_bars(
    symbol: str,
    timeframe: str = Query(default="1D", description="Timeframe aggregation: 1D, 1W, 1M, 1Q"),
):
    """Returns historical OHLCV bars with technical indicators and institutional zone overlays."""
    ds = DataService.get_instance()
    zs = ZoneService.get_instance()

    raw_tf = getattr(timeframe, "default", timeframe)
    tf = str(raw_tf).upper().strip() if isinstance(raw_tf, str) else "1D"
    if tf not in {"1D", "1W", "1M", "1Q"}:
        tf = "1D"

    bars, cur_change, high_52, low_52 = ds.get_symbol_bars(symbol, timeframe=tf)
    if not bars:
        raise HTTPException(status_code=404, detail=f"No data available for symbol '{symbol}'")

    zones = zs.get_symbol_zones(symbol)
    cur_px = bars[-1].close if bars else 0.0

    return CandleHistoryResponse(
        symbol=symbol.upper(),
        timeframe=tf,
        current_price=cur_px,
        current_change_pct=cur_change,
        high_52w=high_52,
        low_52w=low_52,
        bars=bars,
        zones=zones,
    )
