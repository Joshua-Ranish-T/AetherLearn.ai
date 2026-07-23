"""
Manim script and execution result schemas.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ManimScene(BaseModel):
    """Represents a single Manim scene class."""

    class_name: str = Field(description="Python class name, e.g. 'Scene01Intro'")
    scene_number: int
    scene_title: str
    python_code: str = Field(description="Complete Python class definition")
    dependencies: list[str] = Field(
        default_factory=list,
        description="Other scene classes this depends on"
    )


class ManimScript(BaseModel):
    """
    The complete generated Manim CE Python script.
    Each scene is kept as a separate ManimScene for modular rendering.
    """

    project_id: str
    script_version: int = Field(default=1)
    imports: str = Field(
        description="All import statements at the top of the file"
    )
    constants: str = Field(
        default="",
        description="Module-level constants and helper classes"
    )
    scenes: list[ManimScene]
    full_script: str = Field(
        description="Complete assembled Python script (imports + constants + all scenes)"
    )
    main_scene_class: str = Field(
        description="The primary scene class to render (if single file render)"
    )
    manim_version: str = Field(default="0.18.0")
    render_command: str = Field(
        description="Full manim CLI command to render this script"
    )


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SYNTAX_ERROR = "syntax_error"


class ExecutionResult(BaseModel):
    """
    The result of running Manim via subprocess.
    Returned by ManimExecutionService.
    """

    status: ExecutionStatus
    exit_code: int
    stdout: str = Field(default="")
    stderr: str = Field(default="")
    error_message: str = Field(default="")
    traceback: str = Field(default="")
    output_files: list[str] = Field(
        default_factory=list,
        description="Absolute paths to generated media files"
    )
    render_duration_seconds: float = Field(default=0.0)
    script_path: str = Field(default="")
    logs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.status == ExecutionStatus.SUCCESS

    @property
    def primary_output(self) -> str | None:
        """Return the first (primary) output file path, or None."""
        mp4_files = [f for f in self.output_files if f.endswith(".mp4")]
        return mp4_files[0] if mp4_files else (self.output_files[0] if self.output_files else None)
