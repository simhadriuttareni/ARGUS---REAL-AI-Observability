"""
ARGUS Utility Functions
Helper functions used across the application
"""

import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import secrets


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID"""
    return f"{prefix}{secrets.token_hex(16)}" if prefix else secrets.token_hex(16)


def hash_text(text: str) -> str:
    """Hash text using SHA-256"""
    return hashlib.sha256(text.encode()).hexdigest()


def format_cost(cost: float) -> str:
    """Format cost in USD"""
    if cost < 0.001:
        return "$0.00"
    return f"${cost:.4f}"


def format_latency(ms: float) -> str:
    """Format latency in a human-readable format"""
    if ms < 1:
        return f"{ms * 1000:.1f}µs"
    elif ms < 1000:
        return f"{ms:.1f}ms"
    else:
        return f"{ms / 1000:.2f}s"


def parse_duration(duration_str: str) -> int:
    """Parse duration string (e.g., '5m', '1h', '2d') to seconds"""
    pattern = r'^(\d+)([smhdw])$'
    match = re.match(pattern, duration_str.lower())
    
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}")
    
    value = int(match.group(1))
    unit = match.group(2)
    
    unit_map = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800
    }
    
    return value * unit_map.get(unit, 1)


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def safe_json_loads(text: str) -> Dict[str, Any]:
    """Safely load JSON with error handling"""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}


def safe_json_dumps(data: Dict[str, Any]) -> str:
    """Safely dump JSON with error handling"""
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return "{}"


def extract_keywords(text: str, limit: int = 10) -> List[str]:
    """Extract keywords from text"""
    # Simple keyword extraction
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Count word frequencies
    word_count = {}
    for word in words:
        if word not in stop_words and len(word) > 2:
            word_count[word] = word_count.get(word, 0) + 1
    
    # Sort by frequency and return top N
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:limit]]


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self._requests = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        now = datetime.now()
        
        if key not in self._requests:
            self._requests[key] = []
        
        # Remove old requests
        cutoff = now - timedelta(seconds=self.time_window)
        self._requests[key] = [
            ts for ts in self._requests[key]
            if ts > cutoff
        ]
        
        # Check limit
        if len(self._requests[key]) >= self.max_requests:
            return False
        
        # Add request
        self._requests[key].append(now)
        return True
    
    def reset(self, key: str):
        """Reset rate limit for a key"""
        if key in self._requests:
            self._requests[key] = []