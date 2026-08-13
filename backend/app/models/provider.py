"""
ARGUS Provider Models
Model pricing and configuration data
"""

from sqlalchemy import Column, String, Float, DateTime, JSON, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class ModelPrice(Base):
    __tablename__ = "model_prices"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    provider = Column(String, nullable=False)
    model = Column(String, nullable=False, unique=True)
    
    # Pricing in USD per 1M tokens
    input_price_per_1m = Column(Float, nullable=False)
    output_price_per_1m = Column(Float, nullable=False)
    
    # Performance metrics
    latency_p50_ms = Column(Float, nullable=True)
    latency_p95_ms = Column(Float, nullable=True)
    tps_max = Column(Float, nullable=True)  # Tokens per second
    
    # Capabilities
    max_context_tokens = Column(Integer, nullable=True)
    supports_function_calling = Column(Boolean, default=False)
    supports_vision = Column(Boolean, default=False)
    supports_streaming = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    tier = Column(String, default="standard")  # "premium", "standard", "economy"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # CHANGED: 'metadata' is reserved in SQLAlchemy, using 'extra' instead
    extra = Column(JSON, default=dict)
    
    def __repr__(self):
        return f"<ModelPrice {self.provider}/{self.model}>"


class ProviderConfig(Base):
    __tablename__ = "provider_configs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    provider = Column(String, nullable=False, unique=True)
    
    # API configuration
    base_url = Column(String, nullable=True)
    api_version = Column(String, nullable=True)
    
    # Rate limits
    rpm_limit = Column(Integer, nullable=True)
    tpm_limit = Column(Integer, nullable=True)
    
    # Authentication
    auth_type = Column(String, default="api_key")  # "api_key", "oauth", "bearer"
    
    # Status
    is_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # CHANGED: 'metadata' is reserved in SQLAlchemy, using 'extra' instead
    extra = Column(JSON, default=dict)
    
    def __repr__(self):
        return f"<ProviderConfig {self.provider}>"