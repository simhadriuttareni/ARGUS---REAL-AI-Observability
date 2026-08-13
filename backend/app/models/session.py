"""
ARGUS Session Models
User sessions and API key management
"""

from sqlalchemy import Column, String, DateTime, JSON, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    session_token = Column(String, nullable=False, unique=True)
    
    # Session metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    is_active = Column(Boolean, default=True)
    
    # CHANGED: 'metadata' is reserved, using 'extra' instead
    extra = Column(JSON, default=dict)
    
    def __repr__(self):
        return f"<UserSession {self.user_id} ({self.is_active})>"


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    key_prefix = Column(String, nullable=False)
    key_hash = Column(String, nullable=False, unique=True)
    
    name = Column(String, nullable=False)
    permissions = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    # CHANGED: 'metadata' is reserved, using 'extra' instead
    extra = Column(JSON, default=dict)
    
    def __repr__(self):
        return f"<APIKey {self.name} ({self.key_prefix}...)>"