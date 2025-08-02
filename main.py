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
    events_refactored as events,  # Updated to use refactored events router
    leaderboard_supabase as leaderboard, 
    auth, 
    admin, 
    discord, 
    payments,
    teams,  # Updated to use refactored teams router
    matches_refactored as matches,
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
            "name": "Leaderboards",
            "description": "Player and team rankings"
        },
        {
            "name": "Teams",
            "description": "Team management and rosters"
        },
        {
            "name": "Matches",
            "description": "Match results and statistics"
        },
        {
            "name": "Player Stats",
            "description": "Detailed player statistics and performance metrics"
        },
        {
            "name": "Admin",
            "description": "Administrative operations"
        },
        {
            "name": "Discord Integration",
            "description": "Discord bot integration endpoints"
        },
        {
            "name": "Payment Integration",
            "description": "Payment processing endpoints"
        },
        {
            "name": "Health",
            "description": "Service health and status checks"
        },
        {
            "name": "Root",
            "description": "API root endpoints"
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

# Include routers with flattened RESTful structure
# Authentication endpoints remain at root
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(players.router, prefix="/v1/players", tags=["Players"])
app.include_router(events.router, tags=["Events"])  # Prefix already included in the router
app.include_router(leaderboard.router, prefix="/v1/leaderboard", tags=["Leaderboards"])
app.include_router(teams.router, tags=["Teams"])  # Prefix already included in the router
app.include_router(matches.router, tags=["Matches"])  # Prefix already included in the router
app.include_router(player_stats.router, prefix="/v1/player-stats", tags=["Player Stats"])
app.include_router(admin.router, prefix="/v1/admin", tags=["Admin"])
app.include_router(discord.router, prefix="/v1/discord", tags=["Discord Integration"])
app.include_router(payments.router, prefix="/v1/payments", tags=["Payment Integration"])

# Add backward compatibility redirects
from fastapi.responses import RedirectResponse

@app.get("/api/{path:path}", include_in_schema=False)
async def legacy_api_redirect(path: str):
    """
    Redirect legacy /api/* routes to their new flattened counterparts.
    This ensures backward compatibility with existing clients.
    """
    # Map old paths to new paths
    path_mapping = {
        "auth": "/auth",
        "players": "/v1/players",
        "events": "/v1/events",
        "leaderboard": "/v1/leaderboards",
        "teams": "/v1/teams",
        "matches": "/v1/matches",
        "player-stats": "/v1/player-stats",
        "admin": "/v1/admin",
        "discord": "/v1/integrations/discord",
        "payments": "/v1/integrations/payments"
    }
    
    # Extract the first part of the path (the resource)
    parts = path.split('/', 1)
    resource = parts[0]
    
    if resource in path_mapping:
        new_path = path_mapping[resource]
        # If there's a subpath, append it
        if len(parts) > 1:
            new_path = f"{new_path}/{parts[1]}"
        return RedirectResponse(url=new_path)
    
    # If no mapping exists, redirect to the root
    return RedirectResponse(url="/")

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