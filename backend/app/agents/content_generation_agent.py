"""
Content Generation Agent — Core Reasoning Agent.

Responsibilities:
- Understand extracted or raw educational content
- Generate lesson structure, explanation, and teaching flow
- Produce complete storyboard with scene-by-scene visual plan
- Generate narration script
- Return structured LessonPlan (Pydantic model)

Uses Gemini 1.5 Pro for highest quality output.
"""

from __future__ import annotations

import json
from typing import Any

import google.generativeai as genai

from app.core.config import get_settings
from app.core.exceptions import ContentGenerationError
from app.core.logging_config import get_logger
from app.prompts.content_generation import (
    LESSON_PLAN_SYSTEM_PROMPT,
    build_lesson_plan_prompt,
)
from app.schemas.content import ExtractedContent, InputType
from app.schemas.lesson import (
    AnimationPlan,
    LessonPlan,
    SceneAnimation,
    SceneObject,
    StoryboardScene,
)
from app.schemas.state import VideoGenerationState

logger = get_logger(__name__)


class ContentGenerationAgent:
    """
    Core reasoning agent that produces the complete lesson plan
    and storyboard using Gemini Pro.
    """

    def __init__(self) -> None:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            system_instruction=LESSON_PLAN_SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8192,
                response_mime_type="application/json",
            ),
        )

    def run(self, state: VideoGenerationState) -> dict:
        """
        Generate lesson plan and storyboard.

        Returns:
            Partial state update with lesson_plan.
        """
        # ── Resolve input ──────────────────────────────────────────────────
        extracted: ExtractedContent | None = state.get("extracted_content")

        if extracted:
            raw_text = extracted.raw_text
            equations = extracted.equations
            code_blocks = extracted.code_blocks
            input_type = extracted.input_type.value
            subject_domain = extracted.subject_domain or "general"
        else:
            # Direct text/topic input
            raw_text = state.get("input_text", "")
            equations = []
            code_blocks = []
            input_type = state.get("input_type", InputType.TEXT.value)
            subject_domain = self._detect_subject(raw_text)

        if not raw_text.strip():
            raise ContentGenerationError(
                "No content available for lesson generation.",
                context={"input_type": input_type},
            )

        logger.info(
            "Content generation agent executing",
            text_length=len(raw_text),
            subject=subject_domain,
        )

        # ── Build prompt ───────────────────────────────────────────────────
        prompt = build_lesson_plan_prompt(
            extracted_text=raw_text,
            subject_domain=subject_domain,
            equations=equations,
            code_blocks=code_blocks,
            input_type=input_type,
        )

        # ── Call Gemini ────────────────────────────────────────────────────
        try:
            response = self._model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "max_output_tokens": 16384
                }
            )
            raw_json = response.text
        except Exception as exc:
            raise ContentGenerationError(
                f"Gemini API call failed: {exc}",
                context={"model": get_settings().gemini_model},
            ) from exc

        # ── Parse response ─────────────────────────────────────────────────
        try:
            data = self._parse_json_response(raw_json)
        except Exception as exc:
            raise ContentGenerationError(
                f"Failed to parse Gemini response as JSON: {exc}",
                context={"raw_response_preview": raw_json[:500]},
            ) from exc

        # ── Build Pydantic model ───────────────────────────────────────────
        try:
            lesson_plan = self._build_lesson_plan(data)
        except Exception as exc:
            raise ContentGenerationError(
                f"Failed to construct LessonPlan model: {exc}",
                context={"data_keys": list(data.keys())},
            ) from exc

        logger.info(
            "Content generation completed",
            title=lesson_plan.title,
            scenes=len(lesson_plan.storyboard),
            duration=lesson_plan.estimated_video_duration_seconds,
        )

        return {"lesson_plan": lesson_plan}

    # ─────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────

    def _detect_subject(self, text: str) -> str:
        """Heuristic subject detection from text keywords."""
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["derivative", "integral", "calculus", "equation", "theorem"]):
            return "math"
        if any(kw in text_lower for kw in ["force", "velocity", "quantum", "thermodynamics", "momentum"]):
            return "physics"
        if any(kw in text_lower for kw in ["algorithm", "function", "class", "array", "recursion", "def ", "import "]):
            return "cs"
        if any(kw in text_lower for kw in ["molecule", "atom", "reaction", "bond", "element"]):
            return "chemistry"
        return "general"

    def _parse_json_response(self, raw: str) -> dict[str, Any]:
        """Extract and parse JSON from Gemini response."""
        raw = raw.strip()
        
        # If there are markdown fences, extract the content inside the first one
        if "```" in raw:
            import re
            match = re.search(r"```(?:json)?\n(.*?)```", raw, re.DOTALL)
            if match:
                raw = match.group(1).strip()
        
        # In case there's still garbage around the JSON object
        if raw.startswith("{") and not raw.endswith("}"):
            last_brace = raw.rfind("}")
            if last_brace != -1:
                raw = raw[:last_brace+1]
        elif not raw.startswith("{") and "{" in raw:
            first_brace = raw.find("{")
            last_brace = raw.rfind("}")
            if first_brace != -1 and last_brace != -1:
                raw = raw[first_brace:last_brace+1]
                
        return json.loads(raw)

    def _build_lesson_plan(self, data: dict[str, Any]) -> LessonPlan:
        """Construct a validated LessonPlan from raw dict."""
        # Build animation plan
        anim_data = data.get("animation_plan", {})
        animation_plan = AnimationPlan(
            total_scenes=anim_data.get("total_scenes", len(data.get("storyboard", []))),
            estimated_total_duration_seconds=anim_data.get(
                "estimated_total_duration_seconds",
                data.get("estimated_video_duration_seconds", 60.0),
            ),
            visual_theme=anim_data.get("visual_theme", "Dark educational theme"),
            background_color=anim_data.get("background_color", "#1a1a2e"),
            highlight_color=anim_data.get("highlight_color", "#e94560"),
            accent_color=anim_data.get("accent_color", "#0f3460"),
            camera_movements=anim_data.get("camera_movements", []),
            special_effects=anim_data.get("special_effects", []),
            notes=anim_data.get("notes", ""),
        )

        # Build storyboard scenes
        scenes: list[StoryboardScene] = []
        for scene_data in data.get("storyboard", []):
            objects = [
                SceneObject(
                    object_type=obj.get("object_type", "text"),
                    content=obj.get("content", ""),
                    position=str(obj.get("position", "CENTER")),
                    color=obj.get("color", "WHITE"),
                    scale=float(obj.get("scale", 1.0)),
                )
                for obj in scene_data.get("objects", [])
            ]

            animations = [
                SceneAnimation(
                    animation_type=anim.get("animation_type", "FadeIn"),
                    target_object=anim.get("target_object", ""),
                    duration=float(anim.get("duration", 1.0)),
                    parameters={k: str(v) for k, v in anim.get("parameters", {}).items()},
                )
                for anim in scene_data.get("animations", [])
            ]

            scene = StoryboardScene(
                scene_number=scene_data.get("scene_number", len(scenes) + 1),
                scene_title=scene_data.get("scene_title", f"Scene {len(scenes)+1}"),
                learning_objective=scene_data.get("learning_objective", ""),
                objects=objects,
                animations=animations,
                animation_description=scene_data.get("animation_description", ""),
                voice_segment=scene_data.get("voice_segment", ""),
                estimated_duration_seconds=float(
                    scene_data.get("estimated_duration_seconds", 10.0)
                ),
                background_color=scene_data.get("background_color", "#1a1a2e"),
                transition=scene_data.get("transition", "FadeIn"),
                mathematical_expressions=scene_data.get("mathematical_expressions", []),
                code_snippet=scene_data.get("code_snippet", ""),
            )
            scenes.append(scene)

        total_duration = sum(s.estimated_duration_seconds for s in scenes)

        full_narration = data.get("full_narration_script") or " ".join(
            s.voice_segment for s in scenes
        )

        return LessonPlan(
            title=data.get("title", "Educational Lesson"),
            subject=data.get("subject", "general"),
            difficulty_level=data.get("difficulty_level", "intermediate"),
            target_audience=data.get("target_audience", "Students"),
            learning_objectives=data.get("learning_objectives", []),
            prerequisite_knowledge=data.get("prerequisite_knowledge", []),
            key_concepts=data.get("key_concepts", []),
            explanation=data.get("explanation", ""),
            summary=data.get("summary", ""),
            storyboard=scenes,
            animation_plan=animation_plan,
            full_narration_script=full_narration,
            estimated_video_duration_seconds=data.get(
                "estimated_video_duration_seconds", total_duration
            ),
            keywords=data.get("keywords", []),
        )
