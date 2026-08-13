"""
ARGUS API Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# === Enums ===
class ModelProvider(str, Enum):
    OPENAI = "openai"
    GROQ = "groq"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    COHERE = "cohere"


class TraceStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


# === Token Usage ===
class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


# === Ingest Schemas ===
class TraceIngestRequest(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    name: str
    model: str
    provider: ModelProvider
    endpoint: str
    prompt: Optional[str] = None
    response: Optional[str] = None
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    cost: float = 0.0
    start_time: datetime
    end_time: datetime
    latency_ms: float = 0.0
    status: TraceStatus = TraceStatus.SUCCESS
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TraceIngestResponse(BaseModel):
    status: str
    trace_id: str
    stored: bool


class IngestRequest(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    name: str
    model: str
    provider: ModelProvider
    endpoint: str
    prompt: Optional[str] = None
    response: Optional[str] = None
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    cost: float = 0.0
    start_time: datetime
    end_time: datetime
    latency_ms: float = 0.0
    status: TraceStatus = TraceStatus.SUCCESS
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class IngestResponse(BaseModel):
    status: str
    trace_id: str
    stored: bool


class MetricsResponse(BaseModel):
    total_traces: int = 0
    total_cost: float = 0.0
    avg_latency: float = 0.0
    error_rate: float = 0.0
    cache_hit_rate: float = 0.0


# === Monitoring Schemas ===
class UptimeCheckResponse(BaseModel):
    model_name: str
    provider: ModelProvider
    status: str
    latency_ms: float
    ttft_ms: float
    tps: float
    timestamp: datetime
    error: Optional[str] = None


class MonitoringStatusResponse(BaseModel):
    is_running: bool
    last_check: Optional[datetime]
    total_checks: int


# === Alert Schemas ===
class AlertRuleCreate(BaseModel):
    name: str
    type: str
    model: Optional[str] = None
    threshold: float
    severity: AlertSeverity
    enabled: bool = True


class AlertRuleResponse(BaseModel):
    id: str
    name: str
    type: str
    model: Optional[str]
    threshold: float
    severity: AlertSeverity
    enabled: bool
    created_at: datetime


class AlertResponse(BaseModel):
    id: str
    rule_id: str
    rule_name: str
    model: str
    provider: ModelProvider
    severity: AlertSeverity
    status: AlertStatus
    reason: str
    created_at: datetime
    resolved_at: Optional[datetime]
    data: Dict[str, Any] = Field(default_factory=dict)


# === Cost Schemas ===
class CostMetricsRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    model: Optional[str] = None
    provider: Optional[ModelProvider] = None


class CostBreakdown(BaseModel):
    by_model: Dict[str, float] = Field(default_factory=dict)
    by_provider: Dict[str, float] = Field(default_factory=dict)
    total_cost: float = 0.0


# === Cache Schemas ===
class CacheStatsResponse(BaseModel):
    entries: int = 0
    responses: int = 0
    ttl_seconds: int = 3600
    hit_rate: float = 0.0


# === Router Schemas ===
class RouterRequest(BaseModel):
    prompt: str
    task_type: Optional[str] = None
    max_cost: Optional[float] = None
    max_latency: Optional[float] = None


class RouterResponse(BaseModel):
    provider: str
    model: str
    estimated_cost: float
    estimated_latency_ms: float
    reasoning: str


# === Dashboard Schemas ===
class DashboardMetrics(BaseModel):
    total_traces: int = 0
    total_cost: float = 0.0
    active_alerts: int = 0
    cache_hit_rate: float = 0.0
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0