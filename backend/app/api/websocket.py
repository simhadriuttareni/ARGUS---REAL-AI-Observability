"""
ARGUS WebSocket Handler
Real-time monitoring and event streaming
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect

from ..core.monitoring import argus_monitor
from ..core.alerts import alert_engine
from ..core.cache_service import cache_service


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.broadcast_tasks: Dict[str, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        # Start sending updates
        task = asyncio.create_task(self.send_updates(websocket, client_id))
        self.broadcast_tasks[client_id or str(id(websocket))] = task
        
        print(f"🔌 WebSocket connected: {len(self.active_connections)} active")
    
    async def disconnect(self, websocket: WebSocket, client_id: str = None):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        
        if client_id and client_id in self.broadcast_tasks:
            self.broadcast_tasks[client_id].cancel()
            del self.broadcast_tasks[client_id]
        
        print(f"🔌 WebSocket disconnected: {len(self.active_connections)} active")
    
    async def send_updates(self, websocket: WebSocket, client_id: str = None):
        """Send periodic updates to a client"""
        try:
            while True:
                # Gather all metrics
                data = await self.get_live_metrics()
                await websocket.send_json(data)
                await asyncio.sleep(2)  # 2 second interval
        except asyncio.CancelledError:
            pass
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"❌ WebSocket send error: {e}")
    
    async def get_live_metrics(self) -> Dict[str, Any]:
        """Get current live metrics"""
        # Get last check
        last_check = None
        if argus_monitor.checks:
            last_check = argus_monitor.checks[-1]
        
        # Get alert count
        active_alerts = len(alert_engine.active_incidents)
        
        # Get cache stats
        cache_stats = await cache_service.get_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_traces": 0,  # Would come from DB
            "active_alerts": active_alerts,
            "total_cost": 0,  # Would come from DB
            "cache_hit_rate": cache_stats.get("hit_rate", 0),
            "cache_entries": cache_stats.get("entries", 0),
            "last_check": {
                "model": last_check.model_name if last_check else None,
                "status": last_check.status if last_check else None,
                "latency_ms": last_check.latency_ms if last_check else None,
                "timestamp": last_check.timestamp.isoformat() if last_check else None
            } if last_check else None
        }
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = []
        
        for websocket in self.active_connections:
            try:
                await websocket.send_text(message_json)
            except WebSocketDisconnect:
                disconnected.append(websocket)
        
        for websocket in disconnected:
            self.active_connections.discard(websocket)


# Singleton instance
websocket_manager = WebSocketManager()


# === WebSocket Endpoint ===
async def websocket_monitor(websocket: WebSocket):
    """WebSocket endpoint for real-time monitoring"""
    client_id = str(id(websocket))
    await websocket_manager.connect(websocket, client_id)
    
    try:
        # Keep connection alive
        while True:
            # Receive client messages (for control)
            data = await websocket.receive_text()
            print(f"📨 Received from client: {data}")
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, client_id)