"""
Manim Execution Service.

Executes generated Manim Python scripts as subprocesses.

Key change from original: instead of rendering only the CombinedVideoScene,
this service now renders each individual Scene subclass separately (one MP4
per scene). This enables per-scene duration correction and per-scene repair
without re-rendering the entire video.

The CombinedVideoScene is rendered as a fallback if per-scene rendering fails.
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
from app.schemas.manim import ExecutionResult, ExecutionStatus, ManimScene, ManimScript
from app.schemas.narration import SceneAudio, SceneVideo
from app.schemas.state import VideoGenerationState
from app.database.repositories.job_repository import emit_live_log

logger = get_logger(__name__)


class ManimExecutionService:
    """
    Runs Manim scripts via subprocess and returns structured ExecutionResult.
    Renders each Scene subclass independently for per-scene duration control.
    """

    EXECUTION_TIMEOUT_SECONDS = 600  # 10 minutes max per render

    def __init__(self) -> None:
        self._settings = get_settings()

    def execute(self, state: VideoGenerationState) -> ExecutionResult:
        """
        Execute the Manim script — one render per scene class.

        Returns:
            ExecutionResult with status, logs, and output file paths.
            Also populates state update with scene_videos.
        """
        manim_script: ManimScript | None = state.get("manim_script")
        script_path = state.get("manim_script_file_path", "")
        render_quality = state.get("render_quality", "medium_quality")
        project_id = state.get("project_id", "unknown")
        render_dir = state.get("render_output_dir", "./renders")
        scene_audios: list[SceneAudio] = state.get("scene_audios", [])

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

        quality_flag = self._quality_flag(render_quality)
        output_dir = (Path(render_dir) / project_id / "video").resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        # ── Identify individual (non-combined) scene classes ───────────────
        individual_scenes = self._get_individual_scenes(manim_script)
        main_class = manim_script.main_scene_class

        job_id = state.get("job_id", "")
        logger.info(
            "Executing Manim per-scene",
            script=script_path,
            individual_scenes=[s.class_name for s in individual_scenes],
            main_class=main_class,
        )
        emit_live_log(job_id, "manim_execution_service", "in_progress", f"Rendering {len(individual_scenes)} animation scenes...")

        if not individual_scenes:
            logger.error("No individual Scene classes found in Manim script.")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                exit_code=-1,
                error_message="No individual Scene classes found. The LLM failed to generate Scene01, Scene02, etc.",
                logs=["Error: No Scene classes found."],
            )

        # ── Render each scene individually ─────────────────────────────────
        scene_videos: list[SceneVideo] = []
        all_success = True
        combined_logs: list[str] = []
        combined_stderr = ""

        for i, scene in enumerate(individual_scenes):
            # Resolve matching SceneAudio by position
            scene_id = f"scene_{i + 1:02d}"
            if i < len(scene_audios):
                scene_id = scene_audios[i].scene_id

            scene_output_file = str(output_dir / f"{scene_id}_raw.mp4")
            emit_live_log(job_id, "manim_execution_service", "in_progress", f"Rendering scene {i+1}/{len(individual_scenes)}: {scene.class_name}...")
            result = self._render_single_scene(
                script_path=script_path,
                scene_class=scene.class_name,
                quality_flag=quality_flag,
                output_dir=str(output_dir),
                output_filename=f"{scene_id}_raw.mp4",
            )

            combined_logs.extend(result.logs or [])
            combined_stderr += result.stderr or ""

            # Locate the rendered file
            raw_video_path = self._find_scene_output(
                output_dir, script_path, scene.class_name, f"{scene_id}_raw.mp4"
            )

            sv = SceneVideo(
                scene_id=scene_id,
                scene_number=i + 1,
                class_name=scene.class_name,
                raw_video_path=raw_video_path,
                render_success=result.is_success,
                error_message=result.error_message if not result.is_success else "",
            )
            scene_videos.append(sv)

            if not result.is_success:
                all_success = False
                logger.warning(
                    "Scene render failed",
                    scene_class=scene.class_name,
                    error=result.error_message[:200],
                )
                emit_live_log(job_id, "manim_execution_service", "warning", f"Scene {i+1} ({scene.class_name}) failed: {result.error_message[:120]}")
            else:
                logger.info(
                    "Scene render succeeded",
                    scene_id=scene_id,
                    class_name=scene.class_name,
                    raw_video=raw_video_path,
                )
                emit_live_log(job_id, "manim_execution_service", "completed", f"Scene {i+1} ({scene.class_name}) rendered successfully.")

        # ── Store scene_videos in a temporary attribute for node pickup ────
        # (nodes.py reads this via _extra_scene_videos)
        self._last_scene_videos = scene_videos

        if all_success:
            # Return successful ExecutionResult; primary_output is first scene
            primary = scene_videos[0].raw_video_path if scene_videos else ""
            all_paths = [sv.raw_video_path for sv in scene_videos if sv.raw_video_path]
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                exit_code=0,
                stdout="",
                stderr=combined_stderr,
                logs=combined_logs,
                output_files=all_paths,
            )
        else:
            # At least one scene failed.
            failed_scenes = [sv.scene_id for sv in scene_videos if not sv.render_success]
            logger.error(f"Per-scene render failed for: {failed_scenes}")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                exit_code=-1,
                error_message=f"Render failed for scenes: {failed_scenes}",
                logs=combined_logs,
            )

    def get_last_scene_videos(self) -> list[SceneVideo]:
        """Return the scene_videos list from the most recent execute() call."""
        return getattr(self, "_last_scene_videos", [])

    # ─────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────

    def _get_individual_scenes(self, manim_script: ManimScript) -> list[ManimScene]:
        """Return scene classes excluding the CombinedVideoScene."""
        combined_names = {"CombinedVideoScene", "MainScene", "FullVideo"}
        return [
            s for s in manim_script.scenes
            if s.class_name not in combined_names
        ]

    def _render_single_scene(
        self,
        script_path: str,
        scene_class: str,
        quality_flag: str,
        output_dir: str,
        output_filename: str,
    ) -> ExecutionResult:
        """Render a single Manim Scene subclass."""
        command = [
            "manim",
            quality_flag,
            "--media_dir", str(Path(output_dir).resolve()),
            "--disable_caching",
            "--output_file", Path(output_filename).stem,
            str(Path(script_path).resolve()),
            scene_class,
        ]

        logger.debug("Rendering scene", command=" ".join(command))
        start = time.time()
        result = self._run_subprocess(command, script_path)
        result.render_duration_seconds = time.time() - start
        result.script_path = script_path
        return result

    def _render_combined_fallback(
        self,
        script_path: str,
        main_class: str,
        quality_flag: str,
        output_dir: str,
    ) -> ExecutionResult:
        """Fallback: render CombinedVideoScene as a single video."""
        command = [
            "manim",
            quality_flag,
            "--media_dir", str(Path(output_dir).resolve()),
            "--disable_caching",
            str(Path(script_path).resolve()),
            main_class,
        ]
        logger.info("Rendering CombinedVideoScene fallback", main_class=main_class)
        start = time.time()
        result = self._run_subprocess(command, script_path)
        result.render_duration_seconds = time.time() - start
        result.script_path = script_path

        if result.is_success:
            output_files = self._find_output_files(Path(output_dir), script_path)
            result.output_files = output_files
        return result

    def _find_scene_output(
        self,
        output_dir: Path,
        script_path: str,
        scene_class: str,
        expected_filename: str,
    ) -> str:
        """Locate the rendered MP4 for a specific scene class."""
        # Look for file matching our expected name
        expected = output_dir / expected_filename
        if expected.exists():
            return str(expected)

        # Manim puts output in: media_dir/videos/<script_stem>/<quality>/
        script_stem = Path(script_path).stem
        for search_dir in [
            output_dir,
            output_dir / "videos" / script_stem,
            output_dir / "videos",
        ]:
            if not search_dir.exists():
                continue
            for mp4 in search_dir.rglob("*.mp4"):
                # Match by scene class name in filename
                if scene_class.lower() in mp4.stem.lower():
                    return str(mp4)
                if expected_filename.replace(".mp4", "").lower() in mp4.stem.lower():
                    return str(mp4)

        # Last resort: newest MP4 in output_dir
        all_mp4s = list(output_dir.rglob("*.mp4"))
        if all_mp4s:
            return str(max(all_mp4s, key=lambda p: p.stat().st_mtime))

        return ""

    def _find_output_files(self, output_dir: Path, script_path: str) -> list[str]:
        """Search for all generated MP4 files after render."""
        found: list[str] = []
        for mp4 in output_dir.rglob("*.mp4"):
            found.append(str(mp4))
        script_stem = Path(script_path).stem
        for media_dir in [
            output_dir / "videos" / script_stem,
            output_dir / "videos",
            Path("media") / "videos" / script_stem,
        ]:
            if media_dir.exists():
                for mp4 in media_dir.rglob("*.mp4"):
                    if str(mp4) not in found:
                        found.append(str(mp4))
        found.sort(
            key=lambda p: Path(p).stat().st_mtime if Path(p).exists() else 0,
            reverse=True,
        )
        return found

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

    def _parse_error(self, stderr: str, stdout: str) -> tuple[str, str]:
        """Extract error message and traceback from stderr."""
        combined = stderr + "\n" + stdout
        tb_match = re.search(
            r"(Traceback \(most recent call last\):.*?)(?=\n\n|\Z)",
            combined,
            re.DOTALL,
        )
        traceback = tb_match.group(1).strip() if tb_match else ""
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
