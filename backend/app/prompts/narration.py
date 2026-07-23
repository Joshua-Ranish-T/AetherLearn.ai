"""
Narration Generation Prompt Templates.

Guides Gemini to refine and finalize narration scripts that sound
like an experienced, engaging teacher.
"""

from __future__ import annotations

NARRATION_SYSTEM_PROMPT = """You are an experienced educational narrator and instructional designer.
Your narrations should sound like the world's best teacher — clear, engaging, encouraging,
and intellectually stimulating.

Style guidelines:
- Use conversational academic language (not too formal, not too casual)
- Build suspense before revealing answers
- Use rhetorical questions to engage the viewer
- Explain WHY concepts matter, not just what they are
- Use analogies and real-world connections
- Pace is important — allow time for concepts to sink in
- Transitions between topics should feel smooth and natural"""


def build_narration_prompt(
    lesson_title: str,
    storyboard_scenes: list[dict],
) -> str:
    scenes_text = ""
    for scene in storyboard_scenes:
        scenes_text += f"""
Scene {scene['scene_number']}: {scene['scene_title']}
Duration: ~{scene['estimated_duration_seconds']} seconds
Visual: {scene['animation_description']}
Draft narration: {scene['voice_segment']}
---"""

    return f"""Refine the narration for this educational video about "{lesson_title}".

The narration must:
1. Sound like an experienced, engaging teacher
2. Fit naturally within each scene's estimated duration
3. Use clear, precise language appropriate for the subject
4. Build understanding progressively
5. Include natural transitions between scenes

Scenes to narrate:
{scenes_text}

For each scene, provide refined narration text. Return as JSON:
{{
  "segments": [
    {{
      "scene_number": 1,
      "scene_title": "Scene title",
      "refined_narration": "The polished narration text for this scene...",
      "estimated_duration_seconds": 15,
      "speaking_notes": "Emphasize X, pause after Y"
    }}
  ],
  "full_narration": "Complete narration text joining all segments naturally...",
  "total_estimated_duration": 120
}}

Return ONLY the JSON object."""
