"""
ARGUS AgentObs Configuration
Event-based observability with redaction and hooks
"""

from agentobs import AgentObs, Event, hooks, redact
from agentobs.namespaces.trace import SpanPayload
from agentobs.export import get_exporters, export

from backend.app.config import settings


def configure_agentobs():
    """Configure AgentObs for ARGUS"""
    
    # Initialize AgentObs
    agent_obs = AgentObs(
        app_name="argus",
        environment=settings.environment or "development",
        exporters=get_exporters(settings),
    )
    
    # Configure hooks
    @hooks.on_llm_call
    def on_llm_call(span_id: str, **kwargs):
        """Hook triggered on every LLM call"""
        event = Event(
            event_type="llm.call.started",
            source="argus-backend",
            payload={
                "span_id": span_id,
                "model": kwargs.get("model"),
                "provider": kwargs.get("provider"),
            }
        )
        export(event)
    
    @hooks.on_llm_response
    def on_llm_response(span_id: str, **kwargs):
        """Hook triggered on LLM response"""
        event = Event(
            event_type="llm.call.completed",
            source="argus-backend",
            payload={
                "span_id": span_id,
                "tokens": kwargs.get("tokens"),
                "cost": kwargs.get("cost"),
                "latency_ms": kwargs.get("latency_ms"),
            }
        )
        export(event)
    
    @hooks.on_tool_call
    def on_tool_call(tool_name: str, **kwargs):
        """Hook triggered on tool call"""
        event = Event(
            event_type="tool.call.started",
            source="argus-backend",
            payload={
                "tool_name": tool_name,
                "arguments": kwargs.get("arguments"),
            }
        )
        export(event)
    
    @hooks.on_tool_result
    def on_tool_result(tool_name: str, **kwargs):
        """Hook triggered on tool result"""
        event = Event(
            event_type="tool.call.completed",
            source="argus-backend",
            payload={
                "tool_name": tool_name,
                "result": kwargs.get("result"),
            }
        )
        export(event)
    
    # Configure redaction for sensitive data
    redact.add_pattern(r'Bearer\s+[A-Za-z0-9-_]+', 'Bearer [REDACTED]')
    redact.add_pattern(r'api[-_]?key[=:]\s*[A-Za-z0-9-_]+', 'api_key=[REDACTED]')
    redact.add_pattern(r'password[=:]\s*[^\s]+', 'password=[REDACTED]')
    
    return agent_obs