"""
Synchronization Service.

Merges rendered Manim animation video with narration audio and
optional subtitles using FFmpeg to produce the final MP4.
This is NOT an LLM agent — it is a deterministic FFmpeg wrapper.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from app.core.config import get_settings
from app.core.exceptions import SynchronizationError
from app.core.logging_config import get_logger
from app.schemas.state import VideoGenerationState

logger = get_logger(__name__)


def get_ffmpeg_cmd() -> str:
    """Get path to ffmpeg binary from PATH, config, or imageio_ffmpeg package."""
    settings = get_settings()
    if settings.ffmpeg_binary and shutil.which(settings.ffmpeg_binary):
        return settings.ffmpeg_binary
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


class SynchronizationService:
    """
    Combines Manim video + narration audio → final educational video.
    Uses FFmpeg for all media operations.
    """

    FFMPEG_TIMEOUT = 300  # 5 minutes

    def synchronize(self, state: VideoGenerationState) -> dict:
        """
        Merge animation video with audio narration.

        Args:
            state: LangGraph state with execution_result and narration_script.

        Returns:
            Partial state update with video_file_path and video_duration_seconds.
        """
        from app.schemas.narration import NarrationScript
        from app.schemas.manim import ExecutionResult

        execution_result: ExecutionResult | None = state.get("execution_result")
        narration_script: NarrationScript | None = state.get("narration_script")
        project_id = state.get("project_id", "unknown")
        render_dir = state.get("render_output_dir", "./renders")

        if not execution_result or not execution_result.primary_output:
            raise SynchronizationError(
                "No rendered video file available for synchronization.",
                context={"project_id": project_id},
            )

        video_input = execution_result.primary_output
        if not Path(video_input).exists():
            raise SynchronizationError(
                f"Video file not found: {video_input}",
                context={"path": video_input},
            )

        # Output path for final video
        output_dir = Path(render_dir) / project_id / "final"
        output_dir.mkdir(parents=True, exist_ok=True)
        final_video_path = str(output_dir / "final_video.mp4")

        # Determine if we have narration audio
        audio_path = ""
        if narration_script and narration_script.combined_audio_path:
            if Path(narration_script.combined_audio_path).exists():
                audio_path = narration_script.combined_audio_path

        logger.info(
            "Synchronization service executing",
            video_input=video_input,
            audio_path=audio_path or "none",
            output=final_video_path,
        )

        if audio_path:
            success = self._merge_video_audio(
                video_path=video_input,
                audio_path=audio_path,
                output_path=final_video_path,
            )
        else:
            # No audio — just copy/transcode the video
            success = self._transcode_video(
                video_path=video_input,
                output_path=final_video_path,
            )

        if not success:
            raise SynchronizationError(
                "FFmpeg failed to produce the final video.",
                context={"video_input": video_input, "audio_path": audio_path},
            )

        # Get final video duration
        duration = self._get_video_duration(final_video_path)

        logger.info(
            "Synchronization complete",
            output=final_video_path,
            duration=duration,
        )

        return {
            "video_file_path": final_video_path,
            "video_duration_seconds": duration,
        }

    # ─────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────

    def _merge_video_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
    ) -> bool:
        """Merge video and audio streams into final MP4."""
        command = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            # Map video from input 0, audio from input 1
            "-map", "0:v:0",
            "-map", "1:a:0",
            # Re-encode to ensure compatibility
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            # Align audio/video duration
            "-shortest",
            # Ensure proper timestamps
            "-avoid_negative_ts", "make_zero",
            "-movflags", "+faststart",
            output_path,
        ]

        return self._run_ffmpeg(command)

    def _transcode_video(self, video_path: str, output_path: str) -> bool:
        """Transcode video without audio to standardized MP4."""
        command = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-movflags", "+faststart",
            output_path,
        ]
        return self._run_ffmpeg(command)

    def _run_ffmpeg(self, command: list[str]) -> bool:
        """Execute an FFmpeg command."""
        ffmpeg_bin = get_ffmpeg_cmd()
        if command and command[0] == "ffmpeg":
            command[0] = ffmpeg_bin

        try:
            logger.debug("FFmpeg command", cmd=" ".join(command))
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.FFMPEG_TIMEOUT,
            )
            if result.returncode != 0:
                logger.warning(
                    "FFmpeg failed",
                    stderr=result.stderr[-500:] if result.stderr else "",
                    returncode=result.returncode,
                )
                return False
            return True
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timed out")
            return False
        except FileNotFoundError:
            raise SynchronizationError(
                "FFmpeg binary could not be launched."
            )
        except Exception as exc:
            logger.error("FFmpeg error", error=str(exc))
            return False

    def _get_video_duration(self, video_path: str) -> float:
        """Get video duration in seconds using ffprobe or ffmpeg fallback."""
        if shutil.which("ffprobe"):
            try:
                result = subprocess.run(
                    [
                        "ffprobe",
                        "-v", "error",
                        "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1",
                        video_path,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return float(result.stdout.strip())
            except Exception:
                pass

        try:
            ffmpeg_bin = get_ffmpeg_cmd()
            result = subprocess.run(
                [ffmpeg_bin, "-i", video_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", result.stderr or "")
            if match:
                hours, minutes, seconds = match.groups()
                return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        except Exception:
            pass
        return 0.0
