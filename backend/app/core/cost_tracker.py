"""
ARGUS Cost Tracker
Calculates costs for LLM calls and tracks spending
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
import json

from ..models.provider import ModelPrice
from ..config import settings


class CostTracker:
    """Tracks and calculates LLM usage costs"""
    
    def __init__(self):
        self._prices_cache: Dict[str, ModelPrice] = {}
        self._total_cost = 0.0
        self._cost_by_model: Dict[str, float] = {}
        self._cost_by_provider: Dict[str, float] = {}
    
    def calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost for a single LLM call"""
        
        price = self._get_price(provider, model)
        if not price:
            # Fallback to default pricing
            return self._calculate_fallback_cost(input_tokens, output_tokens)
        
        # Calculate cost (per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * price.input_price_per_1m
        output_cost = (output_tokens / 1_000_000) * price.output_price_per_1m
        
        total_cost = input_cost + output_cost
        
        # Update tracking
        self._total_cost += total_cost
        self._cost_by_model[model] = self._cost_by_model.get(model, 0) + total_cost
        self._cost_by_provider[provider] = self._cost_by_provider.get(provider, 0) + total_cost
        
        return total_cost
    
    def _get_price(self, provider: str, model: str) -> Optional[ModelPrice]:
        """Get pricing for a specific model"""
        # Check cache
        cache_key = f"{provider}:{model}"
        if cache_key in self._prices_cache:
            return self._prices_cache[cache_key]
        
        # In production: query database
        # For now, return default pricing
        return self._get_default_price(provider, model)
    
    def _get_default_price(self, provider: str, model: str) -> Optional[ModelPrice]:
        """Get default pricing for popular models"""
        default_prices = {
            "openai": {
                "gpt-4o": ModelPrice(
                    provider="openai",
                    model="gpt-4o",
                    input_price_per_1m=5.00,
                    output_price_per_1m=15.00
                ),
                "gpt-4o-mini": ModelPrice(
                    provider="openai",
                    model="gpt-4o-mini",
                    input_price_per_1m=0.15,
                    output_price_per_1m=0.60
                ),
                "gpt-3.5-turbo": ModelPrice(
                    provider="openai",
                    model="gpt-3.5-turbo",
                    input_price_per_1m=0.50,
                    output_price_per_1m=1.50
                )
            },
            "groq": {
                "llama-3.3-70b-versatile": ModelPrice(
                    provider="groq",
                    model="llama-3.3-70b-versatile",
                    input_price_per_1m=0.59,
                    output_price_per_1m=0.79
                ),
                "mixtral-8x7b-32768": ModelPrice(
                    provider="groq",
                    model="mixtral-8x7b-32768",
                    input_price_per_1m=0.24,
                    output_price_per_1m=0.24
                )
            },
            "anthropic": {
                "claude-3-5-sonnet-20241022": ModelPrice(
                    provider="anthropic",
                    model="claude-3-5-sonnet-20241022",
                    input_price_per_1m=3.00,
                    output_price_per_1m=15.00
                )
            }
        }
        
        provider_prices = default_prices.get(provider, {})
        price = provider_prices.get(model)
        
        if price:
            self._prices_cache[f"{provider}:{model}"] = price
        
        return price
    
    def _calculate_fallback_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost using fallback pricing"""
        # Assume $2 per 1M input, $5 per 1M output
        return (input_tokens / 1_000_000) * 2.0 + (output_tokens / 1_000_000) * 5.0
    
    def get_total_cost(self) -> float:
        """Get total cost tracked"""
        return self._total_cost
    
    def get_cost_by_model(self) -> Dict[str, float]:
        """Get cost breakdown by model"""
        return self._cost_by_model.copy()
    
    def get_cost_by_provider(self) -> Dict[str, float]:
        """Get cost breakdown by provider"""
        return self._cost_by_provider.copy()
    
    def reset_stats(self):
        """Reset cost tracking stats"""
        self._total_cost = 0.0
        self._cost_by_model = {}
        self._cost_by_provider = {}


# Singleton instance
cost_tracker = CostTracker()