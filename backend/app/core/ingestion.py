"""
ARGUS Ingestion Pipeline
Processes incoming traces and stores them
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.trace import Trace
from ..models.alert import Alert
from .cost_tracker import cost_tracker
from .alerts import alert_engine
from ..config import settings


class IngestionPipeline:
    """Processes and stores trace data"""
    
    def __init__(self):
        self.batch_size = 100
        self.batch_timeout = 5  # seconds
        self._batch = []
        self._last_flush = datetime.now()
    
    async def ingest(self, trace_data: Dict[str, Any]) -> bool:
        """Ingest a single trace"""
        try:
            # Validate and enrich trace
            trace = await self._process_trace(trace_data)
            
            # Add to batch
            self._batch.append(trace)
            
            # Flush if batch is full or timeout reached
            if len(self._batch) >= self.batch_size:
                await self._flush()
            elif (datetime.now() - self._last_flush).seconds >= self.batch_timeout:
                await self._flush()
            
            return True
            
        except Exception as e:
            print(f"❌ Ingestion error: {e}")
            return False
    
    async def _process_trace(self, data: Dict[str, Any]) -> Trace:
        """Process and enrich trace data"""
        
        # Extract metadata - CHANGED to extra_data
        extra_data = data.get("extra_data", {})
        extra_data["ingested_at"] = datetime.now().isoformat()
        extra_data["source"] = extra_data.get("source", "api")
        
        # Calculate additional metrics
        if "token_usage" in data:
            token_usage = data["token_usage"]
            data["cost"] = cost_tracker.calculate_cost(
                provider=data.get("provider", "unknown"),
                model=data.get("model", "unknown"),
                input_tokens=token_usage.get("prompt_tokens", 0),
                output_tokens=token_usage.get("completion_tokens", 0)
            )
        
        # Create trace object
        trace = Trace(
            trace_id=data.get("trace_id"),
            span_id=data.get("span_id"),
            parent_span_id=data.get("parent_span_id"),
            name=data.get("name", "unknown"),
            model=data.get("model", "unknown"),
            provider=data.get("provider", "unknown"),
            endpoint=data.get("endpoint", "unknown"),
            prompt_tokens=data.get("token_usage", {}).get("prompt_tokens", 0),
            completion_tokens=data.get("token_usage", {}).get("completion_tokens", 0),
            total_tokens=data.get("token_usage", {}).get("total_tokens", 0),
            cost=data.get("cost", 0.0),
            start_time=datetime.fromisoformat(data.get("start_time")) if data.get("start_time") else datetime.now(),
            end_time=datetime.fromisoformat(data.get("end_time")) if data.get("end_time") else datetime.now(),
            latency_ms=data.get("latency_ms", 0.0),
            status=data.get("status", "success"),
            error=data.get("error"),
            extra_data=extra_data  # CHANGED: using extra_data instead of metadata
        )
        
        return trace
    
    async def _flush(self):
        """Flush batch to database"""
        if not self._batch:
            return
        
        try:
            # Save all traces in batch
            from ..models import get_session
            async with get_session() as session:
                for trace in self._batch:
                    session.add(trace)
                await session.commit()
            
            print(f"📦 Flushed {len(self._batch)} traces to database")
            
            # Check alerts for each trace
            for trace in self._batch:
                await alert_engine.check_trace(trace)
            
            self._batch = []
            self._last_flush = datetime.now()
            
        except Exception as e:
            print(f"❌ Flush error: {e}")
            # Don't clear batch on error - retry next time


# Singleton instance
ingestion_pipeline = IngestionPipeline()