"""
ARGUS Alert Models
SQLAlchemy models for alerts and alert rules
"""

from sqlalchemy import Column, String, Float, DateTime, JSON, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
from enum import Enum

Base = declarative_base()


# === Enums ===
class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"


class AlertRuleType(str, Enum):
    MODEL_DOWN = "model_down"
    LATENCY_SPIKE = "latency_spike"
    COST_SPIKE = "cost_spike"


# === Models ===
class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # "model_down", "latency_spike", "cost_spike"
    model = Column(String, nullable=True)
    threshold = Column(Float, nullable=False)
    severity = Column(String, nullable=False)  # "critical", "warning", "info"
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    extra = Column(JSON, default=dict)
    
    def __repr__(self):
        return f"<AlertRule {self.name} ({self.type})>"


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id = Column(String, nullable=False)
    rule_name = Column(String, nullable=False)
    
    model = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    
    severity = Column(String, nullable=False)
    status = Column(String, default="active")  # "active", "resolved", "acknowledged"
    reason = Column(String, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    
    extra = Column(JSON, default=dict)
    
    def __repr__(self):
        return f"<Alert {self.rule_name} ({self.status})>"