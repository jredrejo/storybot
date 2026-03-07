"""FastAPI dependencies."""

from fastapi import Request

from app.services.hardware_manager import HardwareManager
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
