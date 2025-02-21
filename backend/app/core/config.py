from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Cloud 9")
    
    # Database URLs
    MAIN_DATABASE_URL: str = os.getenv("MAIN_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/cloud9_main")
    PAYMENT_DATABASE_URL: str = os.getenv("PAYMENT_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/cloud9_payments")
    ANALYTICS_DATABASE_URL: str = os.getenv("ANALYTICS_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/cloud9_analytics")
    
    # Elasticsearch settings
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    
    # Redis settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Crypto settings
    BTC_NODE_URL: Optional[str] = os.getenv("BTC_NODE_URL")
    XMR_NODE_URL: Optional[str] = os.getenv("XMR_NODE_URL")
    USDT_NODE_URL: Optional[str] = os.getenv("USDT_NODE_URL")

    class Config:
        case_sensitive = True

settings = Settings()
