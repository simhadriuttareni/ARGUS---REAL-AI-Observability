"""
ARGUS Backend Application
AI Observability Platform
"""

from .main import app
from .config import settings

__version__ = "1.0.0"
__all__ = ["app", "settings"]