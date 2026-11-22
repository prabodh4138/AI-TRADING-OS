"""
AI Trading Operating System (AI-TOS)
WebSocket Connection Manager for Ultra-Low Latency Realtime Streaming.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        payload = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception:
                self.disconnect(connection)

    async def send_personal(self, message: Dict[str, Any], websocket: WebSocket) -> None:
        await websocket.send_text(json.dumps(message))


ws_manager = ConnectionManager()
