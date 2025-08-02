"""
NBA 2K Global Rankings Backend
Main application entry point
"""

import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.supabase import supabase
from app.core.rate_limiter import (
    limiter,
    rate_limit_exceeded_handler,
    get_identifier
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from app.routers import (
    players_supabase as players, 
    events_supabase as events, 
    leaderboard_supabase as leaderboard, 
    auth, 
    admin, 
    discord, 
    payments,
    teams,
    matches,
    player_stats
)

# Initialize FastAPI app
app = FastAPI(
    title="NBA 2K Global Rankings API",
    description="Backend API for NBA 2K Global Rankings system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints"
        },
        {
            "name": "Players",
            "description": "Player profiles and statistics"
        },
        {
            "name": "Events",
            "description": "Tournament and league events"
        },
        {
            "name": "Leaderboard",
            "description": "Player and team rankings"
        },
        {
            "name": "Admin",
            "description": "Administrative operations"
        },
        {
            "name": "Health",
            "description": "Service health and status checks"
        }
    ]
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(429, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
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

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(players.router, prefix="/api/players", tags=["Players"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["Leaderboard"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(discord.router, prefix="/api/discord", tags=["Discord"])
app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])
app.include_router(player_stats.router, prefix="/api/player-stats", tags=["Player Stats"])

@app.get("/", tags=["Root"])
@app.head("/")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def root(request: Request):
    """
    Root endpoint that responds to both GET and HEAD requests.
    
    This endpoint provides basic API information and is rate limited.
    
    Returns:
        dict: A welcome message and API information
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    return {
        "message": "NBA 2K Global Rankings API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", tags=["Health"])
@app.head("/health")
@limiter.exempt
def health_check():
    """
    Health check endpoint that responds to both GET and HEAD requests.
    
    This endpoint is exempt from rate limiting and provides system health status.
    
    Returns:
        dict: Health status of the API and its dependencies
    """
    # Check database connectivity
    db_status = "ok"
    try:
        # Simple query to check database connectivity
        supabase.get_client().rpc('version').execute()
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = f"error: {str(e)}"
    
    # Check Redis connectivity
    redis_status = "ok"
    try:
        from app.core.rate_limiter import redis_client
        redis_client.ping()
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        redis_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "services": {
            "database": db_status,
            "cache": redis_status
        },
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development" if settings.DEBUG else "production"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )