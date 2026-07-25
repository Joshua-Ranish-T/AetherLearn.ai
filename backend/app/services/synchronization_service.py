"""
Synchronization Service.

Merges each padded scene video with its corresponding audio track,
then concatenates all scenes sequentially into the final educational video.
Uses FFmpeg for all media operations.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from app.core.config import get_settings
from app.core.exceptions import SynchronizationError
from app.core.logging_config import get_logger
from app.schemas.state import VideoGenerationState
from app.schemas.narration import SceneAudio, SceneVideo

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
    Combines padded Manim scene videos + scene audio → final educational video.
    """

    FFMPEG_TIMEOUT = 300  # 5 minutes per operation

    def synchronize(self, state: VideoGenerationState) -> dict:
        """
        Merge per-scene padded video with audio, then concat all scenes.

        Returns:
            Partial state update with video_file_path, video_duration_seconds,
            and updated scene_videos.
        """
        scene_videos: list[SceneVideo] = state.get("scene_videos", [])
        scene_audios: list[SceneAudio] = state.get("scene_audios", [])
        project_id = state.get("project_id", "unknown")
        render_dir = state.get("render_output_dir", "./renders")

        if not scene_videos:
            raise SynchronizationError(
                "No scene videos available for synchronization.",
                context={"project_id": project_id},
            )

        output_dir = Path(render_dir) / project_id / "final"
        output_dir.mkdir(parents=True, exist_ok=True)
        final_video_path = str(output_dir / "final_video.mp4")

        logger.info(
            "Synchronization service executing",
            scenes=len(scene_videos),
            output=final_video_path,
        )

        muxed_paths = []

        # 1. Mux each scene
        for i, sv in enumerate(scene_videos):
            if not sv.padded_video_path or not Path(sv.padded_video_path).exists():
                logger.warning(
                    "Skipping scene muxing due to missing padded video",
                    scene_id=sv.scene_id,
                )
                continue

            matching_audio = None
            if i < len(scene_audios) and scene_audios[i].audio_path and Path(scene_audios[i].audio_path).exists():
                matching_audio = scene_audios[i]

            muxed_path = str(output_dir / f"{sv.scene_id}_muxed.mp4")

            if matching_audio:
                success = self._merge_video_audio(
                    video_path=sv.padded_video_path,
                    audio_path=matching_audio.audio_path,
                    output_path=muxed_path,
                )
            else:
                success = self._transcode_video(
                    video_path=sv.padded_video_path,
                    output_path=muxed_path,
                )

            if success and Path(muxed_path).exists():
                sv.final_muxed_path = muxed_path
                muxed_paths.append(muxed_path)
            else:
                logger.error("Failed to mux scene", scene_id=sv.scene_id)

        if not muxed_paths:
            raise SynchronizationError(
                "Failed to produce any muxed scene videos.",
                context={"project_id": project_id},
            )

        # 2. Concat all scenes
        success = self._concat_videos(muxed_paths, final_video_path)

        if not success or not Path(final_video_path).exists():
            raise SynchronizationError(
                "FFmpeg failed to concatenate final video.",
                context={"muxed_paths": muxed_paths},
            )

        duration = self._get_video_duration(final_video_path)

        logger.info(
            "Synchronization complete",
            output=final_video_path,
            duration=duration,
        )

        return {
            "video_file_path": final_video_path,
            "video_duration_seconds": duration,
            "scene_videos": scene_videos,
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
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
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

    def _concat_videos(self, video_paths: list[str], output_path: str) -> bool:
        """Concatenate multiple videos into one using the concat demuxer."""
        if len(video_paths) == 1:
            shutil.copy2(video_paths[0], output_path)
            return True

        # Create concat text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for p in video_paths:
                # FFmpeg requires forward slashes and escaping for file paths in concat demuxer
                safe_path = Path(p).resolve().as_posix()
                f.write(f"file '{safe_path}'\n")
            concat_file = f.name

        command = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            "-movflags", "+faststart",
            output_path,
        ]
        
        success = self._run_ffmpeg(command)
        
        try:
            os.remove(concat_file)
        except Exception:
            pass
            
        return success

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
