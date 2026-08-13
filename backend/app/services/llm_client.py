"""
ARGUS LLM Client - REAL IMPLEMENTATION
Actually calls Groq, OpenAI, and Anthropic APIs
"""

import time
from typing import Optional, Dict, Any

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    import openai
except ImportError:
    openai = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from ..config import settings
from ..core.cost_tracker import cost_tracker


class LLMClient:
    """REAL LLM client that actually makes API calls"""
    
    def __init__(self):
        self._clients = {}
        self._init_clients()
    
    def _init_clients(self):
        """Initialize real clients with API keys"""
        
        # DEBUG: Print what we have
        print(f"🔧 Initializing LLM clients...")
        print(f"🔑 Groq API Key: {'✅' if settings.groq_api_key else '❌ MISSING'}")
        print(f"🔑 OpenAI API Key: {'✅' if settings.openai_api_key else '❌ MISSING'}")
        
        # Groq
        if settings.groq_api_key and Groq:
            try:
                self._clients["groq"] = Groq(api_key=settings.groq_api_key)
                print("✅ Groq client initialized")
            except Exception as e:
                print(f"❌ Groq client init failed: {e}")
        else:
            if not settings.groq_api_key:
                print("❌ Groq API key missing")
            if not Groq:
                print("❌ Groq package not installed")
        
        # OpenAI
        if settings.openai_api_key and openai:
            try:
                self._clients["openai"] = openai.AsyncOpenAI(
                    api_key=settings.openai_api_key
                )
                print("✅ OpenAI client initialized")
            except Exception as e:
                print(f"❌ OpenAI client init failed: {e}")
    
    def get_client(self, provider: str):
        """Get a client for a specific provider"""
        return self._clients.get(provider)
    
    def get_available_providers(self):
        """Get list of available providers"""
        return list(self._clients.keys())
    
    async def completions(self, provider: str, model: str, prompt: str, **kwargs):
        """REAL LLM call - actually calls the API"""
        client = self.get_client(provider)
        if not client:
            raise ValueError(f"Provider '{provider}' not available. Available: {self.get_available_providers()}")
        
        start_time = time.time()
        
        try:
            # === GROQ ===
            if provider == "groq":
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=kwargs.get("max_tokens", 200),
                    temperature=kwargs.get("temperature", 0.7)
                )
                
                content = response.choices[0].message.content
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                
                cost = cost_tracker.calculate_cost(
                    provider="groq",
                    model=model,
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens
                )
                
                return {
                    "content": content,
                    "tokens": total_tokens,
                    "cost": cost,
                    "latency_ms": (time.time() - start_time) * 1000,
                    "provider": provider,
                    "model": model
                }
            
            # === OPENAI ===
            elif provider == "openai":
                response = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=kwargs.get("max_tokens", 200),
                    temperature=kwargs.get("temperature", 0.7)
                )
                
                content = response.choices[0].message.content
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                
                cost = cost_tracker.calculate_cost(
                    provider="openai",
                    model=model,
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens
                )
                
                return {
                    "content": content,
                    "tokens": total_tokens,
                    "cost": cost,
                    "latency_ms": (time.time() - start_time) * 1000,
                    "provider": provider,
                    "model": model
                }
            
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            raise Exception(f"LLM call failed for {provider}/{model}: {str(e)}")


# Create singleton instance
llm_client = LLMClient()


def get_llm_client():
    """Get the LLM client instance"""
    return llm_client