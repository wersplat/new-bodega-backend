"""
Configuration settings for the NBA 2K Global Rankings backend
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/nba2k_rankings"
    
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
    
    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # App
    DEBUG: bool = True
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings() 