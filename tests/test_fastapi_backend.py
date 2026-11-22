"""
Integration tests for FastAPI Backend.
Verifies all REST endpoints and data serialization.
"""

import pytest
from starlette.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["version"] == "3.1.0"


def test_market_status():
    response = client.get("/api/market/status")
    assert response.status_code == 200
    data = response.json()
    assert "as_of_date" in data
    assert data["total_bars"] > 0
    assert data["data_health_score"] == 100.0


def test_market_symbols():
    response = client.get("/api/market/symbols")
    assert response.status_code == 200
    syms = response.json()
    assert isinstance(syms, list)
    assert len(syms) > 0


def test_portfolio_summary():
    response = client.get("/api/portfolio/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_equity" in data
    assert "current_cash" in data
    assert "positions" in data
