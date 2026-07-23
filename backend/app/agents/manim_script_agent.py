"""
Manim Script Generation Agent.

Converts a structured storyboard into executable Manim CE Python code.
Uses Gemini Pro with a specialized system prompt for code generation.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import google.generativeai as genai

from app.core.config import get_settings
from app.core.exceptions import ManimScriptError
from app.core.logging_config import get_logger
from app.prompts.manim_generation import MANIM_SYSTEM_PROMPT, build_manim_script_prompt
from app.schemas.lesson import LessonPlan, StoryboardScene
from app.schemas.manim import ManimScene, ManimScript
from app.schemas.state import VideoGenerationState
from app.utils.file_utils import write_text_file, ensure_dir

logger = get_logger(__name__)

STANDARD_IMPORTS = """from manim import *
import numpy as np
from typing import Optional
"""


class ManimScriptAgent:
    """
    Converts a storyboard into executable Manim CE code.
    Writes the script to disk and returns the ManimScript model.
    """

    def __init__(self) -> None:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            system_instruction=MANIM_SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0.2,    # Low temperature for code generation
                max_output_tokens=8192,
            ),
        )
        self._settings = settings

    def run(self, state: VideoGenerationState) -> dict:
        """
        Generate Manim script from storyboard.

        Returns:
            Partial state update with manim_script and manim_script_file_path.
        """
        lesson_plan: LessonPlan | None = state.get("lesson_plan")
        if not lesson_plan:
            raise ManimScriptError(
                "No lesson plan available for Manim script generation.",
                context={"state_keys": list(state.keys())},
            )

        project_id = state.get("project_id", "unknown")
        render_quality = state.get("render_quality", "medium_quality")
        render_dir = state.get("render_output_dir", "./renders")

        logger.info(
            "Manim script agent executing",
            project_id=project_id,
            scenes=len(lesson_plan.storyboard),
        )

        # ── Build storyboard JSON for prompt ──────────────────────────────
        storyboard_data = [
            scene.model_dump() for scene in lesson_plan.storyboard
        ]
        storyboard_json = json.dumps(storyboard_data, indent=2, default=str)

        # ── Build prompt ───────────────────────────────────────────────────
        prompt = build_manim_script_prompt(
            lesson_title=lesson_plan.title,
            storyboard_json=storyboard_json,
            background_color=lesson_plan.animation_plan.background_color,
            highlight_color=lesson_plan.animation_plan.highlight_color,
            quality=render_quality,
        )

        # ── Call Gemini ────────────────────────────────────────────────────
        try:
            response = self._model.generate_content(prompt)
            raw_code = response.text
        except Exception as exc:
            raise ManimScriptError(
                f"Gemini API call failed during Manim script generation: {exc}"
            ) from exc

        # ── Clean generated code ───────────────────────────────────────────
        clean_code = self._clean_code(raw_code)

        # ── Validate code has Scene classes ───────────────────────────────
        if "class " not in clean_code or "(Scene)" not in clean_code:
            # Attempt to wrap in minimal valid scene
            clean_code = self._wrap_in_fallback_scene(
                clean_code, lesson_plan.title
            )

        # ── Parse individual scene classes ────────────────────────────────
        scenes = self._extract_scene_classes(clean_code, lesson_plan.storyboard)

        # ── Determine main scene class ─────────────────────────────────────
        main_class = self._find_main_scene_class(clean_code, scenes)

        # ── Build render command ───────────────────────────────────────────
        quality_flag = {"low_quality": "-ql", "medium_quality": "-qm", "high_quality": "-qh"}.get(
            render_quality, "-qm"
        )
        script_filename = f"manim_script_{project_id}.py"
        render_command = f"manim {quality_flag} {script_filename} {main_class}"

        # ── Write script to disk ───────────────────────────────────────────
        output_dir = Path(render_dir) / project_id
        ensure_dir(str(output_dir))
        script_path = str(output_dir / script_filename)

        full_script = f"{STANDARD_IMPORTS}\n\n{clean_code}"
        write_text_file(script_path, full_script)

        logger.info(
            "Manim script written",
            path=script_path,
            scenes=len(scenes),
            main_class=main_class,
        )

        manim_script = ManimScript(
            project_id=project_id,
            imports=STANDARD_IMPORTS,
            constants="",
            scenes=scenes,
            full_script=full_script,
            main_scene_class=main_class,
            render_command=render_command,
        )

        return {
            "manim_script": manim_script,
            "manim_script_file_path": script_path,
        }

    # ─────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────

    def _clean_code(self, raw: str) -> str:
        """Strip markdown fences and non-code content from Gemini output."""
        raw = raw.strip()
        # Remove triple-backtick blocks
        if raw.startswith("```"):
            match = re.search(r"```(?:python)?\n(.*?)```", raw, re.DOTALL)
            if match:
                return match.group(1).strip()
        # Remove single trailing backtick lines
        lines = raw.split("\n")
        lines = [l for l in lines if l.strip() not in ("```", "```python")]
        return "\n".join(lines)

    def _extract_scene_classes(
        self, code: str, storyboard: list[StoryboardScene]
    ) -> list[ManimScene]:
        """Extract individual Scene subclasses from the generated code."""
        scenes = []
        # Find all class definitions that inherit from Scene
        class_pattern = re.compile(
            r"(class\s+(\w+)\s*\(.*?Scene.*?\).*?:.*?)(?=\nclass\s|\Z)",
            re.DOTALL,
        )
        for i, match in enumerate(class_pattern.finditer(code)):
            class_body = match.group(1)
            class_name = match.group(2)

            # Map to storyboard scene number
            scene_number = i + 1
            scene_title = ""
            if i < len(storyboard):
                scene_number = storyboard[i].scene_number
                scene_title = storyboard[i].scene_title

            scenes.append(
                ManimScene(
                    class_name=class_name,
                    scene_number=scene_number,
                    scene_title=scene_title or class_name,
                    python_code=class_body,
                )
            )
        return scenes

    def _find_main_scene_class(
        self, code: str, scenes: list[ManimScene]
    ) -> str:
        """Find the combined/main scene class to render."""
        # Prefer CombinedVideoScene or similar
        for candidate in ["CombinedVideoScene", "MainScene", "FullVideo"]:
            if candidate in code:
                return candidate
        # Fall back to last scene class
        if scenes:
            return scenes[-1].class_name
        return "Scene01"

    def _wrap_in_fallback_scene(self, code: str, title: str) -> str:
        """Wrap bare code in a minimal valid Manim scene."""
        safe_title = re.sub(r"[^a-zA-Z0-9]", "", title)[:20] or "Lesson"
        return f"""{STANDARD_IMPORTS}

class {safe_title}Scene(Scene):
    def construct(self):
        self.camera.background_color = "#1a1a2e"
        title = Text("{title}", font_size=48, color=WHITE)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
"""
