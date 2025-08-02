"""
NBA 2K Global Rankings Backend with Supabase
Main application entry point for Supabase version
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, admin, discord, payments
from app.routers.players import router as players_router
from app.routers.events import router as events_router
from app.routers.leaderboard_supabase import router as leaderboard_router

# Initialize FastAPI app
app = FastAPI(
    title="NBA 2K Global Rankings API (Supabase)",
    description="Backend API for NBA 2K Global Rankings system using Supabase",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - using Supabase versions where available
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(players_router, prefix="/players", tags=["Players"])
app.include_router(events_router, prefix="/events", tags=["Events"])
app.include_router(leaderboard_router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(discord.router, prefix="/discord", tags=["Discord"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_supabase:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
