from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv

# Load .env file explicitly
load_dotenv()

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    
    # Observability
    phoenix_endpoint: str = Field(default="http://localhost:6006", alias="PHOENIX_ENDPOINT")
    langsmith_api_key: str = Field(default="", alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="argus-production", alias="LANGSMITH_PROJECT")
    observio_base_url: str = Field(default="http://localhost:8000", alias="OBSERVIO_BASE_URL")
    observio_api_key: str = Field(default="", alias="OBSERVIO_PROJECT_API_KEY")
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./argus.db",
        alias="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")
    
    # Encryption
    encryption_key: str = Field(default="", alias="ENCRYPTION_KEY")
    jwt_secret: str = Field(default="", alias="JWT_SECRET_KEY")
    
    # Configuration
    repetition_threshold: int = Field(default=3, alias="REPETITION_THRESHOLD")
    duration_threshold: int = Field(default=30, alias="DURATION_THRESHOLD")
    confidence_low_threshold: float = Field(default=0.4, alias="CONFIDENCE_LOW_THRESHOLD")
    default_model: str = Field(default="llama-3.3-70b-versatile", alias="MODEL")
    
    # Logging
    log_level: str = Field(default="info", alias="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# Print debug info
print(f"🔑 GROQ_API_KEY loaded: {'✅' if os.getenv('GROQ_API_KEY') else '❌ NOT FOUND'}")
print(f"📁 .env file exists: {'✅' if os.path.exists('.env') else '❌ NOT FOUND'}")
print(f"📁 Current directory: {os.getcwd()}")

settings = Settings()
print(f"🔑 Settings.groq_api_key: {'✅' if settings.groq_api_key else '❌ EMPTY'}")