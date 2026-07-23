"""
Narration Generation Agent.

Responsibilities:
- Refine narration script using Gemini (teacher voice)
- Generate per-scene TTS audio using edge-tts or gtts
- Calculate timestamps and durations
- Return NarrationScript with AudioResult per segment
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
from app.schemas.narration import NarrationScript, NarrationSegment
from app.schemas.state import VideoGenerationState
from app.services.tts_service import TTSService
from app.utils.file_utils import ensure_dir

logger = get_logger(__name__)


class NarrationAgent:
    """
    Generates refined narration and TTS audio for each scene.
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
        Generate narration script and TTS audio files.

        Returns:
            Partial state update with narration_script and audio_file_path.
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
            "Narration agent executing",
            project_id=project_id,
            tts_engine=tts_engine,
            scenes=len(lesson_plan.storyboard),
        )

        # ── Setup output directory ─────────────────────────────────────────
        audio_dir = Path(render_dir) / project_id / "audio"
        ensure_dir(str(audio_dir))

        # ── Refine narration via Gemini ────────────────────────────────────
        refined_data = self._refine_narration(lesson_plan)

        # ── Generate TTS audio per segment ─────────────────────────────────
        tts_service = TTSService(engine=tts_engine, voice=tts_voice)
        segments = self._generate_audio_segments(
            refined_data=refined_data,
            lesson_plan=lesson_plan,
            audio_dir=str(audio_dir),
            tts_service=tts_service,
        )

        # ── Combine audio files ────────────────────────────────────────────
        combined_audio_path = str(audio_dir / "narration_combined.mp3")
        audio_paths = [seg.audio_file_path for seg in segments if seg.audio_file_path]
        if audio_paths:
            tts_service.merge_audio_files(audio_paths, combined_audio_path)

        # ── Write transcript ───────────────────────────────────────────────
        full_text = refined_data.get("full_narration", "") or " ".join(
            seg.text for seg in segments
        )
        transcript_path = str(
            Path(render_dir) / project_id / "transcript.txt"
        )
        self._write_transcript(segments, transcript_path, lesson_plan.title)

        total_duration = sum(seg.duration_seconds for seg in segments)

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
            segments=len(segments),
            total_duration=total_duration,
            combined_audio=combined_audio_path,
        )

        return {
            "narration_script": narration_script,
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
            # Fallback: use original voice_segments
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

    def _generate_audio_segments(
        self,
        refined_data: dict[str, Any],
        lesson_plan: LessonPlan,
        audio_dir: str,
        tts_service: "TTSService",
    ) -> list[NarrationSegment]:
        """Generate TTS audio for each narration segment."""
        segments: list[NarrationSegment] = []
        current_time = 0.0

        refined_segments = refined_data.get("segments", [])

        for i, scene in enumerate(lesson_plan.storyboard):
            # Find matching refined narration
            refined_text = scene.voice_segment
            estimated_duration = scene.estimated_duration_seconds

            for rs in refined_segments:
                if rs.get("scene_number") == scene.scene_number:
                    refined_text = rs.get("refined_narration", refined_text)
                    estimated_duration = float(
                        rs.get("estimated_duration_seconds", estimated_duration)
                    )
                    break

            if not refined_text.strip():
                refined_text = f"Scene {scene.scene_number}: {scene.scene_title}"

            # Generate audio
            audio_path = str(
                Path(audio_dir) / f"scene_{scene.scene_number:02d}.mp3"
            )
            audio_result = tts_service.generate(refined_text, audio_path)

            actual_duration = (
                audio_result.duration_seconds
                if audio_result.success and audio_result.duration_seconds > 0
                else estimated_duration
            )

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

        return segments

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
