"""
ARGUS Phoenix Configuration
OpenTelemetry-based AI observability
"""

import phoenix as px
from openinference.instrumentation.openai import OpenAIInstrumentor
from openinference.instrumentation.groq import GroqInstrumentor
from openinference.instrumentation.litellm import LiteLLMInstrumentor
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from backend.app.config import settings


def configure_phoenix():
    """Configure Phoenix for ARGUS"""
    
    # Launch Phoenix app
    phoenix_app = px.launch_app(
        endpoint=settings.phoenix_endpoint or "http://localhost:6006",
        primary_application_name="argus",
    )
    
    # Set up OpenTelemetry
    resource = Resource.create({
        "service.name": "argus",
        "service.version": "1.0.0",
        "deployment.environment": settings.environment or "development",
    })
    
    tracer_provider = TracerProvider(resource=resource)
    
    # OTLP exporter for Phoenix
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{settings.phoenix_endpoint or 'http://localhost:6006'}/v1/traces",
        insecure=True,
    )
    
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    otel_trace.set_tracer_provider(tracer_provider)
    
    # Instrument LLM providers
    OpenAIInstrumentor().instrument(
        tracer_provider=tracer_provider,
        skip_deprecated=True,
    )
    
    GroqInstrumentor().instrument(
        tracer_provider=tracer_provider,
    )
    
    LiteLLMInstrumentor().instrument(
        tracer_provider=tracer_provider,
    )
    
    LangChainInstrumentor().instrument(
        tracer_provider=tracer_provider,
    )
    
    print(f"✅ Phoenix configured at {settings.phoenix_endpoint}")
    
    return phoenix_app