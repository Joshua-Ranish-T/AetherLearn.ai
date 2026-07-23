"""
Manim Execution Service.

Executes generated Manim Python scripts as subprocesses.
Captures stdout, stderr, execution logs, timing, and output files.
This is NOT an LLM agent — it is a deterministic subprocess runner.
"""

from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.core.exceptions import RenderError
from app.core.logging_config import get_logger
from app.schemas.manim import ExecutionResult, ExecutionStatus, ManimScript
from app.schemas.state import VideoGenerationState

logger = get_logger(__name__)


class ManimExecutionService:
    """
    Runs Manim scripts via subprocess and returns structured ExecutionResult.
    """

    EXECUTION_TIMEOUT_SECONDS = 600  # 10 minutes max per render

    def __init__(self) -> None:
        self._settings = get_settings()

    def execute(self, state: VideoGenerationState) -> ExecutionResult:
        """
        Execute the Manim script referenced in state.

        Args:
            state: Current LangGraph state with manim_script and render config.

        Returns:
            ExecutionResult with status, logs, and output file paths.
        """
        manim_script: ManimScript | None = state.get("manim_script")
        script_path = state.get("manim_script_file_path", "")
        render_quality = state.get("render_quality", "medium_quality")
        project_id = state.get("project_id", "unknown")
        render_dir = state.get("render_output_dir", "./renders")

        if not manim_script:
            raise RenderError(
                "No Manim script available for execution.",
                context={"project_id": project_id},
            )

        if not script_path or not Path(script_path).exists():
            raise RenderError(
                f"Manim script file not found: {script_path}",
                context={"script_path": script_path},
            )

        main_class = manim_script.main_scene_class
        quality_flag = self._quality_flag(render_quality)
        output_dir = Path(render_dir) / project_id / "video"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build the Manim command
        command = self._build_command(
            script_path=str(Path(script_path).absolute()),
            scene_class=main_class,
            quality_flag=quality_flag,
            output_dir=str(Path(output_dir).absolute()),
        )

        logger.info(
            "Executing Manim",
            command=" ".join(command),
            script=script_path,
            scene=main_class,
        )

        start_time = time.time()
        result = self._run_subprocess(command, script_path)
        duration = time.time() - start_time

        result.render_duration_seconds = duration
        result.script_path = script_path

        if result.is_success:
            # Locate generated output files
            output_files = self._find_output_files(output_dir, script_path)
            result.output_files = output_files
            logger.info(
                "Manim execution succeeded",
                duration=duration,
                output_files=output_files,
            )
        else:
            logger.warning(
                "Manim execution failed",
                duration=duration,
                error=result.error_message[:300],
                exit_code=result.exit_code,
            )

        return result

    # ─────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────

    def _build_command(
        self,
        script_path: str,
        scene_class: str,
        quality_flag: str,
        output_dir: str,
    ) -> list[str]:
        """Construct the Manim CLI command."""
        return [
            "manim",
            quality_flag,
            "--media_dir", output_dir,
            "--disable_caching",
            script_path,
            scene_class,
        ]

    def _run_subprocess(
        self, command: list[str], script_path: str
    ) -> ExecutionResult:
        """Run Manim as a subprocess and capture output."""
        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.EXECUTION_TIMEOUT_SECONDS,
                cwd=str(Path(script_path).parent),
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )

            stdout = process.stdout or ""
            stderr = process.stderr or ""
            exit_code = process.returncode

            if exit_code == 0:
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    exit_code=exit_code,
                    stdout=stdout,
                    stderr=stderr,
                    logs=stdout.split("\n"),
                )
            else:
                error_message, traceback = self._parse_error(stderr, stdout)
                status = self._classify_error(stderr)

                return ExecutionResult(
                    status=status,
                    exit_code=exit_code,
                    stdout=stdout,
                    stderr=stderr,
                    error_message=error_message,
                    traceback=traceback,
                    logs=stderr.split("\n"),
                )

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                exit_code=-1,
                error_message=f"Manim execution timed out after {self.EXECUTION_TIMEOUT_SECONDS}s",
                logs=["TIMEOUT"],
            )
        except FileNotFoundError:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                exit_code=-1,
                error_message="'manim' command not found. Is Manim CE installed?",
                logs=["FileNotFoundError: manim not found"],
            )
        except Exception as exc:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                exit_code=-1,
                error_message=f"Subprocess error: {exc}",
                logs=[str(exc)],
            )

    def _parse_error(
        self, stderr: str, stdout: str
    ) -> tuple[str, str]:
        """Extract error message and traceback from stderr."""
        combined = stderr + "\n" + stdout

        # Find Python traceback
        tb_match = re.search(
            r"(Traceback \(most recent call last\):.*?)(?=\n\n|\Z)",
            combined,
            re.DOTALL,
        )
        traceback = tb_match.group(1).strip() if tb_match else ""

        # Find specific error type on last line of traceback
        error_match = re.search(
            r"((?:SyntaxError|NameError|AttributeError|TypeError|ImportError|"
            r"ValueError|RuntimeError|LaTeXError|MathTexWarning|KeyError).*?)(?:\n|\Z)",
            combined,
        )
        error_message = error_match.group(1).strip() if error_match else (
            stderr.strip().split("\n")[-1] if stderr.strip() else "Unknown error"
        )

        return error_message[:500], traceback[:2000]

    def _classify_error(self, stderr: str) -> ExecutionStatus:
        """Classify the type of execution failure."""
        if "SyntaxError" in stderr or "IndentationError" in stderr:
            return ExecutionStatus.SYNTAX_ERROR
        return ExecutionStatus.FAILED

    def _quality_flag(self, quality: str) -> str:
        """Convert quality name to Manim CLI flag."""
        return {
            "low_quality": "-ql",
            "medium_quality": "-qm",
            "high_quality": "-qh",
        }.get(quality, "-qm")

    def _find_output_files(
        self, output_dir: Path, script_path: str
    ) -> list[str]:
        """
        Search for generated media files after successful render.
        Manim places output in media/videos/<script_name>/480p15/ etc.
        """
        found: list[str] = []

        # Search recursively in output_dir for MP4 files
        for mp4 in output_dir.rglob("*.mp4"):
            found.append(str(mp4))

        # Also check Manim's default media folder structure
        script_stem = Path(script_path).stem
        manim_media_dirs = [
            output_dir / "videos" / script_stem,
            output_dir / "videos",
            Path("media") / "videos" / script_stem,
        ]
        for media_dir in manim_media_dirs:
            if media_dir.exists():
                for mp4 in media_dir.rglob("*.mp4"):
                    mp4_str = str(mp4)
                    if mp4_str not in found:
                        found.append(mp4_str)

        # Sort by modification time — newest first
        found.sort(key=lambda p: Path(p).stat().st_mtime if Path(p).exists() else 0, reverse=True)
        return found
