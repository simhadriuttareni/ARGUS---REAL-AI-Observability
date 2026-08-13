"""
ARGUS Semantic Cache
Uses Redis + Vector Similarity for intelligent caching
"""

import hashlib
import json
from typing import Optional, Tuple
import redis.asyncio as redis
import numpy as np

from ..config import settings

class SemanticCache:
    """Semantic cache using Redis and vector similarity"""
    
    def __init__(self):
        self.redis = None
        self.similarity_threshold = 0.95
        self.ttl = 3600  # 1 hour
    
    async def connect(self):
        self.redis = await redis.from_url(settings.redis_url)
    
    async def get(self, query: str, embedding: list) -> Optional[Tuple[str, float]]:
        """Get cached response if similar query exists"""
        if not self.redis:
            await self.connect()
        
        # Get all cached embeddings
        cached = await self.redis.hgetall("cache:embeddings")
        
        if not cached:
            return None
        
        # Find most similar
        best_score = 0
        best_key = None
        
        for key, stored_embedding_str in cached.items():
            stored_embedding = json.loads(stored_embedding_str)
            similarity = self.cosine_similarity(embedding, stored_embedding)
            
            if similarity > best_score:
                best_score = similarity
                best_key = key.decode() if isinstance(key, bytes) else key
        
        if best_score >= self.similarity_threshold:
            # Get cached response
            response = await self.redis.hget("cache:responses", best_key)
            return response.decode() if response else None, best_score
        
        return None
    
    async def set(self, query: str, embedding: list, response: str):
        """Cache a query-response pair"""
        if not self.redis:
            await self.connect()
        
        key = hashlib.md5(query.encode()).hexdigest()
        
        await self.redis.hset("cache:embeddings", key, json.dumps(embedding))
        await self.redis.hset("cache:responses", key, response)
        await self.redis.expire("cache:embeddings", self.ttl)
        await self.redis.expire("cache:responses", self.ttl)
    
    @staticmethod
    def cosine_similarity(a: list, b: list) -> float:
        """Calculate cosine similarity between two vectors"""
        a = np.array(a)
        b = np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    async def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis:
            await self.connect()
        
        embedding_count = await self.redis.hlen("cache:embeddings")
        response_count = await self.redis.hlen("cache:responses")
        
        return {
            "entries": embedding_count,
            "responses": response_count,
            "ttl_seconds": self.ttl
        }

cache_service = SemanticCache()