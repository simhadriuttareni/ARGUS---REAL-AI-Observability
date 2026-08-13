"""
ARGUS Custom Instrumentation
Core instrumentation class combining all observability tools
"""

import os
import asyncio
from functools import wraps
from typing import Optional, Callable, Any, Dict
from datetime import datetime
import json

# === Observio - OPTIONAL (Fixed import) ===
try:
    from observio import Observio, observe
    # Fix: Try different import paths for initialize
    try:
        from observio import initialize as observio_init
    except ImportError:
        try:
            from observio.sdk import initialize as observio_init
        except ImportError:
            observio_init = None
    OBSERVIO_AVAILABLE = True
except ImportError:
    Observio = None
    observe = lambda func: func  # No-op decorator
    observio_init = None
    OBSERVIO_AVAILABLE = False
    print("⚠️ Observio not available - skipping")

# === Phoenix: AI Observability Platform ===
try:
    import phoenix as px
    from openinference.instrumentation.openai import OpenAIInstrumentor
    from openinference.instrumentation.groq import GroqInstrumentor
    from openinference.instrumentation.litellm import LiteLLMInstrumentor
    from openinference.instrumentation.langchain import LangChainInstrumentor
    PHOENIX_AVAILABLE = True
except ImportError:
    px = None
    OpenAIInstrumentor = None
    GroqInstrumentor = None
    LiteLLMInstrumentor = None
    LangChainInstrumentor = None
    PHOENIX_AVAILABLE = False
    print("⚠️ Phoenix not available - skipping")

# === OpenTelemetry ===
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# === AgentObs ===
try:
    from agentobs import Event, hooks, redact
    from agentobs.namespaces.trace import SpanPayload
    from agentobs.export import get_exporters, export
    AGENTOBS_AVAILABLE = True
except ImportError:
    Event = None
    hooks = None
    redact = None
    SpanPayload = None
    get_exporters = None
    export = None
    AGENTOBS_AVAILABLE = False
    print("⚠️ AgentObs not available - skipping")

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config import settings


