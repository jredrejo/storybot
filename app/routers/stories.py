"""Story CRUD API endpoints."""

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.requests import Request

from app.dependencies import get_story_manager
from app.models.story import Story, StoryCreate, StoryList
from app.services.story_manager import StoryManager

router = APIRouter()

# Valid audio content types
VALID_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/x-wav"}


@router.post("/api/stories", response_model=Story, status_code=status.HTTP_201_CREATED)
async def create_story(
    request: Request,
    title: str = Form(...),
    emoji: str = Form(...),
    led_color: str = Form(...),
    audio: UploadFile = File(...),
    cover: UploadFile | None = File(None),
    story_manager: StoryManager = Depends(get_story_manager),
) -> Story:
    """Create a new story with audio file and optional cover image.

    Args:
        request: FastAPI request
        title: Story title
        emoji: Story emoji icon
        led_color: LED color in hex format
        audio: Audio file upload
        cover: Optional cover image upload
        story_manager: StoryManager instance

    Returns:
        Created Story object

    Raises:
        HTTPException: If audio file is invalid or missing
    """
    # Validate audio content type
    if audio.content_type not in VALID_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid audio type. Must be one of: {VALID_AUDIO_TYPES}",
        )

    # Generate UUID for story
    story_id = str(uuid.uuid4())

    # Create story directory
    story_dir = Path("content/stories") / story_id
    story_dir.mkdir(parents=True, exist_ok=True)

    # Save audio file
    audio_ext = Path(audio.filename).suffix or ".mp3"
    audio_path = story_dir / f"audio{audio_ext}"
    with audio_path.open("wb") as f:
        shutil.copyfileobj(audio.file, f)

    # Save cover image if provided
    cover_filename = None
    if cover:
        cover_ext = Path(cover.filename).suffix or ".jpg"
        cover_path = story_dir / f"cover{cover_ext}"
        with cover_path.open("wb") as f:
            shutil.copyfileobj(cover.file, f)
        cover_filename = f"cover{cover_ext}"

    # Create story in manager
    story = story_manager.create_story(
        id=story_id,
        title=title,
        emoji=emoji,
        led_color=led_color,
        audio_file=f"audio{audio_ext}",
        cover_image=cover_filename,
    )

    return story


@router.get("/api/stories", response_model=StoryList)
async def list_stories(
    story_manager: StoryManager = Depends(get_story_manager),
) -> StoryList:
    """List all stories.

    Args:
        story_manager: StoryManager instance

    Returns:
        StoryList with stories and total count
    """
    stories = story_manager.list_stories()
    return StoryList(stories=stories, total=len(stories))


@router.get("/api/stories/{story_id}", response_model=Story)
async def get_story(
    story_id: str,
    story_manager: StoryManager = Depends(get_story_manager),
) -> Story:
    """Get a single story by ID.

    Args:
        story_id: Story ID
        story_manager: StoryManager instance

    Returns:
        Story object

    Raises:
        HTTPException: If story not found
    """
    story = story_manager.get_story(story_id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story '{story_id}' not found",
        )
    return story


@router.delete("/api/stories/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
    story_id: str,
    request: Request,
    story_manager: StoryManager = Depends(get_story_manager),
) -> None:
    """Delete a story by ID.

    Args:
        story_id: Story ID
        request: FastAPI request
        story_manager: StoryManager instance

    Raises:
        HTTPException: If story not found
    """
    # Delete from manager
    deleted = story_manager.delete_story(story_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story '{story_id}' not found",
        )

    # Delete story directory
    story_dir = Path("content/stories") / story_id
    if story_dir.exists():
        shutil.rmtree(story_dir)
