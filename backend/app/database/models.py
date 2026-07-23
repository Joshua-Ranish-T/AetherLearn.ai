"""
Firestore document models.

These TypedDicts map 1-to-1 with Firestore collection documents.
They are the persistence layer representation (not the API layer).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict


class ProjectDocument(TypedDict, total=False):
    """Firestore: /projects/{project_id}"""

    id: str
    title: str
    description: str
    input_type: str                  # "text" | "pdf" | "image" | "topic"
    input_text: str                  # raw text input (if any)
    input_file_url: str              # Firebase Storage URL for uploaded file
    status: str                      # GenerationStatus enum value
    created_at: datetime | str
    updated_at: datetime | str
    metadata: dict[str, Any]


class JobDocument(TypedDict, total=False):
    """Firestore: /jobs/{job_id}"""

    id: str
    project_id: str
    status: str                      # "pending" | "running" | "completed" | "failed"
    current_stage: str               # current LangGraph node name
    stages_completed: list[str]
    progress_percent: float
    error_message: str
    error_stage: str
    retry_count: int
    created_at: datetime | str
    updated_at: datetime | str
    started_at: datetime | str
    completed_at: datetime | str | None
    duration_seconds: float
    logs: list[dict[str, Any]]       # append-only execution log entries
    result_data: dict[str, Any]
    graph_state_ref: str             # Firestore doc path to serialized graph state


class VideoDocument(TypedDict, total=False):
    """Firestore: /videos/{video_id}"""

    id: str
    project_id: str
    job_id: str
    title: str
    duration_seconds: float
    resolution: str                  # e.g. "1280x720"
    file_url: str                    # Firebase Storage signed URL for MP4
    audio_url: str                   # Firebase Storage URL for narration audio
    transcript_url: str              # Firebase Storage URL for transcript text
    manim_script_url: str            # Firebase Storage URL for generated .py
    storyboard_url: str              # Firebase Storage URL for storyboard JSON
    thumbnail_url: str               # Firebase Storage URL for thumbnail image
    file_size_bytes: int
    created_at: datetime | str
    updated_at: datetime | str
    metadata: dict[str, Any]


class CheckpointDocument(TypedDict, total=False):
    """Firestore: /checkpoints/{thread_id}/snapshots/{checkpoint_id}"""

    thread_id: str
    checkpoint_id: str
    parent_checkpoint_id: str
    state: dict[str, Any]           # serialized LangGraph state
    created_at: datetime | str
    metadata: dict[str, Any]
