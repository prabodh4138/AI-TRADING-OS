"""
AI Trading Operating System (AI-TOS)
Master FastAPI Application Entrypoint.
Specification Baseline: Master Final Consolidated System Specification v3.1
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.routes import market, pipeline, portfolio, thesis, ws, zones
from backend.services.data_service import DataService
from backend.services.portfolio_service import PortfolioService
from backend.services.reconciliation_service import ReconciliationService
from backend.services.websocket_manager import ws_manager
from backend.services.zone_service import ZoneService


async def background_market_sync_loop():
    """
    Continuous background synchronization loop:
    1. Immediately syncs latest market data from NSE + Yahoo Finance on startup.
    2. Broadcasts MARKET_DATA_UPDATED over WebSocket to update UI automatically.
    3. Periodically refreshes to ingest new trading sessions.
    """
    # Brief delay so FastAPI server is fully bound and ready to accept requests
    await asyncio.sleep(1.0)
    
    while True:
        try:
            print("⚡ [AUTO-SYNC] Ingesting latest trading sessions from NSE & Yahoo Finance...")
            rec = ReconciliationService.get_instance()
            res = await asyncio.to_thread(rec.sync_latest_market_data)
            print(f"⚡ [AUTO-SYNC] Complete! Latest Trading Date: {res.latest_trading_date} (Health: {res.data_health_score}%)")
            
            # Broadcast update event to all connected frontends
            await ws_manager.broadcast({
                "event": "MARKET_DATA_UPDATED",
                "latest_trading_date": res.latest_trading_date,
                "data_health_score": res.data_health_score,
                "total_bars": res.total_bars_synced,
            })

            # Run automated paper trading engine for recommended stocks & exits
            ps = PortfolioService.get_instance()
            if ps.auto_trading_enabled:
                print("⚡ [AUTO-TRADE] Evaluating positions for trailing exits and entering top recommendations...")
                auto_res = await asyncio.to_thread(ps.run_auto_trading, max_new_trades=3)
                print(f"⚡ [AUTO-TRADE] Cycle complete: {auto_res.new_positions_opened} new entered, {auto_res.positions_closed} closed. Active: {len(auto_res.open_positions)}")
                
                await ws_manager.broadcast({
                    "event": "AUTO_TRADE_CYCLE_COMPLETED",
                    "new_opened": auto_res.new_positions_opened,
                    "closed": auto_res.positions_closed,
                    "open_positions": len(auto_res.open_positions),
                })
        except Exception as exc:
            print(f"⚠️ [AUTO-SYNC] Notice during market sync: {exc}")
        
        # Check every 15 minutes (900 seconds)
        await asyncio.sleep(900)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Warm up services in memory
    print("⚡ [STARTUP] Initializing AI-TOS Core Services...")
    DataService.get_instance()
    PortfolioService.get_instance()
    ZoneService.get_instance()
    print("⚡ [STARTUP] AI-TOS Core Engines Warm and Ready!")
    
    # Launch background auto-sync task
    sync_task = asyncio.create_task(background_market_sync_loop())
    
    yield
    
    sync_task.cancel()
    print("⚡ [SHUTDOWN] Terminating AI-TOS Background Services...")


app = FastAPI(
    title="AI Trading Operating System (AI-TOS) API",
    description="High-Speed Local Institutional Demand & Supply Trading Engine & Quantitative Platform",
    version="3.1.0",
    lifespan=lifespan,
)

# Cross-Origin Resource Sharing (CORS) for local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(market.router)
app.include_router(zones.router)
app.include_router(portfolio.router)
app.include_router(thesis.router)
app.include_router(pipeline.router)
app.include_router(ws.router)


@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint for container and runner probes."""
    return {
        "status": "HEALTHY",
        "system": "AI-TOS Institutional Engine",
        "version": "3.1.0",
        "mode": "LOCAL_PAPER_TRADING_ONLY",
    }


# Mount Frontend static build if it exists
frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="static-assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Don't intercept API or WebSocket routes
        if full_path.startswith("api/") or full_path.startswith("ws/"):
            return None
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(frontend_dist / "index.html"))
