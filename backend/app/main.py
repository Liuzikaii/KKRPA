"""
KKRPA - FastAPI Application Entry Point (Desktop Mode)
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import init_db
from app.api.auth import router as auth_router
from app.api.workflows import router as workflow_router
from app.api.tasks import router as task_router
from app.api.schedules import router as schedule_router
from app.api.license import router as license_router
from app.workers.scheduler import start_scheduler, stop_scheduler
from app.core.license import get_current_edition
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    # Initialize database
    await init_db()
    logger.info("Database initialized (SQLite)")

    # Load license
    edition = get_current_edition()
    settings.EDITION = edition
    logger.info(f"Edition: {edition}")

    # Start scheduler
    start_scheduler()
    logger.info("Scheduler started")

    yield

    # Cleanup
    stop_scheduler()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="自动化流程图形化编程平台 - Desktop Edition",
    lifespan=lifespan,
)

# CORS - allow Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Desktop mode - allow all local origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(license_router)
app.include_router(auth_router)
app.include_router(workflow_router)
app.include_router(task_router)
app.include_router(schedule_router)


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "edition": settings.EDITION,
        "mode": "desktop",
    }
