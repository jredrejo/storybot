"""System status endpoints."""

from fastapi import APIRouter, Depends

from app.dependencies import get_hardware
from app.models.system import SystemStatus
from app.services.hardware_manager import HardwareManager


router = APIRouter()


@router.get("/status", response_model=SystemStatus)
async def get_system_status(
    hardware: HardwareManager = Depends(get_hardware),
) -> SystemStatus:
    """Get system status including all hardware services.

    Returns:
        SystemStatus with hardware states, uptime, and version
    """
    status_dict = await hardware.get_status()
    return SystemStatus(**status_dict)


@router.post("/rescan", response_model=SystemStatus)
async def rescan_hardware(
    hardware: HardwareManager = Depends(get_hardware),
) -> SystemStatus:
    """Rescan for hardware changes.

    Returns:
        Updated SystemStatus after rescan
    """
    status_dict = await hardware.rescan()
    return SystemStatus(**status_dict)
