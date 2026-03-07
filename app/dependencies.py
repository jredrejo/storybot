"""FastAPI dependencies."""

from fastapi import Request

from app.services.hardware_manager import HardwareManager
from app.services.story_manager import StoryManager
from app.config import ConfigManager


async def get_hardware(request: Request) -> HardwareManager:
    """Get hardware manager from app state.

    Args:
        request: FastAPI request

    Returns:
        HardwareManager instance
    """
    return request.app.state.hardware


async def get_config(request: Request) -> ConfigManager:
    """Get config manager from app state.

    Args:
        request: FastAPI request

    Returns:
        ConfigManager instance
    """
    return request.app.state.config


async def get_story_manager(request: Request) -> StoryManager:
    """Get story manager from app state.

    Args:
        request: FastAPI request

    Returns:
        StoryManager instance
    """
    return request.app.state.story_manager
