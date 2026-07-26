"""
API-facing project and generation schemas.

These Pydantic models are used for FastAPI request/response serialization.
They are intentionally separate from database models (Firestore TypedDicts)
to allow independent evolution of the API contract and persistence layer.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class GenerationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InputType(str, Enum):
    TEXT = "text"
    TOPIC = "topic"
    PDF = "pdf"
    IMAGE = "image"
    SCREENSHOT = "screenshot"
    HANDWRITTEN = "handwritten"


# ── Project Schemas ────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    """Request body for POST /projects."""

    title: str = Field(min_length=1, max_length=200, description="Project name")
    description: str = Field(default="", max_length=1000)
    input_type: InputType = Field(default=InputType.TEXT)
    input_text: str = Field(
        default="",
        description="Educational content as plain text (for text/topic inputs)"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProjectResponse(BaseModel):
    """Response model for project read operations."""

    id: str
    user_id: str = ""
    title: str
    description: str
    input_type: str
    input_text: str
    input_file_url: str
    status: GenerationStatus | str
    created_at: datetime | str
    updated_at: datetime | str
    metadata: dict[str, Any]

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Paginated list of projects."""

    items: list[ProjectResponse]
    total: int
    limit: int
    offset: int


# ── Job / Generation Schemas ───────────────────────────────────────────────────

class GenerationRequest(BaseModel):
    """Request body for POST /generate."""

    project_id: str = Field(description="Project to generate video for")
    force_regenerate: bool = Field(
        default=False,
        description="If True, regenerate even if a video already exists"
    )
    quality: str = Field(
        default="medium_quality",
        description="Manim render quality: low_quality | medium_quality | high_quality"
    )
    tts_engine: str = Field(
        default="edge-tts",
        description="TTS engine to use: edge-tts | gtts"
    )
    tts_voice: str = Field(default="en-US-AriaNeural")


class StageLog(BaseModel):
    """A single pipeline log entry."""

    stage: str
    status: str
    message: str
    timestamp: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class JobResponse(BaseModel):
    """Response model for job status queries."""

    id: str
    project_id: str
    user_id: str = ""
    status: GenerationStatus | str = GenerationStatus.PENDING
    current_stage: str = ""
    stages_completed: list[str] = Field(default_factory=list)
    progress_percent: float = 0.0
    result_data: dict[str, Any] = Field(default_factory=dict)
    error_message: str = ""
    error_stage: str = ""
    retry_count: int = 0
    started_at: datetime | str | None = None
    completed_at: datetime | str | None = None
    created_at: datetime | str | None = None
    updated_at: datetime | str | None = None
    duration_seconds: float = 0.0
    graph_state_ref: str = ""
    logs: list[dict[str, Any]] = Field(default_factory=list)

    model_config = {"from_attributes": True}


# ── Video Schemas ─────────────────────────────────────────────────────────────

class VideoResponse(BaseModel):
    """Response model for a generated video."""

    id: str
    project_id: str
    user_id: str = ""
    job_id: str = ""
    title: str = "Generated Video"
    duration_seconds: float = 0.0
    resolution: str = "1080p"
    file_url: str = ""
    audio_url: str = ""
    transcript_url: str = ""
    manim_script_url: str = ""
    storyboard_url: str = ""
    thumbnail_url: str = ""
    file_size_bytes: int = 0
    created_at: datetime | str | None = None
    updated_at: datetime | str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


# ── SSE Progress ──────────────────────────────────────────────────────────────

class ProgressEvent(BaseModel):
    """Server-Sent Event payload for live job progress."""

    event_type: str = Field(
        description="stage_start | stage_complete | log | error | done"
    )
    job_id: str
    stage: str
    message: str
    progress_percent: int = Field(ge=0, le=100)
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: str

    def to_sse(self) -> str:
        """Format as SSE wire format."""
        import json
        data = self.model_dump()
        return f"data: {json.dumps(data)}\n\n"
