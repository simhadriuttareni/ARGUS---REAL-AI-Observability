#!/usr/bin/env python
"""
ARGUS Development Server Runner
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Ensure environment is set
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./argus.db"
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info")
    )