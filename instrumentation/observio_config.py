"""
ARGUS Observio Configuration
Full-stack LLM tracing with decorators
"""

import os
from observio import Observio, observe, initialize


def configure_observio():
    """Configure Observio for ARGUS"""
    
    # Initialize Observio
    initialize(
        project_api_key=os.getenv("OBSERVIO_PROJECT_API_KEY"),
        base_url=os.getenv("OBSERVIO_BASE_URL", "http://localhost:8000"),
    )
    
    # Observio is now ready for @observe decorators
    return Observio