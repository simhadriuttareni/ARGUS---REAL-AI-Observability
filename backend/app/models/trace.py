"""
ARGUS Trace Models
SQLAlchemy models for trace data
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Trace(Base):
    __tablename__ = "traces"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trace_id = Column(String, index=True)
    span_id = Column(String)
    parent_span_id = Column(String, nullable=True)
    
    name = Column(String)
    model = Column(String)
    provider = Column(String)
    endpoint = Column(String)
    
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    latency_ms = Column(Float, default=0.0)
    
    status = Column(String, default="success")
    error = Column(String, nullable=True)
    
    # CHANGED: 'metadata' is reserved, using 'extra_data' instead
    extra_data = Column(JSON, default=dict)
    
    __table_args__ = (
        Index("idx_trace_trace_id", "trace_id"),
        Index("idx_trace_model_time", "model", "start_time"),
    )
    
    def __repr__(self):
        return f"<Trace {self.trace_id} - {self.model}>"