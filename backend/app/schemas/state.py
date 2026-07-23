"""
LangGraph shared state definition.

VideoGenerationState is the single TypedDict passed through every
node in the LangGraph workflow. Nodes return partial updates
(dict with only the fields they mutate).
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

from app.schemas.content import ExtractedContent
from app.schemas.lesson import LessonPlan
from app.schemas.manim import ExecutionResult, ManimScript
from app.schemas.narration import NarrationScript


class VideoGenerationState(TypedDict, total=False):
    """
    Shared state object flowing through every LangGraph node.

    Fields are Optional by default (total=False) so nodes can return
    partial state updates. The Supervisor initializes required fields.
    """

    # ── Identity ──────────────────────────────────────────────────────────
    project_id: str
    job_id: str
    thread_id: str            # LangGraph thread identifier for checkpointing

    # ── Input ─────────────────────────────────────────────────────────────
    input_type: str           # InputType enum value
    input_text: str           # Raw text if input is text/topic
    input_file_path: str      # Local path if input is file (PDF/image)
    input_file_url: str       # Firebase Storage URL of uploaded input

    # ── Routing flags (set by Supervisor) ────────────────────────────────
    requires_ocr: bool        # True when input is PDF / image / handwritten
    ocr_completed: bool
    content_generated: bool
    manim_script_generated: bool
    execution_successful: bool
    narration_completed: bool
    synchronization_completed: bool

    # ── Retry tracking ────────────────────────────────────────────────────
    repair_retry_count: int
    max_repair_retries: int

    # ── Agent outputs ─────────────────────────────────────────────────────
    extracted_content: ExtractedContent | None
    lesson_plan: LessonPlan | None
    manim_script: ManimScript | None
    execution_result: ExecutionResult | None
    narration_script: NarrationScript | None

    # ── File paths (local) ────────────────────────────────────────────────
    render_output_dir: str
    video_file_path: str          # Final MP4 after sync
    audio_file_path: str          # Combined narration audio
    transcript_file_path: str
    manim_script_file_path: str   # The .py file written to disk

    # ── Firebase Storage URLs ─────────────────────────────────────────────
    video_url: str
    audio_url: str
    transcript_url: str
    manim_script_url: str
    storyboard_url: str

    # ── Generation config ─────────────────────────────────────────────────
    render_quality: str           # low_quality | medium_quality | high_quality
    tts_engine: str
    tts_voice: str

    # ── Error tracking ────────────────────────────────────────────────────
    error_message: str
    error_stage: str
    has_error: bool

    # ── Progress / logging ────────────────────────────────────────────────
    current_stage: str
    stage_logs: Annotated[list[dict[str, Any]], operator.add]

    # ── Final output metadata ─────────────────────────────────────────────
    video_id: str
    video_duration_seconds: float


def create_initial_state(
    project_id: str,
    job_id: str,
    input_type: str,
    input_text: str = "",
    input_file_path: str = "",
    input_file_url: str = "",
    render_quality: str = "medium_quality",
    tts_engine: str = "edge-tts",
    tts_voice: str = "en-US-AriaNeural",
    render_output_dir: str = "./renders",
    max_repair_retries: int = 3,
) -> VideoGenerationState:
    """Factory function that creates a fully initialized state object."""
    import uuid
    return VideoGenerationState(
        project_id=project_id,
        job_id=job_id,
        thread_id=f"{project_id}-{job_id}",
        input_type=input_type,
        input_text=input_text,
        input_file_path=input_file_path,
        input_file_url=input_file_url,
        requires_ocr=False,
        ocr_completed=False,
        content_generated=False,
        manim_script_generated=False,
        execution_successful=False,
        narration_completed=False,
        synchronization_completed=False,
        repair_retry_count=0,
        max_repair_retries=max_repair_retries,
        extracted_content=None,
        lesson_plan=None,
        manim_script=None,
        execution_result=None,
        narration_script=None,
        render_output_dir=render_output_dir,
        video_file_path="",
        audio_file_path="",
        transcript_file_path="",
        manim_script_file_path="",
        video_url="",
        audio_url="",
        transcript_url="",
        manim_script_url="",
        storyboard_url="",
        render_quality=render_quality,
        tts_engine=tts_engine,
        tts_voice=tts_voice,
        error_message="",
        error_stage="",
        has_error=False,
        current_stage="supervisor",
        stage_logs=[],
        video_id="",
        video_duration_seconds=0.0,
    )
