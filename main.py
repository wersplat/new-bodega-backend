"""
NBA 2K Global Rankings Backend
Main application entry point
"""

from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.supabase import supabase
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
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
async def root():
    """
    Root endpoint that responds to both GET and HEAD requests.
    
    Returns:
        dict: A welcome message for the NBA 2K Global Rankings API
    """
    return {
        "message": "NBA 2K Global Rankings API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health", tags=["Health"])
@app.head("/health")
async def health_check():
    """
    Health check endpoint that responds to both GET and HEAD requests.
    
    Returns:
        dict: Health status of the API and its dependencies
    """
    # Check database connectivity
    db_status = "ok"
    try:
        # Simple query to check database connectivity
        supabase.get_client().rpc('version').execute()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )