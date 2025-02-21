from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Cloud 9"
    
    # Database URLs
    MAIN_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost/cloud9_main"
    PAYMENT_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost/cloud9_payments"
    ANALYTICS_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost/cloud9_analytics"
    
    # Elasticsearch settings
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Crypto settings
    BTC_NODE_URL: Optional[str] = None
    XMR_NODE_URL: Optional[str] = None
    USDT_NODE_URL: Optional[str] = None

    class Config:
        case_sensitive = True

settings = Settings()
