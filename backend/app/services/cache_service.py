"""
ARGUS Cache Service
Wrapper for semantic cache with service layer
"""

from typing import Optional, Tuple, Dict, Any
import hashlib
import json
import numpy as np
import redis.asyncio as redis

from ..config import settings
from ..core.cache_service import SemanticCache, cache_service as core_cache


class CacheService:
    """
    Service layer for semantic cache operations.
    Extends the core cache with business logic and monitoring.
    """
    
    def __init__(self):
        self._cache = core_cache
        self._hit_count = 0
        self._miss_count = 0
        self._total_queries = 0
    
    async def get(self, query: str, embedding: list) -> Tuple[Optional[str], float, bool]:
        """
        Get cached response with tracking.
        Returns: (response, similarity, was_hit)
        """
        self._total_queries += 1
        
        result = await self._cache.get(query, embedding)
        
        if result:
            response, similarity = result
            self._hit_count += 1
            return response, similarity, True
        
        self._miss_count += 1
        return None, 0.0, False
    
    async def set(self, query: str, embedding: list, response: str):
        """Cache a response with tracking"""
        await self._cache.set(query, embedding, response)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics with hit rate"""
        stats = await self._cache.get_stats()
        
        total = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total * 100) if total > 0 else 0
        
        return {
            **stats,
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "total_queries": self._total_queries,
            "hit_rate": round(hit_rate, 2),
        }
    
    async def clear(self):
        """Clear all cache entries"""
        if not self._cache.redis:
            await self._cache.connect()
        
        await self._cache.redis.delete("cache:embeddings")
        await self._cache.redis.delete("cache:responses")
        
        self._hit_count = 0
        self._miss_count = 0
        self._total_queries = 0
    
    async def get_embedding_count(self) -> int:
        """Get number of cached embeddings"""
        if not self._cache.redis:
            await self._cache.connect()
        
        return await self._cache.redis.hlen("cache:embeddings")
    
    async def get_response_count(self) -> int:
        """Get number of cached responses"""
        if not self._cache.redis:
            await self._cache.connect()
        
        return await self._cache.redis.hlen("cache:responses")


# Singleton instance
cache_service = CacheService()