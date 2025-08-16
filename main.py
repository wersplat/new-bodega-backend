"""
NBA 2K Global Rankings Backend
Main application entry point
"""

import logging
from datetime import datetime
# no typing imports needed at module level

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.supabase import supabase
from app.core.rate_limiter import (
    limiter,
    rate_limit_exceeded_handler,
    is_rate_limiting_enabled,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from app.routers import (
    players,  # Consolidated players router
    tournaments,  # Tournaments router
    leagues,  # Leagues router
    leaderboard_supabase as leaderboard, 
    auth, 
    admin, 
    admin_actions,
    discord, 
    payments,
    teams,  # Updated to use refactored teams router
    matches,  # Consolidated matches router
    player_stats,
    awards_race,  # Awards race router
    player_badges,  # Player badges router
    team_rosters,  # Team rosters router
    tournament_groups,  # Tournament groups router
    team_roster_current,  # Team roster current view router
)
from app.routers import awards as awards_router

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
            "name": "Tournaments",
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
        },
        {
            "name": "Leagues",
            "description": "League management and information"
        }
    ]
)

# Add rate limiting middleware
if is_rate_limiting_enabled():
    app.state.limiter = limiter  # type: ignore[attr-defined]
    app.add_exception_handler(429, rate_limit_exceeded_handler)

# Add rate limiting middleware if enabled
if is_rate_limiting_enabled():
    app.add_middleware(SlowAPIMiddleware)

# CORS middleware (tightened to allowlist)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Admin-Api-Token", "X-API-Key"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
    max_age=600,
)

# Include routers with flattened RESTful structure
# Authentication endpoints remain at root
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(players.router, tags=["Players"])
app.include_router(tournaments.router, tags=["Tournaments"])
app.include_router(leagues.router, tags=["Leagues"])
app.include_router(leaderboard.router, tags=["Leaderboards"])
app.include_router(teams.router, tags=["Teams"])
app.include_router(matches.router, tags=["Matches"])
app.include_router(player_stats.router, tags=["Player Stats"])
app.include_router(admin.router, tags=["Admin"])
app.include_router(admin_actions.router, tags=["Admin"])
app.include_router(discord.router, tags=["Discord Integration"])
app.include_router(payments.router, tags=["Payment Integration"])
app.include_router(awards_router.router, tags=["Awards"])
app.include_router(awards_race.router, tags=["Awards Race"])
app.include_router(player_badges.router, tags=["Player Badges"])
app.include_router(team_rosters.router, tags=["Team Rosters"])
app.include_router(tournament_groups.router, tags=["Tournament Groups"])
app.include_router(team_roster_current.router, tags=["Team Roster Current"]) 
# Add backward compatibility redirects

@app.get("/api/{path:path}", include_in_schema=False)
# @limiter.exempt
async def legacy_api_redirect(path: str):
    """
    Redirect legacy /api/* routes to their new flattened counterparts.
    This ensures backward compatibility with existing clients.
    """
    # Map old paths to new paths
    path_mapping = {
        "auth": "/auth",
        "players": "/v1/players",
        "tournaments": "/v1/tournaments",
        "leaderboard": "/v1/leaderboard",  # Updated to match actual route
        "teams": "/v1/teams",
        "matches": "/v1/matches",
        "player-stats": "/v1/player-stats",
        "admin": "/v1/admin",
        "discord": "/v1/discord",  # Updated to match actual route
        "payments": "/v1/payments",  # Updated to match actual route
        "leagues": "/v1/leagues"
    }
    
    # Extract the first part of the path (the resource)
    parts = path.split('/', 1)
    resource = parts[0]
    
    if resource in path_mapping:
        new_path = path_mapping[resource]
        # If there's a subpath, append it
        if len(parts) > 1:
            new_path = f"{new_path}/{parts[1]}"
        return RedirectResponse(url=new_path, status_code=307)
    
    # If no mapping exists, redirect to the root
    return RedirectResponse(url="/", status_code=307)

@app.get("/", tags=["Root"])
@app.head("/")
# @limiter.limit(settings.RATE_LIMIT_DEFAULT)
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
# @limiter.exempt
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
    
    # Rate limiting status
    rate_limiting_status = "ok"
    try:
        # Report enabled/disabled based on config
        rate_limiting_status = "enabled" if is_rate_limiting_enabled() else "disabled"
    except Exception as e:
        logger.error(f"Rate limiting health check failed: {str(e)}")
        rate_limiting_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "services": {
            "database": db_status,
            "rate_limiting": rate_limiting_status
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