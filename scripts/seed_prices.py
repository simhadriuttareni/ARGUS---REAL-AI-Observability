#!/usr/bin/env python
"""
Seed model pricing data into the database
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.models.provider import ModelPrice, ProviderConfig
from app.config import settings


async def seed_prices():
    """Seed model prices into the database"""
    
    # Import database session
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select
    
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Model prices to seed
    prices = [
        # OpenAI
        ModelPrice(
            provider="openai",
            model="gpt-4o",
            input_price_per_1m=5.00,
            output_price_per_1m=15.00,
            max_context_tokens=128000,
            supports_function_calling=True,
            supports_vision=True,
            tier="premium"
        ),
        ModelPrice(
            provider="openai",
            model="gpt-4o-mini",
            input_price_per_1m=0.15,
            output_price_per_1m=0.60,
            max_context_tokens=128000,
            supports_function_calling=True,
            supports_vision=True,
            tier="economy"
        ),
        ModelPrice(
            provider="openai",
            model="gpt-3.5-turbo",
            input_price_per_1m=0.50,
            output_price_per_1m=1.50,
            max_context_tokens=16384,
            supports_function_calling=True,
            supports_vision=False,
            tier="standard"
        ),
        
        # Groq
        ModelPrice(
            provider="groq",
            model="llama-3.3-70b-versatile",
            input_price_per_1m=0.59,
            output_price_per_1m=0.79,
            max_context_tokens=32768,
            supports_function_calling=True,
            supports_vision=False,
            tier="standard",
            latency_p50_ms=150
        ),
        ModelPrice(
            provider="groq",
            model="mixtral-8x7b-32768",
            input_price_per_1m=0.24,
            output_price_per_1m=0.24,
            max_context_tokens=32768,
            supports_function_calling=True,
            supports_vision=False,
            tier="economy",
            latency_p50_ms=100
        ),
        
        # Anthropic
        ModelPrice(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            input_price_per_1m=3.00,
            output_price_per_1m=15.00,
            max_context_tokens=200000,
            supports_function_calling=True,
            supports_vision=True,
            tier="premium"
        ),
    ]
    
    # Provider configs
    configs = [
        ProviderConfig(
            provider="openai",
            base_url="https://api.openai.com/v1",
            api_version="2024-02-01",
            rpm_limit=500,
            tpm_limit=1000000
        ),
        ProviderConfig(
            provider="groq",
            base_url="https://api.groq.com/openai/v1",
            rpm_limit=30,
            tpm_limit=100000
        ),
        ProviderConfig(
            provider="anthropic",
            base_url="https://api.anthropic.com/v1",
            api_version="2023-06-01",
            rpm_limit=50,
            tpm_limit=200000
        ),
    ]
    
    async with async_session() as session:
        # Check if prices already exist
        existing = await session.execute(select(ModelPrice))
        if existing.scalars().first():
            print("⚠️ Prices already seeded, skipping...")
            return
        
        # Add prices
        for price in prices:
            session.add(price)
        
        # Add configs
        for config in configs:
            session.add(config)
        
        await session.commit()
        print(f"✅ Seeded {len(prices)} model prices and {len(configs)} provider configs")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_prices())