"""
ARGUS Smart Router
Selects the optimal model based on task, cost, and latency requirements
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import re

from ..models.provider import ModelPrice
from ..config import settings


@dataclass
class ModelOption:
    provider: str
    model: str
    cost_per_1k: float
    latency_ms: float
    capabilities: List[str]
    score: float = 0.0


class SmartRouter:
    """Routes requests to the best model based on requirements"""
    
    def __init__(self):
        self._models = self._initialize_models()
    
    def _initialize_models(self) -> List[ModelOption]:
        """Initialize available models with their capabilities"""
        return [
            # Groq Models (ALL AVAILABLE)
            ModelOption(
                provider="groq",
                model="llama-3.3-70b-versatile",
                cost_per_1k=0.00138,
                latency_ms=150,
                capabilities=["complex", "reasoning", "coding"],
                score=0.0
            ),
            ModelOption(
                provider="groq",
                model="llama-3.1-8b-instant",
                cost_per_1k=0.00048,
                latency_ms=100,
                capabilities=["simple", "classification"],
                score=0.0
            ),
            ModelOption(
                provider="groq",
                model="gemma2-9b-it",
                cost_per_1k=0.00048,
                latency_ms=120,
                capabilities=["simple", "classification"],
                score=0.0
            ),
            # REMOVED: mixtral-8x7b-32768 (DECOMMISSIONED by Groq)
            
            # OpenAI Models (if API key is available)
            ModelOption(
                provider="openai",
                model="gpt-4o-mini",
                cost_per_1k=0.00075,
                latency_ms=300,
                capabilities=["simple", "classification", "reasoning"],
                score=0.0
            ),
        ]
    
    async def route(
        self,
        prompt: str,
        task_type: Optional[str] = None,
        max_cost: Optional[float] = None,
        max_latency: Optional[float] = None,
        required_capabilities: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Select the best model for the request"""
        
        # Analyze prompt for complexity
        complexity = self._analyze_complexity(prompt)
        
        # Determine required capabilities
        capabilities = self._determine_capabilities(prompt, task_type)
        
        # Score each model
        scored_models = []
        for model in self._models:
            score = self._score_model(
                model,
                complexity,
                capabilities,
                max_cost,
                max_latency,
                required_capabilities
            )
            scored_models.append((model, score))
        
        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        # Select the best model
        best_model, best_score = scored_models[0] if scored_models else (None, 0)
        
        if not best_model:
            return {
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "estimated_cost": 0.00138,
                "estimated_latency_ms": 150,
                "reasoning": "Fallback to default model"
            }
        
        return {
            "provider": best_model.provider,
            "model": best_model.model,
            "estimated_cost": best_model.cost_per_1k * 0.7,
            "estimated_latency_ms": best_model.latency_ms,
            "reasoning": f"Score: {best_score:.2f} | Complexity: {complexity} | Capabilities: {', '.join(capabilities[:3])}"
        }
    
    def _analyze_complexity(self, prompt: str) -> str:
        """Analyze prompt complexity"""
        word_count = len(prompt.split())
        has_code = bool(re.search(r'```', prompt))
        has_math = bool(re.search(r'[=+\-*/]', prompt))
        
        if word_count > 100 or has_code or has_math:
            return "complex"
        elif word_count > 30:
            return "moderate"
        else:
            return "simple"
    
    def _determine_capabilities(self, prompt: str, task_type: Optional[str]) -> List[str]:
        """Determine required capabilities"""
        capabilities = []
        
        if task_type:
            capabilities.append(task_type)
        
        if re.search(r'(code|program|function|class)', prompt, re.I):
            capabilities.append("coding")
        elif re.search(r'(image|photo|vision|visual)', prompt, re.I):
            capabilities.append("vision")
        elif re.search(r'(reason|think|analyze|complex)', prompt, re.I):
            capabilities.append("reasoning")
        elif re.search(r'(classify|categorize|format|extract)', prompt, re.I):
            capabilities.append("classification")
        
        return capabilities if capabilities else ["simple"]
    
    def _score_model(
        self,
        model: ModelOption,
        complexity: str,
        capabilities: List[str],
        max_cost: Optional[float],
        max_latency: Optional[float],
        required_capabilities: Optional[List[str]]
    ) -> float:
        """Score a model for the request"""
        
        score = 0.0
        
        # Capability match (40% weight)
        if required_capabilities:
            match_count = sum(1 for c in required_capabilities if c in model.capabilities)
            capability_score = match_count / len(required_capabilities) if required_capabilities else 1.0
        else:
            match_count = sum(1 for c in capabilities if c in model.capabilities)
            capability_score = match_count / len(capabilities) if capabilities else 1.0
        
        score += capability_score * 0.4
        
        # Complexity match (30% weight)
        if complexity == "complex":
            complexity_match = 1.0 if "complex" in model.capabilities or "reasoning" in model.capabilities else 0.3
        elif complexity == "moderate":
            complexity_match = 1.0 if "reasoning" in model.capabilities else 0.7
        else:
            complexity_match = 1.0
        
        score += complexity_match * 0.3
        
        # Cost consideration (20% weight)
        if max_cost is not None:
            cost_score = 1.0 if model.cost_per_1k <= max_cost else 0.0
        else:
            cost_score = 1.0 / (model.cost_per_1k * 1000)
        
        score += min(cost_score, 1.0) * 0.2
        
        # Latency consideration (10% weight)
        if max_latency is not None:
            latency_score = 1.0 if model.latency_ms <= max_latency else 0.0
        else:
            latency_score = 1.0 / (model.latency_ms / 100)
        
        score += min(latency_score, 1.0) * 0.1
        
        return score


# Singleton instance
smart_router = SmartRouter()


def get_smart_router() -> SmartRouter:
    """Get the smart router instance"""
    return smart_router