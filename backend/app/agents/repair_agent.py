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

        logger.info(
            "Repair agent executing",
            retry=retry_count + 1,
            max_retries=max_retries,
            error=execution_result.error_message[:200],
        )

        # ── Read current script from disk ──────────────────────────────────
        broken_script = ""
        if script_path and Path(script_path).exists():
            broken_script = read_text_file(script_path)
        else:
            broken_script = manim_script.full_script

        # ── Collect previous error messages from logs ──────────────────────
        previous_errors: list[str] = []
        for log_entry in state.get("stage_logs", []):
            if (
                isinstance(log_entry, dict)
                and log_entry.get("stage") == "repair_agent"
                and log_entry.get("status") == "completed"
            ):
                prev_err = log_entry.get("metadata", {}).get("error_message", "")
                if prev_err:
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

        # ── Update manim_script model ──────────────────────────────────────
        updated_script = ManimScript(
            project_id=manim_script.project_id,
            script_version=manim_script.script_version + 1,
            imports=manim_script.imports,
            constants=manim_script.constants,
            scenes=manim_script.scenes,
            full_script=repaired_code,
            main_scene_class=manim_script.main_scene_class,
            render_command=manim_script.render_command,
        )

        logger.info(
            "Repair agent completed",
            script_version=updated_script.script_version,
            script_path=script_path,
        )

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
