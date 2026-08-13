"""
ARGUS API Tests
Unit tests for API endpoints
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from backend.app.main import app
from backend.app.core.cost_tracker import cost_tracker
from backend.app.core.cache_service import cache_service


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_ingest_trace():
    """Test trace ingestion endpoint"""
    trace_data = {
        "trace_id": "test-123",
        "span_id": "span-456",
        "name": "test_completion",
        "model": "gpt-4o-mini",
        "provider": "openai",
        "endpoint": "/v1/chat/completions",
        "token_usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "cost": 0.0002,
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() + timedelta(seconds=1)).isoformat(),
        "latency_ms": 150.5,
        "status": "success"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/ingest", json=trace_data)
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_monitoring_status():
    """Test monitoring status endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/monitoring/status")
        assert response.status_code == 200
        assert "is_running" in response.json()


@pytest.mark.asyncio
async def test_cost_tracking():
    """Test cost tracking functionality"""
    cost = cost_tracker.calculate_cost(
        provider="openai",
        model="gpt-4o-mini",
        input_tokens=10,
        output_tokens=20
    )
    assert cost > 0


@pytest.mark.asyncio
async def test_cache_operations():
    """Test semantic cache operations"""
    # Clear cache first
    await cache_service.clear()
    
    # Test empty cache
    result = await cache_service.get("test query", [0.1, 0.2, 0.3])
    assert result is None
    
    # Set cache
    await cache_service.set("test query", [0.1, 0.2, 0.3], "test response")
    
    # Test cache hit
    result, similarity, was_hit = await cache_service.get("test query", [0.1, 0.2, 0.3])
    assert result == "test response"
    assert was_hit is True