"""
ARGUS - AI Observability Platform
Main FastAPI application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from datetime import datetime

from .config import settings
from .core.instrumentation import argus_instrumentation
from .core.monitoring import argus_monitor
from .core.alerts import alert_engine
from .api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    
    # Startup
    print("🚀 Starting ARGUS...")
    
    # Initialize instrumentation
    argus_instrumentation.initialize()
    
    # Start background monitoring
    asyncio.create_task(argus_monitor.start())
    
    print("✅ ARGUS ready")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await argus_monitor.stop()


app = FastAPI(
    title="ARGUS - AI Observability Platform",
    description="Complete AI monitoring and observability",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


# ===== HEALTH CHECK =====
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "instrumentation": argus_instrumentation.initialized
    }


# ===== WEBSOCKET FOR REAL-TIME MONITORING =====
@app.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    """WebSocket endpoint for real-time monitoring"""
    await websocket.accept()
    try:
        while True:
            # Send latest metrics
            data = {
                "timestamp": datetime.now().isoformat(),
                "checks": len(argus_monitor.checks),
                "active_alerts": len(alert_engine.active_incidents),
                "total_cost": 0,  # Would come from cost tracker
                "cache_hit_rate": 0  # Would come from cache service
            }
            await websocket.send_json(data)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        print("🔌 Client disconnected from WebSocket")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")


# ===== ROOT ENDPOINT =====
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ARGUS - AI Observability Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }