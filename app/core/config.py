from pydantic_settings import BaseSettings
from functools import lru_cache
from datetime import datetime
import pytz


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "trade_lit_db"

    # Application Configuration
    APP_NAME: str = "TradeLit"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Upstox Configuration
    UPSTOX_API_KEY: str = "870baf4f-5a61-422f-a4b7-6132b40c679c"
    UPSTOX_API_SECRET: str = "kilkj3o63j"
    UPSTOX_REDIRECT_URI: str = "http://localhost:8000/api/v1/upstox/callback"
    UPSTOX_AUTH_URL: str = "https://api.upstox.com/v2/login/authorization/dialog"
    UPSTOX_TOKEN_URL: str = "https://api.upstox.com/v2/login/authorization/token"

    # Timezone Configuration
    TIMEZONE: str = "Asia/Kolkata"  # Indian Standard Time (IST)

    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_timezone(self) -> pytz.timezone:
        """Get the configured timezone object"""
        return pytz.timezone(self.TIMEZONE)

    def now(self) -> datetime:
        """Get current datetime in configured timezone (IST)"""
        return datetime.now(self.get_timezone())

    def now_naive(self) -> datetime:
        """Get current datetime in configured timezone as naive datetime (IST)"""
        return datetime.now(self.get_timezone()).replace(tzinfo=None)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