class ArgusInstrumentation:
    """
    Unified instrumentation layer for ARGUS
    Combines Observio, Phoenix, AgentObs, and OpenTelemetry
    """
    
    def __init__(self):
        self.initialized = False
        self.observio = None
        self.phoenix = None
        self.phoenix_app = None
        self.tracer_provider = None
        self.otel_tracer = None
    
    def initialize(self):
        """Initialize all observability tools"""
        if self.initialized:
            print("⚠️ ARGUS instrumentation already initialized")
            return
        
        print("🔧 Initializing ARGUS instrumentation...")
        
        # 1. Initialize Observio
        self._init_observio()
        
        # 2. Initialize Phoenix with OpenTelemetry
        self._init_phoenix()
        
        # 3. Initialize AgentObs
        self._init_agentobs()
        
        self.initialized = True
        print("✅ ARGUS instrumentation initialized successfully")
    
    def _init_observio(self):
        """Initialize Observio for function-level tracing"""
        try:
            if OBSERVIO_AVAILABLE and settings.observio_api_key:
                if observio_init:
                    observio_init(
                        project_api_key=settings.observio_api_key,
                        base_url=settings.observio_base_url
                    )
                    self.observio = Observio
                    print("  ✅ Observio initialized")
                else:
                    print("  ⚠️ Observio: initialize function not available - skipping")
            else:
                if not settings.observio_api_key:
                    print("  ⚠️ Observio: No API key provided - skipping")
                if not OBSERVIO_AVAILABLE:
                    print("  ⚠️ Observio: Package not available - skipping")
        except Exception as e:
            print(f"  ⚠️ Observio initialization failed: {e}")
    
    def _init_phoenix(self):
        """Initialize Phoenix with OpenTelemetry instrumentation"""
        try:
            if not PHOENIX_AVAILABLE:
                print("  ⚠️ Phoenix: Package not available - skipping")
                return
            
            # Launch Phoenix app
            endpoint = settings.phoenix_endpoint or "http://localhost:6006"
            
            try:
                self.phoenix_app = px.launch_app(
                    endpoint=endpoint,
                    primary_application_name="argus",
                    host="0.0.0.0",
                    port=6006
                )
                print(f"  ✅ Phoenix launched at {endpoint}")
            except Exception as e:
                print(f"  ⚠️ Phoenix launch failed: {e}")
                return
            
            # Set up OpenTelemetry
            resource = Resource.create({
                "service.name": "argus",
                "service.version": "1.0.0",
                "deployment.environment": os.getenv("ENVIRONMENT", "development"),
            })
            
            self.tracer_provider = TracerProvider(resource=resource)
            
            # OTLP exporter for Phoenix
            otlp_exporter = OTLPSpanExporter(
                endpoint=f"{endpoint}/v1/traces",
                insecure=True,
            )
            
            span_processor = BatchSpanProcessor(otlp_exporter)
            self.tracer_provider.add_span_processor(span_processor)
            
            otel_trace.set_tracer_provider(self.tracer_provider)
            self.otel_tracer = otel_trace.get_tracer("argus")
            
            # Instrument LLM providers
            if OpenAIInstrumentor:
                try:
                    OpenAIInstrumentor().instrument(
                        tracer_provider=self.tracer_provider,
                        skip_deprecated=True,
                    )
                    print("  ✅ Phoenix OpenAI instrumentation enabled")
                except Exception as e:
                    print(f"  ⚠️ OpenAI instrumentation: {e}")
            
            if GroqInstrumentor:
                try:
                    GroqInstrumentor().instrument(
                        tracer_provider=self.tracer_provider,
                    )
                    print("  ✅ Phoenix Groq instrumentation enabled")
                except Exception as e:
                    print(f"  ⚠️ Groq instrumentation: {e}")
            
            if LiteLLMInstrumentor:
                try:
                    LiteLLMInstrumentor().instrument(
                        tracer_provider=self.tracer_provider,
                    )
                    print("  ✅ Phoenix LiteLLM instrumentation enabled")
                except Exception as e:
                    print(f"  ⚠️ LiteLLM instrumentation: {e}")
            
            if LangChainInstrumentor:
                try:
                    LangChainInstrumentor().instrument(
                        tracer_provider=self.tracer_provider,
                    )
                    print("  ✅ Phoenix LangChain instrumentation enabled")
                except Exception as e:
                    print(f"  ⚠️ LangChain instrumentation: {e}")
            
            self.phoenix = px
            print(f"  ✅ Phoenix initialized at {endpoint}")
            
        except Exception as e:
            print(f"  ⚠️ Phoenix initialization failed: {e}")
    
    def _init_agentobs(self):
        """Initialize AgentObs for event-based observability"""
        try:
            if not AGENTOBS_AVAILABLE:
                print("  ⚠️ AgentObs: Package not available - skipping")
                return
            
            if hooks is None:
                print("  ⚠️ AgentObs: hooks not available - skipping")
                return
            
            # Configure hooks
            @hooks.on_llm_call
            def on_llm_call(span_id: str, **kwargs):
                """Hook triggered on every LLM call"""
                if export:
                    event = Event(
                        event_type="llm.call.started",
                        source="argus-backend",
                        payload={
                            "span_id": span_id,
                            "model": kwargs.get("model"),
                            "provider": kwargs.get("provider"),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    try:
                        export(event)
                    except Exception:
                        pass
            
            @hooks.on_llm_response
            def on_llm_response(span_id: str, **kwargs):
                """Hook triggered on LLM response"""
                if export:
                    event = Event(
                        event_type="llm.call.completed",
                        source="argus-backend",
                        payload={
                            "span_id": span_id,
                            "tokens": kwargs.get("tokens", 0),
                            "cost": kwargs.get("cost", 0.0),
                            "latency_ms": kwargs.get("latency_ms", 0),
                            "status": kwargs.get("status", "success"),
                        }
                    )
                    try:
                        export(event)
                    except Exception:
                        pass
            
            @hooks.on_tool_call
            def on_tool_call(tool_name: str, **kwargs):
                """Hook triggered on tool call"""
                if export:
                    event = Event(
                        event_type="tool.call.started",
                        source="argus-backend",
                        payload={
                            "tool_name": tool_name,
                            "arguments": kwargs.get("arguments", {}),
                        }
                    )
                    try:
                        export(event)
                    except Exception:
                        pass
            
            # Configure redaction
            if redact:
                redact.add_pattern(r'Bearer\s+[A-Za-z0-9-_]+', 'Bearer [REDACTED]')
                redact.add_pattern(r'api[-_]?key[=:]\s*[A-Za-z0-9-_]+', 'api_key=[REDACTED]')
                redact.add_pattern(r'password[=:]\s*[^\s]+', 'password=[REDACTED]')
                redact.add_pattern(r'Authorization:\s*[A-Za-z0-9-_]+', 'Authorization: [REDACTED]')
                redact.add_pattern(r'gsk_[A-Za-z0-9]+', 'gsk_[REDACTED]')
                redact.add_pattern(r'sk-proj-[A-Za-z0-9]+', 'sk-proj-[REDACTED]')
            
            print("  ✅ AgentObs initialized")
            
        except Exception as e:
            print(f"  ⚠️ AgentObs initialization failed: {e}")
    
    def get_tracer(self):
        """Get OpenTelemetry tracer"""
        return self.otel_tracer
    
    def create_span(self, name: str, attributes: Dict = None):
        """Create a new span for tracing"""
        if self.otel_tracer:
            return self.otel_tracer.start_span(name, attributes=attributes or {})
        return None


# === Convenience Decorator ===
def trace(name: str = None, model: str = None):
    """
    Custom trace decorator for ARGUS
    Works with Observio and OpenTelemetry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the instrumentation instance
            if not argus_instrumentation.initialized:
                argus_instrumentation.initialize()
            
            # Create OpenTelemetry span
            tracer = argus_instrumentation.get_tracer()
            span_name = name or func.__name__
            
            if tracer:
                with tracer.start_as_current_span(span_name, attributes={
                    "function.name": func.__name__,
                    "model": model or "unknown",
                }):
                    result = await func(*args, **kwargs)
                    return result
            else:
                # If no tracer, just execute with Observio decorator
                if observe and OBSERVIO_AVAILABLE:
                    # Observio's @observe decorator handles this
                    return await func(*args, **kwargs)
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def instrument_llm_call(func: Callable) -> Callable:
    """
    Wrapper that instruments any LLM call with all tools
    """
    @wraps(func)
    @observe if OBSERVIO_AVAILABLE and observe else lambda x: x
    async def wrapper(*args, **kwargs):
        if not argus_instrumentation.initialized:
            argus_instrumentation.initialize()
        
        # AgentObs hooks trigger automatically
        # Phoenix auto-instrumentation handles OTel
        # Observio handles function tracing
        
        result = await func(*args, **kwargs)
        return result
    return wrapper


# Singleton instance
argus_instrumentation = ArgusInstrumentation()