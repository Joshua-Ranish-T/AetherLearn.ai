"""
TTS Service — Text-to-Speech audio generation.

Supports:
- edge-tts (primary): Microsoft Edge TTS (free, high quality)
- gtts (fallback): Google Text-to-Speech

Provides audio duration measurement using mutagen/pydub.
"""

from __future__ import annotations

import asyncio
import subprocess
import time
from pathlib import Path

from app.core.exceptions import TTSError
from app.core.logging_config import get_logger
from app.schemas.narration import AudioResult

logger = get_logger(__name__)


class TTSService:
    """
    Text-to-Speech service abstraction.
    Supports edge-tts and gtts engines.
    """

    def __init__(self, engine: str = "edge-tts", voice: str = "en-US-AriaNeural") -> None:
        self.engine = engine
        self.voice = voice

    def generate(self, text: str, output_path: str) -> AudioResult:
        """
        Generate audio from text and save to output_path.

        Args:
            text: The text to synthesize.
            output_path: Local file path for the output MP3.

        Returns:
            AudioResult with success status and duration.
        """
        if not text.strip():
            return AudioResult(
                success=False,
                error_message="Empty text provided to TTS",
                tts_engine=self.engine,
            )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if self.engine == "edge-tts":
            return self._generate_edge_tts(text, output_path)
        elif self.engine == "gtts":
            return self._generate_gtts(text, output_path)
        else:
            # Attempt edge-tts as default
            return self._generate_edge_tts(text, output_path)

    def merge_audio_files(
        self, audio_paths: list[str], output_path: str
    ) -> bool:
        """
        Merge multiple audio files into one using FFmpeg.

        Args:
            audio_paths: List of paths to audio files.
            output_path: Output merged file path.

        Returns:
            True if successful, False otherwise.
        """
        if not audio_paths:
            return False

        if len(audio_paths) == 1:
            # Just copy the single file
            import shutil
            shutil.copy2(audio_paths[0], output_path)
            return True

        try:
            # Build FFmpeg concat command
            input_args = []
            for path in audio_paths:
                if Path(path).exists():
                    input_args.extend(["-i", path])

            if not input_args:
                return False

            filter_complex = (
                f"{''.join(f'[{i}:0]' for i in range(len(audio_paths)))}"
                f"concat=n={len(audio_paths)}:v=0:a=1[out]"
            )

            from app.services.synchronization_service import get_ffmpeg_cmd

            command = [
                get_ffmpeg_cmd(), "-y",
                *input_args,
                "-filter_complex", filter_complex,
                "-map", "[out]",
                "-codec:a", "libmp3lame",
                "-q:a", "2",
                output_path,
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                logger.info("Audio merged", output=output_path, count=len(audio_paths))
                return True
            else:
                logger.warning("FFmpeg audio merge failed", stderr=result.stderr[:200])
                # Fallback: just use the first file
                import shutil
                shutil.copy2(audio_paths[0], output_path)
                return True

        except Exception as exc:
            logger.warning("Audio merge error", error=str(exc))
            try:
                import shutil
                shutil.copy2(audio_paths[0], output_path)
                return True
            except Exception:
                return False

    # ─────────────────────────────────────────────────────────────────────
    # Private engine implementations
    # ─────────────────────────────────────────────────────────────────────

    def _generate_edge_tts(self, text: str, output_path: str) -> AudioResult:
        """Generate audio using Microsoft Edge TTS, capturing word timestamps."""
        try:
            import edge_tts
        except ImportError:
            logger.warning("edge-tts not installed, falling back to gtts")
            return self._generate_gtts(text, output_path)

        try:
            loop = asyncio.new_event_loop()
            try:
                word_timestamps = loop.run_until_complete(
                    self._async_edge_tts(text, output_path, self.voice)
                )
            finally:
                loop.close()

            duration = self._get_audio_duration(output_path)
            return AudioResult(
                success=True,
                audio_file_path=output_path,
                duration_seconds=duration,
                tts_engine="edge-tts",
                voice=self.voice,
                word_timestamps=word_timestamps,
            )
        except Exception as exc:
            logger.warning(
                "edge-tts failed, trying gtts",
                error=str(exc),
                voice=self.voice,
            )
            return self._generate_gtts(text, output_path)

    @staticmethod
    async def _async_edge_tts(text: str, output_path: str, voice: str) -> list[dict]:
        """Async edge-tts call returning word timestamps."""
        import edge_tts
        communicate = edge_tts.Communicate(text=text, voice=voice)
        
        word_timestamps = []
        with open(output_path, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # offset and duration are in 100-nanosecond units
                    start_sec = chunk["offset"] / 10_000_000
                    dur_sec = chunk["duration"] / 10_000_000
                    word_timestamps.append({
                        "word": chunk["text"],
                        "start_time": start_sec,
                        "end_time": start_sec + dur_sec
                    })
                    
        return word_timestamps

    def _generate_gtts(self, text: str, output_path: str) -> AudioResult:
        """Generate audio using Google TTS."""
        try:
            from gtts import gTTS
        except ImportError as exc:
            raise TTSError(
                "Neither edge-tts nor gtts is installed. Run: pip install edge-tts gtts"
            ) from exc

        try:
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(output_path)
            duration = self._get_audio_duration(output_path)
            return AudioResult(
                success=True,
                audio_file_path=output_path,
                duration_seconds=duration,
                tts_engine="gtts",
                voice="en",
            )
        except Exception as exc:
            return AudioResult(
                success=False,
                error_message=str(exc),
                tts_engine="gtts",
            )

    @staticmethod
    def _get_audio_duration(audio_path: str) -> float:
        """Get audio file duration in seconds using ffprobe or ffmpeg."""
        import shutil
        if shutil.which("ffprobe"):
            try:
                result = subprocess.run(
                    [
                        "ffprobe",
                        "-v", "error",
                        "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1",
                        audio_path,
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
            from app.services.synchronization_service import get_ffmpeg_cmd
            import re
            ffmpeg_bin = get_ffmpeg_cmd()
            result = subprocess.run(
                [ffmpeg_bin, "-i", audio_path],
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

        # Estimate based on file size (~1 second per 8KB for MP3)
        try:
            text_size = Path(audio_path).stat().st_size
            return max(1.0, text_size / 8000)
        except Exception:
            return 5.0
