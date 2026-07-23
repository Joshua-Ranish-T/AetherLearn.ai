"""
Lesson and storyboard schemas.

These represent the structured educational output from the
Content Generation Agent — the blueprint for video creation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SceneObject(BaseModel):
    """An object to be displayed in a Manim scene."""

    object_type: str = Field(
        description="Type: text | equation | graph | code | diagram | shape | image"
    )
    content: str = Field(description="The content or expression to display")
    position: str = Field(
        default="CENTER",
        description="Manim position: CENTER | UP | DOWN | LEFT | RIGHT | UL | UR | DL | DR"
    )
    color: str = Field(default="WHITE", description="Manim color name or hex")
    scale: float = Field(default=1.0, description="Scale factor relative to default")


class SceneAnimation(BaseModel):
    """Describes how objects animate within a scene."""

    animation_type: str = Field(
        description="Manim animation: Write | FadeIn | Transform | DrawBorderThenFill | etc."
    )
    target_object: str = Field(description="Which object(s) this animation applies to")
    duration: float = Field(default=1.0, description="Animation duration in seconds")
    parameters: dict[str, str] = Field(
        default_factory=dict,
        description="Extra animation parameters (e.g. run_time, rate_func)"
    )


class StoryboardScene(BaseModel):
    """A single scene in the educational storyboard."""

    scene_number: int
    scene_title: str = Field(description="Short human-readable scene name")
    learning_objective: str = Field(
        description="What the viewer will learn in this scene"
    )
    objects: list[SceneObject] = Field(
        default_factory=list,
        description="Objects to display"
    )
    animations: list[SceneAnimation] = Field(
        default_factory=list,
        description="Animation sequence"
    )
    animation_description: str = Field(
        description="Prose description of what happens visually"
    )
    voice_segment: str = Field(
        description="Narration text spoken during this scene"
    )
    estimated_duration_seconds: float = Field(
        default=5.0, description="Estimated scene duration"
    )
    background_color: str = Field(
        default="#1a1a2e",
        description="Scene background color hex"
    )
    transition: str = Field(
        default="FadeIn",
        description="Transition type to next scene"
    )
    mathematical_expressions: list[str] = Field(
        default_factory=list,
        description="LaTeX expressions used in this scene"
    )
    code_snippet: str = Field(
        default="",
        description="Programming code displayed in this scene (if any)"
    )


class AnimationPlan(BaseModel):
    """High-level animation plan for the complete video."""

    total_scenes: int
    estimated_total_duration_seconds: float
    visual_theme: str = Field(description="Color scheme and style description")
    font_family: str = Field(default="default")
    background_color: str = Field(default="#1a1a2e")
    highlight_color: str = Field(default="#e94560")
    accent_color: str = Field(default="#0f3460")
    camera_movements: list[str] = Field(default_factory=list)
    special_effects: list[str] = Field(default_factory=list)
    notes: str = Field(default="")


class LessonPlan(BaseModel):
    """
    The complete educational lesson structure.
    This is the master document produced by the Content Generation Agent.
    """

    title: str
    subject: str = Field(description="Subject domain: math | physics | cs | chemistry | general")
    difficulty_level: str = Field(
        description="beginner | intermediate | advanced"
    )
    target_audience: str
    learning_objectives: list[str] = Field(
        description="Top-level learning objectives for the full lesson"
    )
    prerequisite_knowledge: list[str] = Field(default_factory=list)
    key_concepts: list[str] = Field(
        description="Core concepts covered in this lesson"
    )
    explanation: str = Field(
        description="Full step-by-step educational explanation (markdown)"
    )
    summary: str = Field(description="Concise lesson summary")
    storyboard: list[StoryboardScene] = Field(
        description="Scene-by-scene storyboard"
    )
    animation_plan: AnimationPlan
    full_narration_script: str = Field(
        description="Complete narration script combining all voice_segments"
    )
    estimated_video_duration_seconds: float
    keywords: list[str] = Field(default_factory=list)
