"""
Narration Generation Agent — Audio-First, Per-Scene.

Pipeline role: runs BEFORE Manim script generation so that
real TTS durations (measured by ffprobe) can be fed into
the Manim prompt as authoritative scene durations.

Responsibilities:
  1. Refine narration text per scene via Gemini (teacher voice).
  2. Generate one .mp3 file per scene via edge-tts / gtts.
  3. Measure each file's duration with ffprobe (never trust TTS API).
  4. Populate state.scene_audios (list[SceneAudio]).
  5. Also write a human-readable transcript for downstream use.
  6. Combine all per-scene audio files into one narration_combined.mp3
     (used as a fallback if per-scene muxing isn't available).
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import google.generativeai as genai

from app.core.config import get_settings
from app.core.exceptions import NarrationError
from app.core.logging_config import get_logger
from app.prompts.narration import NARRATION_SYSTEM_PROMPT, build_narration_prompt
from app.schemas.lesson import LessonPlan
from app.schemas.narration import AudioResult, NarrationScript, NarrationSegment, SceneAudio
from app.schemas.state import VideoGenerationState
from app.services.tts_service import TTSService
from app.utils.file_utils import ensure_dir

logger = get_logger(__name__)


class NarrationAgent:
    """
    Generates refined narration and TTS audio for each scene.
    Runs BEFORE Manim rendering so real durations drive animation timing.
    """

    def __init__(self) -> None:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel(
            model_name=settings.gemini_fast_model,
            system_instruction=NARRATION_SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0.6,
                max_output_tokens=4096,
                response_mime_type="application/json",
            ),
        )
        self._settings = settings

    def run(self, state: VideoGenerationState) -> dict:
        """
        Generate narration script and per-scene TTS audio files.

        Returns:
            Partial state update with narration_script, scene_audios,
            audio_file_path, and transcript_file_path.
        """
        lesson_plan: LessonPlan | None = state.get("lesson_plan")
        if not lesson_plan:
            raise NarrationError(
                "No lesson plan available for narration generation.",
                context={},
            )

        project_id = state.get("project_id", "unknown")
        tts_engine = state.get("tts_engine", self._settings.tts_engine)
        tts_voice = state.get("tts_voice", self._settings.tts_voice)
        render_dir = state.get("render_output_dir", "./renders")

        logger.info(
            "Narration agent executing (audio-first)",
            project_id=project_id,
            tts_engine=tts_engine,
            scenes=len(lesson_plan.storyboard),
        )

        # ── Setup output directory ─────────────────────────────────────────
        audio_dir = Path(render_dir) / project_id / "audio"
        ensure_dir(str(audio_dir))

        # ── Refine narration via Gemini ────────────────────────────────────
        refined_data = self._refine_narration(lesson_plan)

        # ── Generate TTS audio per scene, measure real durations ──────────
        tts_service = TTSService(engine=tts_engine, voice=tts_voice)
        scene_audios, segments = self._generate_scene_audios(
            refined_data=refined_data,
            lesson_plan=lesson_plan,
            audio_dir=str(audio_dir),
            tts_service=tts_service,
        )

        # ── Combine audio files for fallback / transcript use ─────────────
        combined_audio_path = str(audio_dir / "narration_combined.mp3")
        audio_paths = [sa.audio_path for sa in scene_audios if sa.audio_path]
        if audio_paths:
            tts_service.merge_audio_files(audio_paths, combined_audio_path)

        # ── Write transcript ───────────────────────────────────────────────
        full_text = refined_data.get("full_narration", "") or " ".join(
            sa.text for sa in scene_audios
        )
        transcript_path = str(
            Path(render_dir) / project_id / "transcript.txt"
        )
        self._write_transcript(segments, transcript_path, lesson_plan.title)

        total_duration = sum(sa.duration_seconds for sa in scene_audios)

        narration_script = NarrationScript(
            project_id=project_id,
            title=lesson_plan.title,
            full_text=full_text,
            segments=segments,
            total_duration_seconds=total_duration,
            tts_engine=tts_engine,
            tts_voice=tts_voice,
            combined_audio_path=combined_audio_path if audio_paths else "",
            transcript_path=transcript_path,
            word_count=len(full_text.split()),
        )

        logger.info(
            "Narration agent completed",
            scenes=len(scene_audios),
            total_duration=total_duration,
            durations_per_scene=[round(sa.duration_seconds, 2) for sa in scene_audios],
        )

        return {
            "narration_script": narration_script,
            "scene_audios": scene_audios,
            "audio_file_path": combined_audio_path if audio_paths else "",
            "transcript_file_path": transcript_path,
        }

    # ─────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────

    def _refine_narration(self, lesson_plan: LessonPlan) -> dict[str, Any]:
        """Call Gemini to refine the narration script."""
        scenes_data = [scene.model_dump() for scene in lesson_plan.storyboard]
        prompt = build_narration_prompt(lesson_plan.title, scenes_data)

        try:
            response = self._model.generate_content(prompt)
            raw = response.text.strip()
            if raw.startswith("```"):
                import re
                match = re.search(r"```(?:json)?\n(.*?)```", raw, re.DOTALL)
                if match:
                    raw = match.group(1).strip()
            return json.loads(raw)
        except Exception as exc:
            logger.warning(
                "Narration refinement failed, using original script",
                error=str(exc),
            )
            return {
                "segments": [
                    {
                        "scene_number": s.scene_number,
                        "scene_title": s.scene_title,
                        "refined_narration": s.voice_segment,
                        "estimated_duration_seconds": s.estimated_duration_seconds,
                    }
                    for s in lesson_plan.storyboard
                ],
                "full_narration": lesson_plan.full_narration_script,
                "total_estimated_duration": lesson_plan.estimated_video_duration_seconds,
            }

    def _generate_scene_audios(
        self,
        refined_data: dict[str, Any],
        lesson_plan: LessonPlan,
        audio_dir: str,
        tts_service: "TTSService",
    ) -> tuple[list[SceneAudio], list[NarrationSegment]]:
        """
        Generate one TTS audio file per scene.
        Duration is measured via ffprobe — never taken from the TTS API response.

        Returns:
            (scene_audios, segments) — scene_audios drive Manim timing;
            segments are for the human-readable transcript / NarrationScript.
        """
        scene_audios: list[SceneAudio] = []
        segments: list[NarrationSegment] = []
        current_time = 0.0

        refined_segments = refined_data.get("segments", [])

        for i, scene in enumerate(lesson_plan.storyboard):
            # Find matching refined narration
            refined_text = scene.voice_segment
            for rs in refined_segments:
                if rs.get("scene_number") == scene.scene_number:
                    refined_text = rs.get("refined_narration", refined_text)
                    break

            if not refined_text.strip():
                refined_text = f"Scene {scene.scene_number}: {scene.scene_title}"

            # Generate audio
            scene_id = f"scene_{scene.scene_number:02d}"
            audio_path = str(Path(audio_dir) / f"{scene_id}.mp3")
            audio_result: AudioResult = tts_service.generate(refined_text, audio_path)

            # Measure duration via ffprobe — authoritative, not from API
            if audio_result.success and Path(audio_path).exists():
                actual_duration = self._measure_duration_ffprobe(audio_path)
            else:
                # Fallback: use estimated if TTS failed
                actual_duration = scene.estimated_duration_seconds
                logger.warning(
                    "TTS failed for scene, using estimated duration",
                    scene_id=scene_id,
                    error=audio_result.error_message,
                )

            scene_audio = SceneAudio(
                scene_id=scene_id,
                scene_number=scene.scene_number,
                scene_title=scene.scene_title,
                text=refined_text,
                audio_path=audio_path if audio_result.success else "",
                duration_seconds=actual_duration,
                word_timestamps=audio_result.word_timestamps,
            )
            scene_audios.append(scene_audio)

            # Build NarrationSegment for transcript / NarrationScript compatibility
            segment = NarrationSegment(
                scene_number=scene.scene_number,
                scene_title=scene.scene_title,
                text=refined_text,
                start_time_seconds=current_time,
                end_time_seconds=current_time + actual_duration,
                duration_seconds=actual_duration,
                audio_file_path=audio_path if audio_result.success else "",
                word_count=len(refined_text.split()),
            )
            segments.append(segment)
            current_time += actual_duration

            logger.info(
                "Scene audio generated",
                scene_id=scene_id,
                duration=round(actual_duration, 3),
                audio_path=audio_path,
            )

        return scene_audios, segments

    @staticmethod
    def _measure_duration_ffprobe(audio_path: str) -> float:
        """
        Measure audio duration using ffprobe.
        This is the authoritative measurement — do NOT use TTS API reported length.
        """
        import subprocess
        import json as _json
        import shutil

        ffprobe_cmd = "ffprobe" if shutil.which("ffprobe") else None

        if ffprobe_cmd:
            try:
                result = subprocess.run(
                    [
                        "ffprobe",
                        "-v", "error",
                        "-show_entries", "format=duration",
                        "-of", "json",
                        audio_path,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    data = _json.loads(result.stdout)
                    return float(data["format"]["duration"])
            except Exception as exc:
                logger.debug("ffprobe failed, falling back to ffmpeg", error=str(exc))

        # ffmpeg fallback
        try:
            from app.services.synchronization_service import get_ffmpeg_cmd
            import re
            result = subprocess.run(
                [get_ffmpeg_cmd(), "-i", audio_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", result.stderr or "")
            if match:
                hours, minutes, seconds = match.groups()
                return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        except Exception as exc:
            logger.debug("ffmpeg duration fallback failed", error=str(exc))

        # Last resort: file-size heuristic (~8KB/s for 128kbps MP3)
        try:
            size = Path(audio_path).stat().st_size
            return max(1.0, size / 16_000)
        except Exception:
            return 5.0

    def _write_transcript(
        self,
        segments: list[NarrationSegment],
        path: str,
        title: str,
    ) -> None:
        """Write a plain-text transcript with timestamps."""
        lines = [
            f"TRANSCRIPT: {title}",
            f"Generated: {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            "=" * 60,
            "",
        ]
        for seg in segments:
            start = self._format_time(seg.start_time_seconds)
            end = self._format_time(seg.end_time_seconds)
            lines.append(f"[{start} → {end}] Scene {seg.scene_number}: {seg.scene_title}")
            lines.append(seg.text)
            lines.append("")

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text("\n".join(lines), encoding="utf-8")

    @staticmethod
    def _format_time(seconds: float) -> str:
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"
