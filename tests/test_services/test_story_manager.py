"""Tests for StoryManager service."""

import json
from pathlib import Path

import pytest

from app.models.story import Story, StoryCreate
from app.services.story_manager import StoryManager


@pytest.fixture
def temp_content_dir(tmp_path: Path) -> Path:
    """Create a temporary content directory."""
    content_dir = tmp_path / "content" / "stories"
    content_dir.mkdir(parents=True)
    return content_dir


@pytest.fixture
def story_manager(temp_content_dir: Path) -> StoryManager:
    """Create a StoryManager with temporary directory."""
    # Patch the CONTENT_DIR to use temp directory
    manager = StoryManager()
    manager.CONTENT_DIR = temp_content_dir
    manager.INDEX_FILE = temp_content_dir / "stories.json"
    # Initialize empty index
    manager.INDEX_FILE.write_text(
        json.dumps({"version": 1, "stories": {}, "nfc_to_story": {}})
    )
    return manager


@pytest.fixture
def story_create_data() -> dict:
    """Sample story creation data."""
    return {
        "id": "test-story-1",
        "title": "Test Story",
        "emoji": "📚",
        "led_color": "#FF5733",
        "audio_file": "audio.mp3",
        "nfc_uid": None,
        "cover_image": None,
    }


class TestStoryManagerCreate:
    """Test StoryManager.create_story()."""

    def test_create_story_saves_to_index(
        self, story_manager: StoryManager, story_create_data: dict
    ):
        """Test that create_story saves story to index and returns Story object."""
        # Create story
        story = story_manager.create_story(**story_create_data)

        # Verify Story object returned
        assert isinstance(story, Story)
        assert story.id == "test-story-1"
        assert story.title == "Test Story"
        assert story.emoji == "📚"
        assert story.led_color == "#FF5733"
        assert story.audio_file == "audio.mp3"

        # Verify saved to index
        index = json.loads(story_manager.INDEX_FILE.read_text())
        assert "test-story-1" in index["stories"]
        assert index["stories"]["test-story-1"]["title"] == "Test Story"


class TestStoryManagerList:
    """Test StoryManager.list_stories()."""

    def test_list_stories_returns_all_stories(
        self, story_manager: StoryManager, story_create_data: dict
    ):
        """Test that list_stories returns all stories from index."""
        # Create multiple stories
        story_manager.create_story(**story_create_data)
        story_create_data["id"] = "test-story-2"
        story_create_data["title"] = "Another Story"
        story_manager.create_story(**story_create_data)

        # List stories
        stories = story_manager.list_stories()

        # Verify
        assert len(stories) == 2
        assert stories[0].id == "test-story-1"
        assert stories[1].id == "test-story-2"
        assert stories[0].title == "Test Story"
        assert stories[1].title == "Another Story"

    def test_list_stories_empty_returns_empty_list(
        self, story_manager: StoryManager
    ):
        """Test that list_stories returns empty list when no stories."""
        stories = story_manager.list_stories()
        assert stories == []


class TestStoryManagerGet:
    """Test StoryManager.get_story()."""

    def test_get_story_returns_single_story(
        self, story_manager: StoryManager, story_create_data: dict
    ):
        """Test that get_story returns single story or None."""
        # Create story
        created = story_manager.create_story(**story_create_data)

        # Get story
        story = story_manager.get_story("test-story-1")

        # Verify
        assert story is not None
        assert story.id == "test-story-1"
        assert story.title == "Test Story"
        assert story.emoji == "📚"

    def test_get_story_not_found_returns_none(
        self, story_manager: StoryManager
    ):
        """Test that get_story returns None for non-existent story."""
        story = story_manager.get_story("non-existent")
        assert story is None


class TestStoryManagerDelete:
    """Test StoryManager.delete_story()."""

    def test_delete_story_removes_from_index(
        self, story_manager: StoryManager, story_create_data: dict
    ):
        """Test that delete_story removes story from index."""
        # Create story
        story_manager.create_story(**story_create_data)

        # Verify it exists
        assert story_manager.get_story("test-story-1") is not None

        # Delete story
        result = story_manager.delete_story("test-story-1")

        # Verify deletion
        assert result is True
        assert story_manager.get_story("test-story-1") is None

        # Verify removed from index
        index = json.loads(story_manager.INDEX_FILE.read_text())
        assert "test-story-1" not in index["stories"]

    def test_delete_story_not_found_returns_false(
        self, story_manager: StoryManager
    ):
        """Test that delete_story returns False for non-existent story."""
        result = story_manager.delete_story("non-existent")
        assert result is False


class TestStoryManagerNFC:
    """Test StoryManager NFC assignment and lookup."""

    def test_assign_nfc_updates_story(
        self, story_manager: StoryManager, story_create_data: dict
    ):
        """Test that assign_nfc updates story's nfc_uid field."""
        # Create story
        story_manager.create_story(**story_create_data)

        # Assign NFC
        result = story_manager.assign_nfc("test-story-1", "04:A3:B5:C7:D9")

        # Verify returns Story object
        assert isinstance(result, Story)
        assert result.id == "test-story-1"
        assert result.nfc_uid == "04:A3:B5:C7:D9"

        # Verify story was updated
        story = story_manager.get_story("test-story-1")
        assert story.nfc_uid == "04:A3:B5:C7:D9"

        # Verify NFC mapping in index
        index = json.loads(story_manager.INDEX_FILE.read_text())
        assert index["nfc_to_story"]["04:A3:B5:C7:D9"] == "test-story-1"

    def test_assign_nfc_non_existent_story_returns_false(
        self, story_manager: StoryManager
    ):
        """Test that assign_nfc returns None for non-existent story."""
        result = story_manager.assign_nfc("non-existent", "04:A3:B5:C7:D9")
        assert result is None

    def test_get_story_by_nfc_returns_story(
        self, story_manager: StoryManager, story_create_data: dict
    ):
        """Test that get_story_by_nfc returns story for given NFC UID."""
        # Create story and assign NFC
        story_manager.create_story(**story_create_data)
        story_manager.assign_nfc("test-story-1", "04:A3:B5:C7:D9")

        # Get by NFC
        story = story_manager.get_story_by_nfc("04:A3:B5:C7:D9")

        # Verify
        assert story is not None
        assert story.id == "test-story-1"
        assert story.title == "Test Story"

    def test_get_story_by_nfc_not_found_returns_none(
        self, story_manager: StoryManager
    ):
        """Test that get_story_by_nfc returns None for unknown NFC UID."""
        story = story_manager.get_story_by_nfc("unknown-uid")
        assert story is None

    def test_assign_nfc_replaces_existing_nfc(
        self, story_manager: StoryManager, story_create_data: dict
    ):
        """Test that assigning new NFC replaces old one."""
        # Create story and assign first NFC
        story_manager.create_story(**story_create_data)
        story_manager.assign_nfc("test-story-1", "old-nfc-uid")

        # Assign new NFC
        story_manager.assign_nfc("test-story-1", "new-nfc-uid")

        # Verify only new NFC is mapped
        story = story_manager.get_story("test-story-1")
        assert story.nfc_uid == "new-nfc-uid"

        index = json.loads(story_manager.INDEX_FILE.read_text())
        assert "old-nfc-uid" not in index["nfc_to_story"]
        assert index["nfc_to_story"]["new-nfc-uid"] == "test-story-1"
