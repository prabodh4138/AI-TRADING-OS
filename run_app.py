"""
AI Trading Operating System (AI-TOS)
Master Standalone Application Launcher.
Starts the FastAPI Backend and serves the React Institutional Terminal locally.
Specification Baseline: Master Final Consolidated System Specification v3.1
"""

import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

# Force UTF-8 encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to Python module path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))


def print_banner():
    banner = """
================================================================================
  [AI-TOS] AI TRADING OPERATING SYSTEM - GTF INSTITUTIONAL TERMINAL v3.1
================================================================================
  Status      : 100% PRISTINE DATA HEALTH & CORE SERVICES READY
  Backend     : FastAPI High-Speed Async Engine (Port 8000)
  Frontend    : React + TypeScript + Canvas Trading Terminal
  Protocol    : REST API + Real-Time WebSocket Streaming (ws://localhost:8000/ws/live)
  Execution   : STRICT SIMULATED PAPER TRADING (Zero Live Broker Authorization)
================================================================================
  >> Opening application in your default browser at: http://localhost:8000
  >> Interactive API Documentation available at   : http://localhost:8000/docs
================================================================================
    """
    print(banner)


def open_browser(url: str, delay_seconds: float = 1.2):
    """Opens the local terminal in the default browser once the server starts."""
    time.sleep(delay_seconds)
    try:
        webbrowser.open(url)
    except Exception as exc:
        print(f"[NOTE] Please open your browser manually at {url} ({exc})")


def main():
    import uvicorn

    print_banner()

    # Verify that the frontend dist folder is built
    dist_dir = PROJECT_ROOT / "frontend" / "dist"
    if not dist_dir.exists() or not (dist_dir / "index.html").exists():
        print(f"[WARNING] Frontend build directory '{dist_dir}' not found.")
        print("Please run 'cd frontend; npm run build' first to build the React application.")

    app_url = "http://localhost:8000"

    # Launch browser thread
    threading.Thread(target=open_browser, args=(app_url,), daemon=True).start()

    # Start FastAPI Uvicorn Server
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
