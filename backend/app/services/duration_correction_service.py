"""
Duration Correction Service.

Takes raw, independently rendered scene videos (from Manim) and
pads (freeze frame) or trims them so their exact duration matches
the corresponding scene's TTS audio duration.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from app.core.logging_config import get_logger
from app.schemas.narration import SceneAudio, SceneVideo

logger = get_logger(__name__)


class DurationCorrectionService:
    """
    Ensures that every raw Manim scene video exactly matches the duration
    of its corresponding TTS audio file by freeze-framing or trimming.
    """

    def process_scenes(
        self,
        scene_videos: list[SceneVideo],
        scene_audios: list[SceneAudio],
    ) -> list[SceneVideo]:
        """
        Pad or trim each scene video to match its audio duration.
        Mutates the scene_videos list in-place and returns it.
        """
        logger.info(
            "Starting duration correction",
            videos=len(scene_videos),
            audios=len(scene_audios),
        )

        for i, sv in enumerate(scene_videos):
            if not sv.render_success or not sv.raw_video_path:
                logger.warning(
                    "Skipping correction for failed/missing render",
                    scene_id=sv.scene_id,
                )
                continue

            # Find matching audio
            matching_audio = None
            if i < len(scene_audios):
                matching_audio = scene_audios[i]

            if not matching_audio or not matching_audio.audio_path:
                logger.warning(
                    "No matching audio found for scene, skipping correction",
                    scene_id=sv.scene_id,
                )
                sv.padded_video_path = sv.raw_video_path
                continue

            target_duration = matching_audio.duration_seconds
            if target_duration <= 0:
                logger.warning(
                    "Audio duration is 0, skipping correction",
                    scene_id=sv.scene_id,
                )
                sv.padded_video_path = sv.raw_video_path
                continue

            # Determine raw video duration
            raw_duration = self._get_video_duration(sv.raw_video_path)
            if raw_duration <= 0:
                logger.error(
                    "Could not determine raw video duration, skipping correction",
                    raw_video=sv.raw_video_path,
                )
                sv.padded_video_path = sv.raw_video_path
                continue

            # Pad or trim
            out_path = sv.raw_video_path.replace("_raw.mp4", "_padded.mp4")
            
            diff = abs(target_duration - raw_duration)
            if diff < 0.1:
                # Close enough, just copy or link
                logger.debug(
                    "Video duration matches audio perfectly",
                    scene_id=sv.scene_id,
                    diff=round(diff, 3),
                )
                sv.padded_video_path = sv.raw_video_path
                continue

            success = False
            if target_duration > raw_duration:
                # Video is too short — pad with freeze frame
                logger.info(
                    "Padding scene video (freeze frame)",
                    scene_id=sv.scene_id,
                    raw_dur=round(raw_duration, 2),
                    target_dur=round(target_duration, 2),
                )
                success = self._pad_video(sv.raw_video_path, out_path, target_duration)
            else:
                # Video is too long — trim
                logger.info(
                    "Trimming scene video",
                    scene_id=sv.scene_id,
                    raw_dur=round(raw_duration, 2),
                    target_dur=round(target_duration, 2),
                )
                success = self._trim_video(sv.raw_video_path, out_path, target_duration)

            if success and Path(out_path).exists():
                sv.padded_video_path = out_path
            else:
                logger.error("Correction failed, falling back to raw video", scene_id=sv.scene_id)
                sv.padded_video_path = sv.raw_video_path

        return scene_videos

    def _get_video_duration(self, video_path: str) -> float:
        """Measure video duration via ffprobe or ffmpeg fallback."""
        import json
        import shutil
        import re
        
        if shutil.which("ffprobe"):
            cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "format=duration",
                "-of", "json",
                video_path
            ]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                data = json.loads(res.stdout)
                return float(data["format"]["duration"])
            except Exception as e:
                logger.debug("Failed to get video duration with ffprobe", error=str(e))
                
        # Fallback to ffmpeg
        try:
            ffmpeg_bin = self._get_ffmpeg_cmd()
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
        except Exception as e:
            logger.debug("Failed to get video duration with ffmpeg fallback", error=str(e))
            
        return 0.0

    def _pad_video(self, input_path: str, output_path: str, target_duration: float) -> bool:
        """
        Pads video to target_duration by freezing the last frame.
        Uses ffmpeg filter: tpad.
        """
        # Using tpad filter: tpad=stop=-1:stop_mode=clone
        # Then trim to exact target duration.
        cmd = [
            self._get_ffmpeg_cmd(), "-y",
            "-i", input_path,
            "-vf", "tpad=stop=-1:stop_mode=clone",
            "-t", str(target_duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            output_path
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return res.returncode == 0
        except Exception as e:
            logger.error("Padding failed", error=str(e))
            return False

    def _trim_video(self, input_path: str, output_path: str, target_duration: float) -> bool:
        """
        Trims video to exactly target_duration.
        """
        cmd = [
            self._get_ffmpeg_cmd(), "-y",
            "-i", input_path,
            "-t", str(target_duration),
            "-c:v", "copy",
            output_path
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return res.returncode == 0
        except Exception as e:
            logger.error("Trimming failed", error=str(e))
            return False

    @staticmethod
    def _get_ffmpeg_cmd() -> str:
        """Get ffmpeg command (or path to executable)."""
        import shutil
        from app.core.config import get_settings
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
