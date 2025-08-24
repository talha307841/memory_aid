"""
MemoryAid - AI-Powered Memory Assistant
Main FastAPI application with all endpoints and middleware
"""

import os
import asyncio
from contextlib import asynccontextmanager
from typing import List, Optional
import logging

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from routers import memory, chat, health
from services.background_scheduler import BackgroundScheduler
from services.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Global scheduler instance
scheduler: Optional[BackgroundScheduler] = None

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the API key from the Authorization header"""
    settings = get_settings()
    if credentials.credentials != settings.memory_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return credentials.credentials

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global scheduler
    
    # Startup
    logger.info("Starting MemoryAid application...")
    
    # Initialize background scheduler if demo mode is enabled
    settings = get_settings()
    if settings.demo_mode:
        scheduler = BackgroundScheduler()
        await scheduler.start()
        logger.info("Background scheduler started")
    
    yield
    
    # Shutdown
    if scheduler:
        await scheduler.stop()
        logger.info("Background scheduler stopped")
    logger.info("MemoryAid application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="MemoryAid API",
    description="AI-powered memory assistant with image capture and search capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with API key protection
app.include_router(
    memory.router,
    prefix="/memory",
    tags=["memory"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    health.router,
    prefix="/health",
    tags=["health"],
    dependencies=[Depends(verify_api_key)]
)

# Add simulate endpoint directly for easier access
@app.post("/simulate/capture", dependencies=[Depends(verify_api_key)])
async def simulate_capture():
    """Simulate a photo capture immediately"""
    from services.memory_service import MemoryService
    
    try:
        memory_service = MemoryService()
        memory_id = await memory_service.simulate_capture()
        return {
            "success": True,
            "memory_id": memory_id,
            "message": "Simulated capture completed successfully"
        }
    except Exception as e:
        logger.error(f"Error in simulated capture: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Capture simulation failed: {str(e)}"
        )

@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "MemoryAid API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
