"""
ARGUS API Routes
All API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime

from ..services.llm_client import get_llm_client
from ..services.smart_router import get_smart_router
from ..core.cache_service import cache_service
from ..core.monitoring import argus_monitor
from ..core.alerts import alert_engine
from ..core.cost_tracker import cost_tracker
from ..core.ingestion import ingestion_pipeline

router = APIRouter(prefix="/api/v1", tags=["v1"])


# ===== CHAT ENDPOINT - REAL LLM CALL =====
@router.post("/chat")
async def chat(request: dict):
    """
    REAL Chat endpoint - actually calls LLM via Groq/OpenAI
    """
    prompt = request.get("prompt", "")
    model = request.get("model")
    provider = request.get("provider")
    task_type = request.get("task_type", "simple")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    try:
        print(f"📨 Chat request: prompt='{prompt[:50]}...'")
        
        # 1. If no model specified, use Smart Router
        if not model or not provider:
            router_service = get_smart_router()
            route_result = await router_service.route(prompt, task_type)
            provider = route_result["provider"]
            model = route_result["model"]
            print(f"🧠 Router selected: {provider}/{model}")
        
        # 2. Call the actual LLM
        llm = get_llm_client()
        result = await llm.completions(provider, model, prompt)
        
        print(f"✅ LLM response received: {result.get('tokens', 0)} tokens, ${result.get('cost', 0):.6f}")
        
        # 3. Return ALL fields with proper defaults
        return {
            "response": result.get("content", "No response from LLM"),
            "model": model,
            "provider": provider,
            "tokens": result.get("tokens", 0),
            "cost": result.get("cost", 0.0),
            "latency_ms": result.get("latency_ms", 0)
        }
        
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM call failed: {str(e)}")


# ===== SMART ROUTER =====
@router.post("/router/route")
async def route_request(request: dict):
    """Smart Router - analyzes and routes to best model"""
    prompt = request.get("prompt", "")
    task_type = request.get("task_type", "simple")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    router_service = get_smart_router()
    result = await router_service.route(prompt, task_type)
    return result


# ===== TRACE INGESTION =====
@router.post("/ingest")
async def ingest_trace(trace: dict):
    """Ingest a trace for monitoring"""
    try:
        await ingestion_pipeline.ingest(trace)
        return {
            "status": "accepted", 
            "trace_id": trace.get("trace_id", "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


# ===== MONITORING =====
@router.get("/monitoring/status")
async def monitoring_status():
    """Get monitoring status"""
    return {
        "is_running": argus_monitor.is_running,
        "total_checks": len(argus_monitor.checks),
        "last_check": argus_monitor.checks[-1].timestamp if argus_monitor.checks else None
    }


@router.get("/monitoring/checks")
async def get_checks(limit: int = 10):
    """Get recent monitoring checks"""
    checks = argus_monitor.checks[-limit:] if argus_monitor.checks else []
    return [
        {
            "model_name": c.model_name,
            "provider": c.provider,
            "status": c.status,
            "latency_ms": c.latency_ms,
            "ttft_ms": c.ttft_ms,
            "tps": c.tps,
            "timestamp": c.timestamp,
            "error": c.error
        }
        for c in checks
    ]


@router.post("/monitoring/run")
async def run_monitoring():
    """Run a manual monitoring check"""
    try:
        await argus_monitor.run_check()
        return {"status": "completed", "total_checks": len(argus_monitor.checks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring failed: {str(e)}")


# ===== ALERTS =====
@router.get("/alerts")
async def get_alerts(active_only: bool = True):
    """Get current alerts"""
    if active_only:
        return list(alert_engine.active_incidents.values())
    return []


@router.post("/alerts/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    if alert_id in alert_engine.active_incidents:
        alert = alert_engine.active_incidents[alert_id]
        alert.status = "acknowledged"
        return {"status": "acknowledged", "alert_id": alert_id}
    raise HTTPException(status_code=404, detail="Alert not found")


# ===== COST TRACKING =====
@router.get("/cost/stats")
async def cost_stats():
    """Get cost tracking statistics"""
    return {
        "total_cost": cost_tracker.get_total_cost(),
        "by_model": cost_tracker.get_cost_by_model(),
        "by_provider": cost_tracker.get_cost_by_provider()
    }


# ===== CACHE =====
@router.get("/cache/stats")
async def cache_stats():
    """Get semantic cache statistics"""
    return await cache_service.get_stats()


@router.post("/cache/clear")
async def clear_cache():
    """Clear the semantic cache"""
    await cache_service.clear()
    return {"status": "cleared"}


# ===== TRACES =====
@router.get("/traces")
async def get_traces(limit: int = 50, offset: int = 0):
    """Get recent traces"""
    return {
        "traces": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


# ===== DASHBOARD =====
@router.get("/dashboard/metrics")
async def dashboard_metrics():
    """Get dashboard metrics"""
    return {
        "total_traces": 0,
        "total_cost": cost_tracker.get_total_cost(),
        "active_alerts": len(alert_engine.active_incidents),
        "cache_hit_rate": 0,
        "avg_latency_ms": 0,
        "error_rate": 0
    }


# ===== HEALTH =====
@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}