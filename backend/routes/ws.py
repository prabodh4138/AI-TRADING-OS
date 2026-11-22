"""
AI Trading Operating System (AI-TOS)
Real-Time WebSocket Router.
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.data_service import DataService
from backend.services.portfolio_service import PortfolioService
from backend.services.websocket_manager import ws_manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # On connection, send initial status and portfolio summary
        ds = DataService.get_instance()
        ps = PortfolioService.get_instance()

        m_status = ds.get_market_status()
        p_summary = ps.get_summary()

        await ws_manager.send_personal({
            "event": "INITIAL_SNAPSHOT",
            "market": m_status.model_dump(),
            "portfolio": p_summary.model_dump(),
        }, websocket)

        while True:
            # Keep connection open, handle incoming ping/commands
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            elif data == "refresh":
                p_summary = ps.get_summary()
                await ws_manager.send_personal({
                    "event": "PORTFOLIO_REFRESH",
                    "portfolio": p_summary.model_dump(),
                }, websocket)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
