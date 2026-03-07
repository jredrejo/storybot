"""Hardware service manager."""

import time
from typing import Dict

from app.services.base import HardwareService
from app.models.system import HardwareState, SystemStatus


class HardwareManager:
    """Manage hardware services and detect hardware."""

    def __init__(self) -> None:
        """Initialize hardware manager."""
        self._services: Dict[str, HardwareService] = {}
        self._start_time = time.time()
        self._version = "0.1.0"

    def register_service(self, name: str, service: HardwareService) -> None:
        """Register a hardware service.

        Args:
            name: Service name (e.g., "nfc", "led", "audio")
            service: HardwareService instance
        """
        self._services[name] = service

    async def get_status(self) -> dict:
        """Get status of all hardware services.

        Returns:
            dict with SystemStatus data
        """
        hardware_states = {}

        for name, service in self._services.items():
            try:
                service_status = await service.get_status()
                hardware_states[name] = HardwareState(**service_status)
            except Exception as e:
                # If service fails to report status, mark as error
                hardware_states[name] = HardwareState(
                    name=name,
                    is_mock=getattr(service, "is_mock", True),
                    status="error",
                    error_message=str(e),
                )

        status = SystemStatus(
            hardware=hardware_states,
            uptime_seconds=time.time() - self._start_time,
            version=self._version,
        )
        return status.dict()

    async def detect_hardware(self) -> None:
        """Detect available hardware.

        This is a stub for now - individual hardware detection
        will be implemented in subsequent plans.
        """
        # Stub: Hardware detection will be implemented in Plan 02
        pass

    async def rescan(self) -> dict:
        """Rescan for hardware changes.

        Returns:
            Updated SystemStatus dict
        """
        await self.detect_hardware()
        return await self.get_status()

    async def shutdown(self) -> None:
        """Shutdown all hardware services."""
        for service in self._services.values():
            try:
                await service.shutdown()
            except Exception:
                # Ignore shutdown errors
                pass
        self._services.clear()
