"""StoryBot FastAPI application."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import ConfigManager
from app.routers.nfc import router as nfc_router
from app.routers.stories import router as stories_router
from app.routers.system import router as system_router
from app.services.hardware_manager import HardwareManager
from app.services.story_manager import StoryManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Initialize hardware manager, config, and story manager on startup.
    Shutdown services on shutdown.
    """
    # Startup
    hardware = HardwareManager()
    config = ConfigManager()
    story_manager = StoryManager()

    # Store in app state
    app.state.hardware = hardware
    app.state.config = config
    app.state.story_manager = story_manager

    # Initialize config
    _ = config.load()

    # Initialize hardware detection (stub for now)
    await hardware.detect_hardware()

    # Ensure content directory exists
    content_dir = Path("content/stories")
    content_dir.mkdir(parents=True, exist_ok=True)

    # Ensure stories index exists
    index_file = content_dir / "stories.json"
    if not index_file.exists():
        import json
        index_file.write_text(json.dumps({"version": 1, "stories": {}, "nfc_to_story": {}}))

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
app.include_router(stories_router)

# Mount static files for story content
stories_static_dir = Path("content/stories")
if stories_static_dir.exists():
    app.mount("/static/stories", StaticFiles(directory=str(stories_static_dir)), name="stories")
