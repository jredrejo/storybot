"""StoryBot FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import ConfigManager
from app.routers.nfc import router as nfc_router
from app.routers.system import router as system_router
from app.services.hardware_manager import HardwareManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Initialize hardware manager and config on startup.
    Shutdown services on shutdown.
    """
    # Startup
    hardware = HardwareManager()
    config = ConfigManager()

    # Store in app state
    app.state.hardware = hardware
    app.state.config = config

    # Initialize config
    _ = config.load()

    # Initialize hardware detection (stub for now)
    await hardware.detect_hardware()

    yield

    # Shutdown
    await hardware.shutdown()


app = FastAPI(
    title="StoryBot",
    description="Storytelling robot for children",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"status": "ok", "service": "storybot"}


# Include routers
app.include_router(system_router, prefix="/api/system", tags=["system"])
app.include_router(nfc_router)
