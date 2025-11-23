import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.mongodb import MongoDB
from app.api.v1.router import api_router
from app.services.upstox_service import upstox_service
from app.services.scheduler import scheduler_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting TradeLit API...")
    await MongoDB.connect_db()

    # Load Upstox token from database
    await upstox_service.load_token_from_db()

    # Start scheduler and register tasks
    scheduler_service.start()
    scheduler_service.register_tasks()
    print("⏰ Scheduler started with all tasks registered")

    yield
    # Shutdown
    print("👋 Shutting down TradeLit API...")

    # Shutdown scheduler
    scheduler_service.shutdown(wait=True)

    await MongoDB.close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Algo Trading Application API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to TradeLit API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "database": settings.DATABASE_NAME,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }





if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
