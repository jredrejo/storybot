"""NFC reader service with real and mock implementations."""

import threading
import time
from collections.abc import Callable

from app.services.base import HardwareService


class NFCService(HardwareService):
    """Protocol for NFC service."""

    @property
    def is_mock(self) -> bool:
        """Return True if this is a mock service."""
        ...

    async def start_polling(self, callback: Callable[[str], None]) -> None:
        """Start polling for NFC cards.

        Args:
            callback: Function to call when card tapped, receives UID as string.
        """
        ...

    async def stop_polling(self) -> None:
        """Stop polling for NFC cards."""
        ...

    @property
    def is_polling(self) -> bool:
        """Check if currently polling."""
        ...


class RealNFCService(NFCService):
    """Real NFC service using nfcpy."""

    def __init__(self) -> None:
        """Initialize real NFC service."""
        self._polling = False
        self._poll_thread: threading.Thread | None = None
        self._callback: Callable[[str], None] | None = None
        self._available = self._check_availability()

    @property
    def is_mock(self) -> bool:
        """Return False - this is real NFC service."""
        return False

    def _check_availability(self) -> bool:
        """Check if NFC hardware is available."""
        try:
            import nfc

            return True
        except (ImportError, OSError):
            return False

    async def start_polling(self, callback: Callable[[str], None]) -> None:
        """Start polling for NFC cards in background thread."""
        if not self._available:
            raise RuntimeError("NFC hardware not available")

        if self._polling:
            return  # Already polling

        self._callback = callback
        self._polling = True
        self._poll_thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="NFCPoller"
        )
        self._poll_thread.start()

    def _poll_loop(self) -> None:
        """Background thread polling loop."""
        import nfc

        clf = nfc.ContactlessFrontend()

        # Try to open USB reader
        try:
            clf.open("usb")
        except Exception:
            # Failed to open reader
            self._polling = False
            return

        # Poll for cards with exponential backoff on disconnect
        backoff_time = 0.5

        while self._polling:
            try:
                # Wait for card tap
                tag = clf.sense(
                    nfc.clf.RemoteTarget("106A"),  # Type A (MIFARE etc)
                    iterations=1,
                    interval=0.1,
                )

                if tag is not None and self._callback:
                    # Convert tag ID to hex string
                    uid = ":".join([f"{b:02X}" for b in tag.identifier])
                    self._callback(uid)
                    backoff_time = 0.5  # Reset backoff on success

            except Exception:
                # Connection lost - increase backoff
                backoff_time = min(backoff_time * 2, 5.0)

            time.sleep(0.1)

        try:
            clf.close()
        except Exception:
            pass

    async def stop_polling(self) -> None:
        """Stop polling for NFC cards."""
        self._polling = False
        if self._poll_thread:
            self._poll_thread.join(timeout=2.0)
            self._poll_thread = None
        self._callback = None

    @property
    def is_polling(self) -> bool:
        """Check if currently polling."""
        return self._polling

    async def get_status(self) -> dict:
        """Get NFC service status."""
        if not self._available:
            return {
                "name": "nfc",
                "is_mock": self.is_mock,
                "status": "not_connected",
                "error_message": "NFC hardware not available",
            }

        status_val = "ok" if self._polling else "idle"
        return {
            "name": "nfc",
            "is_mock": self.is_mock,
            "status": status_val,
            "error_message": None,
        }

    async def initialize(self) -> None:
        """Initialize NFC service."""
        self._available = self._check_availability()

    async def shutdown(self) -> None:
        """Shutdown NFC service."""
        await self.stop_polling()


class MockNFCService(NFCService):
    """Mock NFC service for testing without hardware."""

    def __init__(self) -> None:
        """Initialize mock NFC service."""
        self._polling = False
        self._callback: Callable[[str], None] | None = None

    @property
    def is_mock(self) -> bool:
        """Return True - this is mock NFC service."""
        return True

    async def start_polling(self, callback: Callable[[str], None]) -> None:
        """Start mock polling (just stores callback)."""
        self._callback = callback
        self._polling = True

    async def stop_polling(self) -> None:
        """Stop mock polling."""
        self._polling = False
        self._callback = None

    @property
    def is_polling(self) -> bool:
        """Check if mock polling."""
        return self._polling

    def simulate_tap(self, uid: str) -> None:
        """Simulate a card tap (for testing).

        Args:
            uid: Card UID as hex string (e.g., "04:A3:5B:C2:D4:30").
        """
        if self._callback:
            self._callback(uid)

    async def get_status(self) -> dict:
        """Get mock NFC service status."""
        return {
            "name": "nfc",
            "is_mock": self.is_mock,
            "status": "ok",
            "error_message": None,
        }

    async def initialize(self) -> None:
        """Initialize mock NFC service."""
        self._polling = False

    async def shutdown(self) -> None:
        """Shutdown mock NFC service."""
        await self.stop_polling()


def create_nfc_service() -> NFCService:
    """Create appropriate NFC service based on hardware availability.

    Returns:
        RealNFCService if NFC hardware available, else MockNFCService.
    """
    # Try real first
    real_service = RealNFCService()
    if real_service._available:
        return real_service
    return MockNFCService()
