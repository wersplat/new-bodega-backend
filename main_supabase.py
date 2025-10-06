"""
NBA 2K Global Rankings Backend with Supabase
Main application entry point for Supabase version
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from app.routers import auth, admin, discord, payments
from app.routers.players import router as players_router
from app.routers.teams import router as teams_router
from app.routers.tournaments import router as tournaments_router
from app.routers.leaderboard_supabase import router as leaderboard_router
from app.routers.admin_matches import router as admin_matches_router
from app.routers.views import router as views_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NBA 2K Global Rankings API (Supabase)",
    description="Backend API for NBA 2K Global Rankings system using Supabase",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting middleware
app.state.limiter = limiter
# Temporarily disable rate limiting to fix deployment issue
# app.add_exception_handler(429, rate_limit_exceeded_handler)
# app.add_middleware(SlowAPIMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
    max_age=600,  # 10 minutes
)

# Include routers - using Supabase versions where available
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(players_router, prefix="/players", tags=["Players"])
app.include_router(teams_router, prefix="/teams", tags=["Teams"])
app.include_router(tournaments_router, prefix="/tournaments", tags=["Tournaments"])
app.include_router(leaderboard_router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(admin_matches_router, prefix="/admin", tags=["Admin Matches"])
app.include_router(discord.router, prefix="/discord", tags=["Discord"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(views_router)

@app.get("/", tags=["Root"])
@app.head("/")
# @limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def root(request: Request):
    """
    Root endpoint that responds to both GET and HEAD requests.
    
    This endpoint provides basic API information and is rate limited.
    
    Returns:
        dict: A welcome message and API information
    """
    return {
        "message": "NBA 2K Global Rankings API (Supabase)",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
@app.head("/health")
# @limiter.exempt
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "development" if settings.DEBUG else "production"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_supabase:app",
        host="0.0.0.0",
        port=10000,
        reload=True
    )
