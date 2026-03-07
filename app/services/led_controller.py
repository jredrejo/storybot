"""LED controller service with real and mock implementations."""

from app.services.base import HardwareService


class LEDService(HardwareService):
    """Protocol for LED service."""

    @property
    def is_mock(self) -> bool:
        """Return True if this is a mock service."""
        ...

    async def set_color(self, r: int, g: int, b: int) -> None:
        """Set LED color.

        Args:
            r: Red component (0-255).
            g: Green component (0-255).
            b: Blue component (0-255).
        """
        ...

    def get_color(self) -> tuple[int, int, int]:
        """Get current LED color.

        Returns:
            Tuple of (r, g, b) values.
        """
        ...

    async def turn_off(self) -> None:
        """Turn off LEDs."""
        ...


class RealLEDService(LEDService):
    """Real LED service (placeholder - hardware TBD)."""

    def __init__(self) -> None:
        """Initialize real LED service."""
        self._color: tuple[int, int, int] = (0, 0, 0)
        self._available = False  # Hardware not verified yet

    @property
    def is_mock(self) -> bool:
        """Return False - this is real LED service."""
        return False

    async def set_color(self, r: int, g: int, b: int) -> None:
        """Set LED color (logs for now - actual hardware TBD)."""
        # Clamp values to 0-255
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        self._color = (r, g, b)

        # TODO: Implement actual LED hardware control
        # Documented in STATE.md: LED hardware needs verification
        # Options: Govee USB, serial RGB controller, etc.

    def get_color(self) -> tuple[int, int, int]:
        """Get current LED color."""
        return self._color

    async def turn_off(self) -> None:
        """Turn off LEDs."""
        await self.set_color(0, 0, 0)

    async def get_status(self) -> dict:
        """Get LED service status."""
        if not self._available:
            return {
                "name": "led",
                "is_mock": self.is_mock,
                "status": "not_connected",
                "error_message": "LED hardware not verified",
            }

        return {
            "name": "led",
            "is_mock": self.is_mock,
            "status": "ok",
            "error_message": None,
        }

    async def initialize(self) -> None:
        """Initialize LED service."""
        # Hardware detection not implemented yet
        self._available = False

    async def shutdown(self) -> None:
        """Shutdown LED service."""
        await self.turn_off()


class MockLEDService(LEDService):
    """Mock LED service for testing without hardware."""

    def __init__(self) -> None:
        """Initialize mock LED service."""
        self._color: tuple[int, int, int] = (0, 0, 0)

    @property
    def is_mock(self) -> bool:
        """Return True - this is mock LED service."""
        return True

    async def set_color(self, r: int, g: int, b: int) -> None:
        """Set mock LED color (tracks state only)."""
        # Clamp values to 0-255
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))

        self._color = (r, g, b)

    def get_color(self) -> tuple[int, int, int]:
        """Get current mock LED color."""
        return self._color

    async def turn_off(self) -> None:
        """Turn off mock LEDs."""
        self._color = (0, 0, 0)

    async def get_status(self) -> dict:
        """Get mock LED service status."""
        return {
            "name": "led",
            "is_mock": self.is_mock,
            "status": "ok",
            "error_message": None,
        }

    async def initialize(self) -> None:
        """Initialize mock LED service."""
        self._color = (0, 0, 0)

    async def shutdown(self) -> None:
        """Shutdown mock LED service."""
        await self.turn_off()


def create_led_service() -> LEDService:
    """Create appropriate LED service based on hardware availability.

    Returns:
        RealLEDService if LED hardware available, else MockLEDService.
    """
    # For now, always return mock until LED hardware is verified
    # TODO: Implement hardware detection once LED device is chosen
    return MockLEDService()
