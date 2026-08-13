"""
ARGUS Instrumentation Tests
Unit tests for instrumentation functionality
"""

import pytest
from unittest.mock import patch, MagicMock

from backend.app.core.instrumentation import (
    argus_instrumentation,
    trace,
    instrument_llm_call,
    ArgusInstrumentation,
)


@pytest.mark.asyncio
async def test_instrumentation_initialization():
    """Test instrumentation initialization"""
    # Reset instrumentation
    argus_instrumentation.initialized = False
    
    # Initialize
    argus_instrumentation.initialize()
    
    assert argus_instrumentation.initialized is True


@pytest.mark.asyncio
async def test_trace_decorator():
    """Test trace decorator functionality"""
    @trace(name="test_function")
    async def test_func():
        return "test result"
    
    result = await test_func()
    assert result == "test result"


@pytest.mark.asyncio
async def test_instrument_llm_call():
    """Test LLM call instrumentation"""
    @instrument_llm_call
    async def test_llm_call():
        return {"content": "test response"}
    
    result = await test_llm_call()
    assert result["content"] == "test response"


@pytest.mark.asyncio
async def test_observio_decorator():
    """Test Observio decorator integration"""
    from backend.app.core.instrumentation import observe
    
    @observe()
    async def test_observio_func():
        return "observio test"
    
    result = await test_observio_func()
    assert result == "observio test"


@pytest.mark.asyncio
async def test_multiple_instrumentation_integration():
    """Test that multiple instrumentation tools work together"""
    
    # Mock all instrumentation tools
    with patch('backend.app.core.instrumentation.observio_init') as mock_observio:
        with patch('backend.app.core.instrumentation.px.launch_app') as mock_phoenix:
            with patch('backend.app.core.instrumentation.AgentObs') as mock_agentobs:
                
                # Initialize
                argus_instrumentation.initialized = False
                argus_instrumentation.initialize()
                
                # Verify all were called
                assert argus_instrumentation.initialized is True