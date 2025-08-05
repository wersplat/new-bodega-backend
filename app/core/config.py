"""
Configuration settings for the NBA 2K Global Rankings backend with Supabase
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Dict, Any, Union
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    
    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    
    # Database (using Supabase connection string)
    DATABASE_URL: str = ""
    
    # JWT
    SECRET_KEY: str = "your-super-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    
    # Discord
    DISCORD_BOT_TOKEN: str = ""
    DISCORD_API_KEY: str = ""
    
    # Email (can be configured to use Supabase Auth email)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_ANONYMOUS: str = "10/minute"
    RATE_LIMIT_AUTHENTICATED: str = "1000/hour"
    RATE_LIMIT_ADMIN: str = "5000/hour"
    
    # Caching
    CACHE_TTL: int = 300  # 5 minutes default
    CACHE_ENABLED: bool = True
    
    # App
    DEBUG: bool = True
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080, http://bodegacatsgc.gg, http://railway.app"
    
    # API Configuration
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "NBA 2K Global Rankings API"
    VERSION: str = "1.0.0"
    
    # Security
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Frontend URL for OAuth redirects
    FRONTEND_URL: str = "http://localhost:3000"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    def model_post_init(self, __context):
        self._validate_required_settings()
    
    def _validate_required_settings(self):
        """Validate required settings based on environment"""
        if self.ENVIRONMENT == "production":
            if not self.SUPABASE_URL or not self.SUPABASE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY are required in production")
            if self.SECRET_KEY == "your-super-secret-key-here-change-in-production":
                raise ValueError("SECRET_KEY must be changed in production")
    
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @property
    def ALLOWED_HOSTS_LIST(self) -> List[str]:
        """Convert ALLOWED_HOSTS string to list"""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]
    
    @property
    def get_supabase_config(self) -> Dict[str, Any]:
        """Get Supabase configuration"""
        return {
            "url": self.SUPABASE_URL,
            "key": self.SUPABASE_KEY or self.SUPABASE_ANON_KEY,
            "debug": self.DEBUG
        }
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.ENVIRONMENT.lower() == "testing"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()ß