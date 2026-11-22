"""
AI Trading Operating System (AI-TOS)
Paper Trading Portfolio & Execution Routes.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from backend.schemas import (
    AutoTradeResultDTO,
    AutoTradeStatusDTO,
    ExecuteTradeRequest,
    GenericApiResponse,
    PortfolioSummaryDTO,
    PositionDTO,
    ResetPortfolioRequest,
)
from backend.services.portfolio_service import PortfolioService
from backend.services.websocket_manager import ws_manager

router = APIRouter(prefix="/api/portfolio", tags=["Paper Trading"])


@router.get("/summary", response_model=PortfolioSummaryDTO)
def get_portfolio_summary():
    """Returns active portfolio summary, equity curve, open positions, and closed trades."""
    ps = PortfolioService.get_instance()
    return ps.get_summary()


@router.post("/execute", response_model=PositionDTO)
async def execute_trade(req: ExecuteTradeRequest):
    """Executes a single approved trade plan into the paper trading ledger."""
    ps = PortfolioService.get_instance()
    pos = ps.execute_trade(req)
    if not pos:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to execute trade for {req.symbol}: Insufficient cash balance (Available: ₹{ps.manager.current_cash:,.2f}) or position already open."
        )

    # Broadcast trade execution via WebSocket
    await ws_manager.broadcast({
        "event": "TRADE_EXECUTED",
        "data": pos.model_dump(),
    })
    return pos


@router.post("/execute-batch", response_model=List[PositionDTO])
async def execute_batch(reqs: List[ExecuteTradeRequest]):
    """Executes batch of high-conviction trade plans into paper portfolio."""
    ps = PortfolioService.get_instance()
    new_pos = ps.execute_batch(reqs)

    if new_pos:
        await ws_manager.broadcast({
            "event": "BATCH_TRADES_EXECUTED",
            "count": len(new_pos),
        })
    return new_pos


@router.post("/reset", response_model=GenericApiResponse)
async def reset_portfolio(req: ResetPortfolioRequest):
    """Resets paper trading ledger to specified cash balance."""
    ps = PortfolioService.get_instance()
    ps.reset_portfolio(capital=req.capital)

    await ws_manager.broadcast({
        "event": "PORTFOLIO_RESET",
        "capital": req.capital,
    })
    return GenericApiResponse(
        success=True,
        message=f"Paper ledger reset successfully to Rs. {req.capital:,.2f}",
        data={"capital": req.capital},
    )


@router.get("/auto-trade/status", response_model=AutoTradeStatusDTO)
def get_auto_trade_status():
    """Returns status and parameters of automated paper trading engine."""
    ps = PortfolioService.get_instance()
    return ps.get_auto_trade_status()


@router.post("/auto-trade/toggle", response_model=AutoTradeStatusDTO)
async def toggle_auto_trading(enabled: Optional[bool] = None):
    """Enables or disables automated paper trading engine."""
    ps = PortfolioService.get_instance()
    is_on = ps.toggle_auto_trading(enabled)
    await ws_manager.broadcast({
        "event": "AUTO_TRADE_STATUS_CHANGED",
        "enabled": is_on,
    })
    return ps.get_auto_trade_status()


@router.post("/auto-trade/run", response_model=AutoTradeResultDTO)
async def run_auto_trade_cycle(max_trades: int = 5):
    """Executes an automated cycle of paper trade entries, trailing stops, and exits."""
    ps = PortfolioService.get_instance()
    result = ps.run_auto_trading(max_new_trades=max_trades)

    await ws_manager.broadcast({
        "event": "AUTO_TRADE_CYCLE_COMPLETED",
        "new_opened": result.new_positions_opened,
        "closed": result.positions_closed,
    })
    return result
