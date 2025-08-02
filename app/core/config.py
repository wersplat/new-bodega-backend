"""
Configuration settings for the NBA 2K Global Rankings backend with Supabase
"""

from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
import os

class Settings(BaseSettings):
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
    
    # App
    DEBUG: bool = True
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }
    
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def get_supabase_config(self) -> Dict[str, Any]:
        """Get Supabase configuration"""
        return {
            "url": self.SUPABASE_URL,
            "key": self.SUPABASE_KEY or self.SUPABASE_ANON_KEY,
            "debug": self.DEBUG
        }

# Global settings instance
settings = Settings()