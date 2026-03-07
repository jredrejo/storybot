"""Base hardware service protocol."""

from typing import Protocol


class HardwareService(Protocol):
    """Protocol for hardware services."""

    @property
    def is_mock(self) -> bool:
        """Return True if this is a mock service."""
        ...

    async def get_status(self) -> dict:
        """Get service status.

        Returns:
            dict with keys: name, is_mock, status, error_message (optional)
        """
        ...

    async def initialize(self) -> None:
        """Initialize the hardware service."""
        ...

    async def shutdown(self) -> None:
        """Shutdown the hardware service."""
        ...
