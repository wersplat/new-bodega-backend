"""
NBA 2K Global Rankings Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.routers import players, events, leaderboard, auth, admin, discord, payments

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

# Initialize FastAPI app
app = FastAPI(
    title="NBA 2K Global Rankings API",
    description="Backend API for NBA 2K Global Rankings system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(players.router, prefix="/players", tags=["Players"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(discord.router, prefix="/discord", tags=["Discord"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NBA 2K Global Rankings API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    ) 