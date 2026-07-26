"""
Repair Agent.

Analyzes Manim execution errors and applies targeted fixes to broken code.
Uses Gemini to understand the traceback and generate a corrected script.

Rules:
- Never regenerate the entire script
- Apply minimal, surgical fixes only
- Track previous error attempts to avoid repeated mistakes
- Increment repair_retry_count on each attempt
"""

from __future__ import annotations

from pathlib import Path

import google.generativeai as genai

from app.core.config import get_settings
from app.core.exceptions import RepairError
from app.core.logging_config import get_logger
from app.database.repositories.job_repository import emit_live_log
from app.prompts.repair import REPAIR_SYSTEM_PROMPT, build_repair_prompt
from app.schemas.manim import ExecutionResult, ManimScript
from app.schemas.state import VideoGenerationState
from app.utils.file_utils import read_text_file, write_text_file

logger = get_logger(__name__)


class RepairAgent:
    """
    Analyzes execution errors and patches generated Manim code.
    """

    def __init__(self) -> None:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            system_instruction=REPAIR_SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0.1,   # Very low temperature for deterministic repairs
                max_output_tokens=8192,
            ),
        )

    def run(self, state: VideoGenerationState) -> dict:
        """
        Read execution errors and produce a repaired Manim script.

        Returns:
            Partial state update with updated manim_script and manim_script_file_path.
        """
        execution_result: ExecutionResult | None = state.get("execution_result")
        manim_script: ManimScript | None = state.get("manim_script")
        script_path = state.get("manim_script_file_path", "")
        retry_count = state.get("repair_retry_count", 0)
        max_retries = state.get("max_repair_retries", 3)

        if not execution_result:
            raise RepairError(
                "No execution result available for repair.",
                context={"retry_count": retry_count},
            )

        if not manim_script:
            raise RepairError(
                "No Manim script available for repair.",
                context={"retry_count": retry_count},
            )

        if retry_count >= max_retries:
            raise RepairError(
                f"Maximum repair retries ({max_retries}) exceeded.",
                context={
                    "retry_count": retry_count,
                    "max_retries": max_retries,
                    "last_error": execution_result.error_message,
                },
            )

        job_id = state.get("job_id", "")
        logger.info(
            "Repair agent executing",
            retry=retry_count + 1,
            max_retries=max_retries,
            error=execution_result.error_message[:200],
        )
        emit_live_log(job_id, "repair_agent", "in_progress", f"Applying AI self-healing repair (attempt {retry_count+1}/{max_retries})...")

        # ── Read current script from disk ──────────────────────────────────
        broken_script = ""
        if script_path and Path(script_path).exists():
            broken_script = read_text_file(script_path)
        else:
            broken_script = manim_script.full_script

        # ── Collect previous error messages from logs ──────────────────────
        previous_errors: list[str] = []
        for log_entry in state.get("stage_logs", []):
            if isinstance(log_entry, dict):
                meta = log_entry.get("metadata", {})
                prev_err = meta.get("error_message") or log_entry.get("error_message") or ""
                if prev_err and prev_err not in previous_errors and prev_err != execution_result.error_message:
                    previous_errors.append(prev_err)

        # ── Build repair prompt ────────────────────────────────────────────
        prompt = build_repair_prompt(
            error_message=execution_result.error_message,
            traceback=execution_result.traceback or execution_result.stderr,
            broken_script=broken_script,
            retry_number=retry_count + 1,
            previous_errors=previous_errors,
        )

        # ── Call Gemini ────────────────────────────────────────────────────
        try:
            response = self._model.generate_content(prompt)
            repaired_code = response.text
        except Exception as exc:
            raise RepairError(
                f"Gemini API call failed during repair: {exc}",
                context={"retry": retry_count + 1},
            ) from exc

        # ── Clean the repaired code ────────────────────────────────────────
        repaired_code = self._clean_code(repaired_code)

        # ── Write repaired script to disk ──────────────────────────────────
        if script_path:
            write_text_file(script_path, repaired_code)
        else:
            # Create a new path if the original is missing
            project_id = state.get("project_id", "unknown")
            render_dir = state.get("render_output_dir", "./renders")
            script_path = str(
                Path(render_dir) / project_id / f"manim_script_{project_id}.py"
            )
            write_text_file(script_path, repaired_code)

        # ── Update manim_script model with freshly extracted scene metadata ──
        from app.agents.manim_script_agent import ManimScriptAgent
        script_agent = ManimScriptAgent()
        lesson_plan = state.get("lesson_plan")
        storyboard = getattr(lesson_plan, "storyboard", None) or []
        new_scenes = script_agent._extract_scene_classes(repaired_code, storyboard)
        new_main_class = script_agent._find_main_scene_class(repaired_code, new_scenes)
        if not new_scenes:
            new_scenes = manim_script.scenes
            new_main_class = manim_script.main_scene_class

        updated_script = ManimScript(
            project_id=manim_script.project_id,
            script_version=manim_script.script_version + 1,
            imports=manim_script.imports,
            constants=manim_script.constants,
            scenes=new_scenes,
            full_script=repaired_code,
            main_scene_class=new_main_class,
            render_command=f"manim -qm {Path(script_path).name} {new_main_class}",
        )

        logger.info(
            "Repair agent completed",
            script_version=updated_script.script_version,
            script_path=script_path,
        )
        emit_live_log(job_id, "repair_agent", "completed", f"Repaired Manim script (v{updated_script.script_version}). Re-rendering animations...")

        return {
            "manim_script": updated_script,
            "manim_script_file_path": script_path,
            # Reset execution state so the execution node runs fresh
            "execution_result": None,
            "execution_successful": False,
        }

    def _clean_code(self, raw: str) -> str:
        """Strip markdown fences from Gemini code output."""
        import re
        raw = raw.strip()
        if raw.startswith("```"):
            match = re.search(r"```(?:python)?\n(.*?)```", raw, re.DOTALL)
            if match:
                return match.group(1).strip()
        lines = raw.split("\n")
        lines = [l for l in lines if l.strip() not in ("```", "```python")]
        return "\n".join(lines)
