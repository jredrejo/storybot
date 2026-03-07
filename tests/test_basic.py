"""Basic import tests to verify setup."""
import sys


def test_imports():
    """Test that all modules can be imported."""
    try:
        from app.config import ConfigManager, Settings
        from app.services.base import HardwareService
        from app.services.hardware_manager import HardwareManager
        from app.models.system import HardwareState, SystemStatus
        from app.dependencies import get_hardware, get_config
        from app.main import app
        print("All imports successful!")
        return True
    except Exception as e:
        print(f"Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
