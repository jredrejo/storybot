"""Pytest configuration and fixtures."""
import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write('{"led_brightness": 255, "audio_volume": 1.0}')
        temp_path = f.name
    yield Path(temp_path)
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)
