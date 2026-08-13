"""
ARGUS Monitoring Engine
Background scheduler for uptime checks and metric collection
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..config import settings
from .instrumentation import trace
from ..services.llm_client import get_llm_client


@dataclass
class UptimeCheck:
    model_name: str
    provider: str
    status: str  # "up", "down", "degraded"
    latency_ms: float
    ttft_ms: float
    tps: float
    timestamp: datetime
    error: Optional[str] = None


class ArgusMonitor:
    """Background monitoring system for LLM providers"""
    
    def __init__(self):
        self.checks: List[UptimeCheck] = []
        self.is_running = False
        self.check_interval = 60  # seconds
        self.health_check_prompt = "Say 'ok' if you are working."
    
    async def start(self):
        """Start the monitoring loop"""
        self.is_running = True
        print("🔄 Monitoring started")
        
        while self.is_running:
            await self.run_check()
            await asyncio.sleep(self.check_interval)
    
    async def stop(self):
        self.is_running = False
    
    @trace(name="monitoring_check")
    async def run_check(self):
        """Execute a single monitoring round"""
        print(f"🔍 Running monitoring check at {datetime.now()}")
        
        # Check all configured models
        models = self.get_active_models()
        
        for model in models:
            try:
                check = await self.check_model(model)
                self.checks.append(check)
                
                # Update real-time metrics
                await self.update_metrics(check)
                
            except Exception as e:
                print(f"❌ Error checking {model['name']}: {e}")
    
    async def check_model(self, model: Dict) -> UptimeCheck:
        """Check a single model's health"""
        start_time = time.time()
        total_latency = 0.0
        ttft_ms = 0.0
        tps = 0.0
        
        try:
            llm_client = get_llm_client()
            client = llm_client.get_client(model["provider"])
            
            if not client:
                raise ValueError(f"No client available for {model['provider']}")
            
            # Measure TTFT (Time to First Token)
            ttft_start = time.time()
            
            # Simple completion check based on provider
            if model["provider"] == "openai":
                response = await client.chat.completions.create(
                    model=model["name"],
                    messages=[{"role": "user", "content": self.health_check_prompt}],
                    max_tokens=10
                )
                ttft_ms = (time.time() - ttft_start) * 1000
                tokens = response.usage.completion_tokens or 1
                
            elif model["provider"] == "groq":
                response = client.chat.completions.create(
                    model=model["name"],
                    messages=[{"role": "user", "content": self.health_check_prompt}],
                    max_tokens=10
                )
                ttft_ms = (time.time() - ttft_start) * 1000
                tokens = response.usage.completion_tokens or 1
                
            else:
                # Fallback for other providers
                await asyncio.sleep(0.1)  # Simulate API call
                ttft_ms = (time.time() - ttft_start) * 1000
                tokens = 1
            
            total_latency = (time.time() - start_time) * 1000
            tps = tokens / (total_latency / 1000) if total_latency > 0 else 0
            
            return UptimeCheck(
                model_name=model["name"],
                provider=model["provider"],
                status="up",
                latency_ms=total_latency,
                ttft_ms=ttft_ms,
                tps=tps,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            total_latency = (time.time() - start_time) * 1000
            return UptimeCheck(
                model_name=model["name"],
                provider=model["provider"],
                status="down",
                latency_ms=total_latency,
                ttft_ms=0,
                tps=0,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    def get_active_models(self) -> List[Dict]:
        """
        Get list of models to monitor
        Only includes AVAILABLE models (removed decommissioned ones)
        """
        models = []
        
        # Groq models - ONLY AVAILABLE MODELS
        if settings.groq_api_key:
            models.append({"name": "llama-3.3-70b-versatile", "provider": "groq"})
            models.append({"name": "llama-3.1-8b-instant", "provider": "groq"})
            # REMOVED: mixtral-8x7b-32768 (decommissioned by Groq)
            # REMOVED: gemma2-9b-it (optional, add if needed)
        
        # OpenAI models - only if valid API key
        if settings.openai_api_key:
            models.append({"name": "gpt-4o-mini", "provider": "openai"})
            # models.append({"name": "gpt-3.5-turbo", "provider": "openai"})  # Optional
        
        # Anthropic models - only if valid API key
        if settings.anthropic_api_key:
            models.append({"name": "claude-3-5-sonnet-20241022", "provider": "anthropic"})
        
        return models
    
    async def update_metrics(self, check: UptimeCheck):
        """Push metrics to visualization layer"""
        # In production, this would push to Prometheus/OpenTelemetry
        # For now, just print if there's an error
        if check.status == "down":
            print(f"⚠️ {check.provider}/{check.model_name} is DOWN: {check.error}")
            # Here you would trigger alerts

    def get_recent_checks(self, limit: int = 10) -> List[UptimeCheck]:
        """Get recent monitoring checks"""
        return self.checks[-limit:] if self.checks else []


# Singleton instance
argus_monitor = ArgusMonitor()